import random
from typing import Any

from ..utils.base import BaseGenerator
from ..utils.schema_models import BooleanFieldConfig


class BooleanGenerator(BaseGenerator):
    """
    Generator for boolean data with configurable probability distribution.
    """

    def __init__(self, field_name: str, config: BooleanFieldConfig):
        """
        Initialize boolean generator with field configuration.

        Args:
            field_name: Name of the field being generated
            config: Boolean field configuration
        """
        super().__init__(field_name, config)
        self.boolean_config = config

    def generate(self) -> bool:
        """
        Generate a single boolean value based on configured probability.

        Returns:
            Generated boolean value
        """
        return random.random() < self.boolean_config.true_probability

    def generate_batch(self, count: int) -> list[bool]:
        """
        Generate multiple boolean values efficiently.

        Args:
            count: Number of values to generate

        Returns:
            List of generated boolean values
        """
        true_prob = self.boolean_config.true_probability
        return [random.random() < true_prob for _ in range(count)]

    def get_distribution_stats(self, sample_size: int = 1000) -> dict[str, float]:
        """
        Generate sample data and return distribution statistics.

        Args:
            sample_size: Number of samples to generate for statistics

        Returns:
            Dictionary with distribution statistics
        """
        sample = self.generate_batch(sample_size)
        true_count = sum(sample)
        false_count = sample_size - true_count

        return {
            "true_probability": true_count / sample_size,
            "false_probability": false_count / sample_size,
            "true_count": true_count,
            "false_count": false_count,
            "sample_size": sample_size,
        }

    def validate_generated_value(self, value: Any) -> bool:
        """
        Validate that generated value is a boolean.

        Args:
            value: Generated value to validate

        Returns:
            True if value is valid, False otherwise
        """
        return isinstance(value, bool)
