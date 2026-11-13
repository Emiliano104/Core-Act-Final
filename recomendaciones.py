"""Recomendaciones básicas de hábitos según los patrones detectados.

Son sugerencias generales, nunca diagnósticos.
"""

# Una recomendación para cada condición definida en analisis.CONDICIONES
RECOMENDACIONES = {
    "duermes menos de 6 horas": (
        "Intenta dormir al menos 7 horas esta semana. Fija una hora para acostarte "
        "y evita las pantallas un rato antes de dormir."
    ),
    "tomas menos de 4 vasos de agua": (
        "Intenta tomar agua a lo largo del día. Tener una botella cerca mientras "
        "estudias ayuda a no olvidarlo."
    ),
    "comes menos de 3 veces al día": (
        "Intenta no saltarte comidas. Aunque sea algo ligero, comer a tus horas "
        "puede ayudarte a sentirte mejor."
    ),
    "no haces ejercicio": (
        "Intenta moverte un poco cada día, aunque sea una caminata corta o "
        "estirarte entre sesiones de estudio."
    ),
}


def generar_recomendaciones(patrones):
    """Recibe la lista de patrones y regresa una lista de (situación, consejo).

    Solo usa los patrones claros, empezando por el que más diferencia muestra.
    """
    claros = [p for p in patrones if p["es_patron"]]
    claros.sort(key=lambda p: p["p_cumple"] - p["p_no_cumple"], reverse=True)
    return [(p["cumple"], RECOMENDACIONES[p["cumple"]]) for p in claros]
