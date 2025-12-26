from typing import List, Set, Optional
from itertools import product


def bruteforce_solve(delta: List[List[int]]) -> Optional[Set[int]]:
    """
    Bruteforce SAT solver: try all possible assignments.
    
    Args:
        delta: List of clauses where each clause is a list of integers.
    
    Returns:
        Set of literals representing satisfying assignment, or None if unsatisfiable.
    """
    if len(delta) == 0:
        return set()
    if [] in delta:
        return None
    
    variables = sorted({abs(lit) for clause in delta for lit in clause})
    
    for vals in product([False, True], repeat=len(variables)):
        assignment = {var if val else -var for var, val in zip(variables, vals)}
        if all(any(lit in assignment for lit in clause) for clause in delta):
            return assignment
    
    return None