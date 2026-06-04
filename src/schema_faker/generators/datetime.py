import random
from datetime import datetime, timedelta
from typing import Any

from faker import Faker

from ..utils.base import BaseGenerator
from ..utils.schema_models import DateFieldConfig


class DateTimeGenerator(BaseGenerator):
    """
    Generator for date and datetime data with configurable ranges and formats.
    """

    def __init__(self, field_name: str, config: DateFieldConfig, locale: str = "en_US"):
        """
        Initialize datetime generator with field configuration.

        Args:
            field_name: Name of the field being generated
            config: Date field configuration
            locale: Faker locale for localized data
        """
        super().__init__(field_name, config)
        self.date_config = config
        self.faker = Faker(locale)

        # Create a dedicated random instance for this generator
        self._random = random.Random()

        # Parse date range
        self.start_date = (
            self._parse_date(config.start_date) if config.start_date else None
        )
        self.end_date = self._parse_date(config.end_date) if config.end_date else None

        # Set default range if not specified
        self._set_default_range()

    def _parse_date(self, date_str: str) -> datetime:
        """
        Parse date string to datetime object.

        Args:
            date_str: Date string in ISO format or configured format

        Returns:
            Parsed datetime object
        """
        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str)
        except ValueError:
            try:
                # Try configured format
                return datetime.strptime(date_str, self.date_config.date_format)
            except ValueError:
                # Try common formats
                common_formats = [
                    "%Y-%m-%d",
                    "%Y/%m/%d",
                    "%m/%d/%Y",
                    "%d/%m/%Y",
                    "%Y-%m-%d %H:%M:%S",
                    "%Y-%m-%d %H:%M",
                ]

                for fmt in common_formats:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue

                raise ValueError(f"Unable to parse date string: {date_str}")

    def _set_default_range(self) -> None:
        """Set default date range if not specified."""
        if self.start_date is None:
            self.start_date = datetime(2020, 1, 1)

        if self.end_date is None:
            self.end_date = datetime.now()

        # Ensure start_date is before end_date
        if self.start_date > self.end_date:
            self.logger.warning(
                f"Start date {self.start_date} is after end date {self.end_date}. Swapping dates."
            )
            self.start_date, self.end_date = self.end_date, self.start_date

    def set_seed(self, seed: int) -> None:
        """
        Set random seed for reproducible data generation.

        Args:
            seed: Random seed value
        """
        self._random.seed(seed)
        self.faker.seed_instance(seed)

    def generate(self) -> str:
        """
        Generate a single date/datetime string based on configuration.

        Returns:
            Generated date/datetime string in configured format
        """
        # Generate random datetime within range
        random_datetime = self._generate_random_datetime()

        # Format according to configuration
        return random_datetime.strftime(self.date_config.date_format)

    def generate_datetime_object(self) -> datetime:
        """
        Generate a datetime object (useful for internal processing).

        Returns:
            Generated datetime object
        """
        return self._generate_random_datetime()

    def _generate_random_datetime(self) -> datetime:
        """
        Generate random datetime between start_date and end_date.

        Returns:
            Random datetime object
        """
        # Calculate time difference
        time_difference = self.end_date - self.start_date
        total_seconds = int(time_difference.total_seconds())

        # Generate random offset
        random_seconds = self._random.randint(0, total_seconds)

        # Return random datetime
        return self.start_date + timedelta(seconds=random_seconds)

    def generate_date_only(self) -> str:
        """
        Generate date string without time component.

        Returns:
            Generated date string (YYYY-MM-DD format)
        """
        random_datetime = self._generate_random_datetime()
        return random_datetime.strftime("%Y-%m-%d")

    def generate_time_only(self) -> str:
        """
        Generate time string without date component.

        Returns:
            Generated time string (HH:MM:SS format)
        """
        random_datetime = self._generate_random_datetime()
        return random_datetime.strftime("%H:%M:%S")

    def generate_with_pattern(self, pattern: str) -> str:
        """
        Generate datetime using specific pattern, ignoring config format.

        Args:
            pattern: Custom strftime pattern

        Returns:
            Generated datetime string with custom pattern
        """
        random_datetime = self._generate_random_datetime()
        return random_datetime.strftime(pattern)

    def generate_business_day(self) -> str:
        """
        Generate datetime that falls on a business day (Monday-Friday).

        Returns:
            Generated business day datetime string
        """
        max_attempts = 100  # Prevent infinite loop

        for _ in range(max_attempts):
            random_datetime = self._generate_random_datetime()

            # Check if it's a business day (Monday=0, Sunday=6)
            if random_datetime.weekday() < 5:  # Monday-Friday
                return random_datetime.strftime(self.date_config.date_format)

        # Fallback: adjust to nearest business day
        random_datetime = self._generate_random_datetime()

        # If weekend, move to Monday
        if random_datetime.weekday() >= 5:
            days_to_monday = 7 - random_datetime.weekday()
            random_datetime += timedelta(days=days_to_monday)

        return random_datetime.strftime(self.date_config.date_format)

    def generate_batch_optimized(self, count: int) -> list[str]:
        """
        Generate multiple datetime values efficiently.

        Args:
            count: Number of values to generate

        Returns:
            List of generated datetime strings
        """
        # Pre-calculate time range
        time_difference = self.end_date - self.start_date
        total_seconds = int(time_difference.total_seconds())

        # Generate all random offsets at once
        random_offsets = [self._random.randint(0, total_seconds) for _ in range(count)]

        # Generate all datetimes and format them
        return [
            (self.start_date + timedelta(seconds=offset)).strftime(
                self.date_config.date_format
            )
            for offset in random_offsets
        ]

    def get_date_range_info(self) -> dict[str, str]:
        """
        Get information about the configured date range.

        Returns:
            Dictionary with date range information
        """
        return {
            "start_date": self.start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": self.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "range_days": (self.end_date - self.start_date).days,
            "format": self.date_config.date_format,
        }

    def validate_generated_value(self, value: Any) -> bool:
        """
        Validate that generated value is a valid date string.

        Args:
            value: Generated value to validate

        Returns:
            True if value is valid, False otherwise
        """
        if not isinstance(value, str):
            return False

        try:
            # Try to parse with configured format
            parsed_date = datetime.strptime(value, self.date_config.date_format)

            # Check if within valid range
            return self.start_date <= parsed_date <= self.end_date

        except ValueError:
            return False
