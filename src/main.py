"""Program entry point for the shared web cache simulator."""

import argparse
import json
import math
from pathlib import Path

from simulator import request_processor, requests_loader, resources_loader


def main(argv=None):
    project_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path,
                        default=project_root / "data" / "resources.csv")
    parser.add_argument("--requests", type=Path,
                        default=project_root / "data" / "requests_reference.csv")
    parser.add_argument("--policy", type=str.upper, choices=("FIFO", "LRU", "LFU"),
                        default="FIFO")
    parser.add_argument("--capacity-bytes", type=int, default=102400)
    parser.add_argument("--hit-latency-ms", type=float, default=5.0)
    args = parser.parse_args(argv)
    if args.capacity_bytes < 0:
        parser.error("--capacity-bytes must be nonnegative")
    if not math.isfinite(args.hit_latency_ms) or args.hit_latency_ms < 0:
        parser.error("--hit-latency-ms must be finite and nonnegative")

    try:
        resources = resources_loader(args.resources)
        requests = requests_loader(args.requests)
        for request in requests:
            if request["url"] not in resources:
                raise ValueError(f"Unknown resource URL: {request['url']}")
        results = request_processor(resources, requests,
                                    cache_capacity_bytes=args.capacity_bytes,
                                    selected_policy=args.policy)
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))

    def new_totals():
        return dict(requests=0, hits=0, requested_bytes=0, hit_bytes=0,
                    total_latency_ms=0.0, origin_bytes=0)

    totals = new_totals()
    clients = {}
    for result in results:
        size = resources[result["url"]]["size_bytes"]
        hit = result["cache_hit"]
        latency = args.hit_latency_ms if hit else result["latency_ms"]
        client = clients.setdefault(result["client_id"], new_totals())
        for counts in (totals, client):
            counts["requests"] += 1
            counts["hits"] += int(hit)
            counts["requested_bytes"] += size
            counts["hit_bytes"] += size if hit else 0
            counts["total_latency_ms"] += latency
            counts["origin_bytes"] += 0 if hit else size

    for counts in (totals, *clients.values()):
        count = counts["requests"]
        byte_count = counts["requested_bytes"]
        counts["misses"] = count - counts["hits"]
        counts["hit_rate"] = counts["hits"] / count if count else 0.0
        counts["byte_hit_rate"] = counts["hit_bytes"] / byte_count if byte_count else 0.0
        counts["average_latency_ms"] = counts["total_latency_ms"] / count if count else 0.0

    print(json.dumps(dict(policy=args.policy, capacity_bytes=args.capacity_bytes,
                         hit_latency_ms=args.hit_latency_ms,
                         totals=totals, clients=clients), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
