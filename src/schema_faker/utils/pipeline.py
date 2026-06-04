"""
Complete data generation and export pipeline.
Orchestrates schema processing, data generation, and multi-format export.
"""

import logging
from pathlib import Path
from typing import Any

from ..exporters import ExporterFactory
from ..utils.base import BasePipeline
from .processor import SchemaProcessor
from .schema_models import DatasetSchema, SchemaConfiguration


class DataPipeline(BasePipeline):
    """
    Complete pipeline for generating and exporting synthetic data.
    Handles multiple datasets and output formats in a single execution.
    """

    def __init__(
        self,
        schema: SchemaConfiguration,
        output_dir: str = "./output",
        locale: str = "en_US",
        logger: logging.Logger | None = None,
    ):
        """
        Initialize pipeline with schema configuration.

        Args:
            schema: Complete schema configuration with datasets and global configuration
            output_dir: Base directory for output files
            locale: Locale for data generation
            logger: Optional logger instance
        """
        # Use first dataset for base pipeline initialization
        if schema.datasets:
            first_dataset_obj = schema.datasets[0]
            if hasattr(first_dataset_obj, "model_dump"):
                first_dataset = first_dataset_obj.model_dump()
            elif isinstance(first_dataset_obj, dict):
                first_dataset = first_dataset_obj
            else:
                # For Pydantic objects without model_dump
                first_dataset = {"table_name": first_dataset_obj.table_name}
        else:
            first_dataset = {"table_name": "unknown"}

        super().__init__(first_dataset, logger)

        self.schema = schema
        self.output_dir = Path(output_dir)
        self.locale = locale

        # Initialize processors and exporters
        self.processors: dict[str, SchemaProcessor] = {}
        self.exporters: dict[str, Any] = {}

        # Global configuration
        self.global_config = schema.global_config or {}

    def parse(self) -> None:
        """
        Parse schema configuration and set up processors and exporters.
        """
        self.logger.info(f"Parsing schema with {len(self.schema.datasets)} datasets...")

        try:
            # Create processors for each dataset
            for dataset_config in self.schema.datasets:
                # Handle both dict and DatasetSchema objects
                if isinstance(dataset_config, dict):
                    dataset_schema = DatasetSchema(**dataset_config)
                    table_name = dataset_schema.table_name
                    config_seed = dataset_config.get("seed")
                else:
                    dataset_schema = dataset_config
                    table_name = dataset_schema.table_name
                    config_seed = getattr(dataset_config, "seed", None)

                # Get seed from global config or dataset config
                seed = self.global_config.get("seed") or config_seed

                processor = SchemaProcessor(
                    dataset_schema=dataset_schema,
                    locale=self.locale,
                    seed=seed,
                    logger=self.logger,
                )

                processor.parse_schema()
                self.processors[table_name] = processor

            # Create exporters for each dataset
            datasets_config = []
            for dataset in self.schema.datasets:
                if hasattr(dataset, "model_dump"):
                    datasets_config.append(dataset.model_dump())
                elif isinstance(dataset, dict):
                    datasets_config.append(dataset)
                else:
                    # Convert Pydantic object to dict manually
                    datasets_config.append(dataset.__dict__)

            self.exporters = ExporterFactory.create_exporters_for_datasets(
                datasets_config=datasets_config,
                global_options=self.global_config.get("export_options", {}),
                logger=self.logger,
            )

            self.logger.info(
                f"Successfully created {len(self.processors)} processors and "
                f"{len(self.exporters)} exporters"
            )

        except Exception as e:
            self.logger.error(f"Failed to parse schema: {e}")
            raise

    def generate(
        self, record_count: int | None = None
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Generate synthetic data for all datasets.

        Args:
            record_count: Optional override for number of records (uses schema default if None)

        Returns:
            Dictionary mapping table names to generated data
        """
        if not self.processors:
            raise ValueError("No processors available. Call parse() first.")

        all_generated_data = {}

        for dataset_config in self.schema.datasets:
            if isinstance(dataset_config, dict):
                table_name = dataset_config.get("table_name", "unknown")
                dataset_record_count = record_count or dataset_config.get(
                    "record_count", 1000
                )
            else:  # DatasetSchema object
                table_name = dataset_config.table_name
                dataset_record_count = record_count or dataset_config.record_count

            processor = self.processors.get(table_name)
            if processor is None:
                self.logger.warning(f"No processor found for table: {table_name}")
                continue

            try:
                # Use optimized generation if available
                if hasattr(processor, "process_dataset_optimized"):
                    data = processor.process_dataset_optimized(dataset_record_count)
                else:
                    data = processor.process_dataset(dataset_record_count)

                all_generated_data[table_name] = data

                self.logger.info(
                    f"Generated {len(data)} records for table: {table_name}"
                )

            except Exception as e:
                self.logger.error(
                    f"Failed to generate data for table '{table_name}': {e}"
                )
                continue

        total_records = sum(len(data) for data in all_generated_data.values())
        self.logger.info(
            f"Generated data for {len(all_generated_data)} tables "
            f"({total_records} total records)"
        )

        return all_generated_data

    def export(
        self,
        data: dict[str, list[dict[str, Any]]] | list[dict[str, Any]],
        output_path: str | None = None,
        format_type: str = "json",
    ) -> dict[str, str]:
        """
        Export generated data to specified formats and paths.

        Args:
            data: Data to export (dict for multiple tables, list for single table)
            output_path: Optional override for output path
            format_type: Export format for single table export

        Returns:
            Dictionary mapping table names to output file paths
        """
        if isinstance(data, list):
            # Single table export
            table_name = self.table_name
            return self._export_single_table(data, table_name, output_path, format_type)
        else:
            # Multiple tables export
            return self._export_multiple_tables(data, output_path)

    def _export_single_table(
        self,
        data: list[dict[str, Any]],
        table_name: str,
        output_path: str | None = None,
        format_type: str = "json",
    ) -> dict[str, str]:
        """Export data for a single table."""
        if output_path is None:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            output_path = str(self.output_dir / f"{table_name}.{format_type}")

        # Create exporter
        exporter = ExporterFactory.create_exporter(
            format_type=format_type,
            table_name=table_name,
            options=self.global_config.get("export_options", {}),
            logger=self.logger,
        )

        exporter.export(data, output_path)
        return {table_name: output_path}

    def _export_multiple_tables(
        self,
        data: dict[str, list[dict[str, Any]]],
        output_path: str | None = None,
    ) -> dict[str, str]:
        """Export data for multiple tables."""
        output_dir = Path(output_path) if output_path else self.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        exported_files = {}

        for table_name, table_data in data.items():
            exporter = self.exporters.get(table_name)
            if exporter is None:
                self.logger.warning(f"No exporter found for table: {table_name}")
                continue

            try:
                # Determine output file path
                format_type = exporter.get_export_format()
                output_file = output_dir / f"{table_name}.{format_type}"

                exporter.export(table_data, str(output_file))
                exported_files[table_name] = str(output_file)

            except Exception as e:
                self.logger.error(f"Failed to export table '{table_name}': {e}")
                continue

        return exported_files

    def run_pipeline(
        self,
        record_count: int | None = None,
        output_path: str | None = None,
        format_type: str = "json",
    ) -> dict[str, str]:
        """
        Execute the complete pipeline: parse -> generate -> export.

        Args:
            record_count: Optional override for number of records
            output_path: Optional override for output path
            format_type: Export format (used only for single dataset schemas)

        Returns:
            Dictionary mapping table names to output file paths
        """
        self.logger.info("Starting data generation pipeline...")

        # Parse schema
        self.parse()

        # Generate data
        generated_data = self.generate(record_count)

        # Export data
        exported_files = self.export(generated_data, output_path, format_type)

        self.logger.info(
            f"Pipeline completed successfully! "
            f"Exported {len(exported_files)} files: {list(exported_files.values())}"
        )

        return exported_files

    def validate_pipeline(self) -> dict[str, Any]:
        """
        Validate the entire pipeline configuration.

        Returns:
            Dictionary with validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "dataset_validations": {},
            "exporter_validations": {},
        }

        try:
            # Validate each dataset schema
            for dataset_config in self.schema.datasets:
                if isinstance(dataset_config, dict):
                    table_name = dataset_config.get("table_name", "unknown")
                    dataset_schema = DatasetSchema(**dataset_config)
                else:
                    table_name = dataset_config.table_name
                    dataset_schema = dataset_config

                # Create temporary processor for validation
                temp_processor = SchemaProcessor(
                    dataset_schema=dataset_schema,
                    locale=self.locale,
                    logger=self.logger,
                )

                dataset_validation = temp_processor.validate_schema()
                validation_result["dataset_validations"][
                    table_name
                ] = dataset_validation

                if not dataset_validation["valid"]:
                    validation_result["valid"] = False
                    validation_result["errors"].extend(dataset_validation["errors"])

            # Validate export configurations
            for dataset_config in self.schema.datasets:
                if isinstance(dataset_config, dict):
                    table_name = dataset_config.get("table_name", "unknown")
                    output_format = dataset_config.get("output_format", "json")
                    export_options = dataset_config.get("export_options", {})
                else:
                    table_name = dataset_config.table_name
                    output_format = getattr(dataset_config, "output_format", "json")
                    export_options = getattr(dataset_config, "export_options", {})

                # Validate export format and options
                format_valid, format_errors = ExporterFactory.validate_format_options(
                    output_format, export_options
                )

                validation_result["exporter_validations"][table_name] = {
                    "format": output_format,
                    "valid": format_valid,
                    "errors": format_errors,
                }

                if not format_valid:
                    validation_result["valid"] = False
                    validation_result["errors"].extend(format_errors)

        except Exception as e:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Pipeline validation failed: {str(e)}")

        return validation_result

    def get_pipeline_stats(self) -> dict[str, Any]:
        """
        Get statistics about the pipeline configuration.

        Returns:
            Dictionary with pipeline statistics
        """
        stats = {
            "total_datasets": len(self.schema.datasets),
            "output_directory": str(self.output_dir),
            "locale": self.locale,
            "global_config": self.global_config,
            "datasets": {},
            "supported_formats": ExporterFactory.get_supported_formats(),
        }

        for dataset_config in self.schema.datasets:
            if isinstance(dataset_config, dict):
                table_name = dataset_config.get("table_name", "unknown")
                record_count = dataset_config.get("record_count", 1000)
                output_format = dataset_config.get("output_format", "json")
            else:
                table_name = dataset_config.table_name
                record_count = dataset_config.record_count
                output_format = getattr(dataset_config, "output_format", "json")

            dataset_stats = {
                "table_name": table_name,
                "record_count": record_count,
                "output_format": output_format,
                "processor_ready": table_name in self.processors,
                "exporter_ready": table_name in self.exporters,
            }

            # Add field statistics if processor exists
            if table_name in self.processors:
                processor = self.processors[table_name]
                dataset_stats.update(processor.get_generation_stats())

            stats["datasets"][table_name] = dataset_stats

        return stats
