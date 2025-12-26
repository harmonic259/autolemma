from itertools import product

def solve_cnf(clauses, variables):
    for assignment in product([False, True], repeat=len(variables)):
        env = dict(zip(variables, assignment))
        if all(any(env.get(abs(lit), lit>0) if lit>0 else not env.get(-lit) for lit in clause) for clause in clauses):
            return True, env
    return False, None
