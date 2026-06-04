# Schema-Faker Project

## Overview
Configurable synthetic data generator CLI tool built with modern Python practices, inspired by the energy-analytics project architecture.

## Project Structure
```
schema-faker/
├── README.md                   # User documentation
├── CLAUDE.md                   # This file - Project context for Claude
├── PLAN.md                     # Implementation roadmap
├── pyproject.toml              # UV package management (Python 3.11+)
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── .coveragerc                 # Coverage reporting configuration
├── .gitignore                  # Git ignore patterns
├── examples/                   # Example schema configurations
│   └── users_schema.yaml       # Sample user dataset schema
├── src/                        # Main source code
│   └── schema_faker/           # Package root
│       ├── __init__.py
│       ├── cli.py              # Click-based CLI interface
│       ├── generators/         # Data generation implementations
│       │   └── __init__.py
│       ├── exporters/          # Output format handlers
│       │   └── __init__.py
│       └── utils/              # Core utilities and base classes
│           ├── __init__.py
│           ├── base.py         # Abstract base classes
│           └── schema_models.py # Pydantic schema definitions
├── tests/                      # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py             # Central fixture definitions
│   ├── unit/                   # Unit tests
│   │   ├── __init__.py
│   │   └── test_schema_models.py # Schema validation tests
│   ├── integration/            # Integration tests (planned)
│   │   └── __init__.py
│   ├── e2e/                   # End-to-end tests (planned)
│   │   └── __init__.py
│   └── fixtures/              # Test data and configurations (planned)
│       └── __init__.py
├── sql/                       # SQL schema definitions (planned)
├── .venv/                     # Virtual environment (ignored)
└── htmlcov/                   # HTML coverage reports (ignored)
```

## Current Status 🎉 PHASE 3 COMPLETE

### Completed Features
- **Modern Project Foundation**: Clean architecture with separation of concerns
- **Pydantic Schema Models**: Type-safe configuration with comprehensive validation
- **Abstract Base Classes**: Extensible framework for generators and exporters
- **CLI Framework**: Click-based interface with proper argument parsing
- **Core Data Generators**: Full implementation with advanced features and seed reproducibility
- **Export System**: Complete CSV, JSON, SQL exporters with multi-dialect support
- **Pipeline Architecture**: Full orchestration with multi-dataset support and validation
- **Schema Processing Pipeline**: Complete orchestration and validation
- **Test Infrastructure**: 100+ optimized tests with comprehensive coverage
- **Development Tooling**: UV, ruff, pre-commit, pytest integration
- **Production CLI**: Full-featured command-line interface with progress reporting

### Architecture Highlights
- **Clean Architecture**: Following energy-analytics patterns with utils/, generators/, exporters/
- **Pydantic Validation**: Comprehensive field validation with custom validators
- **Abstract Base Classes**: `BaseGenerator`, `BaseProcessor`, `BaseExporter`, `BasePipeline`
- **Factory Patterns**: `GeneratorFactory` and `ExporterFactory` for polymorphic creation
- **Advanced Data Generation**: Statistical distributions, Faker integration, optimized batch processing
- **Export System**: Multi-format exporters (CSV, JSON, SQL) with dialect-specific optimizations
- **Pipeline Architecture**: Complete `DataPipeline` orchestration with validation and error handling
- **Type Safety**: Modern Python 3.11+ type hints throughout
- **Composition over Inheritance**: Flexible, maintainable design patterns
- **Seed Reproducibility**: Instance-specific random generators for consistent test data

## Key Commands
```bash
# Installation and setup
uv sync --link-mode=copy          # Install all dependencies
uv sync --group dev --group test  # Install dev and test dependencies

# CLI usage (Production ready)
uv run schema-faker --help                              # Show CLI options
uv run schema-faker --list-formats                      # List export formats
uv run schema-faker -s examples/users_schema.yaml -f json  # Generate JSON
uv run schema-faker -s examples/users_schema.yaml -f csv -r 5000  # Generate CSV
uv run schema-faker -s examples/users_schema.yaml --validate-only # Validate only

# Testing and code quality
uv run pytest                     # Run all tests with coverage
uv run pytest tests/unit/ -v      # Run unit tests with verbose output
uv run ruff check .               # Check code quality
uv run ruff format .              # Format code
uv run pre-commit run --all-files # Run all pre-commit hooks

# Development workflow
uv run pre-commit install         # Install git hooks
git add . && git commit -m "msg"  # Triggers automatic quality checks
```

## Schema Configuration Format

### YAML Example
```yaml
version: "1.0"
datasets:
  - table_name: "users"
    record_count: 1000
    output_format: "json"
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
      - name: "age"
        type: "numeric"
        nullable: true
        null_probability: 0.1
        config:
          subtype: "integer"
          min_value: 18
          max_value: 100
```

### Supported Data Types
- **Numeric**: integer, float, decimal with min/max ranges
- **String**: random, name, email, address, phone, ip_address, uuid
- **Boolean**: configurable true/false probability
- **Date/DateTime**: date ranges with custom formatting
- **Advanced Features**: nullable fields, choices, custom patterns

## Development Approach
Following the energy-analytics project patterns:

### Code Quality Standards
- **Type Safety**: Full Pydantic integration with validation
- **Testing**: Comprehensive unit tests with fixtures and parametrization
- **Architecture**: Clean separation with abstract base classes
- **Modern Tooling**: UV package manager, ruff formatting, pre-commit hooks

### Testing Strategy
- **Unit Tests**: Schema validation, field configurations, edge cases
- **Integration Tests**: (Planned) Generator and exporter integration
- **End-to-End Tests**: (Planned) Full pipeline workflows
- **Coverage Target**: 100% on core business logic

## Implementation Roadmap

### Phase 1: Foundation ✅ COMPLETE
- [x] Project structure and configuration
- [x] Pydantic schema models with validation
- [x] Abstract base classes
- [x] CLI framework
- [x] Test infrastructure
- [x] Development tooling

### Phase 2: Core Data Generation ✅ COMPLETE
- [x] `NumericGenerator` with statistical distributions (uniform, normal, exponential)
- [x] `StringGenerator` with Faker integration (names, emails, addresses, phones, IPs, UUIDs)
- [x] `BooleanGenerator` with configurable probability
- [x] `DateTimeGenerator` with date ranges, formats, business days
- [x] `GeneratorFactory` for polymorphic creation
- [x] `SchemaProcessor` pipeline with validation and optimization
- [x] Comprehensive test suite (100+ optimized tests)

### Phase 3: Export System ✅ COMPLETE
- [x] `CSVExporter` with configurable delimiters and proper null handling
- [x] `JSONExporter` with type-safe serialization and metadata
- [x] `SQLExporter` with multi-dialect support (PostgreSQL, MySQL, SQLite, MSSQL)
- [x] `ExporterFactory` for polymorphic creation with format validation
- [x] Multiple dataset support with combined or separate file export
- [x] Output validation and formatting for all export types

### Phase 4: CLI Integration ✅ COMPLETE
- [x] Complete `DataPipeline` orchestration
- [x] Comprehensive error handling and user feedback
- [x] Progress reporting for large datasets with progress bars
- [x] Schema validation mode and format listing
- [x] Seed override and locale configuration
- [x] Verbose logging and file size reporting

## Technical Decisions

### Dependencies
- **Core**: `pydantic` (validation), `click` (CLI), `faker` (data generation), `pyyaml` (config)
- **Dev**: `ruff` (linting/formatting), `pre-commit` (hooks), `pytest` (testing)
- **Package Manager**: UV for modern Python dependency management

### Design Patterns Applied
- **Template Method**: `BasePipeline.run_pipeline()` defines workflow skeleton
- **Factory Pattern**: Generator selection based on field type
- **Abstract Base Classes**: Enforced interfaces with clear contracts
- **Composition**: Flexible generator and exporter combinations
- **Dependency Injection**: Logger and configuration injection

## Phase 2 Achievements

### Core Data Generators Implemented
1. **NumericGenerator**: Integers, floats, decimals with min/max ranges, precision control, and statistical distributions
2. **StringGenerator**: Complete Faker integration for realistic names, emails, addresses, phones, IPs, UUIDs
3. **BooleanGenerator**: Configurable true/false probability with distribution statistics
4. **DateTimeGenerator**: Date ranges, custom formats, business day filtering, batch optimization

### Advanced Features
- **Statistical Distributions**: Uniform, normal, exponential with customizable parameters
- **Batch Processing**: Optimized generation for large datasets
- **Validation**: Comprehensive value validation for all generator types
- **Reproducibility**: Seed-based generation for consistent test data
- **Factory Pattern**: Polymorphic generator creation with `GeneratorFactory`

### Schema Processing Pipeline
- **SchemaProcessor**: Complete orchestration of multiple generators
- **Validation**: Schema validation with detailed error reporting
- **Optimization**: Batch generation and nullable field handling
- **Statistics**: Generation statistics and performance metrics

### Test Infrastructure
- **100+ Tests**: Comprehensive coverage of all generators and edge cases
- **Optimized Performance**: Reduced iteration counts for fast test execution
- **Parametrized Testing**: Multiple scenario validation
- **Error Testing**: Invalid configuration and edge case handling

## Project Complete - Production Ready
Schema-Faker is now a complete, production-ready synthetic data generator with:

1. **Full Export System**: CSV, JSON, and SQL exporters with multi-dialect support
2. **Multi-Dataset Support**: Generate multiple related tables in single execution
3. **Complete CLI Pipeline**: Full orchestration with validation, progress reporting, and error handling
4. **Robust Testing**: All features tested with 100+ comprehensive tests
5. **Reproducible Generation**: Seed-based generation for consistent test data across all generators

## Development Notes
- **Windows Compatibility**: Using `--link-mode=copy` for UV on Windows
- **Test Coverage**: Focus on business logic, exclude CLI entry points initially
- **Code Quality**: Pre-commit hooks ensure consistent formatting and style
- **Architecture**: Clean separation allows independent development of components
