# Architecture — Network Routing Simulator

## Overview

A pure-Python (stdlib only) implementation of the **Distance Vector routing protocol** using the Bellman-Ford algorithm. Simulates convergence across an arbitrary network topology defined in a plain-text config file.

## Component Map

```
configs/config.txt          ← topology definition (routers + link costs)
        │
        ▼  initializer.py
Network topology parsed into adjacency structure
        │
        ▼  router.py
Router class — distance-vector state machine:
  - Maintains routing table: { destination: (cost, next_hop) }
  - Implements Bellman-Ford update rule:
      cost(D) = min over neighbours N of [ cost(N) + link_cost(self, N) ]
  - Sends/receives distance-vector advertisements to neighbours
        │
        ▼  main_engine.py
Simulation loop:
  - Round-by-round execution until convergence
  - Detects steady state (no routing table changes in a round)
  - CLI output: routing tables per router per round
        │
        ▼  gui.py  (optional)
Tkinter GUI:
  - Node graph visualisation with live routing table display
  - Step-through and auto-run modes
  - Highlights path changes per round
```

## Algorithm

**Bellman-Ford (distributed):**

Each router R maintains a distance vector `D_R[v]` = estimated cost to reach every destination v.

At each round, every router:
1. Broadcasts its current distance vector to direct neighbours
2. Updates: `D_R[v] = min_N ( link_cost(R, N) + D_N[v] )` for all v
3. Convergence when no router changes its table

Time complexity: O(V × E) per full convergence, where V = routers, E = links.

## Config File Format

```
# config1.txt
router A
router B
router C
link A B 1
link B C 3
link A C 7
```

One router or link definition per line. Link costs are symmetric.

## Running

```bash
# CLI simulation
python main_engine.py --config configs/config1.txt

# GUI simulation
python gui.py --config configs/config1.txt
```

## Design Decisions

**Zero external dependencies** — the entire simulator runs on Python 3.x stdlib (tkinter, threading, re). Any machine with Python installed can run it without a virtual environment or pip.

**Config-file topology** — separating topology from code means different network scenarios can be tested without touching source files. Three example configs are included.

**Tkinter GUI** — chosen over web frameworks (Flask, Streamlit) to maintain the zero-dependency constraint while still providing interactive visualisation.
