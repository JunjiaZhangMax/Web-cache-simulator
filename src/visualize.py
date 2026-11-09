"""Generate a standalone, offline cache simulation player."""

import argparse
import json
import math
from pathlib import Path

from cache import SharedCache
from simulator import request_processor, requests_loader, resources_loader


def build_trace(resources, requests, capacity_bytes=102400, hit_latency_ms=5.0):
    """Replay simulator results with snapshots at each visible cache operation."""
    if capacity_bytes < 0 or not math.isfinite(hit_latency_ms) or hit_latency_ms < 0:
        raise ValueError("Capacity and hit latency must be finite and nonnegative")
    for url, resource in resources.items():
        if resource["size_bytes"] < 0 or not math.isfinite(resource["origin_latency_ms"]) or resource["origin_latency_ms"] < 0:
            raise ValueError(f"Invalid resource size or latency: {url}")
    for request in requests:
        if request["url"] not in resources:
            raise ValueError(f"Unknown resource URL: {request['url']}")

    traces = {}
    for policy in ("FIFO", "LRU", "LFU"):
        results = request_processor(resources, requests, capacity_bytes, policy)
        cache = SharedCache(capacity_bytes)
        frames = []
        totals = dict(requests=0, hits=0, bytes=0, hit_bytes=0, latency_ms=0, origin_bytes=0)

        def snapshot(index, phase, message, focus=None):
            frames.append(dict(request_index=index, phase=phase, message=message,
                               focus=focus, used_bytes=cache.used_bytes,
                               entries=[dict(url=url, **entry) for url, entry in cache.entries.items()],
                               totals=totals.copy()))

        snapshot(-1, "start", "初始缓存为空；所有客户端共享同一份缓存。")
        for index, result in enumerate(results):
            url = result["url"]
            resource = resources[url]
            size = resource["size_bytes"]
            result["size_bytes"] = size
            result["latency_ms"] = hit_latency_ms if result["cache_hit"] else result["latency_ms"]
            snapshot(index, "request", "客户端发出请求，按 URL 查询共享缓存。", url)
            entry = cache.get(url)
            if result["cache_hit"]:
                assert entry is not None
                snapshot(index, "hit", "缓存命中：更新最近访问顺序与访问次数，无需访问源站。", url)
            else:
                assert entry is None
                snapshot(index, "miss", "缓存未命中：从源站获取资源，产生源站流量与延迟。", url)
                if size > capacity_bytes:
                    snapshot(index, "bypass", "资源大于缓存总容量，直接返回，不淘汰现有资源。", url)
                else:
                    for victim in result["removed_urls"]:
                        cache.remove(victim)
                        snapshot(index, "evict", f"按 {policy} 规则淘汰资源，释放空间；空间不足时继续淘汰。", victim)
                    inserted = cache.insert(url, resource)
                    assert inserted
                    snapshot(index, "insert", "空间足够，将资源写入缓存；访问次数初始化为 1。", url)
            totals["requests"] += 1
            totals["hits"] += int(result["cache_hit"])
            totals["bytes"] += size
            totals["hit_bytes"] += size if result["cache_hit"] else 0
            totals["latency_ms"] += result["latency_ms"]
            totals["origin_bytes"] += 0 if result["cache_hit"] else size
            snapshot(index, "return", "向客户端返回资源，并累计本次请求的指标。", url)
            result["frame_index"] = len(frames) - 1
        traces[policy] = dict(frames=frames, results=results)
    return dict(capacity_bytes=capacity_bytes, hit_latency_ms=hit_latency_ms, traces=traces)


def main(argv=None):
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resources", type=Path, default=root / "data/resources.csv")
    parser.add_argument("--requests", type=Path, default=root / "data/requests_reference.csv")
    parser.add_argument("--capacity-bytes", type=int, default=102400)
    parser.add_argument("--hit-latency-ms", type=float, default=5.0)
    parser.add_argument("--output", type=Path, default=root / "cache-flow.html")
    args = parser.parse_args(argv)
    try:
        data = build_trace(resources_loader(args.resources), requests_loader(args.requests),
                           args.capacity_bytes, args.hit_latency_ms)
        data["source"] = dict(resources=args.resources.name, requests=args.requests.name)
        payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
        template = Path(__file__).with_name("cache_flow.html").read_text(encoding="utf-8")
        args.output.write_text(template.replace("__TRACE_DATA__", payload), encoding="utf-8")
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(f"Visualization: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
