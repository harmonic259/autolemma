from typing import List, Set, Optional
from .utils.core import unit_propagate_with_graph, find_unassigned_literal
from .utils.implication_graph import ImplicationGraph, analyze_conflict


def dpll_plus_solve(delta: List[List[int]]) -> Optional[Set[int]]:
    """
    DPLL+ algorithm with conflict-driven clause learning.
    
    Args:
        delta: List of clauses where each clause is a list of integers.
    
    Returns:
        Set of literals representing satisfying assignment, or None if unsatisfiable.
    """
    gamma = []
    assignment = set()
    graph = ImplicationGraph()
    decision_level = 0
    
    while True:
        conflict_clause = unit_propagate_with_graph(delta, gamma, assignment, graph)
        
        if conflict_clause is not None:
            if decision_level == 0:
                return None
            
            learned_clause, backtrack_level = analyze_conflict(conflict_clause, graph)
            gamma.append(learned_clause)
            
            graph.clear_level(backtrack_level)
            decision_level = backtrack_level
            
            assignment = {lit for lit in assignment if graph.get_level(abs(lit)) >= 0}
        
        else:
            literal = find_unassigned_literal(delta, gamma, assignment)
            
            if literal is None:
                return assignment
            
            decision_level += 1
            assignment.add(literal)
            graph.add_decision(literal, decision_level)