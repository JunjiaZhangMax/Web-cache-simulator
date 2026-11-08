"""First-in, first-out (FIFO) cache replacement policy."""

def select_victim(entries):
    return min(entries, key=lambda url: entries[url]["insertion_order"])
