"""Shared cache data structure and basic operations."""

class SharedCache:
    
    # Byte-limited cache shared by all clients and keyed by resource URL.

    def __init__(self, capacity_bytes=102400):
        
        self.capacity_bytes = capacity_bytes
        self.used_bytes = 0
        self.entries = {}  
        self._order = 0

    def __len__(self):
        return len(self.entries)

    def __contains__(self, url):
        # Check membership withou
        # t changing access metadata.
        return url in self.entries

    def get(self, url):
        # Return an entry and record a hit, or return None on a miss.
        entry = self.entries.get(url)  
        if entry is not None:
            self._order += 1
            entry["last_access"] = self._order
            entry["access_count"] += 1
        return entry

    def insert(self, url, resource):
        # Copy a resource into the cache, returning whether it fits or not.
        # The case that the resource is already present is included. If we prevent duplication in the simulator, it could be removed from here.
        new_size = resource["size_bytes"]
        previous = self.entries.get(url)
        previous_size = previous["size_bytes"] if previous is not None else 0
        new_used = self.used_bytes - previous_size + new_size
        if new_used > self.capacity_bytes:
            return False

        entry = dict(resource)
        self._order += 1
        entry["last_access"] = self._order
        entry["access_count"] = (
                    previous["access_count"] + 1 if previous is not None else 1)
        entry["insertion_order"] = (
            previous["insertion_order"] if previous is not None else self._order)
        self.entries[url] = entry
        self.used_bytes = new_used
        return True

    def remove(self, url):
        # Remove and return an entry, or return None if it is absent.
        entry = self.entries.pop(url, None)
        if entry is not None:
            self.used_bytes -= entry["size_bytes"]
        return entry
