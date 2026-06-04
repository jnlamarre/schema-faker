"""
Factory for creating exporters based on output format.
Implements the Factory pattern for polymorphic exporter creation.
"""

import logging
from typing import Any

from ..utils.base import BaseExporter
from .csv import CSVExporter
from .json import JSONExporter
from .sql import SQLExporter


class ExporterFactory:
    """
    Factory class for creating appropriate exporters based on output format.
    Supports CSV, JSON, and SQL export formats with configurable options.
    """

    # Registry of exporter classes by format
    _exporter_registry: dict[str, type[BaseExporter]] = {
        "csv": CSVExporter,
        "json": JSONExporter,
        "sql": SQLExporter,
    }

    @classmethod
    def create_exporter(
        cls,
        format_type: str,
        table_name: str,
        options: dict[str, Any] | None = None,
        logger: logging.Logger | None = None,
    ) -> BaseExporter:
        """
        Create appropriate exporter for the given format type.

        Args:
            format_type: Export format (csv, json, sql)
            table_name: Name of the table/dataset being exported
            options: Format-specific options
            logger: Optional logger instance

        Returns:
            Configured exporter instance

        Raises:
            ValueError: If format type is unsupported or options are invalid
        """
        format_type = format_type.lower().strip()
        options = options or {}

        # Get exporter class from registry
        exporter_class = cls._exporter_registry.get(format_type)
        if exporter_class is None:
            supported_formats = list(cls._exporter_registry.keys())
            raise ValueError(
                f"Unsupported export format: {format_type}. "
                f"Supported formats: {supported_formats}"
            )

        try:
            # Create exporter instance with format-specific options
            if format_type == "csv":
                return CSVExporter(
                    table_name=table_name,
                    delimiter=options.get("delimiter", ","),
                    quote_char=options.get("quote_char", '"'),
                    include_header=options.get("include_header", True),
                    logger=logger,
                )

            elif format_type == "json":
                return JSONExporter(
                    table_name=table_name,
                    indent=options.get("indent", 2),
                    sort_keys=options.get("sort_keys", False),
                    ensure_ascii=options.get("ensure_ascii", False),
                    logger=logger,
                )

            elif format_type == "sql":
                return SQLExporter(
                    table_name=table_name,
                    dialect=options.get("dialect", "postgresql"),
                    batch_size=options.get("batch_size", 1000),
                    include_schema=options.get("schema"),
                    logger=logger,
                )

            else:
                raise ValueError(f"Unsupported format type: {format_type}")

        except Exception as e:
            raise ValueError(
                f"Failed to create {format_type} exporter for table '{table_name}': {str(e)}"
            ) from e

    @classmethod
    def create_exporters_for_datasets(
        cls,
        datasets_config: list[dict[str, Any]],
        global_options: dict[str, Any] | None = None,
        logger: logging.Logger | None = None,
    ) -> dict[str, BaseExporter]:
        """
        Create exporters for multiple datasets.

        Args:
            datasets_config: List of dataset configurations
            global_options: Global export options
            logger: Optional logger instance

        Returns:
            Dictionary mapping table names to exporter instances
        """
        global_options = global_options or {}
        exporters = {}

        for dataset_config in datasets_config:
            table_name = dataset_config.get("table_name", "unknown")
            format_type = dataset_config.get("output_format", "json")

            # Merge global and dataset-specific options
            merged_options = global_options.copy()
            merged_options.update(dataset_config.get("export_options", {}))

            try:
                exporter = cls.create_exporter(
                    format_type=format_type,
                    table_name=table_name,
                    options=merged_options,
                    logger=logger,
                )
                exporters[table_name] = exporter

            except Exception as e:
                if logger:
                    logger.error(
                        f"Failed to create exporter for dataset '{table_name}': {e}"
                    )
                continue

        return exporters

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """
        Get list of supported export formats.

        Returns:
            List of supported format strings
        """
        return list(cls._exporter_registry.keys())

    @classmethod
    def get_format_options(cls, format_type: str) -> dict[str, Any]:
        """
        Get available options for a specific format type.

        Args:
            format_type: Export format to get options for

        Returns:
            Dictionary describing available options
        """
        format_type = format_type.lower().strip()

        options_map = {
            "csv": {
                "delimiter": {
                    "description": "CSV delimiter character",
                    "type": "string",
                    "default": ",",
                    "examples": [",", ";", "|", "\t"],
                },
                "quote_char": {
                    "description": "Quote character for string values",
                    "type": "string",
                    "default": '"',
                    "examples": ['"', "'"],
                },
                "include_header": {
                    "description": "Whether to include column headers",
                    "type": "boolean",
                    "default": True,
                },
            },
            "json": {
                "indent": {
                    "description": "JSON indentation (None for compact output)",
                    "type": "integer|null",
                    "default": 2,
                },
                "sort_keys": {
                    "description": "Whether to sort dictionary keys",
                    "type": "boolean",
                    "default": False,
                },
                "ensure_ascii": {
                    "description": "Whether to escape non-ASCII characters",
                    "type": "boolean",
                    "default": False,
                },
            },
            "sql": {
                "dialect": {
                    "description": "SQL dialect",
                    "type": "string",
                    "default": "postgresql",
                    "examples": ["postgresql", "mysql", "sqlite", "mssql"],
                },
                "batch_size": {
                    "description": "Number of records per INSERT statement",
                    "type": "integer",
                    "default": 1000,
                },
                "schema": {
                    "description": "Optional schema name to prefix table name",
                    "type": "string|null",
                    "default": None,
                },
            },
        }

        return options_map.get(format_type, {})

    @classmethod
    def register_exporter(
        cls, format_type: str, exporter_class: type[BaseExporter]
    ) -> None:
        """
        Register a custom exporter class for a format type.

        This allows extending the factory with custom exporters.

        Args:
            format_type: Format type to associate with exporter
            exporter_class: Exporter class to register
        """
        if not issubclass(exporter_class, BaseExporter):
            raise ValueError("Exporter class must inherit from BaseExporter")

        format_type = format_type.lower().strip()
        cls._exporter_registry[format_type] = exporter_class

    @classmethod
    def validate_format_options(
        cls, format_type: str, options: dict[str, Any]
    ) -> tuple[bool, list[str]]:
        """
        Validate options for a specific format type.

        Args:
            format_type: Export format to validate options for
            options: Options dictionary to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        format_type = format_type.lower().strip()
        errors = []

        if format_type not in cls._exporter_registry:
            return False, [f"Unsupported format type: {format_type}"]

        try:
            # Try creating an exporter with the options to validate them
            cls.create_exporter(
                format_type=format_type,
                table_name="test_table",
                options=options,
            )
            return True, []

        except Exception as e:
            errors.append(f"Invalid options for {format_type}: {str(e)}")
            return False, errors

    @classmethod
    def get_exporter_info(cls, format_type: str) -> dict[str, Any]:
        """
        Get information about an exporter class.

        Args:
            format_type: Format type to get info for

        Returns:
            Dictionary with exporter information
        """
        format_type = format_type.lower().strip()
        exporter_class = cls._exporter_registry.get(format_type)

        if exporter_class is None:
            return {"error": f"Unsupported format type: {format_type}"}

        return {
            "format_type": format_type,
            "class_name": exporter_class.__name__,
            "module": exporter_class.__module__,
            "docstring": exporter_class.__doc__,
            "available_options": cls.get_format_options(format_type),
        }
