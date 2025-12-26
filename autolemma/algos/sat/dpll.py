from typing import List, Set, Optional, Tuple
from .utils.core import unit_resolution, is_satisfiable, choose_literal



def dpll_solve(delta: List[List[int]]) -> Optional[Set[int]]:
    """
    DPLL algorithm: SAT solver with unit propagation.
    
    Args:
        delta: List of clauses where each clause is a list of integers.
               Positive int i represents variable Pi, negative -i represents ¬Pi.
    
    Returns:
        Set of literals representing satisfying assignment, or None if unsatisfiable.
    """
    I, gamma = unit_resolution(delta)
    
    status = is_satisfiable(gamma)
    if status is True:
        return I
    if status is False:
        return None
    
    literal = choose_literal(gamma)
    
    for branch_literal in [literal, -literal]:
        L = dpll_solve(gamma + [[branch_literal]])
        if L is not None:
            return L | I
    
    return None