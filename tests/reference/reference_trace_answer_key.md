# Shared Web Cache — Reference Trace Answer Key

This is an instructor/reference solution for `requests_reference.csv` using the existing `resources.csv`.

## Simulation assumptions

- Cache capacity: **100 KiB (102,400 bytes)**; initially empty.
- Sequential GET requests; ignore Cache-Control and expiration for this core exercise.
- Hit latency: **5 ms**; miss latency: `origin_latency_ms`.
- All five selected resources fit individually. Cache admission is mandatory on a miss; evict until enough space exists.
- FIFO: oldest insertion; a hit does not change insertion order. LRU: oldest last access. LFU: smallest access count since insertion; ties broken by LRU. Counts reset on eviction/reinsertion.
- All cache contents columns are ordered by insertion age, not eviction priority.
- Origin traffic is the sum of `size_bytes` on misses. No network traffic is counted on hits.

## Resource legend

| ID | URL | Size (KiB) | Origin latency (ms) |
|---|---|---:|---:|
| A | `https://learn.university.edu/courses/ics/index.html` | 32 | 125 |
| B | `https://learn.university.edu/static/main.css` | 42 | 90 |
| C | `https://learn.university.edu/static/logo.svg` | 14 | 80 |
| D | `https://cdn.university.edu/images/avatar-default.png` | 24 | 95 |
| E | `https://pypi.org/static/css/warehouse.css` | 57 | 210 |

## Summary

| Policy | Hits | Misses | Hit ratio | Origin traffic (KiB) | Average response (ms) |
|---|---:|---:|---:|---:|---:|
| FIFO | 3 | 12 | 20.00% | 412 | 95.33 |
| LRU | 3 | 12 | 20.00% | 394 | 92.33 |
| LFU | 4 | 11 | 26.67% | 362 | 84.33 |

## FIFO — step-by-step expected results

| Step | Resource | Hit/Miss | Evicted | Cache (insertion order) | Used KiB | Response ms |
|---:|---|---|---|---|---:|---:|
| 1 | A | MISS | - | A | 32 | 125 |
| 2 | B | MISS | - | A,B | 74 | 90 |
| 3 | C | MISS | - | A,B,C | 88 | 80 |
| 4 | A | HIT | - | A,B,C | 88 | 5 |
| 5 | B | HIT | - | A,B,C | 88 | 5 |
| 6 | D | MISS | A | B,C,D | 80 | 95 |
| 7 | A | MISS | B | C,D,A | 70 | 125 |
| 8 | C | HIT | - | C,D,A | 70 | 5 |
| 9 | E | MISS | C,D | A,E | 89 | 210 |
| 10 | B | MISS | A | E,B | 99 | 90 |
| 11 | D | MISS | E | B,D | 66 | 95 |
| 12 | A | MISS | - | B,D,A | 98 | 125 |
| 13 | E | MISS | B,D | A,E | 89 | 210 |
| 14 | C | MISS | A | E,C | 71 | 80 |
| 15 | B | MISS | E | C,B | 56 | 90 |

## LRU — step-by-step expected results

| Step | Resource | Hit/Miss | Evicted | Cache (insertion order) | Used KiB | Response ms |
|---:|---|---|---|---|---:|---:|
| 1 | A | MISS | - | A | 32 | 125 |
| 2 | B | MISS | - | A,B | 74 | 90 |
| 3 | C | MISS | - | A,B,C | 88 | 80 |
| 4 | A | HIT | - | A,B,C | 88 | 5 |
| 5 | B | HIT | - | A,B,C | 88 | 5 |
| 6 | D | MISS | C | A,B,D | 98 | 95 |
| 7 | A | HIT | - | A,B,D | 98 | 5 |
| 8 | C | MISS | B | A,D,C | 70 | 80 |
| 9 | E | MISS | D,A | C,E | 71 | 210 |
| 10 | B | MISS | C | E,B | 99 | 90 |
| 11 | D | MISS | E | B,D | 66 | 95 |
| 12 | A | MISS | - | B,D,A | 98 | 125 |
| 13 | E | MISS | B,D | A,E | 89 | 210 |
| 14 | C | MISS | A | E,C | 71 | 80 |
| 15 | B | MISS | E | C,B | 56 | 90 |

## LFU — step-by-step expected results

| Step | Resource | Hit/Miss | Evicted | Cache (insertion order) | Used KiB | Response ms |
|---:|---|---|---|---|---:|---:|
| 1 | A | MISS | - | A | 32 | 125 |
| 2 | B | MISS | - | A,B | 74 | 90 |
| 3 | C | MISS | - | A,B,C | 88 | 80 |
| 4 | A | HIT | - | A,B,C | 88 | 5 |
| 5 | B | HIT | - | A,B,C | 88 | 5 |
| 6 | D | MISS | C | A,B,D | 98 | 95 |
| 7 | A | HIT | - | A,B,D | 98 | 5 |
| 8 | C | MISS | D | A,B,C | 88 | 80 |
| 9 | E | MISS | C,B | A,E | 89 | 210 |
| 10 | B | MISS | E | A,B | 74 | 90 |
| 11 | D | MISS | - | A,B,D | 98 | 95 |
| 12 | A | HIT | - | A,B,D | 98 | 5 |
| 13 | E | MISS | B,D | A,E | 89 | 210 |
| 14 | C | MISS | E | A,C | 46 | 80 |
| 15 | B | MISS | - | A,C,B | 88 | 90 |

The companion `expected_fifo.csv`, `expected_lru.csv`, and `expected_lfu.csv` contain machine-checkable per-request outputs including cumulative traffic and hits.
