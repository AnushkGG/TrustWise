import argparse

from scheduler.continuous import run_continuous_updates


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run periodic TrustWise updates")
    parser.add_argument(
        "--query",
        action="append",
        default=[],
        help="Query/topic to refresh. Use multiple --query flags for multiple topics.",
    )
    parser.add_argument("--interval", type=int, default=60, help="Update interval in minutes")
    parser.add_argument("--cycles", type=int, default=1, help="Number of cycles (0 = infinite)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    queries = args.query or [
        "Latest AI developments in healthcare",
        "Graph neural networks research updates",
    ]

    run_continuous_updates(queries, interval_minutes=args.interval, max_cycles=args.cycles)


if __name__ == "__main__":
    main()
