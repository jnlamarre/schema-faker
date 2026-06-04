from typing import Any, Dict, Type

from ..utils.base import BaseGenerator
from ..utils.schema_models import (
    FieldDefinition,
    DataType,
    NumericFieldConfig,
    StringFieldConfig,
    DateFieldConfig,
    BooleanFieldConfig,
)
from .numeric import NumericGenerator
from .string import StringGenerator
from .datetime import DateTimeGenerator
from .boolean import BooleanGenerator


class GeneratorFactory:
    """
    Factory class for creating appropriate generators based on field definitions.
    Implements the Factory pattern for polymorphic generator creation.
    """

    # Registry of generator classes by data type
    _generator_registry: Dict[DataType, Type[BaseGenerator]] = {
        DataType.NUMERIC: NumericGenerator,
        DataType.STRING: StringGenerator,
        DataType.DATE: DateTimeGenerator,
        DataType.DATETIME: DateTimeGenerator,
        DataType.BOOLEAN: BooleanGenerator,
    }

    @classmethod
    def create_generator(
        cls,
        field_definition: FieldDefinition,
        locale: str = "en_US",
        seed: int = None
    ) -> BaseGenerator:
        """
        Create appropriate generator for the given field definition.

        Args:
            field_definition: Field definition containing type and configuration
            locale: Locale for generators that support localization (e.g., StringGenerator)
            seed: Random seed for reproducible generation

        Returns:
            Configured generator instance

        Raises:
            ValueError: If field type is unsupported or configuration is invalid
        """
        field_type = field_definition.type
        field_name = field_definition.name
        config = field_definition.config

        # Get generator class from registry
        generator_class = cls._generator_registry.get(field_type)
        if generator_class is None:
            raise ValueError(f"Unsupported field type: {field_type}")

        # Create default configuration if none provided
        if config is None:
            config = cls._create_default_config(field_type)

        # Create generator instance based on type
        try:
            if field_type == DataType.NUMERIC:
                if not isinstance(config, NumericFieldConfig):
                    config = NumericFieldConfig(**config) if isinstance(config, dict) else config
                generator = NumericGenerator(field_name, config)

            elif field_type == DataType.STRING:
                if not isinstance(config, StringFieldConfig):
                    config = StringFieldConfig(**config) if isinstance(config, dict) else config
                generator = StringGenerator(field_name, config, locale)

            elif field_type in (DataType.DATE, DataType.DATETIME):
                if not isinstance(config, DateFieldConfig):
                    config = DateFieldConfig(**config) if isinstance(config, dict) else config
                generator = DateTimeGenerator(field_name, config, locale)

            elif field_type == DataType.BOOLEAN:
                if not isinstance(config, BooleanFieldConfig):
                    config = BooleanFieldConfig(**config) if isinstance(config, dict) else config
                generator = BooleanGenerator(field_name, config)

            else:
                raise ValueError(f"Unsupported field type: {field_type}")

            # Set seed if provided
            if seed is not None and hasattr(generator, 'set_seed'):
                generator.set_seed(seed)

            return generator

        except Exception as e:
            raise ValueError(
                f"Failed to create generator for field '{field_name}' of type '{field_type}': {str(e)}"
            ) from e

    @classmethod
    def _create_default_config(cls, field_type: DataType) -> Any:
        """
        Create default configuration for a field type.

        Args:
            field_type: Type of field to create config for

        Returns:
            Default configuration object
        """
        defaults = {
            DataType.NUMERIC: NumericFieldConfig(),
            DataType.STRING: StringFieldConfig(),
            DataType.DATE: DateFieldConfig(),
            DataType.DATETIME: DateFieldConfig(),
            DataType.BOOLEAN: BooleanFieldConfig(),
        }

        return defaults.get(field_type, {})

    @classmethod
    def register_generator(cls, field_type: DataType, generator_class: Type[BaseGenerator]) -> None:
        """
        Register a custom generator class for a field type.
        
        This allows extending the factory with custom generators.

        Args:
            field_type: Data type to associate with generator
            generator_class: Generator class to register
        """
        if not issubclass(generator_class, BaseGenerator):
            raise ValueError("Generator class must inherit from BaseGenerator")

        cls._generator_registry[field_type] = generator_class

    @classmethod
    def get_supported_types(cls) -> list[DataType]:
        """
        Get list of supported data types.

        Returns:
            List of supported DataType values
        """
        return list(cls._generator_registry.keys())

    @classmethod
    def create_generators_for_dataset(
        cls,
        field_definitions: list[FieldDefinition],
        locale: str = "en_US",
        seed: int = None
    ) -> Dict[str, BaseGenerator]:
        """
        Create generators for all fields in a dataset.

        Args:
            field_definitions: List of field definitions
            locale: Locale for generators that support localization
            seed: Base random seed (each generator gets seed + field_index)

        Returns:
            Dictionary mapping field names to generator instances
        """
        generators = {}

        for i, field_def in enumerate(field_definitions):
            # Use incremental seeds for each field to ensure variety
            field_seed = (seed + i) if seed is not None else None
            
            try:
                generator = cls.create_generator(field_def, locale, field_seed)
                generators[field_def.name] = generator
            except Exception as e:
                # Log error and continue with other fields
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create generator for field '{field_def.name}': {e}")
                continue

        return generators

    @classmethod
    def validate_field_definition(cls, field_definition: FieldDefinition) -> bool:
        """
        Validate that a field definition can be used to create a generator.

        Args:
            field_definition: Field definition to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to create a generator (without seed to avoid side effects)
            generator = cls.create_generator(field_definition)
            return True
        except Exception:
            return False

    @classmethod
    def get_generator_info(cls, field_type: DataType) -> Dict[str, Any]:
        """
        Get information about a generator class.

        Args:
            field_type: Type of field to get info for

        Returns:
            Dictionary with generator information
        """
        generator_class = cls._generator_registry.get(field_type)
        if generator_class is None:
            return {"error": f"Unsupported field type: {field_type}"}

        return {
            "class_name": generator_class.__name__,
            "module": generator_class.__module__,
            "docstring": generator_class.__doc__,
            "supported_type": field_type.value
        }