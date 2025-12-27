from typing import List

def simplify(delta: List[List[int]]) -> List[List[int]]:
    """
    Simplify clauses.
    
    Args:
        delta: List of clauses.
    
    Returns:
        Simplified clause list.
    """
    simplified = []
    
    for clause in delta:
        if literal in clause:
            continue
        
        new_clause = [lit for lit in clause if lit != -literal]
        simplified.append(new_clause)
    
    return simplified
