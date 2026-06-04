import json
import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from ..utils.base import BaseExporter


class JSONExporter(BaseExporter):
    """
    Exporter for JSON format output.
    Handles converting generated data to JavaScript Object Notation format.
    """

    def __init__(
        self,
        table_name: str,
        indent: int | None = 2,
        sort_keys: bool = False,
        ensure_ascii: bool = False,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize JSON exporter with formatting options.

        Args:
            table_name: Name of the table/dataset being exported
            indent: JSON indentation (None for compact output)
            sort_keys: Whether to sort dictionary keys
            ensure_ascii: Whether to escape non-ASCII characters
            logger: Optional logger instance
        """
        super().__init__(table_name, logger)
        self.indent = indent
        self.sort_keys = sort_keys
        self.ensure_ascii = ensure_ascii

    def export(self, data: list[dict[str, Any]], output_path: str) -> None:
        """
        Export data to JSON file.

        Args:
            data: Generated data to export
            output_path: Path where the JSON should be exported

        Raises:
            ValueError: If data validation fails
            IOError: If file cannot be written
        """
        if not self.validate_data(data):
            raise ValueError("Data validation failed for JSON export")

        try:
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"Exporting {len(data)} records to JSON: {output_path}")

            # Convert data to JSON-serializable format
            json_data = self._prepare_data_for_json(data)

            # Create output structure
            output_structure = {
                "table_name": self.table_name,
                "record_count": len(data),
                "data": json_data,
            }

            with open(output_file, "w", encoding="utf-8") as jsonfile:
                json.dump(
                    output_structure,
                    jsonfile,
                    indent=self.indent,
                    sort_keys=self.sort_keys,
                    ensure_ascii=self.ensure_ascii,
                    default=self._json_serializer,
                )

            self.logger.info(
                f"Successfully exported {len(data)} records to {output_path}"
            )

        except Exception as e:
            self.logger.error(f"Failed to export JSON to {output_path}: {e}")
            raise OSError(f"JSON export failed: {e}") from e

    def export_multiple_tables(
        self,
        datasets: dict[str, list[dict[str, Any]]],
        output_dir: str,
        single_file: bool = False,
    ) -> dict[str, str]:
        """
        Export multiple datasets to JSON files.

        Args:
            datasets: Dictionary mapping table names to data lists
            output_dir: Directory to write JSON files
            single_file: If True, export all datasets to single JSON file

        Returns:
            Dictionary mapping table names to output file paths
        """
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        exported_files = {}

        if single_file:
            # Export all datasets to single file
            combined_output_path = output_dir_path / "datasets.json"
            self._export_combined_datasets(datasets, str(combined_output_path))

            # Return the same path for all tables
            for table_name in datasets.keys():
                exported_files[table_name] = str(combined_output_path)
        else:
            # Export each dataset to separate files
            for table_name, data in datasets.items():
                json_filename = f"{table_name}.json"
                output_path = output_dir_path / json_filename

                # Create a separate exporter for each table
                table_exporter = JSONExporter(
                    table_name=table_name,
                    indent=self.indent,
                    sort_keys=self.sort_keys,
                    ensure_ascii=self.ensure_ascii,
                    logger=self.logger,
                )

                table_exporter.export(data, str(output_path))
                exported_files[table_name] = str(output_path)

        self.logger.info(f"Exported {len(datasets)} datasets to JSON in {output_dir}")

        return exported_files

    def _export_combined_datasets(
        self, datasets: dict[str, list[dict[str, Any]]], output_path: str
    ) -> None:
        """
        Export multiple datasets to a single JSON file.

        Args:
            datasets: Dictionary mapping table names to data lists
            output_path: Path for combined JSON file
        """
        try:
            # Prepare combined structure
            total_records = sum(len(data) for data in datasets.values())

            combined_structure = {
                "export_metadata": {
                    "total_tables": len(datasets),
                    "total_records": total_records,
                    "tables": list(datasets.keys()),
                },
                "datasets": {},
            }

            # Add each dataset with metadata
            for table_name, data in datasets.items():
                json_data = self._prepare_data_for_json(data)

                combined_structure["datasets"][table_name] = {
                    "table_name": table_name,
                    "record_count": len(data),
                    "data": json_data,
                }

            with open(output_path, "w", encoding="utf-8") as jsonfile:
                json.dump(
                    combined_structure,
                    jsonfile,
                    indent=self.indent,
                    sort_keys=self.sort_keys,
                    ensure_ascii=self.ensure_ascii,
                    default=self._json_serializer,
                )

            self.logger.info(
                f"Successfully exported {len(datasets)} datasets "
                f"({total_records} total records) to {output_path}"
            )

        except Exception as e:
            self.logger.error(f"Failed to export combined JSON to {output_path}: {e}")
            raise OSError(f"Combined JSON export failed: {e}") from e

    def _prepare_data_for_json(
        self, data: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Prepare data for JSON serialization by handling special types.

        Args:
            data: Raw data from generators

        Returns:
            JSON-serializable data
        """
        if not data:
            return []

        prepared_data = []

        for record in data:
            prepared_record = {}

            for field, value in record.items():
                prepared_record[field] = self._convert_value_for_json(value)

            prepared_data.append(prepared_record)

        return prepared_data

    def _convert_value_for_json(self, value: Any) -> Any:
        """
        Convert a single value to JSON-compatible format.

        Args:
            value: Value to convert

        Returns:
            JSON-compatible value
        """
        if value is None:
            return None
        elif isinstance(value, str | int | float | bool):
            return value
        elif isinstance(value, Decimal):
            return float(value)
        elif isinstance(value, date | datetime):
            return value.isoformat()
        elif isinstance(value, list | tuple):
            return [self._convert_value_for_json(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._convert_value_for_json(v) for k, v in value.items()}
        else:
            # For other types, convert to string
            return str(value)

    def _json_serializer(self, obj: Any) -> Any:
        """
        Custom JSON serializer for special object types.

        Args:
            obj: Object to serialize

        Returns:
            Serializable representation

        Raises:
            TypeError: If object cannot be serialized
        """
        if isinstance(obj, date | datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    def get_export_format(self) -> str:
        """
        Get the export format identifier.

        Returns:
            Format identifier string
        """
        return "json"

    def validate_data(self, data: list[dict[str, Any]]) -> bool:
        """
        Enhanced validation for JSON export compatibility.

        Args:
            data: Data to validate

        Returns:
            True if data is valid for JSON export
        """
        # Use base validation first
        if not super().validate_data(data):
            return False

        if not data:
            return True

        # Test JSON serializability with a sample record
        try:
            sample_record = data[0] if data else {}
            json_sample = self._prepare_data_for_json([sample_record])
            json.dumps(
                json_sample[0] if json_sample else {}, default=self._json_serializer
            )

            self.logger.debug(f"JSON validation passed for {len(data)} records")
            return True

        except Exception as e:
            self.logger.error(f"JSON serialization validation failed: {e}")
            return False
