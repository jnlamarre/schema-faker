#!/usr/bin/env python3
"""
Schema-Faker CLI
Configurable synthetic data generator for dev/test environments.
"""

import json
import logging
import sys
from pathlib import Path

import click
import yaml

from .exporters import ExporterFactory
from .utils.pipeline import DataPipeline
from .utils.schema_models import SchemaConfiguration


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    return logging.getLogger("schema-faker")


def load_schema(schema_path: Path) -> SchemaConfiguration:
    """Load and parse schema configuration file."""
    try:
        with open(schema_path, encoding="utf-8") as file:
            if schema_path.suffix.lower() in [".yaml", ".yml"]:
                config_data = yaml.safe_load(file)
            elif schema_path.suffix.lower() == ".json":
                config_data = json.load(file)
            else:
                raise ValueError(
                    f"Unsupported schema file format: {schema_path.suffix}"
                )

        return SchemaConfiguration(**config_data)

    except Exception as e:
        raise click.ClickException(f"Failed to load schema from {schema_path}: {e}")


@click.command()
@click.option(
    "--schema",
    "-s",
    type=click.Path(exists=True, path_type=Path),
    help="Path to schema configuration file (YAML or JSON)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output directory for generated files",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv", "sql"], case_sensitive=False),
    help="Override output format for all datasets",
)
@click.option(
    "--records",
    "-r",
    type=int,
    help="Override number of records to generate for all datasets",
)
@click.option("--seed", type=int, help="Random seed for reproducible data generation")
@click.option(
    "--locale",
    type=str,
    default="en_US",
    help="Locale for data generation (default: en_US)",
)
@click.option(
    "--validate-only",
    is_flag=True,
    help="Only validate schema configuration without generating data",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--list-formats", is_flag=True, help="List supported export formats and exit"
)
@click.version_option(version="1.0.0")
def main(
    schema: Path,
    output: Path,
    format: str,
    records: int,
    seed: int,
    locale: str,
    validate_only: bool,
    verbose: bool,
    list_formats: bool,
):
    """
    Generate synthetic datasets based on schema configuration.

    Schema-Faker supports multiple output formats and can generate
    realistic synthetic data for development and testing environments.
    Examples:
        schema-faker -s users.yaml -f json -o ./output/
        schema-faker -s config.json --seed 42 --records 5000
        schema-faker -s schema.yaml --validate-only
        schema-faker --list-formats
    """
    # Setup logging
    logger = setup_logging(verbose)

    # Handle list formats request
    if list_formats:
        click.echo("Supported export formats:")
        for fmt in ExporterFactory.get_supported_formats():
            format_info = ExporterFactory.get_exporter_info(fmt)
            click.echo(f"  {fmt}: {format_info.get('class_name', 'N/A')}")

            # Show format options
            options = ExporterFactory.get_format_options(fmt)
            if options:
                click.echo(f"    Options: {', '.join(options.keys())}")
        return 0

    # Validate required arguments
    if not schema:
        raise click.ClickException("Missing required option '--schema' / '-s'.")

    # Display header
    click.echo("Schema-Faker v1.0.0 - Phase 3 Complete!")
    click.echo(f"Schema file: {schema}")

    try:
        # Load and parse schema
        click.echo("Loading schema configuration...")
        schema_config = load_schema(schema)

        # Determine output directory
        output_dir = output or schema_config.global_config.get("output_dir", "./output")
        click.echo(f"Output directory: {output_dir}")

        # Apply global seed if provided
        if seed is not None:
            if schema_config.global_config is None:
                schema_config.global_config = {}
            schema_config.global_config["seed"] = seed
            click.echo(f"Random seed: {seed}")

        # Create pipeline
        pipeline = DataPipeline(
            schema=schema_config,
            output_dir=str(output_dir),
            locale=locale,
            logger=logger,
        )

        # Validate schema if requested
        if validate_only:
            click.echo("Validating schema configuration...")
            validation_result = pipeline.validate_pipeline()

            if validation_result["valid"]:
                click.echo("Schema validation passed!")

                # Show pipeline statistics
                stats = pipeline.get_pipeline_stats()
                click.echo(f"Found {stats['total_datasets']} datasets:")
                for table_name, dataset_stats in stats["datasets"].items():
                    click.echo(
                        f"  - {table_name}: {dataset_stats['record_count']} records ({dataset_stats['output_format']})"
                    )
            else:
                click.echo("Schema validation failed!")
                for error in validation_result["errors"]:
                    click.echo(f"  Error: {error}", err=True)
                return 1

            return 0

        # Override format for all datasets if specified
        if format:
            for dataset in schema_config.datasets:
                if isinstance(dataset, dict):
                    dataset["output_format"] = format.lower()
                else:
                    dataset.output_format = format.lower()
            click.echo(f"Output format override: {format.lower()}")

        # Show generation plan
        click.echo("Generation plan:")
        total_records = 0
        for dataset in schema_config.datasets:
            if isinstance(dataset, dict):
                table_name = dataset.get("table_name", "unknown")
                record_count = records or dataset.get("record_count", 1000)
                output_format = dataset.get("output_format", "json")
            else:
                table_name = dataset.table_name
                record_count = records or dataset.record_count
                output_format = getattr(dataset, "output_format", "json")

            total_records += record_count
            click.echo(
                f"  - {table_name}: {record_count:,} records -> {output_format.upper()}"
            )

        click.echo(
            f"  Total: {total_records:,} records across {len(schema_config.datasets)} datasets"
        )

        # Generate data
        click.echo("\nStarting data generation...")
        with click.progressbar(length=100, label="Generating data") as bar:
            # Run the complete pipeline
            exported_files = pipeline.run_pipeline(
                record_count=records, output_path=str(output_dir)
            )
            bar.update(100)

        # Show results
        click.echo("\nData generation completed successfully!")
        click.echo("Generated files:")
        for table_name, file_path in exported_files.items():
            file_size = Path(file_path).stat().st_size
            size_str = _format_file_size(file_size)
            click.echo(f"  - {table_name}: {file_path} ({size_str})")

        click.echo(f"\nSuccessfully generated {len(exported_files)} datasets!")

        return 0

    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        if verbose:
            import traceback

            traceback.print_exc()
        click.echo(f"Error: {e}", err=True)
        return 1


def _format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


if __name__ == "__main__":
    sys.exit(main())
