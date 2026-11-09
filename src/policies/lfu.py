"""Least frequently used (LFU) cache replacement policy."""

def select_victim(entries):
    return min(entries, key=lambda url: (entries[url]["access_count"], entries[url]["last_access"]))
