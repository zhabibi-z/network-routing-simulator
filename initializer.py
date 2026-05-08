import re
from router import Router


class Initializer:
    def __init__(self, config_file):
        self.config_file = config_file
        self.routers = {}

    def load(self):
        """
        Parse the configuration file and build the router network.
        Uses two passes: first to register all router names, then to wire
        up neighbors and costs so every router's init_table has the full
        list of destinations available.
        """
        self.routers = {}

        with open(self.config_file, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]

        num_routers = int(lines[0])
        router_lines = lines[1:num_routers + 1]

        for line in router_lines:
            label = line.split(":")[0].strip()
            self.routers[label] = Router(label)

        for line in router_lines:
            parts = line.split(":", 1)
            label = parts[0].strip()
            router = self.routers[label]

            pairs = re.findall(r'\((\w+),\s*(\d+)\)', parts[1])
            for neighbor_name, cost_str in pairs:
                cost = int(cost_str)
                router.neighbors.append(neighbor_name)
                router.costs[neighbor_name] = cost

        all_names = list(self.routers.keys())
        for router in self.routers.values():
            router.init_table(all_names)

        return self.routers

    def get_routers(self):
        return self.routers
