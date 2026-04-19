"""
bono.py — La Conspiración del Aeropuerto Internacional

Durante la madrugada, se detectó un cargamento ilegal en el aeropuerto internacional.
La Supervisora Lara tenía acceso a la zona de carga. El Técnico Ruiz también tenía acceso
y fue visto cerca del cargamento ilegal. El Operador Silva manipuló los registros digitales.
Ninguno de ellos tiene coartada verificada. Además, Lara, Silva y Ruiz pertenecen a una red
de tráfico ilegal. Un informante reportó a Lara. Ortega, un guardia, no tiene coartada pero
no fue visto en la escena.

Como detective, se establecen las siguientes reglas:
Quien tiene acceso y fue visto en la escena estuvo involucrado en el crimen.
Manipular registros digitales constituye encubrimiento.
Pertenecer a una red ilegal implica tener motivo.
Quien sin coartada, con motivo y que estuvo involucrado es culpable.
Si dos culpables pertenecen a la misma red, hay operación conjunta.
Si una persona reportada resulta ser culpable, el reporte se confirma.
"""

from src.crime_case import CrimeCase, QuerySpec
from src.predicate_logic import ExistsGoal, ForallGoal, KnowledgeBase, Predicate, Rule, Term


def crear_kb() -> KnowledgeBase:
    kb = KnowledgeBase()

    # Constantes 
    lara = Term("lara")
    silva = Term("silva")
    ruiz = Term("ruiz")
    ortega = Term("ortega")
    red = Term("red_trafico")

    # Hechos
    kb.add_fact(Predicate("acceso", (lara,)))
    kb.add_fact(Predicate("acceso", (ruiz,)))

    kb.add_fact(Predicate("visto_escena", (ruiz,)))
    kb.add_fact(Predicate("visto_escena", (lara,)))

    kb.add_fact(Predicate("manipulo_registros", (silva,)))

    kb.add_fact(Predicate("sin_coartada", (lara,)))
    kb.add_fact(Predicate("sin_coartada", (silva,)))
    kb.add_fact(Predicate("sin_coartada", (ruiz,)))
    kb.add_fact(Predicate("sin_coartada", (ortega,)))

    kb.add_fact(Predicate("pertenece_red", (lara, red)))
    kb.add_fact(Predicate("pertenece_red", (silva, red)))
    kb.add_fact(Predicate("pertenece_red", (ruiz, red)))

    kb.add_fact(Predicate("reportado", (lara,)))

    kb.add_fact(Predicate("guardia", (ortega,)))

    # Variables
    x = Term("$X")
    y = Term("$Y")
    r = Term("$R")

    # Reglas 
    kb.add_rule(Rule(
        [Predicate("acceso", (x,)), Predicate("visto_escena", (x,))],
        Predicate("involucrado", (x,))
    ))

    kb.add_rule(Rule(
        [Predicate("manipulo_registros", (x,))],
        Predicate("encubridor", (x,))
    ))

    kb.add_rule(Rule(
        [Predicate("pertenece_red", (x, r))],
        Predicate("motivo", (x,))
    ))

    kb.add_rule(Rule(
        [Predicate("guardia", (x,))],
        Predicate("acceso", (x,))
    ))
    
    kb.add_rule(Rule(
        [
            Predicate("involucrado", (x,)),
            Predicate("sin_coartada", (x,)),
            Predicate("motivo", (x,)),
            Predicate("visto_escena", (x,))
        ],
        Predicate("culpable", (x,))
    ))

    kb.add_rule(Rule(
        [
            Predicate("culpable", (x,)),
            Predicate("culpable", (y,)),
            Predicate("pertenece_red", (x, r)),
            Predicate("pertenece_red", (y, r)),
            Predicate("visto_escena", (x,))
        ],
        Predicate("operacion_conjunta", (x, y))
    ))
    
    kb.add_rule(Rule(
        [Predicate("reportado", (x,)), Predicate("culpable", (x,))],
        Predicate("reporte_confirmado", (x,))
    ))

    return kb


CASE = CrimeCase(
    id="conspiracion_aeropuerto",
    title="La Conspiración del Aeropuerto Internacional",
    suspects=("lara", "silva", "ruiz", "ortega"),
    narrative=__doc__,
    description=(
        "Un caso de tráfico ilegal en el aeropuerto donde acceso, presencia en la escena "
        "y pertenencia a una red criminal permiten identificar a los culpables."
    ),
    create_kb=crear_kb,
    queries=(

        QuerySpec(
            description="¿Ruiz es culpable?",
            goal=Predicate("culpable", (Term("ruiz"),)),
        ),

        QuerySpec(
            description="¿Silva es encubridor?",
            goal=Predicate("encubridor", (Term("silva"),)),
        ),

        QuerySpec(
            description="¿Existe una operación conjunta?",
            goal=ExistsGoal("$X", Predicate("operacion_conjunta", (Term("$X"), Term("ruiz")))),
        ),

        QuerySpec(
            description="¿El reporte contra Lara está confirmado?",
            goal=Predicate("reporte_confirmado", (Term("lara"),)),
        ),

        QuerySpec(
            description="¿Alguien pertenece a la red criminal?",
            goal=ExistsGoal("$X", Predicate("pertenece_red", (Term("$X"), Term("red_trafico")))),
        ),
        
        QuerySpec(
            description="¿Todos los culpables pertenecen a la red?",
            goal=ForallGoal(
                "$X",
                Predicate("culpable", (Term("$X"),)),
                Predicate("pertenece_red", (Term("$X"), Term("red_trafico")))
            ),
        ),
    ),
)