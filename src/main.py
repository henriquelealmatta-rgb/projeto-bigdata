"""Main entry point for the Movies Big Data Pipeline."""

import argparse
import sys

from src.infrastructure.config import get_settings
from src.presentation.cli import PipelineCLI


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Movies Big Data Pipeline - Process and analyze movie datasets"
    )

    parser.add_argument(
        "--stage",
        type=str,
        choices=["ingestion", "transformation", "loading", "all"],
        default="all",
        help="Pipeline stage to execute (default: all)",
    )

    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default=None,
        help="Logging level (overrides environment variable)",
    )

    return parser.parse_args()


def main() -> int:
    """Main function.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    args = parse_arguments()

    # Load settings
    settings = get_settings()

    # Override log level if specified
    if args.log_level:
        settings.log_level = args.log_level

    # Initialize CLI
    cli = PipelineCLI(settings)

    # Execute pipeline
    if args.stage == "all":
        success = cli.run_full_pipeline()
    else:
        success = cli.run_stage(args.stage)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

