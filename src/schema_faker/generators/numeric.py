import random
from decimal import Decimal, getcontext
from typing import Any, Union

from ..utils.base import BaseGenerator
from ..utils.schema_models import NumericFieldConfig, NumericSubtype


class NumericGenerator(BaseGenerator):
    """
    Generator for numeric data with support for integers, floats, and decimals.
    Supports min/max ranges and statistical distributions.
    """

    def __init__(self, field_name: str, config: NumericFieldConfig):
        """
        Initialize numeric generator with field configuration.

        Args:
            field_name: Name of the field being generated
            config: Numeric field configuration
        """
        super().__init__(field_name, config)
        self.numeric_config = config
        
        # Set default ranges based on subtype if not specified
        self._set_default_ranges()
        
        # Set decimal precision for decimal types
        if config.subtype == NumericSubtype.DECIMAL and config.precision:
            getcontext().prec = max(config.precision + 10, 28)  # Ensure sufficient precision

    def _set_default_ranges(self) -> None:
        """Set reasonable default min/max values based on numeric subtype."""
        if self.numeric_config.min_value is None or self.numeric_config.max_value is None:
            defaults = {
                NumericSubtype.INTEGER: (0, 2147483647),  # 32-bit signed int range
                NumericSubtype.FLOAT: (0.0, 1000000.0),
                NumericSubtype.DECIMAL: (0.0, 1000000.0)
            }
            
            default_min, default_max = defaults[self.numeric_config.subtype]
            
            if self.numeric_config.min_value is None:
                self.numeric_config.min_value = default_min
            if self.numeric_config.max_value is None:
                self.numeric_config.max_value = default_max

    def generate(self) -> Union[int, float, Decimal]:
        """
        Generate a single numeric value based on configuration.

        Returns:
            Generated numeric value (int, float, or Decimal)
        """
        min_val = self.numeric_config.min_value
        max_val = self.numeric_config.max_value
        
        if min_val > max_val:
            self.logger.warning(
                f"Min value {min_val} is greater than max value {max_val}. Swapping values."
            )
            min_val, max_val = max_val, min_val

        if self.numeric_config.subtype == NumericSubtype.INTEGER:
            return self._generate_integer(int(min_val), int(max_val))
        
        elif self.numeric_config.subtype == NumericSubtype.FLOAT:
            return self._generate_float(float(min_val), float(max_val))
        
        elif self.numeric_config.subtype == NumericSubtype.DECIMAL:
            return self._generate_decimal(float(min_val), float(max_val))
        
        else:
            raise ValueError(f"Unsupported numeric subtype: {self.numeric_config.subtype}")

    def _generate_integer(self, min_val: int, max_val: int) -> int:
        """
        Generate a random integer within specified range.

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)

        Returns:
            Random integer
        """
        return random.randint(min_val, max_val)

    def _generate_float(self, min_val: float, max_val: float) -> float:
        """
        Generate a random float within specified range.

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (exclusive)

        Returns:
            Random float
        """
        value = random.uniform(min_val, max_val)
        
        # Round to precision if specified
        if self.numeric_config.precision is not None:
            value = round(value, self.numeric_config.precision)
        
        return value

    def _generate_decimal(self, min_val: float, max_val: float) -> Decimal:
        """
        Generate a random Decimal within specified range.

        Args:
            min_val: Minimum value (inclusive)
            max_val: Maximum value (exclusive)

        Returns:
            Random Decimal with specified precision
        """
        # Generate as float first, then convert to Decimal for precision control
        float_value = random.uniform(min_val, max_val)
        
        if self.numeric_config.precision is not None:
            # Create format string for specified decimal places
            decimal_places = self.numeric_config.precision
            format_str = f"{{:.{decimal_places}f}}"
            formatted_value = format_str.format(float_value)
            return Decimal(formatted_value)
        else:
            return Decimal(str(float_value))

    def generate_with_distribution(self, distribution: str = "uniform", **kwargs) -> Union[int, float, Decimal]:
        """
        Generate numeric value using specified statistical distribution.

        Args:
            distribution: Distribution type ("uniform", "normal", "exponential")
            **kwargs: Distribution-specific parameters

        Returns:
            Generated numeric value following specified distribution
        """
        min_val = float(self.numeric_config.min_value)
        max_val = float(self.numeric_config.max_value)
        
        if distribution == "uniform":
            # Default uniform distribution (same as generate())
            raw_value = random.uniform(min_val, max_val)
        
        elif distribution == "normal":
            # Normal distribution with mean at midpoint and configurable std dev
            mean = kwargs.get("mean", (min_val + max_val) / 2)
            std_dev = kwargs.get("std_dev", (max_val - min_val) / 6)  # 99.7% within range
            
            raw_value = random.normalvariate(mean, std_dev)
            # Clamp to valid range
            raw_value = max(min_val, min(max_val, raw_value))
        
        elif distribution == "exponential":
            # Exponential distribution scaled to fit range
            lambda_param = kwargs.get("lambda", 1.0)
            raw_value = random.expovariate(lambda_param)
            # Scale to fit range
            raw_value = min_val + (raw_value % (max_val - min_val))
        
        else:
            raise ValueError(f"Unsupported distribution: {distribution}")

        # Convert to appropriate type based on subtype
        if self.numeric_config.subtype == NumericSubtype.INTEGER:
            return int(raw_value)
        elif self.numeric_config.subtype == NumericSubtype.FLOAT:
            if self.numeric_config.precision is not None:
                return round(raw_value, self.numeric_config.precision)
            return raw_value
        elif self.numeric_config.subtype == NumericSubtype.DECIMAL:
            if self.numeric_config.precision is not None:
                decimal_places = self.numeric_config.precision
                format_str = f"{{:.{decimal_places}f}}"
                formatted_value = format_str.format(raw_value)
                return Decimal(formatted_value)
            return Decimal(str(raw_value))

    def validate_generated_value(self, value: Any) -> bool:
        """
        Validate that generated value meets configuration constraints.

        Args:
            value: Generated value to validate

        Returns:
            True if value is valid, False otherwise
        """
        if not isinstance(value, (int, float, Decimal)):
            return False
        
        min_val = self.numeric_config.min_value
        max_val = self.numeric_config.max_value
        
        # Convert to float for comparison if dealing with Decimal
        if isinstance(value, Decimal):
            value = float(value)
        
        return min_val <= value <= max_val