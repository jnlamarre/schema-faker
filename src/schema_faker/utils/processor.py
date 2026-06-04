import logging
import random
from typing import Any, Dict, List, Optional

from .base import BaseProcessor
from .schema_models import DatasetSchema, FieldDefinition
from ..generators import GeneratorFactory


class SchemaProcessor(BaseProcessor):
    """
    Processes schema configurations and orchestrates data generation.
    Implements the template method pattern for schema-driven data generation.
    """

    def __init__(
        self,
        dataset_schema: DatasetSchema,
        locale: str = "en_US",
        seed: Optional[int] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize schema processor with dataset configuration.

        Args:
            dataset_schema: Dataset schema configuration
            locale: Locale for generators that support localization
            seed: Random seed for reproducible generation
            logger: Optional logger instance
        """
        # Convert to dict for compatibility with base class
        schema_config = dataset_schema.model_dump()
        super().__init__(schema_config, logger)
        
        self.dataset_schema = dataset_schema
        self.locale = locale
        self.seed = seed
        
        # Initialize empty generators dict
        self.generators: Dict[str, Any] = {}
        
        # Set random seed if provided
        if seed is not None:
            random.seed(seed)

    def parse_schema(self) -> None:
        """
        Parse schema configuration and create appropriate generators for each field.
        """
        self.logger.info(f"Parsing schema for dataset: {self.dataset_schema.table_name}")
        
        try:
            # Create generators for all fields using the factory
            self.generators = GeneratorFactory.create_generators_for_dataset(
                field_definitions=self.dataset_schema.fields,
                locale=self.locale,
                seed=self.seed
            )
            
            self.logger.info(f"Created {len(self.generators)} generators for {len(self.dataset_schema.fields)} fields")
            
            # Log any missing generators
            created_fields = set(self.generators.keys())
            expected_fields = {field.name for field in self.dataset_schema.fields}
            missing_fields = expected_fields - created_fields
            
            if missing_fields:
                self.logger.warning(f"Failed to create generators for fields: {missing_fields}")
                
        except Exception as e:
            self.logger.error(f"Failed to parse schema: {e}")
            raise

    def process_dataset(self, record_count: int) -> List[Dict[str, Any]]:
        """
        Generate a complete dataset using configured generators.

        Args:
            record_count: Number of records to generate

        Returns:
            List of generated records
        """
        if not self.generators:
            raise ValueError("No generators available. Call parse_schema() first.")
        
        self.logger.info(f"Generating {record_count} records for {self.dataset_schema.table_name}")
        
        records = []
        
        for i in range(record_count):
            record = self._generate_single_record()
            records.append(record)
            
            # Log progress for large datasets
            if record_count > 1000 and (i + 1) % 1000 == 0:
                self.logger.info(f"Generated {i + 1}/{record_count} records")
        
        self.logger.info(f"Successfully generated {len(records)} records")
        return records

    def _generate_single_record(self) -> Dict[str, Any]:
        """
        Generate a single record using all configured generators.

        Returns:
            Dictionary representing a single record
        """
        record = {}
        
        for field_def in self.dataset_schema.fields:
            field_name = field_def.name
            generator = self.generators.get(field_name)
            
            if generator is None:
                # Field generator not available, skip or use None
                self.logger.warning(f"No generator available for field: {field_name}")
                record[field_name] = None
                continue
            
            # Handle nullable fields
            if field_def.nullable and random.random() < field_def.null_probability:
                record[field_name] = None
            else:
                try:
                    # Generate value using the appropriate generator
                    value = generator.generate()
                    record[field_name] = value
                except Exception as e:
                    self.logger.error(f"Error generating value for field '{field_name}': {e}")
                    record[field_name] = None
        
        return record

    def process_dataset_optimized(self, record_count: int) -> List[Dict[str, Any]]:
        """
        Generate dataset using optimized batch processing where possible.
        
        This method tries to use batch generation for better performance.

        Args:
            record_count: Number of records to generate

        Returns:
            List of generated records
        """
        if not self.generators:
            raise ValueError("No generators available. Call parse_schema() first.")
        
        self.logger.info(f"Generating {record_count} records (optimized) for {self.dataset_schema.table_name}")
        
        # Pre-generate all values for each field
        field_values = {}
        
        for field_def in self.dataset_schema.fields:
            field_name = field_def.name
            generator = self.generators.get(field_name)
            
            if generator is None:
                field_values[field_name] = [None] * record_count
                continue
            
            try:
                # Use batch generation if available
                if hasattr(generator, 'generate_batch_optimized'):
                    values = generator.generate_batch_optimized(record_count)
                elif hasattr(generator, 'generate_batch'):
                    values = generator.generate_batch(record_count)
                else:
                    # Fall back to individual generation
                    values = [generator.generate() for _ in range(record_count)]
                
                # Handle nullable fields
                if field_def.nullable and field_def.null_probability > 0:
                    values = self._apply_null_probability(values, field_def.null_probability)
                
                field_values[field_name] = values
                
            except Exception as e:
                self.logger.error(f"Error generating batch values for field '{field_name}': {e}")
                field_values[field_name] = [None] * record_count
        
        # Combine field values into records
        records = []
        for i in range(record_count):
            record = {field_name: values[i] for field_name, values in field_values.items()}
            records.append(record)
        
        self.logger.info(f"Successfully generated {len(records)} records (optimized)")
        return records

    def _apply_null_probability(self, values: List[Any], null_probability: float) -> List[Any]:
        """
        Apply null probability to a list of generated values.

        Args:
            values: List of generated values
            null_probability: Probability of null (0.0 to 1.0)

        Returns:
            List with some values replaced with None based on probability
        """
        return [
            None if random.random() < null_probability else value
            for value in values
        ]

    def validate_schema(self) -> Dict[str, Any]:
        """
        Validate that the schema can be processed and generators can be created.

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "field_validations": {}
        }
        
        try:
            # Validate overall schema structure
            if not self.dataset_schema.fields:
                validation_result["errors"].append("Dataset has no fields defined")
                validation_result["valid"] = False
            
            # Validate each field definition
            for field_def in self.dataset_schema.fields:
                field_validation = self._validate_field_definition(field_def)
                validation_result["field_validations"][field_def.name] = field_validation
                
                if not field_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend(field_validation["errors"])
        
        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Schema validation failed: {str(e)}")
        
        return validation_result

    def _validate_field_definition(self, field_def: FieldDefinition) -> Dict[str, Any]:
        """
        Validate a single field definition.

        Args:
            field_def: Field definition to validate

        Returns:
            Dictionary with field validation results
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Check if generator can be created
            is_valid = GeneratorFactory.validate_field_definition(field_def)
            
            if not is_valid:
                result["valid"] = False
                result["errors"].append(f"Cannot create generator for field type: {field_def.type}")
            
            # Validate nullable configuration
            if field_def.nullable and not (0 <= field_def.null_probability <= 1):
                result["valid"] = False
                result["errors"].append("Null probability must be between 0 and 1")
            
        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Field validation error: {str(e)}")
        
        return result

    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current schema and generators.

        Returns:
            Dictionary with generation statistics
        """
        stats = {
            "dataset_name": self.dataset_schema.table_name,
            "total_fields": len(self.dataset_schema.fields),
            "active_generators": len(self.generators),
            "fields": {},
            "nullable_fields": 0,
            "supported_types": GeneratorFactory.get_supported_types()
        }
        
        for field_def in self.dataset_schema.fields:
            field_stats = {
                "type": field_def.type.value,
                "nullable": field_def.nullable,
                "null_probability": field_def.null_probability,
                "has_generator": field_def.name in self.generators
            }
            
            if field_def.nullable:
                stats["nullable_fields"] += 1
            
            stats["fields"][field_def.name] = field_stats
        
        return stats