from typing import List, Set, Tuple, Optional
from .implication_graph import ImplicationGraph

def unit_resolution(delta: List[List[int]]) -> Tuple[Set[int], List[List[int]]]:
    """
    Perform unit resolution on clauses.
    
    Args:
        delta: List of clauses.
    
    Returns:
        Tuple of (assigned literals, remaining clauses after unit propagation).
    """
    I = set()
    gamma = [clause[:] for clause in delta]
    
    changed = True
    while changed:
        changed = False
        unit_clauses = [clause for clause in gamma if len(clause) == 1]
        
        if not unit_clauses:
            break
        
        for unit_clause in unit_clauses:
            literal = unit_clause[0]
            if literal not in I and -literal not in I:
                I.add(literal)
                gamma = simplify(gamma, literal)
                changed = True
    
    return I, gamma


def unit_propagate_with_graph(delta: List[List[int]], gamma: List[List[int]], 
                               assignment: set, graph: ImplicationGraph) -> Optional[List[int]]:
    """
    Perform unit propagation with implication graph tracking.
    
    Args:
        delta: Original clauses.
        gamma: Learned clauses.
        assignment: Current assignment set.
        graph: Implication graph.
    
    Returns:
        Conflicting clause if conflict detected, None otherwise.
    """
    combined = delta + gamma
    
    changed = True
    while changed:
        changed = False
        
        for clause in combined:
            satisfied = any(lit in assignment for lit in clause)
            if satisfied:
                continue
            
            unsatisfied = [lit for lit in clause if -lit not in assignment]
            
            if len(unsatisfied) == 0:
                return clause
            
            if len(unsatisfied) == 1:
                literal = unsatisfied[0]
                if literal not in assignment:
                    assignment.add(literal)
                    graph.add_implication(literal, clause, graph.current_level)
                    changed = True
    
    return None


def find_unassigned_literal(delta: List[List[int]], gamma: List[List[int]], assignment: set) -> Optional[int]:
    """
    Find an unassigned literal.
    
    Args:
        delta: Original clauses.
        gamma: Learned clauses.
        assignment: Current assignment.
    
    Returns:
        Unassigned literal or None.
    """
    all_vars = {abs(lit) for clause in delta + gamma for lit in clause}
    
    for var in sorted(all_vars):
        if var not in assignment and -var not in assignment:
            return var
    
    return None


def simplify(delta: List[List[int]], literal: int) -> List[List[int]]:
    """
    Simplify clauses given a literal assignment.
    
    Args:
        delta: List of clauses.
        literal: Assigned literal.
    
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


def is_satisfiable(delta: List[List[int]]) -> Optional[bool]:
    """
    Check if formula is trivially satisfiable or unsatisfiable.
    
    Args:
        delta: List of clauses.
    
    Returns:
        True if empty (satisfiable), False if contains empty clause (unsatisfiable), None otherwise.
    """
    if len(delta) == 0:
        return True
    if [] in delta:
        return False
    return None


def choose_literal(gamma: List[List[int]]) -> int:
    """
    Choose a literal from remaining clauses.
    
    Args:
        gamma: List of clauses.
    
    Returns:
        Selected literal.
    """
    for clause in gamma:
        if clause:
            return clause[0]
    return 1

def unit_propagate(delta: List[List[int]], gamma: List[List[int]], D: List[int]) -> Tuple[Optional[List[int]], Optional[Tuple[List[int], int]]]:
    """
    Perform unit propagation and detect conflicts.
    
    Args:
        delta: Original clauses.
        gamma: Learned clauses.
        D: Decision sequence.
    
    Returns:
        Tuple of (implied literals list, conflict clause with assertion level) or (implied, None) if no conflict.
    """
    implied = []
    combined = delta + gamma
    assignment = set(D)
    
    changed = True
    while changed:
        changed = False
        
        for clause in combined:
            satisfied = any(lit in assignment for lit in clause)
            if satisfied:
                continue
            
            unsatisfied = [lit for lit in clause if -lit not in assignment]
            
            if len(unsatisfied) == 0:
                asserting_clause = clause
                assertion_level = compute_assertion_level(clause, D)
                return implied, (asserting_clause, assertion_level)
            
            if len(unsatisfied) == 1:
                literal = unsatisfied[0]
                if literal not in assignment:
                    assignment.add(literal)
                    implied.append(literal)
                    changed = True
    
    return implied if implied else None, None


def compute_assertion_level(clause: List[int], D: List[int]) -> int:
    """
    Compute assertion level of a clause.
    
    Args:
        clause: Conflicting clause.
        D: Decision sequence.
    
    Returns:
        Assertion level.
    """
    levels = []
    for i, decision in enumerate(D):
        if -decision in clause:
            levels.append(i)
    
    return levels[-2] if len(levels) >= 2 else -1


def find_unassigned_literal(delta: List[List[int]], gamma: List[List[int]], D: List[int]) -> Optional[int]:
    """
    Find a literal that is not implied by unit resolution.
    
    Args:
        delta: Original clauses.
        gamma: Learned clauses.
        D: Decision sequence.
    
    Returns:
        Unassigned literal or None.
    """
    assignment = set(D)
    all_vars = {abs(lit) for clause in delta + gamma for lit in clause}
    
    for var in sorted(all_vars):
        if var not in assignment and -var not in assignment:
            return var
    
    return None