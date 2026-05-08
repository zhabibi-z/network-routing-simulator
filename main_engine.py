from initializer import Initializer


class MainEngine:
    def __init__(self, config_file):
        self.config_file = config_file
        self.routers = {}

    def run_convergence(self):
        """
        Run the distance-vector convergence loop. Each router broadcasts its
        routing vector; neighbors apply Bellman-Ford and update their tables.
        Repeats until no table changes occur (network has converged).
        Returns the number of iterations required.
        """
        max_iterations = len(self.routers) * len(self.routers)
        iteration = 0

        while iteration < max_iterations:
            any_updated = False

            packets = {}
            for name, router in self.routers.items():
                packets[name] = router.builder()

            for name, router in self.routers.items():
                for sender_name, packet in packets.items():
                    if sender_name != name and sender_name in router.costs:
                        updated = router.listener(packet)
                        if updated:
                            any_updated = True 

            iteration += 1
            if not any_updated:
                break

        return iteration

    def load(self, config_file=None):
        """Load a new config file."""
        if config_file:
            self.config_file = config_file
        init = Initializer(self.config_file)
        self.routers = init.load()
        return self.routers

    def run(self, config_file=None, verbose=True):
        """Load, converge, display tables, then demonstrate a dynamic cost update."""
        self.load(config_file)
        if verbose:
            print(f"\n[+] Loaded {len(self.routers)} routers from: {self.config_file}")

        iters = self.run_convergence()
        if verbose:
            print(f"[+] Converged in {iters} iteration(s)\n")
            print("[+] Initial Routing Tables:")
            for router in self.routers.values():
                router.display_table()

        router_list = list(self.routers.values())
        if len(router_list) > 0:
            target_router = router_list[0]
            if len(target_router.neighbors) > 0:
                result = target_router.change_cost(1, 999)
                if result and verbose:
                    neighbor_name, old_cost = result
                    print(f"\n[+] Cost change applied: {target_router.name} → "
                          f"{neighbor_name}: {old_cost}ms → 999ms")

                iters2 = self.run_convergence()
                if verbose:
                    print(f"[+] Re-converged in {iters2} iteration(s)\n")
                    print("[+] Updated Routing Tables:")
                    for router in self.routers.values():
                        router.display_table()

        return self.routers

    def apply_change_cost(self, router_name, neighbor_index, new_cost):
        """Update a link cost and re-run convergence. Returns the updated router map and a status message."""
        router = self.routers.get(router_name)
        if not router:
            return None, f"Router {router_name} not found."

        result = router.change_cost(neighbor_index, new_cost)
        if result is None:
            return None, f"Invalid neighbor index {neighbor_index} for {router_name}."

        neighbor_name, old_cost = result
        self.run_convergence()
        return self.routers, f"Changed cost {router_name}→{neighbor_name}: {old_cost}ms → {new_cost}ms. Re-converged."


if __name__ == "__main__":
    import sys
    config = sys.argv[1] if len(sys.argv) > 1 else "configs/config1.txt"
    engine = MainEngine(config)
    engine.run()
