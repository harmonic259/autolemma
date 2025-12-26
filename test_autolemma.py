from autolemma.core import Var, And, Or, Not, tseitin_cnf, Const, Implies, Iff
from autolemma.algos.sat import brute_solve



# build a formula: (A ∧ B) ∨ C
A = Var("A")
B = Var("B")
C = Var("C")
f = Or(Not(And(A, B, C)), C)
f2 = f.substitute({"C": Const(True)})

print("Formula:", f.nnf())

clauses, vmap = tseitin_cnf(f, start_id=1)

print("Bruteforce SAT solver:")
variables = list(vmap.values())
print(brute_solve(clauses, variables))

print("\nTseitin CNF (clauses as lists of ints):")
for cl in clauses:
    print(" ", cl)

print("\nVariable mapping (name -> id):")
for name, vid in sorted(vmap.items(), key=lambda kv: kv[1]):
    print(" ", name, "->", vid)

# quick sanity checks
assert A.free_vars() == {"A"}
assert f.free_vars() == {"A", "B", "C"}

# substitution example

print("\nAfter substitution C -> True:", f2)

# some additional small examples
phi = Implies(And(A, B), C)   # (A ∧ B) -> C
psi = Iff(A, B)               # A ↔ B
print("\nMore formulas:", phi, psi)

print("\nBasic tests passed.")
