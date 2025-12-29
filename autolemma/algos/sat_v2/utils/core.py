
from typing import List, Set, Optional


def simplify(clauses: List[List[int]], literal: int) -> List[List[int]]:
    """
    Simplify clauses by assigning a literal.
    Remove clauses satisfied by literal, and remove -literal from others.
    """
    simplified = []
    for clause in clauses:
        if literal in clause:
            continue  # Clause is satisfied
        new_clause = [lit for lit in clause if lit != -literal]
        simplified.append(new_clause)
    return simplified

def is_clause_true(clause: List[int], M: Set[int]) -> bool:
    """Return True if clause is true under assignment M."""
    return any(lit in M for lit in clause)

def is_clause_false(clause: List[int], M: Set[int]) -> bool:
    """Return True if clause is false under assignment M."""
    return all(-lit in M for lit in clause)

def find_unit_literal(clauses: List[List[int]], M: Set[int]) -> Optional[int]:
    """
    Find a unit literal in N not yet assigned in M.
    Returns the literal if found, else None.
    """
    for clause in clauses:
        unassigned = [lit for lit in clause if lit not in M and -lit not in M]
        if len(unassigned) == 1:
            # Check if all other literals are assigned false
            if all(-lit in M for lit in clause if lit != unassigned[0]):
                return unassigned[0]
    return None

def find_pure_literal(clauses: List[List[int]], M: Set[int]) -> Optional[int]:
    """
    Find a pure literal in N not yet assigned in M.
    Returns the literal if found, else None.
    """
    counts = {}
    for clause in clauses:
        for lit in clause:
            if lit in M or -lit in M:
                continue
            counts[lit] = counts.get(lit, 0) + 1
    for lit in counts:
        if -lit not in counts:
            return lit
    return None
