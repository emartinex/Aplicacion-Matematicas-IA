"""Contenido pedagógico y ejemplos basados en los ocho apuntes proporcionados."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Field:
    key: str
    label: str
    kind: str
    description: str
    example: str


@dataclass(frozen=True)
class Lesson:
    id: str
    group: str
    title: str
    formula: str
    theory: str
    fields: tuple[Field, ...]
    scenario: str
    question: str
    source: str


def f(key, label, kind, description, example):
    return Field(key, label, kind, description, example)


VA = f("a", "Vector a", "vector", "Colección ordenada de n componentes reales.", "3 -2 4")
VB = f("b", "Vector b", "vector", "Segundo vector: debe tener las mismas n componentes que a.", "1 5 -2")
K = f("k", "Escalar k", "scalar", "Número que multiplica todas las componentes; puede ser negativo o cero.", "2")
MA = f("a", "Matriz A", "matrix", "Arreglo de m filas y n columnas. Escribe una fila por línea.", "3 -2\n4 5")
MB = f("b", "Matriz B", "matrix", "Debe tener la misma cantidad de filas y columnas que A.", "-1 6\n2 -3")


LESSONS = [
    Lesson("v_add", "Vectores", "Suma de vectores", "cᵢ = aᵢ + bᵢ", 
           "Un vector de ℝⁿ es una colección ordenada de n números reales. La suma combina componentes en la misma posición y requiere igual dimensión. El resultado también pertenece a ℝⁿ.",
           (VA, VB), "Representaciones de texto: un modelo puede sumar el embedding de una palabra y un vector de posición de igual dimensión. Así combina información de contenido y ubicación antes de procesarla.",
           "¿Qué sucedería si una componente representara metros en a y segundos en b?", "Apuntes: definición de vector y ejercicio 1."),
    Lesson("v_sub", "Vectores", "Resta de vectores", "cᵢ = aᵢ − bᵢ",
           "La resta calcula la diferencia componente a componente. Geométricamente, a − b es el desplazamiento desde b hasta a. El vector diferencia no es una distancia: su norma sí produce una distancia euclidiana.",
           (VA, VB), "Aprendizaje supervisado: al restar un vector de objetivos de un vector de predicciones se obtienen residuos. Sus componentes muestran cuánto se equivoca el modelo en cada observación.",
           "Si cambias a − b por b − a, ¿cómo cambia el resultado?", "Apuntes: resta de vectores y ejercicio 1."),
    Lesson("v_scale", "Vectores", "Vector por escalar", "uᵢ = k·aᵢ",
           "Un escalar es un número. Multiplicar por k cambia la magnitud del vector por |k|; si k es negativo invierte su sentido. El vector cero permanece cero.",
           (VA, K), "Entrenamiento: el descenso de gradiente multiplica el gradiente por una tasa de aprendizaje η. Después resta ese cambio a los pesos: w nuevo = w − η·gradiente.",
           "¿Qué efecto tendría duplicar la tasa de aprendizaje sobre el cambio de pesos?", "Apuntes: multiplicación por un escalar."),
    Lesson("v_dot", "Vectores", "Producto punto", "a·b = Σᵢ aᵢbᵢ",
           "Se multiplican los pares de componentes correspondientes y se suman sus productos. Los vectores deben tener igual dimensión. El resultado es un escalar, no un vector. Depende tanto de la orientación como de la magnitud.",
           (VA, VB), "Recomendación: un vector puede representar preferencias de un usuario y otro atributos de una película. Su producto punto produce una puntuación que el modelo puede usar para ordenar recomendaciones; no es por sí sola una probabilidad.",
           "¿Por qué dos productos punto no son comparables como similitud de dirección si las magnitudes cambian mucho?", "Apuntes: producto punto; ejemplo (3, −2, 4)·(1, 5, −2) = −15."),
    Lesson("v_norm", "Vectores", "Magnitud · norma L₂", "‖a‖₂ = √(Σᵢ aᵢ²)",
           "La norma euclidiana mide la longitud de un vector y siempre es no negativa. Solo es cero para el vector cero. Dividir un vector no nulo entre su norma produce un vector unitario.",
           (f("a", "Vector a", "vector", "Vector cuya magnitud quieres medir.", "3 4"),),
           "Búsqueda de vecinos cercanos: la norma de la diferencia entre dos vectores mide su distancia. También se usa ‖w‖₂² como penalización L₂ para limitar pesos grandes durante el entrenamiento.",
           "¿Por qué no se puede normalizar el vector cero dividiéndolo entre su norma?", "Apuntes: magnitud de un vector; ‖(3, 4)‖₂ = 5."),
    Lesson("m_dimensions", "Matrices", "Dimensiones de una matriz", "A ∈ ℝᵐˣⁿ · m filas, n columnas",
           "Una matriz es un arreglo rectangular. Su dimensión se escribe filas × columnas. Todas las filas deben tener la misma longitud. Es cuadrada cuando m = n.",
           (f("a", "Matriz A", "matrix", "Cada fila puede representar una observación y cada columna una característica.", "120 3 2\n80 2 1\n200 4 3"),),
           "Datos de viviendas: cada fila representa una casa y las columnas corresponden a superficie, habitaciones y baños. Una matriz de 3 × 3 contiene tres observaciones con tres características, no nueve casas.",
           "Si agregas una casa nueva sin cambiar las características, ¿cambian las filas o las columnas?", "Apuntes: matrices y tabla de casas."),
    Lesson("m_add", "Matrices", "Suma de matrices", "Cᵢⱼ = Aᵢⱼ + Bᵢⱼ",
           "Se suman las entradas que ocupan la misma fila i y columna j. A y B deben tener exactamente las mismas dimensiones. C conserva esa forma.",
           (MA, MB), "Redes neuronales residuales: una conexión puede sumar una matriz de activaciones a otra de la misma forma. Cada posición combina información correspondiente de ambas rutas.",
           "¿Basta con tener el mismo número total de elementos para sumar dos matrices?", "Apuntes: suma y resta; ejercicio 3."),
    Lesson("m_sub", "Matrices", "Resta de matrices", "Cᵢⱼ = Aᵢⱼ − Bᵢⱼ",
           "Se restan entradas correspondientes de matrices con la misma forma. El orden importa: A − B = −(B − A).",
           (MA, MB), "Visión artificial: restar imágenes alineadas del mismo tamaño ayuda a construir mapas de diferencias, útiles como entrada para detectar cambios o movimiento. En imágenes a color también hay que alinear los canales.",
           "¿Qué valor obtienes al restar una matriz de sí misma?", "Apuntes: suma y resta; ejercicio 3."),
    Lesson("m_scale", "Matrices", "Matriz por escalar", "Cᵢⱼ = k·Aᵢⱼ",
           "El mismo escalar multiplica cada entrada de la matriz. La dimensión no cambia. Esta operación no es un producto de matrices.",
           (MA, K), "Entrenamiento de una red: multiplicar la matriz de gradientes por la tasa de aprendizaje determina la magnitud de la actualización de todos los pesos de una capa.",
           "¿Qué ocurriría con una actualización si k fuera cero?", "Apuntes: ejercicio 3, cálculo de 2A."),
    Lesson("m_combo", "Matrices", "Combinación lineal", "C = αA + βB",
           "Una combinación lineal escala matrices y luego las suma. A y B deben tener la misma forma; α y β son números reales. Para 3A − 2B, introduce α = 3 y β = −2.",
           (MA, MB, f("alpha", "Coeficiente α", "scalar", "Peso que multiplica A.", "3"), f("beta", "Coeficiente β", "scalar", "Peso que multiplica B; usa un valor negativo para restar.", "-2")),
           "Promedio móvil de parámetros: θ promedio nuevo = α·θ promedio anterior + (1 − α)·θ actual. Ayuda a suavizar fluctuaciones del entrenamiento cuando los parámetros corresponden a la misma arquitectura.",
           "Para promediar A y B con la misma importancia, ¿qué valores darías a α y β?", "Apuntes: ejercicio 3, expresión 3A − 2B."),
    Lesson("m_product", "Matrices", "Multiplicación de matrices", "Cᵢⱼ = Σₖ AᵢₖBₖⱼ",
           "Cada entrada del producto es el producto punto de una fila de A y una columna de B. Si A es m × n y B es n × p, C es m × p. En general, AB ≠ BA; incluso uno de los dos productos podría no estar definido.",
           (f("a", "Matriz A", "matrix", "Matriz izquierda de m × n.", "2 1 0\n1 3 2"), f("b", "Matriz B", "matrix", "Matriz derecha de n × p: sus filas deben coincidir con las columnas de A.", "1 0\n2 1\n0 3")),
           "Una capa neuronal procesa un lote mediante Z = XW: X reúne observaciones por filas y W contiene pesos. El producto genera varias salidas por observación. El sesgo y la función de activación se aplican después, según el modelo.",
           "Si X tiene forma 20 × 3 y W tiene forma 3 × 5, ¿cuántas salidas tendrá cada observación?", "Apuntes: página titulada función de regresión lineal; producto [[4, 1], [7, 9]]."),
    Lesson("m_identity", "Matrices", "Matriz identidad", "Iᵢⱼ = 1 si i = j; 0 en otro caso",
           "La identidad de orden n es cuadrada, con unos en la diagonal principal y ceros en las demás posiciones. Actúa como elemento neutro del producto: AI = A e IA = A cuando las dimensiones son compatibles.",
           (f("n", "Orden n", "scalar", "Número entero de filas y columnas, entre 1 y 8.", "3"),),
           "Regresión ridge: sumar λI a XᵀX penaliza los pesos y ayuda a resolver problemas de dependencia entre características. En formulaciones habituales se evita penalizar el sesgo.",
           "¿Qué diferencia hay entre una matriz identidad y una matriz llena de unos?", "Apuntes: matriz identidad de órdenes 2 y 3."),
    Lesson("m_transpose", "Matrices", "Transposición", "(Aᵀ)ᵢⱼ = Aⱼᵢ",
           "Transponer intercambia filas y columnas, sin cambiar el valor de las entradas. Una matriz m × n se transforma en una n × m. Transponer dos veces recupera A.",
           (f("a", "Matriz A", "matrix", "Puede ser rectangular o cuadrada.", "1 8 4\n2 9 5\n5 21 6\n6 32 2"),),
           "Regresión: Xᵀ permite agrupar productos por característica. La expresión XᵀX aparece en mínimos cuadrados; para interpretarla como covarianza también se necesitan centrar los datos y aplicar el factor de escala adecuado.",
           "Si A es de 4 × 3, ¿qué forma tiene Aᵀ?", "Apuntes: transposición de matriz."),
    Lesson("m_inverse", "Matrices", "Inversa de una matriz", "AA⁻¹ = A⁻¹A = I",
           "La inversa deshace una transformación lineal. Existe únicamente para matrices cuadradas no singulares y, cuando existe, es única. Se calcula reduciendo [A | I] con Gauss–Jordan. En general, (A + B)⁻¹ ≠ A⁻¹ + B⁻¹.",
           (f("a", "Matriz A", "matrix", "Matriz cuadrada; la aplicación comprobará si es invertible.", "1 2\n4 5"),),
           "Transformaciones de coordenadas: una transformación lineal invertible permite convertir representaciones geométricas y recuperarlas. En aprendizaje automático, para resolver Ax = b suele preferirse resolver el sistema sin formar A⁻¹ explícitamente.",
           "Si dos filas son iguales, ¿se conserva suficiente información para deshacer la transformación?", "Apuntes: matriz inversa y sus propiedades."),
    Lesson("system", "Modelos lineales", "Sistema de ecuaciones", "Ax = b",
           "Cada fila de A contiene los coeficientes de una ecuación; x reúne las incógnitas y b los términos independientes. Gauss–Jordan identifica solución única, infinitas soluciones o incompatibilidad. Se admiten sistemas rectangulares.",
           (f("a", "Coeficientes A", "matrix", "Una fila por ecuación y una columna por incógnita.", "1 2\n4 5"), f("b", "Términos b", "vector", "Un término independiente por ecuación, en el mismo orden.", "3 6")),
           "Ajuste de un modelo: A puede reunir características, x los pesos desconocidos y b los objetivos. Un sistema compatible reproduce los objetivos exactamente; con datos ruidosos se suele minimizar el error en vez de exigir igualdad exacta.",
           "¿Por qué repetir la misma ecuación no aporta una restricción nueva?", "Apuntes: representación matricial del sistema x + 2y = 3; 4x + 5y = 6."),
    Lesson("prediction", "Modelos lineales", "Predicción · suma ponderada", "ŷ = w·x + b",
           "Un modelo lineal multiplica cada característica por su peso, suma los productos y agrega un sesgo. Los pesos ya están dados. Una neurona puede aplicar después una activación; esta operación muestra únicamente la salida lineal.",
           (f("x", "Características x", "vector", "Valores de una observación en el orden esperado por el modelo.", "8 7 9"), f("w", "Pesos w", "vector", "Un coeficiente por característica, en el mismo orden que x.", "0.5 0.3 0.2"), f("bias", "Sesgo b", "scalar", "Término constante que desplaza la salida; escribe 0 para omitirlo.", "0")),
           "Ejemplo de tus apuntes: tres calificaciones 8, 7 y 9 con pesos 0.5, 0.3 y 0.2 producen 7.9. Es una ponderación ilustrativa. En una regresión entrenada, los pesos se estiman a partir de datos y no tienen que sumar uno.",
           "¿Cómo cambia la predicción si aumentas el sesgo en una unidad?", "Apuntes: evaluación ponderada y neurona artificial simplificada."),
    Lesson("regression", "Modelos lineales", "Ajuste de una recta", "w = Σ(xᵢ−x̄)(yᵢ−ȳ) / Σ(xᵢ−x̄)²; b = ȳ−wx̄",
           "Extensión práctica de los apuntes: la regresión lineal simple aprende una pendiente w y un sesgo b minimizando la suma de errores cuadrados. Cada par (xᵢ, yᵢ) es una observación. Se requieren al menos dos pares y variación en x.",
           (f("x", "Observaciones x", "vector", "Una característica medida en varias observaciones; entre 2 y 8 valores.", "1 2 3 4"), f("y", "Objetivos y", "vector", "Un objetivo por observación, en el mismo orden que x.", "2 3 5 4")),
           "Predicción de precios: con superficies y precios de casas se aprende una recta. Usa las mismas unidades al predecir. Un buen ajuste en estas observaciones no demuestra causalidad ni garantiza acierto con casas nuevas.",
           "¿Qué limitaciones tendría predecir el precio de una casa usando únicamente su superficie?", "Extensión didáctica: distingue entrenar una regresión de calcular XW."),
]

BY_ID = {lesson.id: lesson for lesson in LESSONS}
