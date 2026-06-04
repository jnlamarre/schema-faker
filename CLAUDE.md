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

## Current Status ✅ PHASE 2 COMPLETE

### Completed Features
- **Modern Project Foundation**: Clean architecture with separation of concerns
- **Pydantic Schema Models**: Type-safe configuration with comprehensive validation
- **Abstract Base Classes**: Extensible framework for generators and exporters
- **CLI Framework**: Click-based interface with proper argument parsing
- **Core Data Generators**: Full implementation with advanced features
- **Schema Processing Pipeline**: Complete orchestration and validation
- **Test Infrastructure**: 100+ optimized tests with comprehensive coverage
- **Development Tooling**: UV, ruff, pre-commit, pytest integration
- **Example Configuration**: Complete YAML schema demonstrating capabilities

### Architecture Highlights
- **Clean Architecture**: Following energy-analytics patterns with utils/, generators/, exporters/
- **Pydantic Validation**: Comprehensive field validation with custom validators
- **Abstract Base Classes**: `BaseGenerator`, `BaseProcessor`, `BaseExporter`, `BasePipeline`
- **Factory Pattern**: `GeneratorFactory` for polymorphic generator creation
- **Advanced Data Generation**: Statistical distributions, Faker integration, optimized batch processing
- **Schema Processing**: Complete pipeline with validation, optimization, and error handling
- **Type Safety**: Modern Python 3.11+ type hints throughout
- **Composition over Inheritance**: Flexible, maintainable design patterns

## Key Commands
```bash
# Installation and setup
uv sync --link-mode=copy          # Install all dependencies
uv sync --group dev --group test  # Install dev and test dependencies

# CLI usage (Phase 1 - foundation testing)
uv run schema-faker --help        # Show CLI options
uv run schema-faker -s examples/users_schema.yaml -f json

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

### Phase 3: Export System (Next)
- [ ] `CSVExporter` and `JSONExporter` implementations
- [ ] `SQLExporter` for database inserts
- [ ] Multiple dataset support
- [ ] Output validation and formatting

### Phase 4: CLI Integration
- [ ] Complete pipeline orchestration
- [ ] Error handling and user feedback
- [ ] Progress reporting for large datasets
- [ ] Documentation and examples

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

## Next Steps for Phase 3
1. Implement export system (`CSVExporter`, `JSONExporter`, `SQLExporter`)
2. Add multi-dataset support for generating related tables
3. Integrate complete CLI pipeline with export functionality
4. Add progress reporting and error handling for large datasets

## Development Notes
- **Windows Compatibility**: Using `--link-mode=copy` for UV on Windows
- **Test Coverage**: Focus on business logic, exclude CLI entry points initially
- **Code Quality**: Pre-commit hooks ensure consistent formatting and style
- **Architecture**: Clean separation allows independent development of components
