# Dynamic Routing Simulator

A Python-based simulator for the **Distance Vector (Bellman-Ford) routing protocol**, built as a Computer Networks final project. Includes both a command-line engine and a dark-themed GUI for interactive exploration.

## Overview

The simulator models a network of routers exchanging distance-vector packets. Each router applies the Bellman-Ford algorithm to compute shortest paths to all other routers. Supports loading custom network topologies from config files and dynamically changing link costs to observe re-convergence in real time.

## Project Structure

```
├── gui.py            # Tkinter GUI — interactive routing simulator
├── main_engine.py    # Simulation engine: load, converge, apply cost changes
├── router.py         # Router class: Bellman-Ford, builder/listener protocol
├── initializer.py    # Config file parser and network builder
└── configs/
    ├── config1.txt   # 5-router example topology
    ├── config2.txt   # Alternate topology
    └── config3.txt   # Alternate topology
```

## How It Works

1. **Config file** defines the network: number of routers and each router's neighbors with link costs (ms).
2. **Initializer** parses the config and creates `Router` objects wired with neighbors and costs.
3. **MainEngine** runs the convergence loop — routers broadcast distance vectors, neighbors update via Bellman-Ford — until no table changes occur.
4. **`change_cost()`** lets you update a link cost mid-simulation; the engine re-converges and the GUI reflects the new tables instantly.

## Config File Format

```
<number_of_routers>
<RouterName>: (<Neighbor>, <cost_ms>), ...
```

Example (`configs/config1.txt`):
```
5
R1: (R2, 140), (R4, 180)
R2: (R1, 140), (R3, 300), (R5, 450)
R3: (R2, 300), (R4, 200), (R5, 100)
R4: (R1, 180), (R3, 200)
R5: (R2, 450), (R3, 100)
```

## Running the Simulator

### GUI (recommended)

```bash
python gui.py
```

1. Click **Browse Config** to load a topology file from `configs/`.
2. Click **Run** to converge the network and display all routing tables.
3. Use the **View Router Table** dropdown to inspect a single router.
4. Use **Change Cost Simulator** to update a link cost and watch the network re-converge.
5. Click **Reset** to start over.

### Command Line

```bash
python main_engine.py configs/config1.txt
```

Prints initial routing tables, applies a sample cost change to the first router's first neighbor, then prints the updated tables after re-convergence.

## Requirements

- Python 3.x (standard library only — `tkinter`, `threading`, `re`)
- No external packages required

## Author

Ziauddin Habibi
