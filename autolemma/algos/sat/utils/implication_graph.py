from typing import List, Dict, Set, Optional, Tuple


class ImplicationGraph:
    """
    Implication graph for DPLL+ conflict analysis.
    """
    
    def __init__(self):
        self.graph: Dict[int, Tuple[Optional[List[int]], int]] = {}
        self.level: Dict[int, int] = {}
        self.current_level = 0
    
    def add_decision(self, literal: int, level: int):
        """Add a decision literal."""
        self.graph[literal] = (None, level)
        self.level[literal] = level
        self.current_level = level
    
    def add_implication(self, literal: int, antecedent: List[int], level: int):
        """Add an implied literal with its antecedent clause."""
        self.graph[literal] = (antecedent, level)
        self.level[literal] = level
    
    def get_antecedent(self, literal: int) -> Optional[List[int]]:
        """Get antecedent clause of a literal."""
        if literal in self.graph:
            return self.graph[literal][0]
        return None
    
    def get_level(self, literal: int) -> int:
        """Get decision level of a literal."""
        return self.level.get(literal, -1)
    
    def clear_level(self, level: int):
        """Remove all literals at or above given level."""
        to_remove = [lit for lit, lv in self.level.items() if lv > level]
        for lit in to_remove:
            del self.graph[lit]
            del self.level[lit]
        self.current_level = level


def analyze_conflict(conflict_clause: List[int], graph: ImplicationGraph) -> Tuple[List[int], int]:
    """
    Analyze conflict using 1UIP learning scheme.
    
    Args:
        conflict_clause: The conflicting clause.
        graph: Implication graph.
    
    Returns:
        Tuple of (learned clause, backtrack level).
    """
    if graph.current_level == 0:
        return conflict_clause, -1
    
    learned = set(conflict_clause)
    current_level_lits = {lit for lit in learned if graph.get_level(abs(lit)) == graph.current_level}
    
    while len(current_level_lits) > 1:
        lit = next(iter(current_level_lits))
        antecedent = graph.get_antecedent(-lit)
        
        if antecedent is None:
            current_level_lits.remove(lit)
            continue
        
        learned.remove(lit)
        for ant_lit in antecedent:
            if -ant_lit != -lit:
                learned.add(ant_lit)
        
        current_level_lits = {lit for lit in learned if graph.get_level(abs(lit)) == graph.current_level}
    
    learned_clause = list(learned)
    
    levels = sorted({graph.get_level(abs(lit)) for lit in learned_clause if graph.get_level(abs(lit)) < graph.current_level})
    backtrack_level = levels[-1] if levels else 0
    
    return learned_clause, backtrack_level