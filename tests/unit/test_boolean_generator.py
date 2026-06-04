import pytest

from schema_faker.generators.boolean import BooleanGenerator
from schema_faker.utils.schema_models import BooleanFieldConfig


class TestBooleanGenerator:
    """Test cases for BooleanGenerator."""

    def test_basic_boolean_generation(self):
        """Test basic boolean generation."""
        config = BooleanFieldConfig(true_probability=0.5)
        generator = BooleanGenerator("test_bool", config)

        for _ in range(10):
            value = generator.generate()
            assert isinstance(value, bool)

    def test_always_true(self):
        """Test generation with 100% true probability."""
        config = BooleanFieldConfig(true_probability=1.0)
        generator = BooleanGenerator("test_true", config)

        for _ in range(5):
            value = generator.generate()
            assert value is True

    def test_always_false(self):
        """Test generation with 0% true probability."""
        config = BooleanFieldConfig(true_probability=0.0)
        generator = BooleanGenerator("test_false", config)

        for _ in range(5):
            value = generator.generate()
            assert value is False

    def test_batch_generation(self):
        """Test batch generation."""
        config = BooleanFieldConfig(true_probability=0.7)
        generator = BooleanGenerator("test_batch", config)

        batch = generator.generate_batch(20)
        assert len(batch) == 20
        assert all(isinstance(v, bool) for v in batch)

        # Check approximate distribution (70% true expected)
        true_count = sum(batch)
        true_ratio = true_count / len(batch)
        # Allow some variance in random distribution
        assert 0.5 < true_ratio < 0.9

    def test_distribution_stats(self):
        """Test distribution statistics calculation."""
        config = BooleanFieldConfig(true_probability=0.3)
        generator = BooleanGenerator("test_stats", config)

        stats = generator.get_distribution_stats(sample_size=1000)

        assert "true_probability" in stats
        assert "false_probability" in stats
        assert "true_count" in stats
        assert "false_count" in stats
        assert "sample_size" in stats

        assert stats["sample_size"] == 1000
        assert stats["true_count"] + stats["false_count"] == 1000

        # Check that probabilities add up to 1
        assert abs(stats["true_probability"] + stats["false_probability"] - 1.0) < 0.001

        # Check approximate distribution (30% true expected)
        assert 0.2 < stats["true_probability"] < 0.4

    def test_validation(self):
        """Test value validation."""
        config = BooleanFieldConfig(true_probability=0.5)
        generator = BooleanGenerator("test_validation", config)

        assert generator.validate_generated_value(True) is True
        assert generator.validate_generated_value(False) is True
        assert generator.validate_generated_value("true") is False
        assert generator.validate_generated_value(1) is False
        assert generator.validate_generated_value(0) is False
        assert generator.validate_generated_value(None) is False

    @pytest.mark.parametrize("probability", [0.0, 0.25, 0.5, 0.75, 1.0])
    def test_various_probabilities(self, probability):
        """Test generation with various probability values."""
        config = BooleanFieldConfig(true_probability=probability)
        generator = BooleanGenerator("test_prob", config)

        sample = generator.generate_batch(200)
        true_ratio = sum(sample) / len(sample)

        # Allow reasonable variance for random generation
        expected = probability
        tolerance = 0.2 if expected not in [0.0, 1.0] else 0.0

        assert abs(true_ratio - expected) <= tolerance
