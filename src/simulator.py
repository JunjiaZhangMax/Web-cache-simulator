"""Trace-driven simulation using requests from a CSV file."""

# Read the trace and process requests in order.

import csv
from pathlib import Path
from cache import SharedCache
from policies.fifo import select_victim as fifo_policy
from policies.lru import select_victim as lru_policy
from policies.lfu import select_victim as lfu_policy

policy = "FIFO"  # Default policy, can be changed to "FIFO" or "LFU" as needed

def resources_loader(file_path):
    # Load resources from a CSV file.
    resources = {}

    with open(file_path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
          url = f"{row['scheme']}://{row['host']}{row['path']}"  # Construct the URL from the scheme, host, and path

          if url in resources:
              raise ValueError(f"Duplicate resource URL found: {url}")
          
          resources[url] = {
               "size_bytes": int(row["size_bytes"]),
               "origin_latency_ms": float(row["origin_latency_ms"]),
            }

    return resources


def requests_loader(file_path):
    # Load requests from a CSV file.
    requests = []

    with open(file_path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:

            url = f"{row['scheme']}://{row['host']}{row['path']}"

            request = {
                "timestamp": row["timestamp"],
                "client_id": row["client_id"],
                "url": url,
            }
            requests.append(request)
     
    return requests


def request_processor(resources, requests, cache_capacity_bytes=102400, selected_policy=policy):
    # Simulate processing requests with a shared cache.
    policies = {"FIFO": fifo_policy, "LRU": lru_policy, "LFU": lfu_policy}
    select_victim = policies[selected_policy]
    cache = SharedCache(capacity_bytes=cache_capacity_bytes)
    results = []

    for request in requests:
        removed_urls = []
        url = request["url"]
        resource = resources.get(url)

        entry = cache.get(url)
        if entry is not None:
            # Cache hit
            result = {
                "timestamp": request["timestamp"],
                "client_id": request["client_id"],
                "url": url,
                "cache_hit": True,
                "latency_ms": 5,
            }
        else:
            # Cache miss
            latency_ms = resource["origin_latency_ms"]
            if resource["size_bytes"] <= cache.capacity_bytes:
                if not cache.insert(url, resource):
                    while cache.used_bytes + resource["size_bytes"] > cache.capacity_bytes:
                        victim_url = select_victim(cache.entries)
                        cache.remove(victim_url)
                        removed_urls.append(victim_url)
                    cache.insert(url, resource)

            result = {
                "timestamp": request["timestamp"],
                "client_id": request["client_id"],
                "url": url,
                "cache_hit": False,
                "latency_ms": latency_ms,
            }

        result["removed_urls"] = removed_urls
        results.append(result)

    return results

if __name__ == "__main__":
     project_root = Path(__file__).resolve().parent.parent

     resources = resources_loader(project_root / "data" / "resources.csv")
     requests = requests_loader(project_root / "data" / "requests_reference.csv")

     first_request = requests[0]
     resource = resources[first_request["url"]]