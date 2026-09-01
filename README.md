# The Chroma Escape: Intelligent Search Path Algorithms 🎮🧩

An interactive 2D puzzle & pathfinding game powered by **Artificial Intelligence & Informed/Uninformed Search Algorithms** written in Python using **Pygame**.

Developed for the **Smart Search Algorithms** course at the **Faculty of Information Engineering, Damascus University**.

---

## 🌟 Implemented Search Algorithms

The project features a suite of **8 AI Search Algorithms** implemented to solve complex color-matching block puzzle levels:

### 1. Uninformed Search Algorithms
- **BFS (Breadth-First Search)**: Guarantees shortest path solution in unweighted state spaces using FIFO queue.
- **DFS (Depth-First Search)**: Explores deepest search nodes first using LIFO stack.
- **DFS Recursive**: Recursive implementation of depth-first traversal.
- **IDDFS (Iterative Deepening DFS)**: Combines depth-first search space efficiency with breadth-first completeness.
- **UCS (Uniform Cost Search)**: Finds optimal path cost using Priority Queue.

### 2. Informed (Heuristic) Search Algorithms
- **A\* Search**: Combines exact path cost $g(n)$ and admissible heuristic $h(n)$ for optimal pathfinding.
- **Greedy Best-First Search**: Uses heuristic $h(n)$ evaluation to prioritize promising goal-oriented nodes.
- **Hill Climbing Search**: Local search algorithm continuously moving towards local heuristic improvements.

---

## 🛠️ Tech Stack & Architecture

- **Language**: Python 3.10+
- **Game Engine / UI**: Pygame
- **Design Pattern**: Model-View-Controller (MVC):
  - `model.py`: Game board state, block movement physics, exit matching rules.
  - `view.py`: Pygame rendering engine, animations, and sound effects manager (`sound_manager.py`).
  - `controller.py`: User input handling, solver execution, step-by-step auto-solution replay.
  - `search_algorithms/`: Decoupled AI search algorithms library.
  - `utils/comparison.py`: Benchmark tool comparing execution time, expanded nodes, and path costs across algorithms.

---

## 📂 Project Structure

```
The-Chroma-Escape/
├── search_algorithms/
│   ├── base.py             # Base search solver & heuristic evaluation
│   ├── astar.py            # A* Search algorithm
│   ├── bfs.py              # Breadth-First Search
│   ├── dfs.py              # Iterative Depth-First Search
│   ├── dfs_recursive.py    # Recursive DFS
│   ├── iddfs.py            # Iterative Deepening DFS
│   ├── ucs.py              # Uniform Cost Search
│   ├── greedy.py           # Greedy Best-First Search
│   └── hillclimbing.py     # Hill Climbing Search
├── levels/                 # Level JSON configurations (level_01 to level_04)
├── utils/
│   └── comparison.py       # Benchmark comparison utility
├── controller.py           # Game controller & solver connector
├── model.py                # Game logic & state space
├── view.py                 # Pygame graphics renderer
├── main.py                 # Application entry point
├── .gitignore              # Git exclusion rules
└── README.md               # Official Documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Pygame**

```bash
# Clone the repository
git clone https://github.com/MohammedHashemBdier/The-Chroma-Escape.git
cd The-Chroma-Escape

# Install Pygame
pip install pygame
```

### Running the Game

```bash
python main.py
```

### Running Algorithm Benchmarks

To compare performance across all search algorithms:

```bash
python -m utils.comparison
```

---

## 📄 License & Course Information

- **Course**: Smart Search Algorithms (السنة الرابعة - هندسة المعلوماتية)
- **University**: Damascus University (جامعة دمشق)
- **Author**: Mohammed Hashem Bdier
