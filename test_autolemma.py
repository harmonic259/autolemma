from autolemma.core import Var, And, Or, Not, tseitin_cnf, Const, Implies, Iff
from autolemma.algos.sat import bruteforce_solve, sat2_solve, dpll_solve, dpll_plus_solve



# build a formula: (A ∧ B) ∨ C
A = Var("A")
B = Var("B")
C = Var("C")
f = And(Or(A, B), C)

print("Formula:", f)
print("NNF Formula:", f.nnf())

clauses, vmap = tseitin_cnf(f, start_id=1)

print("\nVariable mapping (name -> id):")
for name, vid in sorted(vmap.items(), key=lambda kv: kv[1]):
    print(" ", name, "->", vid)

print("\nTseitin CNF (clauses as lists of ints):")
for cl in clauses:
    print(" ", cl)


print("Bruteforce SAT solver:")
print(bruteforce_solve(clauses))

print("DFS SAT solver:")
print(sat2_solve(clauses))

print("DPLL SAT solver:")
print(dpll_solve(clauses))

print("DPLL+ SAT solver:")
print(dpll_plus_solve(clauses))
