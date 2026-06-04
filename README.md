# Schema-Faker

A configurable synthetic data generator for development and testing environments.

## Features

- **Multiple Data Types**: Generate numeric, string, boolean, date, and datetime data
- **Advanced String Types**: Names, emails, addresses, phone numbers, UUIDs, IP addresses
- **Flexible Configuration**: YAML or JSON schema definitions with Pydantic validation
- **Multiple Output Formats**: JSON, CSV, and SQL export options
- **Multiple Datasets**: Generate multiple related tables in a single run
- **Reproducible**: Configurable random seeds for consistent test data

## Installation

```bash
# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

## Quick Start

1. Create a schema configuration file:

```yaml
# users_schema.yaml
version: "1.0"
datasets:
  - table_name: "users"
    record_count: 1000
    fields:
      - name: "id"
        type: "numeric"
        config:
          subtype: "integer"
          min_value: 1
          max_value: 999999
      - name: "email"
        type: "string"
        config:
          subtype: "email"
```

2. Generate synthetic data:

```bash
# Generate JSON output (default)
schema-faker -s users_schema.yaml -o ./output/

# Generate CSV with custom record count
schema-faker -s users_schema.yaml -f csv -r 5000 -o ./output/

# Generate SQL with seed for reproducible data
schema-faker -s users_schema.yaml -f sql --seed 42 -o ./output/

# Validate schema without generating data
schema-faker -s users_schema.yaml --validate-only

# List all supported export formats
schema-faker --list-formats
```

## CLI Options

- `-s, --schema`: Path to YAML/JSON schema configuration file
- `-o, --output`: Output directory for generated files
- `-f, --format`: Export format (json, csv, sql)
- `-r, --records`: Override record count for all datasets
- `--seed`: Random seed for reproducible generation
- `--locale`: Locale for data generation (default: en_US)
- `--validate-only`: Validate schema without generating data
- `--list-formats`: Show supported export formats and options
- `-v, --verbose`: Enable verbose logging

## Project Status

🎉 **Phase 3 Complete** - Production-ready synthetic data generator with full export system

### Phase 1: Foundation ✅
- ✅ **Project Structure**: Clean architecture with clear separation of concerns
- ✅ **Pydantic Schema Models**: Type-safe configuration with comprehensive validation
- ✅ **Abstract Base Classes**: Extensible framework for generators and exporters
- ✅ **CLI Framework**: Click-based interface with proper argument parsing
- ✅ **Development Tooling**: UV, ruff, pre-commit hooks, pytest integration

### Phase 2: Core Data Generation ✅
- ✅ **NumericGenerator**: Integers, floats, decimals with statistical distributions (uniform, normal, exponential)
- ✅ **StringGenerator**: Faker integration for names, emails, addresses, phones, IPs, UUIDs
- ✅ **BooleanGenerator**: Configurable true/false probability
- ✅ **DateTimeGenerator**: Date ranges, custom formats, business day filtering with seed reproducibility
- ✅ **GeneratorFactory**: Polymorphic creation with factory pattern
- ✅ **SchemaProcessor**: Complete pipeline orchestration with validation and optimization
- ✅ **Test Infrastructure**: 100+ optimized tests with comprehensive coverage

### Phase 3: Export System ✅
- ✅ **CSVExporter**: Configurable CSV output with proper quoting and null handling
- ✅ **JSONExporter**: Structured JSON with metadata, type-safe serialization
- ✅ **SQLExporter**: Multi-dialect SQL (PostgreSQL, MySQL, SQLite, MSSQL) with batched INSERTs
- ✅ **ExporterFactory**: Polymorphic exporter creation with format validation
- ✅ **DataPipeline**: Complete orchestration with multi-dataset support
- ✅ **CLI Integration**: Full featured command-line interface with validation, progress reporting

## Development

```bash
# Install development dependencies
uv sync --group dev --group test

# Run tests
pytest

# Code formatting and linting
uv run ruff format .
uv run ruff check .

# Pre-commit hooks
uv run pre-commit install
```

## Architecture

Built with modern Python best practices:

- **Clean Architecture**: Clear separation between data generation, processing, and export
- **Abstract Base Classes**: Extensible generator and exporter interfaces
- **Pydantic Models**: Type-safe configuration with automatic validation
- **Composition over Inheritance**: Flexible, maintainable design patterns
- **Comprehensive Testing**: Unit, integration, and end-to-end test coverage

## License

MIT License
