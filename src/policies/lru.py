"""Least recently used (LRU) cache replacement policy."""

def select_victim(entries):
    return min(entries, key=lambda url: entries[url]["last_access"])
