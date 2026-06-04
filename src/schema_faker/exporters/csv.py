import csv
import logging
from pathlib import Path
from typing import Any

from ..utils.base import BaseExporter


class CSVExporter(BaseExporter):
    """
    Exporter for CSV format output.
    Handles converting generated data to comma-separated values format.
    """

    def __init__(
        self,
        table_name: str,
        delimiter: str = ",",
        quote_char: str = '"',
        include_header: bool = True,
        logger: logging.Logger | None = None,
    ):
        """
        Initialize CSV exporter with formatting options.

        Args:
            table_name: Name of the table/dataset being exported
            delimiter: CSV delimiter character (default: comma)
            quote_char: Quote character for string values
            include_header: Whether to include column headers
            logger: Optional logger instance
        """
        super().__init__(table_name, logger)
        self.delimiter = delimiter
        self.quote_char = quote_char
        self.include_header = include_header

    def export(self, data: list[dict[str, Any]], output_path: str) -> None:
        """
        Export data to CSV file.

        Args:
            data: Generated data to export
            output_path: Path where the CSV should be exported

        Raises:
            ValueError: If data validation fails
            IOError: If file cannot be written
        """
        if not self.validate_data(data):
            raise ValueError("Data validation failed for CSV export")

        if not data:
            self.logger.warning("Empty dataset, creating empty CSV file")
            Path(output_path).touch()
            return

        try:
            # Ensure output directory exists
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Extract field names from first record
            fieldnames = list(data[0].keys())

            self.logger.info(f"Exporting {len(data)} records to CSV: {output_path}")

            with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fieldnames,
                    delimiter=self.delimiter,
                    quotechar=self.quote_char,
                    quoting=csv.QUOTE_MINIMAL,
                )

                if self.include_header:
                    writer.writeheader()

                # Write data rows
                for record in data:
                    # Convert None values to empty strings for CSV compatibility
                    cleaned_record = {
                        field: "" if value is None else value
                        for field, value in record.items()
                    }
                    writer.writerow(cleaned_record)

            self.logger.info(
                f"Successfully exported {len(data)} records to {output_path}"
            )

        except Exception as e:
            self.logger.error(f"Failed to export CSV to {output_path}: {e}")
            raise OSError(f"CSV export failed: {e}") from e

    def export_multiple_tables(
        self, datasets: dict[str, list[dict[str, Any]]], output_dir: str
    ) -> dict[str, str]:
        """
        Export multiple datasets to separate CSV files.

        Args:
            datasets: Dictionary mapping table names to data lists
            output_dir: Directory to write CSV files

        Returns:
            Dictionary mapping table names to output file paths
        """
        output_dir_path = Path(output_dir)
        output_dir_path.mkdir(parents=True, exist_ok=True)

        exported_files = {}

        for table_name, data in datasets.items():
            csv_filename = f"{table_name}.csv"
            output_path = output_dir_path / csv_filename

            # Create a separate exporter for each table to maintain proper logging
            table_exporter = CSVExporter(
                table_name=table_name,
                delimiter=self.delimiter,
                quote_char=self.quote_char,
                include_header=self.include_header,
                logger=self.logger,
            )

            table_exporter.export(data, str(output_path))
            exported_files[table_name] = str(output_path)

        self.logger.info(
            f"Exported {len(datasets)} datasets to {len(exported_files)} CSV files in {output_dir}"
        )

        return exported_files

    def get_export_format(self) -> str:
        """
        Get the export format identifier.

        Returns:
            Format identifier string
        """
        return "csv"

    def validate_data(self, data: list[dict[str, Any]]) -> bool:
        """
        Enhanced validation for CSV export compatibility.

        Args:
            data: Data to validate

        Returns:
            True if data is valid for CSV export
        """
        # Use base validation first
        if not super().validate_data(data):
            return False

        if not data:
            return True

        # Validate that all records have consistent field structure
        first_record_keys = set(data[0].keys())

        for i, record in enumerate(data[1:], 1):
            if set(record.keys()) != first_record_keys:
                self.logger.error(
                    f"Inconsistent field structure at record {i}. "
                    f"Expected: {first_record_keys}, Got: {set(record.keys())}"
                )
                return False

        # Validate that field names don't contain problematic characters
        problematic_chars = ["\n", "\r", self.delimiter]
        for field_name in first_record_keys:
            if any(char in field_name for char in problematic_chars):
                self.logger.error(
                    f"Field name '{field_name}' contains problematic characters for CSV export"
                )
                return False

        self.logger.debug(f"CSV validation passed for {len(data)} records")
        return True
