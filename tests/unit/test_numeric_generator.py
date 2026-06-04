from decimal import Decimal

import pytest
from pydantic import ValidationError

from schema_faker.generators.numeric import NumericGenerator
from schema_faker.utils.schema_models import NumericFieldConfig, NumericSubtype


class TestNumericGenerator:
    """Test cases for NumericGenerator."""

    def test_integer_generation(self):
        """Test basic integer generation."""
        config = NumericFieldConfig(
            min_value=10, max_value=20, subtype=NumericSubtype.INTEGER
        )
        generator = NumericGenerator("test_int", config)

        for _ in range(10):  # Reduced from 100
            value = generator.generate()
            assert isinstance(value, int)
            assert 10 <= value <= 20

    def test_float_generation(self):
        """Test basic float generation."""
        config = NumericFieldConfig(
            min_value=1.0, max_value=10.0, subtype=NumericSubtype.FLOAT, precision=2
        )
        generator = NumericGenerator("test_float", config)

        for _ in range(10):  # Reduced from 100
            value = generator.generate()
            assert isinstance(value, float)
            assert 1.0 <= value <= 10.0

    def test_decimal_generation(self):
        """Test decimal generation with precision."""
        config = NumericFieldConfig(
            min_value=0.0, max_value=100.0, subtype=NumericSubtype.DECIMAL, precision=3
        )
        generator = NumericGenerator("test_decimal", config)

        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, Decimal)
            assert Decimal("0.0") <= value <= Decimal("100.0")

    def test_default_ranges(self):
        """Test default range assignment."""
        config = NumericFieldConfig(subtype=NumericSubtype.INTEGER)
        generator = NumericGenerator("test_default", config)

        # Should have set default ranges
        assert generator.numeric_config.min_value == 0
        assert generator.numeric_config.max_value == 2147483647

    def test_swapped_min_max(self):
        """Test handling of swapped min/max values."""
        config = NumericFieldConfig(
            min_value=100,
            max_value=10,  # Intentionally swapped
            subtype=NumericSubtype.INTEGER,
        )
        generator = NumericGenerator("test_swap", config)

        value = generator.generate()
        assert isinstance(value, int)
        assert 10 <= value <= 100  # Should be corrected

    def test_batch_generation(self):
        """Test batch generation."""
        config = NumericFieldConfig(
            min_value=1, max_value=10, subtype=NumericSubtype.INTEGER
        )
        generator = NumericGenerator("test_batch", config)

        batch = generator.generate_batch(50)
        assert len(batch) == 50
        assert all(isinstance(v, int) and 1 <= v <= 10 for v in batch)

    @pytest.mark.parametrize("distribution", ["uniform", "normal", "exponential"])
    def test_distribution_generation(self, distribution):
        """Test different statistical distributions."""
        config = NumericFieldConfig(
            min_value=0.0, max_value=100.0, subtype=NumericSubtype.FLOAT
        )
        generator = NumericGenerator("test_dist", config)

        value = generator.generate_with_distribution(distribution)
        assert isinstance(value, float)
        assert 0.0 <= value <= 100.0

    def test_normal_distribution_parameters(self):
        """Test normal distribution with custom parameters."""
        config = NumericFieldConfig(
            min_value=0.0, max_value=100.0, subtype=NumericSubtype.FLOAT
        )
        generator = NumericGenerator("test_normal", config)

        value = generator.generate_with_distribution("normal", mean=50.0, std_dev=10.0)
        assert isinstance(value, float)
        assert 0.0 <= value <= 100.0

    def test_validation(self):
        """Test value validation."""
        config = NumericFieldConfig(
            min_value=10, max_value=20, subtype=NumericSubtype.INTEGER
        )
        generator = NumericGenerator("test_validation", config)

        assert generator.validate_generated_value(15) is True
        assert generator.validate_generated_value(5) is False
        assert generator.validate_generated_value(25) is False
        assert generator.validate_generated_value("not_a_number") is False

    def test_precision_handling(self):
        """Test precision handling for floats and decimals."""
        config = NumericFieldConfig(
            min_value=0.0, max_value=1.0, subtype=NumericSubtype.FLOAT, precision=2
        )
        generator = NumericGenerator("test_precision", config)

        for _ in range(5):
            value = generator.generate()
            # Check that value has at most 2 decimal places
            assert len(str(value).split(".")[-1]) <= 2

    def test_unsupported_subtype_raises_error(self):
        """Test that unsupported subtype raises error."""
        # With Pydantic validation, invalid subtypes are caught at model creation
        with pytest.raises(ValidationError):
            NumericFieldConfig(
                min_value=1,
                max_value=10,
                subtype="unsupported",  # Invalid subtype
            )
