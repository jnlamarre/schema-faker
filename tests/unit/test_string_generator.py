import pytest
import uuid
import re

from schema_faker.generators.string import StringGenerator
from schema_faker.utils.schema_models import StringFieldConfig, StringSubtype


class TestStringGenerator:
    """Test cases for StringGenerator."""

    def test_random_string_generation(self):
        """Test random string generation."""
        config = StringFieldConfig(
            subtype=StringSubtype.RANDOM,
            min_length=5,
            max_length=10
        )
        generator = StringGenerator("test_random", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            assert 5 <= len(value) <= 10

    def test_name_generation(self):
        """Test name generation using Faker."""
        config = StringFieldConfig(subtype=StringSubtype.NAME)
        generator = StringGenerator("test_name", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            assert len(value) > 0
            # Names typically contain spaces or letters
            assert any(c.isalpha() or c.isspace() for c in value)

    def test_first_name_generation(self):
        """Test first name generation."""
        config = StringFieldConfig(subtype=StringSubtype.FIRST_NAME)
        generator = StringGenerator("test_first", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            assert len(value) > 0
            assert value.isalpha() or "'" in value or "-" in value  # Handle names like O'Connor or Jean-Luc

    def test_last_name_generation(self):
        """Test last name generation."""
        config = StringFieldConfig(subtype=StringSubtype.LAST_NAME)
        generator = StringGenerator("test_last", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            assert len(value) > 0

    def test_email_generation(self):
        """Test email generation."""
        config = StringFieldConfig(subtype=StringSubtype.EMAIL)
        generator = StringGenerator("test_email", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            assert "@" in value
            assert "." in value.split("@")[-1]
            # Basic email validation
            assert len(value.split("@")) == 2

    def test_address_generation(self):
        """Test address generation."""
        config = StringFieldConfig(subtype=StringSubtype.ADDRESS)
        generator = StringGenerator("test_address", config)
        
        for _ in range(10):
            value = generator.generate()
            assert isinstance(value, str)
            assert len(value) > 0
            # Address should contain some digits and letters
            assert any(c.isdigit() for c in value)
            assert any(c.isalpha() for c in value)

    def test_phone_generation(self):
        """Test phone number generation."""
        config = StringFieldConfig(subtype=StringSubtype.PHONE)
        generator = StringGenerator("test_phone", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            assert len(value) > 0
            # Phone should contain some digits
            assert any(c.isdigit() for c in value)

    def test_company_generation(self):
        """Test company name generation."""
        config = StringFieldConfig(subtype=StringSubtype.COMPANY)
        generator = StringGenerator("test_company", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            assert len(value) > 0

    def test_uuid_generation(self):
        """Test UUID generation."""
        config = StringFieldConfig(subtype=StringSubtype.UUID)
        generator = StringGenerator("test_uuid", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            # Should be valid UUID format
            uuid_obj = uuid.UUID(value)
            assert str(uuid_obj) == value

    def test_ip_address_generation(self):
        """Test IP address generation."""
        config = StringFieldConfig(subtype=StringSubtype.IP_ADDRESS)
        generator = StringGenerator("test_ip", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            # Basic IPv4 validation
            parts = value.split(".")
            assert len(parts) == 4
            for part in parts:
                assert 0 <= int(part) <= 255

    def test_choices_generation(self):
        """Test generation from predefined choices."""
        choices = ["option1", "option2", "option3"]
        config = StringFieldConfig(
            subtype=StringSubtype.RANDOM,
            choices=choices
        )
        generator = StringGenerator("test_choices", config)
        
        for _ in range(3):  # Even smaller for choices test
            value = generator.generate()
            assert value in choices

    def test_length_constraints_truncation(self):
        """Test that long generated values are truncated."""
        config = StringFieldConfig(
            subtype=StringSubtype.EMAIL,
            max_length=10
        )
        generator = StringGenerator("test_truncate", config)
        
        value = generator.generate()
        assert len(value) <= 10

    def test_length_constraints_padding(self):
        """Test that short generated values are padded."""
        config = StringFieldConfig(
            subtype=StringSubtype.RANDOM,
            min_length=20,
            max_length=25
        )
        generator = StringGenerator("test_pad", config)
        
        value = generator.generate()
        assert 20 <= len(value) <= 25

    def test_pattern_generation(self):
        """Test generation based on regex patterns."""
        config = StringFieldConfig(
            subtype=StringSubtype.RANDOM,
            pattern="\\d{3}-\\d{3}-\\d{4}"  # Phone number pattern
        )
        generator = StringGenerator("test_pattern", config)
        
        value = generator.generate()
        assert isinstance(value, str)
        # Should match basic phone pattern structure
        assert len(value.replace("-", "")) >= 9

    def test_batch_generation_optimized(self):
        """Test optimized batch generation."""
        config = StringFieldConfig(subtype=StringSubtype.EMAIL)
        generator = StringGenerator("test_batch", config)
        
        batch = generator.generate_batch_optimized(30)
        assert len(batch) == 30
        assert all(isinstance(v, str) and "@" in v for v in batch)

    def test_validation(self):
        """Test value validation."""
        config = StringFieldConfig(
            subtype=StringSubtype.EMAIL,
            min_length=5,
            max_length=50
        )
        generator = StringGenerator("test_validation", config)
        
        # Valid email
        assert generator.validate_generated_value("test@example.com") is True
        
        # Invalid - not string
        assert generator.validate_generated_value(123) is False
        
        # Invalid - too short
        assert generator.validate_generated_value("a@b") is False
        
        # Invalid - no @ symbol
        assert generator.validate_generated_value("notanemail") is False

    def test_uuid_validation(self):
        """Test UUID validation."""
        config = StringFieldConfig(subtype=StringSubtype.UUID)
        generator = StringGenerator("test_uuid_val", config)
        
        # Valid UUID
        valid_uuid = str(uuid.uuid4())
        assert generator.validate_generated_value(valid_uuid) is True
        
        # Invalid UUID
        assert generator.validate_generated_value("not-a-uuid") is False

    def test_ip_validation(self):
        """Test IP address validation."""
        config = StringFieldConfig(subtype=StringSubtype.IP_ADDRESS)
        generator = StringGenerator("test_ip_val", config)
        
        # Valid IP
        assert generator.validate_generated_value("192.168.1.1") is True
        
        # Invalid IP - out of range
        assert generator.validate_generated_value("256.1.1.1") is False
        
        # Invalid IP - wrong format
        assert generator.validate_generated_value("192.168.1") is False

    def test_choices_validation(self):
        """Test validation with choices."""
        choices = ["red", "green", "blue"]
        config = StringFieldConfig(
            subtype=StringSubtype.RANDOM,
            choices=choices
        )
        generator = StringGenerator("test_choices_val", config)
        
        assert generator.validate_generated_value("red") is True
        assert generator.validate_generated_value("yellow") is False

    def test_seed_reproducibility(self):
        """Test that setting seed produces reproducible results."""
        config = StringFieldConfig(subtype=StringSubtype.NAME)
        
        generator1 = StringGenerator("test_seed1", config)
        generator1.set_seed(42)
        
        generator2 = StringGenerator("test_seed2", config)
        generator2.set_seed(42)
        
        values1 = [generator1.generate() for _ in range(10)]
        values2 = [generator2.generate() for _ in range(10)]
        
        assert values1 == values2