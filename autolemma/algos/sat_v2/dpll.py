from typing import List, Set, Optional
from .utils.core import is_clause_true, is_clause_false, find_unit_literal, find_pure_literal, simplify

def dpll(M: Set[int], N: List[List[int]]) -> bool:
	"""
	DPLL SAT solver.
	Args:
		M: Set of assigned literals (model).
		N: List of clauses (CNF), each clause is a list of ints.
	Returns:
		True if satisfiable, False otherwise.
	"""
	# 1. If all clauses are true in M, return True
	if all(is_clause_true(clause, M) for clause in N):
		return True
	# 2. If some clause is false in M, return False
	if any(is_clause_false(clause, M) for clause in N):
		return False
	# 3. Unit clause
	unit = find_unit_literal(N, M)
	if unit is not None:
		return dpll(M | {unit}, simplify(N, unit))
	# 4. Pure literal
	pure = find_pure_literal(N, M)
	if pure is not None:
		return dpll(M | {pure}, simplify(N, pure))
	# 5. Choose a variable not assigned in M
	vars_in_N = set(abs(lit) for clause in N for lit in clause)
	assigned_vars = set(abs(lit) for lit in M)
	unassigned = vars_in_N - assigned_vars
	if not unassigned:
		return False  # No variables left, but not all clauses are true
	P = next(iter(unassigned))
	# Try assigning -P first (as in the pseudocode)
	if dpll(M | {-P}, simplify(N, -P)):
		return True
	return dpll(M | {P}, simplify(N, P))
