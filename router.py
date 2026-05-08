import threading


class Router:
    def __init__(self, name):
        self.name = name
        self.neighbors = []       # ordered list of directly connected router names
        self.costs = {}           # {neighbor_name: link_cost_ms}
        self.routing_table = {}   # {dest: {"line": next_hop, "cost": total_cost}}
        self.destinations = []    # all router names in the network
        self.lock = threading.Lock()

    def init_table(self, all_routers):
        """Initialize the routing table for all known routers in the network."""
        with self.lock:
            self.destinations = list(all_routers)
            for dest in all_routers:
                if dest == self.name:
                    self.routing_table[dest] = {"line": self.name, "cost": 0}
                elif dest in self.costs:
                    self.routing_table[dest] = {"line": dest, "cost": self.costs[dest]}
                else:
                    self.routing_table[dest] = {"line": "-", "cost": -1}

    def display_table(self):
        """Print the routing table to console."""
        with self.lock:
            snapshot = {dest: dict(info) for dest, info in self.routing_table.items()}
        print(f"\n{'='*50}")
        print(f"  Routing Table for Router: {self.name}")
        print(f"{'='*50}")
        print(f"  {'Destination':<15} {'Next Hop':<15} {'Cost (ms)'}")
        print(f"  {'-'*40}")
        for dest, info in sorted(snapshot.items()):
            cost_str = str(info['cost']) if info['cost'] != -1 else "unreachable"
            print(f"  {dest:<15} {info['line']:<15} {cost_str}")
        print(f"{'='*50}\n")

    def builder(self):
        """Build and return a distance-vector packet containing all known destinations and costs."""
        with self.lock:
            known = [
                (dest, info["cost"])
                for dest, info in self.routing_table.items()
                if info["cost"] != -1 and dest != self.name
            ]
        return {"sender": self.name, "neighbors": known}

    def listener(self, packet):
        """
        Process an incoming distance-vector packet from a neighboring router.
        Applies Bellman-Ford to update the routing table with any shorter paths found.
        Routes that pass through the sender are always refreshed to reflect cost changes.
        """
        sender = packet["sender"]

        if sender not in self.costs:
            return False

        cost_to_sender = self.costs[sender]
        updated = False

        with self.lock:
            for dest, dest_cost in packet["neighbors"]:
                if dest == self.name:
                    continue
                if dest_cost == -1:
                    continue

                new_cost = cost_to_sender + dest_cost
                current = self.routing_table.get(dest, {"line": "-", "cost": -1})

                if (current["cost"] == -1
                        or new_cost < current["cost"]
                        or (current["line"] == sender and new_cost != current["cost"])):
                    self.routing_table[dest] = {"line": sender, "cost": new_cost}
                    updated = True

        return updated

    def change_cost(self, neighbor_index, new_cost):
        """
        Update the link cost to a neighbor identified by its 1-based position
        in the neighbors list. Triggers builder() so the change propagates to
        the rest of the network. Returns (neighbor_name, old_cost), or None if
        the index is out of range.
        """
        if neighbor_index < 1 or neighbor_index > len(self.neighbors):
            return None

        neighbor_name = self.neighbors[neighbor_index - 1]
        old_cost = self.costs[neighbor_name]
        self.costs[neighbor_name] = new_cost

        with self.lock:
            self.routing_table[neighbor_name] = {"line": neighbor_name, "cost": new_cost}

        self.builder()
        return neighbor_name, old_cost

    def get_table_snapshot(self):
        """Return a thread-safe copy of the current routing table."""
        with self.lock:
            return {dest: dict(info) for dest, info in self.routing_table.items()}
