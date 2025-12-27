# autolemma/core/formula.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Iterable, Set, Dict, List, Optional, Iterator

SubstMap = Dict[str, "Formula"]

class Formula:
    """Base class for formula AST nodes."""

    def free_vars(self) -> Set[str]:
        raise NotImplementedError

    def substitute(self, mapping: SubstMap) -> "Formula":
        raise NotImplementedError

    def nnf(self) -> "Formula":
        """Return formula in negation normal form (push negations to literals)."""
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return str(self)

    def positions(self) -> Set[str]:
        raise NotImplementedError

    def subformula_at(self, pos: str) -> "Formula":
        raise NotImplementedError


@dataclass(frozen=True)
class Var(Formula):
    name: str

    def free_vars(self) -> Set[str]:
        return {self.name}

    def substitute(self, mapping: SubstMap) -> Formula:
        return mapping.get(self.name, self)

    def nnf(self) -> Formula:
        return self

    def __str__(self):
        return self.name

    def positions(self) -> Set[str]:
        return {""}

    def subformula_at(self, pos: str) -> Formula:
        if pos == "":
            return self
        raise ValueError(f"Invalid position {pos} for Var")


@dataclass(frozen=True)
class Const(Formula):
    value: bool

    def free_vars(self) -> Set[str]:
        return set()

    def substitute(self, mapping: SubstMap) -> Formula:
        return self

    def nnf(self) -> Formula:
        return self

    def __str__(self):
        return "⊤" if self.value else "⊥"

    def positions(self) -> Set[str]:
        return {""}

    def subformula_at(self, pos: str) -> Formula:
        if pos == "":
            return self
        raise ValueError(f"Invalid position {pos} for Const")


@dataclass(frozen=True)
class Not(Formula):
    child: Formula

    def free_vars(self) -> Set[str]:
        return self.child.free_vars()

    def substitute(self, mapping: SubstMap) -> Formula:
        return Not(self.child.substitute(mapping))

    def nnf(self) -> Formula:
        c = self.child
        # push negation
        if isinstance(c, Not):
            return c.child.nnf()
        if isinstance(c, And):
            return Or(*(Not(x).nnf() for x in c.children))
        if isinstance(c, Or):
            return And(*(Not(x).nnf() for x in c.children))
        if isinstance(c, Implies):
            # ¬(A -> B) == A ∧ ¬B
            return And(c.left.nnf(), Not(c.right).nnf())
        if isinstance(c, Iff):
            # ¬(A ↔ B) == (A ∧ ¬B) ∨ (¬A ∧ B)
            return Or(And(c.left.nnf(), Not(c.right).nnf()),
                      And(Not(c.left).nnf(), c.right.nnf()))
        return Not(c.nnf())

    def __str__(self):
        return f"¬({self.child})"

    def positions(self) -> Set[str]:
        child_positions = self.child.positions()
        return {""} | {"1." + p for p in child_positions}

    def subformula_at(self, pos: str) -> Formula:
        if pos == "":
            return self
        if pos.startswith("1."):
            return self.child.subformula_at(pos[2:])
        raise ValueError(f"Invalid position {pos} for Not")


@dataclass(frozen=True)
class And(Formula):
    children: Tuple[Formula, ...]

    def __init__(self, *children: Formula):
        flat: List[Formula] = []
        for c in children:
            if isinstance(c, And):
                flat.extend(c.children)
            else:
                flat.append(c)
        object.__setattr__(self, "children", tuple(flat))

    def free_vars(self) -> Set[str]:
        s: Set[str] = set()
        for c in self.children:
            s |= c.free_vars()
        return s

    def substitute(self, mapping: SubstMap) -> Formula:
        return And(*(c.substitute(mapping) for c in self.children))

    def nnf(self) -> Formula:
        return And(*(c.nnf() for c in self.children))

    def __str__(self):
        return "(" + " ∧ ".join(str(c) for c in self.children) + ")"

    def positions(self) -> Set[str]:
        all_positions = {""}
        for i, child in enumerate(self.children, start=1):
            child_positions = child.positions()
            all_positions.update({f"{i}." + p for p in child_positions})
        return all_positions

    def subformula_at(self, pos: str) -> Formula:
        if pos == "":
            return self
        parts = pos.split(".", 1)
        if len(parts) == 2 and parts[0].isdigit():
            idx = int(parts[0]) - 1
            if 0 <= idx < len(self.children):
                return self.children[idx].subformula_at(parts[1])
        raise ValueError(f"Invalid position {pos} for And")


@dataclass(frozen=True)
class Or(Formula):
    children: Tuple[Formula, ...]

    def __init__(self, *children: Formula):
        flat: List[Formula] = []
        for c in children:
            if isinstance(c, Or):
                flat.extend(c.children)
            else:
                flat.append(c)
        object.__setattr__(self, "children", tuple(flat))

    def free_vars(self) -> Set[str]:
        s: Set[str] = set()
        for c in self.children:
            s |= c.free_vars()
        return s

    def substitute(self, mapping: SubstMap) -> Formula:
        return Or(*(c.substitute(mapping) for c in self.children))

    def nnf(self) -> Formula:
        return Or(*(c.nnf() for c in self.children))

    def __str__(self):
        return "(" + " ∨ ".join(str(c) for c in self.children) + ")"

    def positions(self) -> Set[str]:
        all_positions = {""}
        for i, child in enumerate(self.children, start=1):
            child_positions = child.positions()
            all_positions.update({f"{i}." + p for p in child_positions})
        return all_positions

    def subformula_at(self, pos: str) -> Formula:
        if pos == "":
            return self
        parts = pos.split(".", 1)
        if len(parts) == 2 and parts[0].isdigit():
            idx = int(parts[0]) - 1
            if 0 <= idx < len(self.children):
                return self.children[idx].subformula_at(parts[1])
        raise ValueError(f"Invalid position {pos} for Or")


@dataclass(frozen=True)
class Implies(Formula):
    left: Formula
    right: Formula

    def free_vars(self) -> Set[str]:
        return self.left.free_vars() | self.right.free_vars()

    def substitute(self, mapping: SubstMap) -> Formula:
        return Implies(self.left.substitute(mapping), self.right.substitute(mapping))

    def nnf(self) -> Formula:
        # A -> B == ¬A ∨ B
        return Or(Not(self.left).nnf(), self.right.nnf())

    def __str__(self):
        return f"({self.left} → {self.right})"

    def positions(self) -> Set[str]:
        left_positions = self.left.positions()
        right_positions = self.right.positions()
        return {""} | {"1." + p for p in left_positions} | {"2." + p for p in right_positions}

    def subformula_at(self, pos: str) -> Formula:
        if pos == "":
            return self
        if pos.startswith("1."):
            return self.left.subformula_at(pos[2:])
        if pos.startswith("2."):
            return self.right.subformula_at(pos[2:])
        raise ValueError(f"Invalid position {pos} for Implies")


@dataclass(frozen=True)
class Iff(Formula):
    left: Formula
    right: Formula

    def free_vars(self) -> Set[str]:
        return self.left.free_vars() | self.right.free_vars()

    def substitute(self, mapping: SubstMap) -> Formula:
        return Iff(self.left.substitute(mapping), self.right.substitute(mapping))

    def nnf(self) -> Formula:
        # A ↔ B == (A ∧ B) ∨ (¬A ∧ ¬B)
        return Or(And(self.left.nnf(), self.right.nnf()),
                  And(Not(self.left).nnf(), Not(self.right).nnf()))

    def __str__(self):
        return f"({self.left} ↔ {self.right})"

    def positions(self) -> Set[str]:
        left_positions = self.left.positions()
        right_positions = self.right.positions()
        return {""} | {"1." + p for p in left_positions} | {"2." + p for p in right_positions}

    def subformula_at(self, pos: str) -> Formula:
        if pos == "":
            return self
        if pos.startswith("1."):
            return self.left.subformula_at(pos[2:])
        if pos.startswith("2."):
            return self.right.subformula_at(pos[2:])
        raise ValueError(f"Invalid position {pos} for Iff")



# Tseitin CNF conversion (top-level)


def _fresh_ints(start: int = 1) -> Iterator[int]:
    n = start
    while True:
        yield n
        n += 1


def tseitin_cnf(formula: Formula, start_id: int = 1
               ) -> Tuple[List[List[int]], Dict[str, int]]:
    """
    Convert 'formula' to CNF using Tseitin transformation.

    Returns:
      (clauses, var_map)
      - clauses: list of clauses as lists of ints (positive = var, negative = ¬var)
      - var_map: mapping from variable name / internal key -> int id
    The returned clauses include a unit clause asserting the root variable true.
    """
    counter = _fresh_ints(start_id)
    clauses: List[List[int]] = []
    var_map: Dict[str, int] = {}

    def new_tmp(name_hint: Optional[str] = None) -> int:
        v = next(counter)
        key = f"__tmp_{name_hint}_{v}" if name_hint else f"__tmp_{v}"
        var_map[key] = v
        return v

    def get_or_assign_var_for_name(name: str) -> int:
        if name in var_map:
            return var_map[name]
        v = next(counter)
        var_map[name] = v
        return v

    def encode(node: Formula) -> int:
        """Encode node and return an integer id representing the truth of node."""
        if isinstance(node, Var):
            return get_or_assign_var_for_name(node.name)
        if isinstance(node, Const):
            v = new_tmp("const")
            # enforce v == const.value
            clauses.append([v] if node.value else [-v])
            return v
        if isinstance(node, Not):
            cid = encode(node.child)
            v = new_tmp("not")
            # v <-> ¬cid  encoded as: (¬v ∨ ¬cid) and (v ∨ cid)
            clauses.append([-v, -cid])
            clauses.append([v, cid])
            return v
        if isinstance(node, And):
            child_ids = [encode(c) for c in node.children]
            v = new_tmp("and")
            # v -> ci  : (¬v ∨ ci) for each ci
            for cid in child_ids:
                clauses.append([-v, cid])
            # (ci -> v) : (¬ci ∨ v) combined as (¬c1 ∨ ¬c2 ∨ ... ∨ v)
            negs = [-cid for cid in child_ids]
            clauses.append(negs + [v])
            return v
        if isinstance(node, Or):
            child_ids = [encode(c) for c in node.children]
            v = new_tmp("or")
            # v -> (c1 ∨ c2 ∨ ...)  encoded as (¬v ∨ c1 ∨ c2 ∨ ...)
            clauses.append([-v] + child_ids)
            # each ci -> v : (¬ci ∨ v)
            for cid in child_ids:
                clauses.append([-cid, v])
            return v
        if isinstance(node, Implies):
            # A -> B == ¬A ∨ B
            return encode(Or(Not(node.left), node.right))
        if isinstance(node, Iff):
            # A ↔ B == (A -> B) ∧ (B -> A)
            return encode(And(Implies(node.left, node.right), Implies(node.right, node.left)))
        # fallback: encode nnf
        return encode(node.nnf())

    root_vid = encode(formula)
    # assert root true
    clauses.append([root_vid])
    return clauses, var_map
