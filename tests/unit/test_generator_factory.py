import pytest

from schema_faker.generators.factory import GeneratorFactory
from schema_faker.generators import (
    NumericGenerator,
    StringGenerator,
    DateTimeGenerator,
    BooleanGenerator
)
from schema_faker.utils.schema_models import (
    FieldDefinition,
    DataType,
    NumericFieldConfig,
    StringFieldConfig,
    DateFieldConfig,
    BooleanFieldConfig,
    NumericSubtype,
    StringSubtype
)


class TestGeneratorFactory:
    """Test cases for GeneratorFactory."""

    def test_create_numeric_generator(self):
        """Test creation of numeric generator."""
        field_def = FieldDefinition(
            name="age",
            type=DataType.NUMERIC,
            config=NumericFieldConfig(
                min_value=18,
                max_value=100,
                subtype=NumericSubtype.INTEGER
            )
        )
        
        generator = GeneratorFactory.create_generator(field_def)
        assert isinstance(generator, NumericGenerator)
        assert generator.field_name == "age"

    def test_create_string_generator(self):
        """Test creation of string generator."""
        field_def = FieldDefinition(
            name="name",
            type=DataType.STRING,
            config=StringFieldConfig(
                subtype=StringSubtype.NAME,
                min_length=2,
                max_length=50
            )
        )
        
        generator = GeneratorFactory.create_generator(field_def)
        assert isinstance(generator, StringGenerator)
        assert generator.field_name == "name"

    def test_create_boolean_generator(self):
        """Test creation of boolean generator."""
        field_def = FieldDefinition(
            name="is_active",
            type=DataType.BOOLEAN,
            config=BooleanFieldConfig(true_probability=0.8)
        )
        
        generator = GeneratorFactory.create_generator(field_def)
        assert isinstance(generator, BooleanGenerator)
        assert generator.field_name == "is_active"

    def test_create_date_generator(self):
        """Test creation of date generator."""
        field_def = FieldDefinition(
            name="birth_date",
            type=DataType.DATE,
            config=DateFieldConfig(
                start_date="1990-01-01",
                end_date="2005-12-31",
                date_format="%Y-%m-%d"
            )
        )
        
        generator = GeneratorFactory.create_generator(field_def)
        assert isinstance(generator, DateTimeGenerator)
        assert generator.field_name == "birth_date"

    def test_create_datetime_generator(self):
        """Test creation of datetime generator."""
        field_def = FieldDefinition(
            name="created_at",
            type=DataType.DATETIME,
            config=DateFieldConfig(
                start_date="2023-01-01 00:00:00",
                end_date="2023-12-31 23:59:59",
                date_format="%Y-%m-%d %H:%M:%S"
            )
        )
        
        generator = GeneratorFactory.create_generator(field_def)
        assert isinstance(generator, DateTimeGenerator)
        assert generator.field_name == "created_at"

    def test_create_generator_with_default_config(self):
        """Test creation of generator with default configuration."""
        field_def = FieldDefinition(
            name="test_field",
            type=DataType.NUMERIC
            # No config provided
        )
        
        generator = GeneratorFactory.create_generator(field_def)
        assert isinstance(generator, NumericGenerator)
        assert generator.field_name == "test_field"
        # Should have default configuration
        assert generator.numeric_config is not None

    def test_create_generator_with_dict_config(self):
        """Test creation of generator with dictionary configuration."""
        field_def = FieldDefinition(
            name="test_field",
            type=DataType.STRING,
            config={
                "subtype": "email",
                "min_length": 5,
                "max_length": 100
            }
        )
        
        generator = GeneratorFactory.create_generator(field_def)
        assert isinstance(generator, StringGenerator)
        assert generator.string_config.subtype == StringSubtype.EMAIL

    def test_create_generator_with_seed(self):
        """Test creation of generator with seed."""
        field_def = FieldDefinition(
            name="test_field",
            type=DataType.STRING,
            config=StringFieldConfig(subtype=StringSubtype.NAME)
        )
        
        generator = GeneratorFactory.create_generator(field_def, seed=42)
        assert isinstance(generator, StringGenerator)

    def test_create_generator_with_locale(self):
        """Test creation of generator with custom locale."""
        field_def = FieldDefinition(
            name="test_field",
            type=DataType.STRING,
            config=StringFieldConfig(subtype=StringSubtype.NAME)
        )
        
        generator = GeneratorFactory.create_generator(field_def, locale="fr_FR")
        assert isinstance(generator, StringGenerator)

    def test_unsupported_type_raises_error(self):
        """Test that unsupported field type raises error."""
        # Create field with invalid type (this would normally be caught by Pydantic)
        field_def = FieldDefinition(
            name="test_field",
            type="unsupported_type",  # Invalid
            config=None
        )
        
        with pytest.raises(ValueError, match="Unsupported field type"):
            GeneratorFactory.create_generator(field_def)

    def test_get_supported_types(self):
        """Test getting list of supported types."""
        supported_types = GeneratorFactory.get_supported_types()
        
        assert DataType.NUMERIC in supported_types
        assert DataType.STRING in supported_types
        assert DataType.BOOLEAN in supported_types
        assert DataType.DATE in supported_types
        assert DataType.DATETIME in supported_types

    def test_create_generators_for_dataset(self):
        """Test creation of generators for entire dataset."""
        field_definitions = [
            FieldDefinition(
                name="id",
                type=DataType.NUMERIC,
                config=NumericFieldConfig(
                    min_value=1,
                    max_value=1000,
                    subtype=NumericSubtype.INTEGER
                )
            ),
            FieldDefinition(
                name="name",
                type=DataType.STRING,
                config=StringFieldConfig(subtype=StringSubtype.NAME)
            ),
            FieldDefinition(
                name="is_active",
                type=DataType.BOOLEAN,
                config=BooleanFieldConfig(true_probability=0.7)
            ),
            FieldDefinition(
                name="created_at",
                type=DataType.DATETIME,
                config=DateFieldConfig(date_format="%Y-%m-%d %H:%M:%S")
            )
        ]
        
        generators = GeneratorFactory.create_generators_for_dataset(
            field_definitions,
            locale="en_US",
            seed=42
        )
        
        assert len(generators) == 4
        assert "id" in generators
        assert "name" in generators
        assert "is_active" in generators
        assert "created_at" in generators
        
        assert isinstance(generators["id"], NumericGenerator)
        assert isinstance(generators["name"], StringGenerator)
        assert isinstance(generators["is_active"], BooleanGenerator)
        assert isinstance(generators["created_at"], DateTimeGenerator)

    def test_validate_field_definition(self):
        """Test field definition validation."""
        # Valid field definition
        valid_field = FieldDefinition(
            name="test",
            type=DataType.NUMERIC,
            config=NumericFieldConfig(min_value=1, max_value=10)
        )
        
        assert GeneratorFactory.validate_field_definition(valid_field) is True

    def test_get_generator_info(self):
        """Test getting generator information."""
        info = GeneratorFactory.get_generator_info(DataType.NUMERIC)
        
        assert "class_name" in info
        assert "module" in info
        assert "docstring" in info
        assert "supported_type" in info
        
        assert info["class_name"] == "NumericGenerator"
        assert info["supported_type"] == "numeric"

    def test_get_generator_info_unsupported(self):
        """Test getting info for unsupported type."""
        info = GeneratorFactory.get_generator_info("unsupported")
        
        assert "error" in info

    def test_register_custom_generator(self):
        """Test registering a custom generator."""
        from schema_faker.utils.base import BaseGenerator
        
        class CustomGenerator(BaseGenerator):
            def generate(self):
                return "custom_value"
        
        # Register custom generator
        custom_type = "custom"
        GeneratorFactory.register_generator(custom_type, CustomGenerator)
        
        # Check it was registered
        assert custom_type in GeneratorFactory._generator_registry
        
        # Clean up
        del GeneratorFactory._generator_registry[custom_type]

    def test_register_invalid_generator_raises_error(self):
        """Test that registering invalid generator raises error."""
        class NotAGenerator:
            pass
        
        with pytest.raises(ValueError, match="must inherit from BaseGenerator"):
            GeneratorFactory.register_generator("invalid", NotAGenerator)

    def test_create_generators_with_incremental_seeds(self):
        """Test that generators get incremental seeds."""
        field_definitions = [
            FieldDefinition(name="field1", type=DataType.STRING),
            FieldDefinition(name="field2", type=DataType.STRING),
            FieldDefinition(name="field3", type=DataType.STRING),
        ]
        
        generators = GeneratorFactory.create_generators_for_dataset(
            field_definitions,
            seed=100
        )
        
        assert len(generators) == 3
        # Each generator should have been created with seed + index
        # This is hard to test directly but we can verify all generators were created