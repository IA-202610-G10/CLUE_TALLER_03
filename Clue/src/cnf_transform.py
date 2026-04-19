"""
cnf_transform.py — Transformaciones a Forma Normal Conjuntiva (CNF).
El pipeline completo to_cnf() llama a todas las transformaciones en orden.
"""

from __future__ import annotations

from src.logic_core import And, Atom, Formula, Iff, Implies, Not, Or


# --- FUNCION GUÍA SUMINISTRADA COMPLETA ---


def eliminate_double_negation(formula: Formula) -> Formula:
    """
    Elimina dobles negaciones recursivamente.

    Transformacion:
        Not(Not(a)) -> a

    Se aplica recursivamente hasta que no queden dobles negaciones.

    Ejemplo:
        >>> eliminate_double_negation(Not(Not(Atom('p'))))
        Atom('p')
        >>> eliminate_double_negation(Not(Not(Not(Atom('p')))))
        Not(Atom('p'))
    """
    if isinstance(formula, Atom):
        return formula
    if isinstance(formula, Not):
        if isinstance(formula.operand, Not):
            return eliminate_double_negation(formula.operand.operand)
        return Not(eliminate_double_negation(formula.operand))
    if isinstance(formula, And):
        return And(*(eliminate_double_negation(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        return Or(*(eliminate_double_negation(d) for d in formula.disjuncts))
    return formula


# --- FUNCIONES QUE DEBEN IMPLEMENTAR ---


def eliminate_iff(formula: Formula) -> Formula:
    """
    Elimina bicondicionales recursivamente.

    Transformacion:
        Iff(a, b) -> And(Implies(a, b), Implies(b, a))

    Debe aplicarse recursivamente a todas las sub-formulas.

    Ejemplo:
        >>> eliminate_iff(Iff(Atom('p'), Atom('q')))
        And(Implies(Atom('p'), Atom('q')), Implies(Atom('q'), Atom('p')))

    Hint: Usa pattern matching sobre el tipo de la formula.
          Para cada tipo, aplica eliminate_iff recursivamente a los operandos,
          y solo transforma cuando encuentras un Iff.
    """
    #Version Original
    #if isinstance(formula, Iff):
       # left_rec = eliminate_iff(formula.left)
        #right_rec = eliminate_iff(formula.right)
       # return And(Implies(left_rec, right_rec), Implies(right_rec, left_rec))
    #elif isinstance(formula, Implies):
       # return Implies(eliminate_iff(formula.antecedent), eliminate_iff(formula.consequent))
    #elif isinstance(formula, And):
        #return And(*(eliminate_iff(c) for c in formula.conjuncts))
    #elif isinstance(formula, Or):
        #return Or(*(eliminate_iff(d) for d in formula.disjuncts))
    #elif isinstance(formula, Not):
        #return Not(eliminate_iff(formula.operand))
    #return formula
    
    #Version final 
    #Prompt: Segun lo que pide el taller y sin cambiar su funcionalidad,
    #como optimizarias este codigo?
    if isinstance(formula, Iff):
        left = eliminate_iff(formula.left)
        right = eliminate_iff(formula.right)
        return And(Implies(left, right), Implies(right, left))

    if isinstance(formula, Implies):
        return Implies( eliminate_iff(formula.antecedent),eliminate_iff(formula.consequent))
    if isinstance(formula, And):
        return And(*[eliminate_iff(c) for c in formula.conjuncts])
    if isinstance(formula, Or):
        return Or(*[eliminate_iff(d) for d in formula.disjuncts])
    if isinstance(formula, Not):
        return Not(eliminate_iff(formula.operand))
    return formula

def eliminate_implication(formula: Formula) -> Formula:
    """
    Elimina implicaciones recursivamente.

    Transformacion:
        Implies(a, b) -> Or(Not(a), b)

    Debe aplicarse recursivamente a todas las sub-formulas.

    Ejemplo:
        >>> eliminate_implication(Implies(Atom('p'), Atom('q')))
        Or(Not(Atom('p')), Atom('q'))

    Hint: Similar a eliminate_iff. Recorre recursivamente y transforma
          solo los nodos Implies.
    """
    if isinstance(formula, Implies):
        ant_rec = eliminate_implication(formula.antecedent)
        con_rec = eliminate_implication(formula.consequent)
        return Or(Not(ant_rec), con_rec)
    elif isinstance(formula, Iff):
        return Iff(eliminate_implication(formula.left), eliminate_implication(formula.right))
    elif isinstance(formula, And):
        return And(*(eliminate_implication(c) for c in formula.conjuncts))
    elif isinstance(formula, Or):
        return Or(*(eliminate_implication(d) for d in formula.disjuncts))
    elif isinstance(formula, Not):
        return Not(eliminate_implication(formula.operand))
    return formula


def push_negation_inward(formula: Formula) -> Formula:
    """
    Aplica las leyes de De Morgan y mueve negaciones hacia los atomos.

    Transformaciones:
        Not(And(a, b, ...)) -> Or(Not(a), Not(b), ...)   (De Morgan)
        Not(Or(a, b, ...))  -> And(Not(a), Not(b), ...)   (De Morgan)

    Debe aplicarse recursivamente a todas las sub-formulas.

    Ejemplo:
        >>> push_negation_inward(Not(And(Atom('p'), Atom('q'))))
        Or(Not(Atom('p')), Not(Atom('q')))
        >>> push_negation_inward(Not(Or(Atom('p'), Atom('q'))))
        And(Not(Atom('p')), Not(Atom('q')))

    Hint: Cuando encuentres un Not, revisa que hay adentro:
          - Si es Not(And(...)): aplica De Morgan para convertir en Or de negaciones.
          - Si es Not(Or(...)): aplica De Morgan para convertir en And de negaciones.
          - Si es Not(Atom): dejar como esta.
          Para And y Or sin negacion encima, simplemente recursa sobre los hijos.

    Nota: Esta funcion se llama DESPUES de eliminar Iff e Implies,
          asi que no necesitas manejar esos tipos.
    """
    if isinstance(formula, Not):
        if isinstance(formula.operand, And):
            return Or(*(push_negation_inward(Not(c)) for c in formula.operand.conjuncts))
        elif isinstance(formula.operand, Or):
            return And(*(push_negation_inward(Not(d)) for d in formula.operand.disjuncts))
        else:
            return Not(push_negation_inward(formula.operand))
    elif isinstance(formula, And):
        return And(*(push_negation_inward(c) for c in formula.conjuncts))
    elif isinstance(formula, Or):
        return Or(*(push_negation_inward(d) for d in formula.disjuncts))
    return formula


def distribute_or_over_and(formula: Formula) -> Formula:
    """
    Distribuye Or sobre And para obtener CNF.

    Transformacion:
        Or(A, And(B, C)) -> And(Or(A, B), Or(A, C))

    Debe aplicarse recursivamente hasta que no queden Or que contengan And.

    Ejemplo:
        >>> distribute_or_over_and(Or(Atom('p'), And(Atom('q'), Atom('r'))))
        And(Or(Atom('p'), Atom('q')), Or(Atom('p'), Atom('r')))

    Hint: Para un nodo Or, primero distribuye recursivamente en los hijos.
          Luego busca si algun hijo es un And. Si lo encuentras, aplica la
          distribucion y recursa sobre el resultado (podria haber mas).
          Para And, simplemente recursa sobre cada conjuncion.
          Atomos y Not se retornan sin cambio.

    Nota: Esta funcion se llama DESPUES de mover negaciones hacia adentro,
          asi que solo veras Atom, Not(Atom), And y Or.
    """
    #Version original
    #if isinstance(formula, And):
        #return And(*(distribute_or_over_and(c) for c in formula.conjuncts))
    #elif isinstance(formula, Or):
        #disjuncts = [distribute_or_over_and(d) for d in formula.disjuncts]
        #for i, d in enumerate(disjuncts):
            #if isinstance(d, And):
                #rest = disjuncts[:i] + disjuncts[i+1:]
                #A = rest[0] if len(rest) == 1 else Or(*rest)
                #new_conjuncts = [distribute_or_over_and(Or(A, c)) for c in d.conjuncts]
               # return And(*new_conjuncts)
        #return Or(*disjuncts)
    #elif isinstance(formula, Not):
       # return Not(distribute_or_over_and(formula.operand))
    #return formula
    
    #Version final
    #Prompt:Segun lo que pide el taller y sin cambiar su funcionalidad,
    #como optimizarias este codigo?
    if isinstance(formula, And):
        return And(*(distribute_or_over_and(c) for c in formula.conjuncts))
    if isinstance(formula, Or):
        disjuncts = [distribute_or_over_and(d) for d in formula.disjuncts]
        and_index = next((i for i, d in enumerate(disjuncts) if isinstance(d, And)), None)
        if and_index is not None:
            and_formula = disjuncts[and_index]
            rest = disjuncts[:and_index] + disjuncts[and_index + 1:]
            return And(*[
                distribute_or_over_and(
                    Or(*(rest + [c]))
                )
                for c in and_formula.conjuncts
            ])
        return Or(*disjuncts)
    if isinstance(formula, Not):
        return Not(distribute_or_over_and(formula.operand))
    return formula


def flatten(formula: Formula) -> Formula:
    """
    Aplana conjunciones y disyunciones anidadas.

    Transformaciones:
        And(And(a, b), c) -> And(a, b, c)
        Or(Or(a, b), c)   -> Or(a, b, c)

    Debe aplicarse recursivamente.

    Ejemplo:
        >>> flatten(And(And(Atom('a'), Atom('b')), Atom('c')))
        And(Atom('a'), Atom('b'), Atom('c'))
        >>> flatten(Or(Or(Atom('a'), Atom('b')), Atom('c')))
        Or(Atom('a'), Atom('b'), Atom('c'))

    Hint: Para un And, recorre cada hijo. Si un hijo tambien es And,
          agrega sus conjuncts directamente en vez de agregar el And.
          Igual para Or con sus disjuncts.
          Si al final solo queda 1 elemento, retornalo directamente.
    """
    #if isinstance(formula, And):
        #new_conjuncts = []
        #for c in formula.conjuncts:
           # flat_c = flatten(c)
            #if isinstance(flat_c, And):
               # new_conjuncts.extend(flat_c.conjuncts)
           # else:
                #new_conjuncts.append(flat_c)
        #if len(new_conjuncts) == 1:
            #return new_conjuncts[0]
        #return And(*new_conjuncts)
    #elif isinstance(formula, Or):
        #new_disjuncts = []
        #for d in formula.disjuncts:
            #flat_d = flatten(d)
            #if isinstance(flat_d, Or):
               # new_disjuncts.extend(flat_d.disjuncts)
            #else:
                #new_disjuncts.append(flat_d)
        #if len(new_disjuncts) == 1:
           # return new_disjuncts[0]
        #return Or(*new_disjuncts)
    #elif isinstance(formula, Not):
        #return Not(flatten(formula.operand))
    #elif isinstance(formula, Implies):
       # return Implies(flatten(formula.antecedent), flatten(formula.consequent))
    #elif isinstance(formula, Iff):
        #return Iff(flatten(formula.left), flatten(formula.right))
    #return formula
    
    #Version final
    #Prompt:Segun lo que pide el taller y sin cambiar su funcionalidad,
    #como optimizarias este codigo? 
    if isinstance(formula, And):
        items = []
        for c in formula.conjuncts:
            flat = flatten(c)
            if isinstance(flat, And):
                items.extend(flat.conjuncts)
            else:
                items.append(flat)
        return items[0] if len(items) == 1 else And(*items)

    if isinstance(formula, Or):
        items = []
        for d in formula.disjuncts:
            flat = flatten(d)
            if isinstance(flat, Or):
                items.extend(flat.disjuncts)
            else:
                items.append(flat)
        return items[0] if len(items) == 1 else Or(*items)

    if isinstance(formula, Not):
        return Not(flatten(formula.operand))

    if isinstance(formula, Implies):
        return Implies(
            flatten(formula.antecedent),
            flatten(formula.consequent)
        )

    if isinstance(formula, Iff):
        return Iff(
            flatten(formula.left),
            flatten(formula.right)
        )

    return formula


# --- PIPELINE COMPLETO ---


def to_cnf(formula: Formula) -> Formula:
    """
    [DADO] Pipeline completo de conversion a CNF.

    Aplica todas las transformaciones en el orden correcto:
    1. Eliminar bicondicionales (Iff)
    2. Eliminar implicaciones (Implies)
    3. Mover negaciones hacia adentro (Not)
    4. Eliminar dobles negaciones (Not Not)
    5. Distribuir Or sobre And
    6. Aplanar conjunciones/disyunciones

    Ejemplo:
        >>> to_cnf(Implies(Atom('p'), And(Atom('q'), Atom('r'))))
        And(Or(Not(Atom('p')), Atom('q')), Or(Not(Atom('p')), Atom('r')))
    """
    formula = eliminate_iff(formula)
    formula = eliminate_implication(formula)
    formula = push_negation_inward(formula)
    formula = eliminate_double_negation(formula)
    formula = distribute_or_over_and(formula)
    formula = flatten(formula)
    return formula
