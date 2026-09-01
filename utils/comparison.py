# في utils/comparison.py
import time
import psutil
import os
from typing import Dict, Any
from search_algorithms.astar import AStarSolver
from search_algorithms.bfs import BFSSolver
from search_algorithms.dfs import DFSSolver
from search_algorithms.ucs import UCSSolver
from search_algorithms.hillclimbing import HillClimbingSolver
from model import GameState

class AlgorithmComparator:
    def __init__(self):
        self.results = {}
        
    def compare_algorithms(self, initial_state: GameState) -> Dict[str, Dict[str, Any]]:
        algorithms = {
            "BFS": BFSSolver,
            "DFS": DFSSolver,
            "A*": AStarSolver,
            "UCS": UCSSolver,
            "Hill_Climbing": HillClimbingSolver
        }
        
        for algo_name, algo_class in algorithms.items():
            print(f"\n{'='*60}")
            print(f"Testing {algo_name}")
            print(f"{'='*60}")
            
            try:
                process = psutil.Process(os.getpid())
                memory_before = process.memory_info().rss / 1024 / 1024  # MB
                
                start_time = time.time()
                
                solver = algo_class()
                solution = solver.solve(initial_state)
                
                end_time = time.time()
                
                # قياس استخدام الذاكرة بعد التنفيذ
                memory_after = process.memory_info().rss / 1024 / 1024  # MB
                
                self.results[algo_name] = {
                    "time_taken": end_time - start_time,
                    "memory_used": memory_after - memory_before,
                    "nodes_explored": solver.nodes_explored,
                    "solution_found": solution is not None and len(solution) > 0,
                    "solution_length": len(solution) if solution else 0,
                    "is_optimal": algo_name in ["BFS", "UCS"],  # BFS و UCS يعطيان الحل الأمثل
                    "moves_to_solution": self._count_moves_in_solution(solution) if solution else 0
                }
                
                print(f"Time: {self.results[algo_name]['time_taken']:.2f} seconds")
                print(f"Memory: {self.results[algo_name]['memory_used']:.2f} MB")
                print(f"Nodes explored: {self.results[algo_name]['nodes_explored']}")
                print(f"Solution found: {self.results[algo_name]['solution_found']}")
                if solution:
                    print(f"Solution length: {len(solution)} states")
                    print(f"Moves to win: {self.results[algo_name]['moves_to_solution']}")
                
            except Exception as e:
                print(f"Error in {algo_name}: {str(e)}")
                self.results[algo_name] = {
                    "time_taken": 0,
                    "memory_used": 0,
                    "nodes_explored": 0,
                    "solution_found": False,
                    "solution_length": 0,
                    "is_optimal": False,
                    "moves_to_solution": 0,
                    "error": str(e)
                }
        
        return self.results
    
    def _count_moves_in_solution(self, solution_path):
        moves = 0
        for i in range(len(solution_path) - 1):
            if solution_path[i+1].action is not None:
                moves += 1
        return moves
    
    def print_comparison_table(self):
        print("\n" + "="*100)
        print("COMPARISON TABLE - LEVEL 01 (LARGE BOARD)")
        print("="*100)
        print(f"{'Algorithm':<20} {'Time(s)':<10} {'Memory(MB)':<12} {'Nodes':<12} {'Solution':<10} {'Moves':<10} {'Optimal':<10}")
        print("-"*100)
        
        for algo_name, result in self.results.items():
            print(f"{algo_name:<20} "
                  f"{result['time_taken']:<10.2f} "
                  f"{result['memory_used']:<12.2f} "
                  f"{result['nodes_explored']:<12} "
                  f"{'YES' if result['solution_found'] else 'NO':<10} "
                  f"{result['moves_to_solution']:<10} "
                  f"{'YES' if result['is_optimal'] else 'NO':<10}")
        
        print("="*100)
        
        successful = {k:v for k,v in self.results.items() if v['solution_found']}
        if successful:
            best_time = min(successful.items(), key=lambda x: x[1]['time_taken'])
            best_memory = min(successful.items(), key=lambda x: x[1]['memory_used'])
            best_nodes = min(successful.items(), key=lambda x: x[1]['nodes_explored'])
            
            print(f"\nBEST ALGORITHM BY TIME: {best_time[0]} ({best_time[1]['time_taken']:.2f}s)")
            print(f"BEST ALGORITHM BY MEMORY: {best_memory[0]} ({best_memory[1]['memory_used']:.2f}MB)")
            print(f"BEST ALGORITHM BY NODES: {best_nodes[0]} ({best_nodes[1]['nodes_explored']} nodes)")