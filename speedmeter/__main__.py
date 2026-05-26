"""Main entry point for SpeedMeter."""

import argparse
import logging
import sys

from speedmeter.app import SpeedMeterApp
from speedmeter.config import get_default_config, load_config


def parse_args(argv=None):
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="speedmeter",
        description="Cyberpunk terminal-based internet speed meter — real-time network monitoring.",
        epilog="Run without arguments to launch the interactive TUI.",
    )
    parser.add_argument(
        "-q",
        "--quick",
        action="store_true",
        help="Run a quick speed test once and exit (no TUI).",
    )
    parser.add_argument(
        "-m",
        "--monitor",
        action="store_true",
        help="Launch TUI with continuous network monitoring enabled.",
    )
    parser.add_argument(
        "-w",
        "--widget",
        action="store_true",
        help="Launch the lightweight desktop GUI speed widget.",
    )
    parser.add_argument(
        "-l",
        "--list-servers",
        action="store_true",
        help="List available speedtest.net servers.",
    )
    parser.add_argument(
        "-s",
        "--server",
        type=int,
        metavar="ID",
        help="Specify a speedtest.net server by ID.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        metavar="PATH",
        help="Path to custom config file.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="PATH",
        help="Save test results to a JSON file.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit.",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Main entry point."""
    args = parse_args(argv)
    config = load_config(args.config) if args.config else get_default_config()

    if args.version:
        from speedmeter import __version__

        print(f"SpeedMeter v{__version__}")
        return 0

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    # Launch desktop widget mode
    if args.widget:
        try:
            from speedmeter.widget_gui import launch_widget

            launch_widget()
        except ImportError as e:
            print(f"ERROR: Could not launch widget: {e}", file=sys.stderr)
            return 1
        return 0

    # Quick test mode
    if args.quick:
        from speedmeter.tester import run_quick_test

        result = run_quick_test(server_id=args.server, output=args.output)
        if result:
            print(result.format())
        return 0

    # List servers mode
    if args.list_servers:
        from speedmeter.tester import list_servers

        servers = list_servers()
        for s in servers:
            print(f"  {s['id']:>6}  {s['name']:<30}  {s['location']:<20}  {s['country']:<20}  {s['sponsor']:<30}")
        print(f"\nTotal: {len(servers)} servers")
        return 0

    # Launch the TUI
    try:
        app = SpeedMeterApp(
            config=config,
            server_id=args.server,
            output=args.output,
            start_monitor=args.monitor,
        )
        app.run()
    except Exception as e:
        logging.error("Fatal error: %s", e, exc_info=args.verbose)
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
