import random
import re
import string
import uuid
from typing import Any

from faker import Faker

from ..utils.base import BaseGenerator
from ..utils.schema_models import StringFieldConfig, StringSubtype


class StringGenerator(BaseGenerator):
    """
    Generator for string data with support for various subtypes using Faker library.
    Supports names, addresses, emails, phone numbers, UUIDs, IP addresses, and more.
    """

    def __init__(
        self, field_name: str, config: StringFieldConfig, locale: str = "en_US"
    ):
        """
        Initialize string generator with field configuration.

        Args:
            field_name: Name of the field being generated
            config: String field configuration
            locale: Faker locale for localized data (default: en_US)
        """
        super().__init__(field_name, config)
        self.string_config = config
        self.faker = Faker(locale)

        # Seed faker for reproducible results if needed
        # (This can be overridden by calling set_seed later)
        self.faker.seed_instance(42)

    def set_seed(self, seed: int) -> None:
        """
        Set random seed for reproducible data generation.

        Args:
            seed: Random seed value
        """
        random.seed(seed)
        self.faker.seed_instance(seed)

    def generate(self) -> str:
        """
        Generate a single string value based on configuration.

        Returns:
            Generated string value
        """
        # Handle predefined choices first
        if self.string_config.choices:
            return random.choice(self.string_config.choices)

        # Generate based on subtype
        generated_value = self._generate_by_subtype()

        # Apply length constraints if specified
        return self._apply_length_constraints(generated_value)

    def _generate_by_subtype(self) -> str:
        """
        Generate string based on configured subtype.

        Returns:
            Generated string value
        """
        subtype = self.string_config.subtype

        generators = {
            StringSubtype.RANDOM: self._generate_random_string,
            StringSubtype.NAME: self._generate_full_name,
            StringSubtype.FIRST_NAME: self._generate_first_name,
            StringSubtype.LAST_NAME: self._generate_last_name,
            StringSubtype.EMAIL: self._generate_email,
            StringSubtype.ADDRESS: self._generate_address,
            StringSubtype.PHONE: self._generate_phone,
            StringSubtype.COMPANY: self._generate_company,
            StringSubtype.UUID: self._generate_uuid,
            StringSubtype.IP_ADDRESS: self._generate_ip_address,
        }

        generator_func = generators.get(subtype)
        if generator_func is None:
            raise ValueError(f"Unsupported string subtype: {subtype}")

        return generator_func()

    def _generate_random_string(self) -> str:
        """Generate random alphanumeric string."""
        # Determine length
        min_len = self.string_config.min_length or 5
        max_len = self.string_config.max_length or 20
        length = random.randint(min_len, max_len)

        # Use custom pattern if provided
        if self.string_config.pattern:
            return self._generate_from_pattern()

        # Generate random alphanumeric string
        characters = string.ascii_letters + string.digits
        return "".join(random.choice(characters) for _ in range(length))

    def _generate_from_pattern(self) -> str:
        """
        Generate string based on regex pattern.

        Note: This is a simplified pattern generator.
        For complex patterns, consider using external libraries like rstr.
        """
        pattern = self.string_config.pattern

        # Handle quantifiers first (like {3}, {2,5}, etc.)
        def expand_quantifiers(text):
            # Handle {n} quantifiers
            text = re.sub(
                r"(\\[dws]|\[[^\]]+\])\{(\d+)\}",
                lambda m: m.group(1) * int(m.group(2)),
                text,
            )
            # Handle {n,m} quantifiers - use minimum for simplicity
            text = re.sub(
                r"(\\[dws]|\[[^\]]+\])\{(\d+),\d+\}",
                lambda m: m.group(1) * int(m.group(2)),
                text,
            )
            return text

        expanded_pattern = expand_quantifiers(pattern)

        # Simple pattern substitutions
        pattern_substitutions = {
            r"\\d": lambda: str(random.randint(0, 9)),
            r"\\w": lambda: random.choice(string.ascii_letters + string.digits + "_"),
            r"\\s": lambda: " ",
            r"[0-9]": lambda: str(random.randint(0, 9)),
            r"[a-z]": lambda: random.choice(string.ascii_lowercase),
            r"[A-Z]": lambda: random.choice(string.ascii_uppercase),
            r"[a-zA-Z]": lambda: random.choice(string.ascii_letters),
        }

        result = expanded_pattern
        for pattern_regex, replacement_func in pattern_substitutions.items():
            # Use re.sub with a function to replace all occurrences at once
            result = re.sub(pattern_regex, lambda m: replacement_func(), result)

        return result

    def _generate_full_name(self) -> str:
        """Generate full name using Faker."""
        return self.faker.name()

    def _generate_first_name(self) -> str:
        """Generate first name using Faker."""
        return self.faker.first_name()

    def _generate_last_name(self) -> str:
        """Generate last name using Faker."""
        return self.faker.last_name()

    def _generate_email(self) -> str:
        """Generate email address using Faker."""
        return self.faker.email()

    def _generate_address(self) -> str:
        """Generate street address using Faker."""
        return self.faker.address().replace(
            "\n", ", "
        )  # Convert multiline to single line

    def _generate_phone(self) -> str:
        """Generate phone number using Faker."""
        return self.faker.phone_number()

    def _generate_company(self) -> str:
        """Generate company name using Faker."""
        return self.faker.company()

    def _generate_uuid(self) -> str:
        """Generate UUID string."""
        return str(uuid.uuid4())

    def _generate_ip_address(self) -> str:
        """Generate IP address using Faker."""
        return self.faker.ipv4()

    def _apply_length_constraints(self, value: str) -> str:
        """
        Apply min/max length constraints to generated string.

        Args:
            value: Original generated string

        Returns:
            String adjusted to meet length constraints
        """
        min_len = self.string_config.min_length
        max_len = self.string_config.max_length

        # Truncate if too long
        if max_len is not None and len(value) > max_len:
            value = value[:max_len]

        # Pad if too short
        if min_len is not None and len(value) < min_len:
            # For most subtypes, pad with spaces or repeat the value
            if self.string_config.subtype == StringSubtype.RANDOM:
                # Pad random strings with random characters
                padding_needed = min_len - len(value)
                characters = string.ascii_letters + string.digits
                padding = "".join(
                    random.choice(characters) for _ in range(padding_needed)
                )
                value += padding
            else:
                # For semantic types (names, emails, etc.), pad with spaces
                value = value.ljust(min_len)

        return value

    def generate_batch_optimized(self, count: int) -> list[str]:
        """
        Generate multiple string values efficiently.

        Override the base class method for better performance with Faker.

        Args:
            count: Number of values to generate

        Returns:
            List of generated string values
        """
        # For certain subtypes, we can use Faker's batch generation
        if self.string_config.choices:
            return [random.choice(self.string_config.choices) for _ in range(count)]

        # Use Faker providers that support batch generation when available
        if self.string_config.subtype == StringSubtype.EMAIL:
            return [self.faker.email() for _ in range(count)]
        elif self.string_config.subtype == StringSubtype.NAME:
            return [self.faker.name() for _ in range(count)]
        elif self.string_config.subtype == StringSubtype.FIRST_NAME:
            return [self.faker.first_name() for _ in range(count)]
        elif self.string_config.subtype == StringSubtype.LAST_NAME:
            return [self.faker.last_name() for _ in range(count)]
        elif self.string_config.subtype == StringSubtype.UUID:
            return [str(uuid.uuid4()) for _ in range(count)]

        # Fall back to standard generation for other types
        return [self.generate() for _ in range(count)]

    def validate_generated_value(self, value: Any) -> bool:
        """
        Validate that generated value meets configuration constraints.

        Args:
            value: Generated value to validate

        Returns:
            True if value is valid, False otherwise
        """
        if not isinstance(value, str):
            return False

        # Check length constraints
        if (
            self.string_config.min_length is not None
            and len(value) < self.string_config.min_length
        ):
            return False

        if (
            self.string_config.max_length is not None
            and len(value) > self.string_config.max_length
        ):
            return False

        # Check choices constraint
        if self.string_config.choices and value not in self.string_config.choices:
            return False

        # Basic format validation for certain subtypes
        if self.string_config.subtype == StringSubtype.EMAIL:
            return "@" in value and "." in value.split("@")[-1]
        elif self.string_config.subtype == StringSubtype.UUID:
            try:
                uuid.UUID(value)
                return True
            except ValueError:
                return False
        elif self.string_config.subtype == StringSubtype.IP_ADDRESS:
            # Simple IPv4 validation
            parts = value.split(".")
            if len(parts) != 4:
                return False
            try:
                return all(0 <= int(part) <= 255 for part in parts)
            except ValueError:
                return False

        return True
