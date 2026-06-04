import pytest
from pydantic import ValidationError

from schema_faker.utils.schema_models import (
    DatasetSchema,
    DataType,
    FieldDefinition,
    NumericFieldConfig,
    NumericSubtype,
    OutputFormat,
    SchemaConfiguration,
    StringFieldConfig,
    StringSubtype,
)


class TestFieldDefinition:
    """Test cases for FieldDefinition model."""

    def test_valid_field_creation(self):
        """Test creating a valid field definition."""
        field = FieldDefinition(
            name="test_field",
            type=DataType.STRING,
            nullable=False,
            config=StringFieldConfig(subtype=StringSubtype.NAME),
        )

        assert field.name == "test_field"
        assert field.type == DataType.STRING
        assert field.nullable is False
        assert isinstance(field.config, StringFieldConfig)

    def test_field_without_config(self):
        """Test field creation without explicit config."""
        field = FieldDefinition(name="simple_field", type=DataType.BOOLEAN)

        assert field.name == "simple_field"
        assert field.type == DataType.BOOLEAN
        assert field.config is None

    @pytest.mark.parametrize("probability", [-0.1, 1.5, 2.0])
    def test_invalid_null_probability(self, probability):
        """Test validation of null probability values."""
        with pytest.raises(ValidationError):
            FieldDefinition(
                name="test", type=DataType.STRING, null_probability=probability
            )

    def test_valid_null_probability(self):
        """Test valid null probability values."""
        field = FieldDefinition(
            name="test", type=DataType.STRING, nullable=True, null_probability=0.3
        )

        assert field.null_probability == 0.3


class TestNumericFieldConfig:
    """Test cases for NumericFieldConfig model."""

    def test_valid_numeric_config(self):
        """Test creating valid numeric configuration."""
        config = NumericFieldConfig(
            min_value=0, max_value=100, precision=2, subtype=NumericSubtype.FLOAT
        )

        assert config.min_value == 0
        assert config.max_value == 100
        assert config.precision == 2
        assert config.subtype == NumericSubtype.FLOAT

    def test_negative_precision_raises_error(self):
        """Test that negative precision raises validation error."""
        with pytest.raises(ValidationError):
            NumericFieldConfig(precision=-1)

    def test_default_values(self):
        """Test default configuration values."""
        config = NumericFieldConfig()

        assert config.min_value is None
        assert config.max_value is None
        assert config.precision is None
        assert config.subtype == NumericSubtype.INTEGER


class TestStringFieldConfig:
    """Test cases for StringFieldConfig model."""

    def test_valid_string_config(self):
        """Test creating valid string configuration."""
        config = StringFieldConfig(
            min_length=1, max_length=50, subtype=StringSubtype.EMAIL
        )

        assert config.min_length == 1
        assert config.max_length == 50
        assert config.subtype == StringSubtype.EMAIL

    @pytest.mark.parametrize("length", [-1, -10])
    def test_negative_length_raises_error(self, length):
        """Test that negative lengths raise validation error."""
        with pytest.raises(ValidationError):
            StringFieldConfig(min_length=length)

        with pytest.raises(ValidationError):
            StringFieldConfig(max_length=length)

    def test_choices_configuration(self):
        """Test string configuration with predefined choices."""
        choices = ["option1", "option2", "option3"]
        config = StringFieldConfig(choices=choices)

        assert config.choices == choices


class TestDatasetSchema:
    """Test cases for DatasetSchema model."""

    def test_valid_dataset_schema(self, sample_dataset_schema):
        """Test creating a valid dataset schema."""
        assert sample_dataset_schema.table_name == "users"
        assert sample_dataset_schema.record_count == 100
        assert len(sample_dataset_schema.fields) == 2
        assert sample_dataset_schema.output_format == OutputFormat.JSON

    def test_empty_table_name_raises_error(self):
        """Test that empty table name raises validation error."""
        with pytest.raises(ValidationError):
            DatasetSchema(
                table_name="",
                record_count=10,
                fields=[FieldDefinition(name="test", type=DataType.STRING)],
            )

    def test_negative_record_count_raises_error(self):
        """Test that negative record count raises validation error."""
        with pytest.raises(ValidationError):
            DatasetSchema(
                table_name="test",
                record_count=-1,
                fields=[FieldDefinition(name="test", type=DataType.STRING)],
            )

    def test_zero_record_count_raises_error(self):
        """Test that zero record count raises validation error."""
        with pytest.raises(ValidationError):
            DatasetSchema(
                table_name="test",
                record_count=0,
                fields=[FieldDefinition(name="test", type=DataType.STRING)],
            )

    def test_no_fields_raises_error(self):
        """Test that empty fields list raises validation error."""
        with pytest.raises(ValidationError):
            DatasetSchema(table_name="test", record_count=10, fields=[])

    def test_duplicate_field_names_raises_error(self):
        """Test that duplicate field names raise validation error."""
        fields = [
            FieldDefinition(name="duplicate", type=DataType.STRING),
            FieldDefinition(name="duplicate", type=DataType.NUMERIC),
        ]

        with pytest.raises(ValidationError):
            DatasetSchema(table_name="test", record_count=10, fields=fields)

    def test_table_name_whitespace_trimmed(self):
        """Test that table name whitespace is trimmed."""
        schema = DatasetSchema(
            table_name="  test_table  ",
            record_count=10,
            fields=[FieldDefinition(name="test", type=DataType.STRING)],
        )

        assert schema.table_name == "test_table"


class TestSchemaConfiguration:
    """Test cases for SchemaConfiguration model."""

    def test_valid_schema_configuration(self, sample_dataset_schema):
        """Test creating a valid schema configuration."""
        config = SchemaConfiguration(version="1.0", datasets=[sample_dataset_schema])

        assert config.version == "1.0"
        assert len(config.datasets) == 1
        assert config.global_config is None

    def test_empty_datasets_raises_error(self):
        """Test that empty datasets list raises validation error."""
        with pytest.raises(ValidationError):
            SchemaConfiguration(datasets=[])

    def test_duplicate_table_names_raises_error(self, sample_numeric_field):
        """Test that duplicate table names raise validation error."""
        dataset1 = DatasetSchema(
            table_name="duplicate", record_count=10, fields=[sample_numeric_field]
        )
        dataset2 = DatasetSchema(
            table_name="duplicate", record_count=20, fields=[sample_numeric_field]
        )

        with pytest.raises(ValidationError):
            SchemaConfiguration(datasets=[dataset1, dataset2])

    def test_with_global_config(self, sample_dataset_schema):
        """Test schema configuration with global settings."""
        global_settings = {"output_dir": "./output", "seed": 42}
        config = SchemaConfiguration(
            datasets=[sample_dataset_schema], global_config=global_settings
        )

        assert config.global_config == global_settings
