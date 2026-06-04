from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class DataType(str, Enum):
    """Supported data types for field generation."""
    NUMERIC = "numeric"
    STRING = "string"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"


class StringSubtype(str, Enum):
    """Supported string subtypes."""
    RANDOM = "random"
    NAME = "name"
    FIRST_NAME = "first_name"
    LAST_NAME = "last_name"
    ADDRESS = "address"
    EMAIL = "email"
    IP_ADDRESS = "ip_address"
    UUID = "uuid"
    PHONE = "phone"
    COMPANY = "company"


class NumericSubtype(str, Enum):
    """Supported numeric subtypes."""
    INTEGER = "integer"
    FLOAT = "float"
    DECIMAL = "decimal"


class OutputFormat(str, Enum):
    """Supported output formats."""
    JSON = "json"
    CSV = "csv"
    SQL = "sql"


class NumericFieldConfig(BaseModel):
    """Configuration for numeric fields."""
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    precision: Optional[int] = None  # For decimal places
    subtype: NumericSubtype = NumericSubtype.INTEGER

    @field_validator('precision')
    @classmethod
    def validate_precision(cls, v):
        if v is not None and v < 0:
            raise ValueError("Precision must be non-negative")
        return v


class StringFieldConfig(BaseModel):
    """Configuration for string fields."""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    subtype: StringSubtype = StringSubtype.RANDOM
    pattern: Optional[str] = None  # For custom regex patterns
    choices: Optional[List[str]] = None  # For predefined choices

    @field_validator('min_length', 'max_length')
    @classmethod
    def validate_length(cls, v):
        if v is not None and v < 0:
            raise ValueError("Length must be non-negative")
        return v


class DateFieldConfig(BaseModel):
    """Configuration for date/datetime fields."""
    start_date: Optional[str] = None  # ISO format: "2023-01-01"
    end_date: Optional[str] = None    # ISO format: "2023-12-31"
    date_format: str = "%Y-%m-%d"


class BooleanFieldConfig(BaseModel):
    """Configuration for boolean fields."""
    true_probability: float = 0.5  # Probability of generating True

    @field_validator('true_probability')
    @classmethod
    def validate_probability(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Probability must be between 0 and 1")
        return v


class FieldDefinition(BaseModel):
    """Definition for a single field in the dataset."""
    name: str
    type: DataType
    nullable: bool = False
    null_probability: float = 0.0  # Probability of null when nullable=True
    config: Optional[Union[
        NumericFieldConfig,
        StringFieldConfig,
        DateFieldConfig,
        BooleanFieldConfig,
        Dict[str, Any]  # For custom configurations
    ]] = None

    @field_validator('null_probability')
    @classmethod
    def validate_null_probability(cls, v):
        if not 0 <= v <= 1:
            raise ValueError("Null probability must be between 0 and 1")
        return v

    @field_validator('config')
    @classmethod
    def validate_config(cls, v, info):
        """Validate that config matches the field type."""
        if v is None:
            return v
        
        field_type = info.data.get('type')
        
        # If config is already a proper config object, return as-is
        if isinstance(v, (NumericFieldConfig, StringFieldConfig, DateFieldConfig, BooleanFieldConfig)):
            return v
        
        # If config is a dict, try to convert to appropriate config class
        if isinstance(v, dict):
            if field_type == DataType.NUMERIC:
                return NumericFieldConfig(**v)
            elif field_type == DataType.STRING:
                return StringFieldConfig(**v)
            elif field_type in (DataType.DATE, DataType.DATETIME):
                return DateFieldConfig(**v)
            elif field_type == DataType.BOOLEAN:
                return BooleanFieldConfig(**v)
        
        return v


class DatasetSchema(BaseModel):
    """Schema definition for a complete dataset."""
    table_name: str
    record_count: int = Field(gt=0, description="Number of records to generate")
    fields: List[FieldDefinition]
    output_format: OutputFormat = OutputFormat.JSON
    output_path: Optional[str] = None

    @field_validator('table_name')
    @classmethod
    def validate_table_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Table name cannot be empty")
        return v.strip()

    @field_validator('fields')
    @classmethod
    def validate_fields(cls, v):
        if not v:
            raise ValueError("At least one field must be defined")
        
        # Check for duplicate field names
        field_names = [field.name for field in v]
        if len(field_names) != len(set(field_names)):
            raise ValueError("Field names must be unique")
        
        return v


class SchemaConfiguration(BaseModel):
    """Root configuration containing multiple datasets."""
    version: str = "1.0"
    datasets: List[DatasetSchema]
    global_config: Optional[Dict[str, Any]] = None

    @field_validator('datasets')
    @classmethod
    def validate_datasets(cls, v):
        if not v:
            raise ValueError("At least one dataset must be defined")
        
        # Check for duplicate table names
        table_names = [dataset.table_name for dataset in v]
        if len(table_names) != len(set(table_names)):
            raise ValueError("Table names must be unique")
        
        return v


# Type aliases for better readability
FieldConfig = Union[NumericFieldConfig, StringFieldConfig, DateFieldConfig, BooleanFieldConfig]