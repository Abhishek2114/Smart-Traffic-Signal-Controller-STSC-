import json
import re
import os

class CacheSimulator:
    def __init__(self, config):
        self.cache_size = config['cache_size']
        self.block_size = config['block_size']
        self.associativity = config['associativity']
        self.replacement_policy = config['replacement_policy']
        self.trace_file = config['trace_file']
        self.output_file = config['output_file']

        self.num_sets = self.cache_size // (self.block_size * self.associativity)

        # Initialize cache: list of sets, each set is list of (tag, lru_counter)
        self.cache = [[(-1, 0) for _ in range(self.associativity)] for _ in range(self.num_sets)]

        # Statistics
        self.hits = 0
        self.misses = 0
        self.accesses = 0
        self.global_lru_counter = 0

    def get_set_index(self, address):
        # Address is word address, but for simplicity, assume byte address
        # Block offset: log2(block_size)
        block_offset_bits = self.block_size.bit_length() - 1
        set_index_bits = self.num_sets.bit_length() - 1
        set_index = (address >> block_offset_bits) % self.num_sets
        tag = address >> (block_offset_bits + set_index_bits)
        return set_index, tag

    def access_cache(self, address):
        self.accesses += 1
        set_index, tag = self.get_set_index(address)
        set_cache = self.cache[set_index]

        # Check for hit
        for i, (cached_tag, _) in enumerate(set_cache):
            if cached_tag == tag:
                self.hits += 1
                # Update LRU
                self.global_lru_counter += 1
                set_cache[i] = (tag, self.global_lru_counter)
                return True  # Hit

        # Miss
        self.misses += 1
        # Find replacement
        if self.replacement_policy == 'LRU':
            min_lru = min(lru for _, lru in set_cache)
            for i, (_, lru) in enumerate(set_cache):
                if lru == min_lru:
                    self.global_lru_counter += 1
                    set_cache[i] = (tag, self.global_lru_counter)
                    break
        else:
            # Default to random or FIFO, but for simplicity, replace first
            set_cache[0] = (tag, self.global_lru_counter)
        return False  # Miss

    def parse_trace(self):
        with open(self.trace_file, 'r') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('Cycle') or line.startswith('------') or line.startswith('Note'):
                continue
            parts = line.split('|')
            if len(parts) < 3:
                continue
            instruction = parts[2].strip()
            # Extract memory accesses
            if 'lw' in instruction or 'sw' in instruction:
                # Parse address, e.g., lw x5, 0(x0) -> address 0
                match = re.search(r'(lw|sw)\s+\w+,\s*(\d+)\(\w+\)', instruction)
                if match:
                    offset = int(match.group(2))
                    # Assume base is x0, so address = offset
                    address = offset
                    self.access_cache(address)

    def run_simulation(self):
        self.parse_trace()
        results = {
            'total_accesses': self.accesses,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / self.accesses if self.accesses > 0 else 0,
            'miss_rate': self.misses / self.accesses if self.accesses > 0 else 0,
            'amat': 1 + (self.misses / self.accesses) * 10 if self.accesses > 0 else 0  # Assume 10 cycles for miss
        }
        with open(self.output_file, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Simulation complete. Results saved to {self.output_file}")
        print(json.dumps(results, indent=4))

if __name__ == '__main__':
    config_path = os.path.join(os.path.dirname(__file__), '../config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    sim = CacheSimulator(config)
    sim.run_simulation()
