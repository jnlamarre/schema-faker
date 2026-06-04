import pytest
from datetime import datetime, timedelta

from schema_faker.generators.datetime import DateTimeGenerator
from schema_faker.utils.schema_models import DateFieldConfig


class TestDateTimeGenerator:
    """Test cases for DateTimeGenerator."""

    def test_basic_datetime_generation(self):
        """Test basic datetime generation."""
        config = DateFieldConfig(
            start_date="2023-01-01",
            end_date="2023-12-31",
            date_format="%Y-%m-%d"
        )
        generator = DateTimeGenerator("test_datetime", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            
            # Parse and validate date is within range
            parsed_date = datetime.strptime(value, "%Y-%m-%d")
            start = datetime(2023, 1, 1)
            end = datetime(2023, 12, 31)
            assert start <= parsed_date <= end

    def test_default_date_range(self):
        """Test generation with default date range."""
        config = DateFieldConfig(date_format="%Y-%m-%d")
        generator = DateTimeGenerator("test_default", config)
        
        value = generator.generate()
        assert isinstance(value, str)
        
        # Should be parseable and reasonable
        parsed_date = datetime.strptime(value, "%Y-%m-%d")
        assert datetime(2020, 1, 1) <= parsed_date <= datetime.now() + timedelta(days=1)

    def test_custom_date_format(self):
        """Test generation with custom date format."""
        config = DateFieldConfig(
            start_date="2023-06-01",
            end_date="2023-06-30",
            date_format="%m/%d/%Y"
        )
        generator = DateTimeGenerator("test_format", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            
            # Should match MM/DD/YYYY format
            parsed_date = datetime.strptime(value, "%m/%d/%Y")
            assert datetime(2023, 6, 1) <= parsed_date <= datetime(2023, 6, 30)

    def test_datetime_with_time(self):
        """Test datetime generation including time."""
        config = DateFieldConfig(
            start_date="2023-01-01 00:00:00",
            end_date="2023-01-02 23:59:59",
            date_format="%Y-%m-%d %H:%M:%S"
        )
        generator = DateTimeGenerator("test_time", config)
        
        for _ in range(5):
            value = generator.generate()
            assert isinstance(value, str)
            
            # Should include time component
            assert " " in value
            parsed_datetime = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            start = datetime(2023, 1, 1, 0, 0, 0)
            end = datetime(2023, 1, 2, 23, 59, 59)
            assert start <= parsed_datetime <= end

    def test_datetime_object_generation(self):
        """Test generation of datetime objects."""
        config = DateFieldConfig(
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        generator = DateTimeGenerator("test_obj", config)
        
        for _ in range(5):
            dt_obj = generator.generate_datetime_object()
            assert isinstance(dt_obj, datetime)
            assert datetime(2023, 1, 1) <= dt_obj <= datetime(2023, 1, 31)

    def test_date_only_generation(self):
        """Test date-only generation."""
        config = DateFieldConfig(
            start_date="2023-01-01",
            end_date="2023-01-31"
        )
        generator = DateTimeGenerator("test_date_only", config)
        
        for _ in range(5):
            value = generator.generate_date_only()
            assert isinstance(value, str)
            
            # Should be in YYYY-MM-DD format
            parsed_date = datetime.strptime(value, "%Y-%m-%d")
            assert datetime(2023, 1, 1) <= parsed_date <= datetime(2023, 1, 31)

    def test_time_only_generation(self):
        """Test time-only generation."""
        config = DateFieldConfig()
        generator = DateTimeGenerator("test_time_only", config)
        
        for _ in range(5):
            value = generator.generate_time_only()
            assert isinstance(value, str)
            
            # Should be in HH:MM:SS format
            time_parts = value.split(":")
            assert len(time_parts) == 3
            assert 0 <= int(time_parts[0]) <= 23  # Hours
            assert 0 <= int(time_parts[1]) <= 59  # Minutes
            assert 0 <= int(time_parts[2]) <= 59  # Seconds

    def test_custom_pattern_generation(self):
        """Test generation with custom pattern."""
        config = DateFieldConfig(
            start_date="2023-01-01",
            end_date="2023-12-31"
        )
        generator = DateTimeGenerator("test_pattern", config)
        
        # Test different patterns
        patterns = [
            "%Y",          # Year only
            "%B %Y",       # Month Year
            "%d/%m/%Y",    # Day/Month/Year
            "%A, %B %d"    # Weekday, Month Day
        ]
        
        for pattern in patterns:
            value = generator.generate_with_pattern(pattern)
            assert isinstance(value, str)
            assert len(value) > 0

    def test_business_day_generation(self):
        """Test business day generation."""
        config = DateFieldConfig(
            start_date="2023-01-01",  # Sunday
            end_date="2023-01-31",
            date_format="%Y-%m-%d"
        )
        generator = DateTimeGenerator("test_business", config)
        
        for _ in range(5):
            value = generator.generate_business_day()
            parsed_date = datetime.strptime(value, "%Y-%m-%d")
            
            # Should be Monday-Friday (weekday 0-4)
            assert 0 <= parsed_date.weekday() <= 4

    def test_batch_generation_optimized(self):
        """Test optimized batch generation."""
        config = DateFieldConfig(
            start_date="2023-01-01",
            end_date="2023-01-31",
            date_format="%Y-%m-%d"
        )
        generator = DateTimeGenerator("test_batch", config)
        
        batch = generator.generate_batch_optimized(50)
        assert len(batch) == 50
        assert all(isinstance(v, str) for v in batch)
        
        # All should be valid dates in range
        for value in batch:
            parsed_date = datetime.strptime(value, "%Y-%m-%d")
            assert datetime(2023, 1, 1) <= parsed_date <= datetime(2023, 1, 31)

    def test_date_range_info(self):
        """Test date range information retrieval."""
        config = DateFieldConfig(
            start_date="2023-06-01",
            end_date="2023-06-30",
            date_format="%Y-%m-%d"
        )
        generator = DateTimeGenerator("test_info", config)
        
        info = generator.get_date_range_info()
        assert "start_date" in info
        assert "end_date" in info
        assert "range_days" in info
        assert "format" in info
        
        assert info["range_days"] == 29  # June has 30 days, so range is 29
        assert info["format"] == "%Y-%m-%d"

    def test_validation(self):
        """Test value validation."""
        config = DateFieldConfig(
            start_date="2023-01-01",
            end_date="2023-12-31",
            date_format="%Y-%m-%d"
        )
        generator = DateTimeGenerator("test_validation", config)
        
        # Valid date in range
        assert generator.validate_generated_value("2023-06-15") is True
        
        # Invalid - not string
        assert generator.validate_generated_value(20230615) is False
        
        # Invalid - wrong format
        assert generator.validate_generated_value("06/15/2023") is False
        
        # Invalid - out of range
        assert generator.validate_generated_value("2024-01-01") is False

    def test_swapped_dates_handling(self):
        """Test handling of swapped start/end dates."""
        config = DateFieldConfig(
            start_date="2023-12-31",  # Later date
            end_date="2023-01-01",    # Earlier date
            date_format="%Y-%m-%d"
        )
        # Should handle this gracefully by swapping
        generator = DateTimeGenerator("test_swap", config)
        
        value = generator.generate()
        parsed_date = datetime.strptime(value, "%Y-%m-%d")
        # Should be in the corrected range
        assert datetime(2023, 1, 1) <= parsed_date <= datetime(2023, 12, 31)

    def test_various_date_formats_parsing(self):
        """Test parsing of various input date formats."""
        test_cases = [
            ("2023-01-01", "%Y-%m-%d"),
            ("2023/01/01", "%Y-%m-%d"),
            ("01/01/2023", "%Y-%m-%d"),
            ("2023-01-01 12:00:00", "%Y-%m-%d %H:%M:%S"),
        ]
        
        for start_date, format_str in test_cases:
            config = DateFieldConfig(
                start_date=start_date,
                end_date="2023-12-31",
                date_format=format_str
            )
            # Should not raise exception during initialization
            generator = DateTimeGenerator("test_parse", config)
            
            # Should generate valid values
            value = generator.generate()
            assert isinstance(value, str)

    def test_seed_reproducibility(self):
        """Test that setting seed produces reproducible results."""
        config = DateFieldConfig(
            start_date="2023-01-01",
            end_date="2023-12-31",
            date_format="%Y-%m-%d"
        )
        
        generator1 = DateTimeGenerator("test_seed1", config)
        generator1.set_seed(42)
        
        generator2 = DateTimeGenerator("test_seed2", config)
        generator2.set_seed(42)
        
        values1 = [generator1.generate() for _ in range(10)]
        values2 = [generator2.generate() for _ in range(10)]
        
        assert values1 == values2