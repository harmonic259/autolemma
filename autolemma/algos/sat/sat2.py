from typing import List, Set, Optional
from .utils.core import simplify


def sat2_solve(delta: List[List[int]], d: int = 0) -> Optional[Set[int]]:
    """
    SAT II algorithm: recursive SAT solver using depth-first search.
    
    Args:
        delta: List of clauses where each clause is a list of integers.
               Positive int i represents variable Pi, negative -i represents ¬Pi.
        d: Recursion depth, default 0.
    
    Returns:
        Set of literals representing satisfying assignment, or None if unsatisfiable.
    """
    if len(delta) == 0:
        return set()
    
    if [] in delta:
        return None
    
    variable = d + 1
    
    delta_with_var = simplify(delta, variable)
    L = sat2_solve(delta_with_var, d + 1)
    
    if L is not None:
        return L | {variable}
    
    delta_without_var = simplify(delta, -variable)
    L = sat2_solve(delta_without_var, d + 1)
    
    if L is not None:
        return L | {-variable}
    
    return None


