import pytest
from typing import Dict, Any
from schema_faker.utils.schema_models import (
    DatasetSchema,
    FieldDefinition,
    DataType,
    NumericFieldConfig,
    StringFieldConfig,
    StringSubtype,
    NumericSubtype,
    OutputFormat
)


@pytest.fixture(scope="session")
def sample_numeric_field():
    """Sample numeric field definition."""
    return FieldDefinition(
        name="age",
        type=DataType.NUMERIC,
        config=NumericFieldConfig(
            min_value=18,
            max_value=100,
            subtype=NumericSubtype.INTEGER
        )
    )


@pytest.fixture(scope="session")
def sample_string_field():
    """Sample string field definition."""
    return FieldDefinition(
        name="name",
        type=DataType.STRING,
        config=StringFieldConfig(
            subtype=StringSubtype.NAME,
            min_length=2,
            max_length=50
        )
    )


@pytest.fixture(scope="session")
def sample_email_field():
    """Sample email field definition."""
    return FieldDefinition(
        name="email",
        type=DataType.STRING,
        config=StringFieldConfig(
            subtype=StringSubtype.EMAIL
        )
    )


@pytest.fixture(scope="session")
def sample_dataset_schema(sample_numeric_field, sample_string_field):
    """Sample complete dataset schema."""
    return DatasetSchema(
        table_name="users",
        record_count=100,
        fields=[sample_numeric_field, sample_string_field],
        output_format=OutputFormat.JSON
    )


@pytest.fixture(scope="session")
def invalid_schema_configs():
    """Factory for invalid schema configurations for testing validation."""
    return {
        "empty_table_name": {
            "table_name": "",
            "record_count": 10,
            "fields": []
        },
        "negative_record_count": {
            "table_name": "test",
            "record_count": -1,
            "fields": []
        },
        "no_fields": {
            "table_name": "test",
            "record_count": 10,
            "fields": []
        },
        "duplicate_field_names": {
            "table_name": "test",
            "record_count": 10,
            "fields": [
                {"name": "field1", "type": "numeric"},
                {"name": "field1", "type": "string"}
            ]
        }
    }


@pytest.fixture(scope="session")
def field_config_factory():
    """Factory function for creating field configurations."""
    def _create_field_config(field_type: str, **kwargs) -> Dict[str, Any]:
        base_config = {
            "name": kwargs.pop("name", "test_field"),
            "type": field_type
        }
        
        if kwargs:
            base_config["config"] = kwargs
            
        return base_config
    
    return _create_field_config


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir