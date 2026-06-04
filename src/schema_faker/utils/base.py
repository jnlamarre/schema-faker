import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseGenerator(ABC):
    """
    Abstract base class for data generators.
    Defines the common interface for generating synthetic data.
    """

    def __init__(self, field_name: str, config: Dict[str, Any]):
        """
        Initialize generator with field name and configuration.

        Args:
            field_name: Name of the field being generated
            config: Configuration dictionary for this generator
        """
        self.field_name = field_name
        self.config = config
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{field_name}")

    @abstractmethod
    def generate(self) -> Any:
        """
        Generate a single synthetic data value.

        Returns:
            Generated synthetic data value
        """
        pass  # pragma: no cover

    def generate_batch(self, count: int) -> List[Any]:
        """
        Generate multiple synthetic data values.

        Args:
            count: Number of values to generate

        Returns:
            List of generated synthetic data values
        """
        return [self.generate() for _ in range(count)]


class BaseProcessor(ABC):
    """
    Abstract base class for data processors.
    Handles schema parsing and generator orchestration.
    """

    def __init__(self, schema_config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize processor with schema configuration and optional logger.

        Args:
            schema_config: Schema configuration dictionary
            logger: Optional logger instance for processor operations
        """
        self.schema_config = schema_config
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}")
        self.generators: Dict[str, BaseGenerator] = {}

    @abstractmethod
    def parse_schema(self) -> None:
        """
        Parse schema configuration and create appropriate generators.
        """
        pass  # pragma: no cover

    @abstractmethod
    def process_dataset(self, record_count: int) -> List[Dict[str, Any]]:
        """
        Generate a complete dataset using configured generators.

        Args:
            record_count: Number of records to generate

        Returns:
            List of generated records
        """
        pass  # pragma: no cover


class BaseExporter(ABC):
    """
    Abstract base class for data exporters.
    Handles exporting generated data to various formats.
    """

    def __init__(self, table_name: str, logger: Optional[logging.Logger] = None):
        """
        Initialize exporter with table name and optional logger.

        Args:
            table_name: Name of the table/dataset being exported
            logger: Optional logger instance for exporter operations
        """
        self.table_name = table_name
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}.{table_name}")

    @abstractmethod
    def export(self, data: List[Dict[str, Any]], output_path: str) -> None:
        """
        Export data to the specified output path.

        Args:
            data: Generated data to export
            output_path: Path where the data should be exported
        """
        pass  # pragma: no cover

    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate data before export.

        Args:
            data: Data to validate

        Returns:
            True if data is valid for export
        """
        if not isinstance(data, list):
            self.logger.error("Data must be a list of dictionaries")
            return False

        if not data:
            self.logger.warning("Data list is empty")
            return True

        if not all(isinstance(record, dict) for record in data):
            self.logger.error("All records must be dictionaries")
            return False

        return True


class BasePipeline(ABC):
    """
    Abstract base class for data generation pipelines.
    Defines the common interface for parse -> generate -> export operations.
    """

    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        Initialize pipeline with configuration and optional logger.

        Args:
            config: Pipeline configuration dictionary
            logger: Optional logger instance for pipeline operations
        """
        self.config = config
        self.table_name = config.get("table_name", "unknown")
        self.logger = logger or logging.getLogger(f"{self.__class__.__name__}.{self.table_name}")

    @abstractmethod
    def parse(self) -> None:
        """
        Parse configuration and set up generators.
        """
        pass  # pragma: no cover

    @abstractmethod
    def generate(self, record_count: int) -> List[Dict[str, Any]]:
        """
        Generate synthetic data.

        Args:
            record_count: Number of records to generate

        Returns:
            Generated synthetic data
        """
        pass  # pragma: no cover

    @abstractmethod
    def export(self, data: List[Dict[str, Any]], output_path: str, format_type: str) -> None:
        """
        Export generated data.

        Args:
            data: Data to export
            output_path: Output file path
            format_type: Export format (csv, json, etc.)
        """
        pass  # pragma: no cover

    def run_pipeline(
        self,
        record_count: int,
        output_path: str,
        format_type: str = "json"
    ) -> None:
        """
        Execute the complete pipeline: parse -> generate -> export.

        Args:
            record_count: Number of records to generate
            output_path: Output file path
            format_type: Export format (csv, json, etc.)
        """
        self.logger.info(f"Starting {self.__class__.__name__} pipeline for {self.table_name}...")

        # Parse configuration
        self.parse()
        self.logger.info("Schema parsing completed")

        # Generate data
        data = self.generate(record_count)
        self.logger.info(f"Generated {len(data)} records")

        # Export data
        self.export(data, output_path, format_type)
        self.logger.info(f"Data exported to {output_path}")

        self.logger.info(f"{self.__class__.__name__} pipeline completed successfully!")