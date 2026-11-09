"""Check that displayed snapshots agree with the reference simulation."""

import csv
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from simulator import requests_loader, resources_loader
from visualize import build_trace


class VisualizationTests(unittest.TestCase):
    def test_reference_snapshots(self):
        data = build_trace(resources_loader(ROOT / "data/resources.csv"),
                           requests_loader(ROOT / "data/requests_reference.csv"))
        for policy, trace in data["traces"].items():
            with (ROOT / f"tests/reference/expected_{policy.lower()}.csv").open(encoding="utf-8-sig", newline="") as file:
                expected = list(csv.DictReader(file))
            self.assertEqual(len(trace["results"]), len(expected))
            for result, row in zip(trace["results"], expected):
                frame = trace["frames"][result["frame_index"]]
                self.assertEqual(result["cache_hit"], row["result"] == "HIT")
                self.assertEqual(result["latency_ms"], float(row["response_ms"]))
                self.assertEqual(frame["used_bytes"], float(row["cache_used_KiB"]) * 1024)
                self.assertEqual(frame["totals"]["hits"], int(row["cumulative_hits"]))
                self.assertEqual(frame["totals"]["origin_bytes"], int(row["cumulative_origin_bytes"]))
            for frame in trace["frames"]:
                self.assertEqual(frame["used_bytes"], sum(e["size_bytes"] for e in frame["entries"]))
                self.assertLessEqual(frame["used_bytes"], data["capacity_bytes"])

    def test_multiple_evictions_and_bypass(self):
        resources = {url: dict(size_bytes=size, origin_latency_ms=100)
                     for url, size in (("A", 4), ("B", 4), ("C", 8), ("D", 20))}
        requests = [dict(url=url, timestamp=str(i), client_id=f"client-{i % 2}")
                    for i, url in enumerate(("A", "A", "B", "C", "D"))]
        for policy, trace in build_trace(resources, requests, 10, 2)["traces"].items():
            results, frames = trace["results"], trace["frames"]
            self.assertEqual(results[1]["latency_ms"], 2)
            self.assertEqual(results[3]["removed_urls"], ["B", "A"] if policy == "LFU" else ["A", "B"])
            evictions = [f for f in frames if f["request_index"] == 3 and f["phase"] == "evict"]
            self.assertEqual([f["used_bytes"] for f in evictions], [4, 0])
            self.assertEqual(frames[results[3]["frame_index"]]["entries"], frames[-1]["entries"])
            self.assertEqual(frames[-1]["totals"]["hits"], 1)
            self.assertTrue(any(f["phase"] == "bypass" for f in frames))

    def test_empty_trace_and_unknown_resource(self):
        for trace in build_trace({}, [], 0)["traces"].values():
            self.assertEqual(len(trace["frames"]), 1)
            self.assertEqual(trace["frames"][0]["used_bytes"], 0)
        with self.assertRaisesRegex(ValueError, "Unknown resource"):
            build_trace({}, [dict(url="missing")])


if __name__ == "__main__":
    unittest.main()
