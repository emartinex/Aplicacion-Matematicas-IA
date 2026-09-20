"""Motor independiente de la interfaz. Las operaciones racionales son exactas."""

from dataclasses import dataclass
from fractions import Fraction
from math import sqrt
import re


MAX_DIM = 8
Q = Fraction
Matrix = list[list[Fraction]]


class InputError(ValueError):
    """Un dato no cumple las condiciones matemáticas o de formato."""


@dataclass
class Result:
    value: object
    summary: str
    steps: list[str]
    interpretation: str = ""


def fmt(value):
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else str(value)
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value)


def display(value):
    if isinstance(value, list):
        if not value:
            return "[]"
        if isinstance(value[0], list):
            rows = [[fmt(x) for x in row] for row in value]
            widths = [max(len(row[j]) for row in rows) for j in range(len(rows[0]))]
            return "\n".join("[ " + "   ".join(x.rjust(widths[j]) for j, x in enumerate(row)) + " ]" for row in rows)
        return "[ " + ", ".join(fmt(x) for x in value) + " ]"
    return fmt(value)


def number(text):
    text = str(text).strip()
    if not text or len(text) > 32:
        raise InputError("Escribe un número de hasta 32 caracteres; por ejemplo, -2, 0.5 o 1/3.")
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d{1,2})?|[+-]?\d+/[+-]?\d+", text):
        raise InputError(f"«{text}» no es válido. Usa punto decimal o una fracción como 1/3; no se aceptan expresiones.")
    try:
        value = Q(text)
    except (ValueError, ZeroDivisionError):
        raise InputError(f"«{text}» no es válido. El denominador de una fracción no puede ser cero.") from None
    if abs(value) > 10**12 or (value and abs(value) < Q(1, 10**12)):
        raise InputError("Usa cero o números con valor absoluto entre 10⁻¹² y 10¹².")
    return value


def vector(text):
    tokens = str(text).split()
    if not 1 <= len(tokens) <= MAX_DIM:
        raise InputError(f"El vector debe tener entre 1 y {MAX_DIM} componentes separadas por espacios.")
    return [number(token) for token in tokens]


def matrix(text):
    lines = str(text).strip().replace(";", "\n").splitlines()
    if not 1 <= len(lines) <= MAX_DIM or any(not line.strip() for line in lines):
        raise InputError(f"La matriz debe tener entre 1 y {MAX_DIM} filas, sin filas vacías intermedias.")
    rows = [vector(line) for line in lines]
    if len({len(row) for row in rows}) != 1:
        raise InputError("Todas las filas de la matriz deben tener la misma cantidad de columnas.")
    return rows


def same_vectors(a, b):
    if len(a) != len(b):
        raise InputError(f"Los vectores deben tener la misma dimensión: recibí {len(a)} y {len(b)}.")


def same_matrices(a, b):
    if (len(a), len(a[0])) != (len(b), len(b[0])):
        raise InputError("Las matrices deben tener exactamente las mismas filas y columnas.")


def identity(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def multiply(a, b):
    if len(a[0]) != len(b):
        raise InputError(f"Para A·B, columnas de A ({len(a[0])}) debe coincidir con filas de B ({len(b)}).")
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), Q(0)) for j in range(len(b[0]))] for i in range(len(a))]


def rref(a, coefficient_columns):
    """Gauss–Jordan exacto, sin pivotar sobre columnas de términos independientes."""
    rows = [row[:] for row in a]
    pivot_row = 0
    pivots, steps = [], []
    for col in range(coefficient_columns):
        candidate = next((i for i in range(pivot_row, len(rows)) if rows[i][col]), None)
        if candidate is None:
            continue
        if candidate != pivot_row:
            rows[pivot_row], rows[candidate] = rows[candidate], rows[pivot_row]
            steps.append(f"Intercambiar F{pivot_row + 1} ↔ F{candidate + 1}.\n{display(rows)}")
        pivot = rows[pivot_row][col]
        if pivot != 1:
            rows[pivot_row] = [x / pivot for x in rows[pivot_row]]
            steps.append(f"F{pivot_row + 1} ← F{pivot_row + 1} / ({fmt(pivot)}).\n{display(rows)}")
        for i in range(len(rows)):
            factor = rows[i][col]
            if i != pivot_row and factor:
                rows[i] = [x - factor * y for x, y in zip(rows[i], rows[pivot_row])]
                steps.append(f"F{i + 1} ← F{i + 1} − ({fmt(factor)})·F{pivot_row + 1}.\n{display(rows)}")
        pivots.append(col)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, pivots, steps


def null_basis(reduced, pivots, n):
    """Una base del núcleo a partir de la RREF de los coeficientes."""
    basis = []
    for free in (j for j in range(n) if j not in pivots):
        v = [Q(0)] * n
        v[free] = Q(1)
        for i, pivot in enumerate(pivots):
            v[pivot] = -reduced[i][free]
        basis.append(v)
    return basis


def basis_text(basis):
    return "\n".join(f"v{i+1} = {display(v)}" for i, v in enumerate(basis)) if basis else "Base vacía; el espacio contiene únicamente el vector cero."


def determinant(a):
    """Eliminación sin escalar filas: det(A) = signo · producto de pivotes."""
    n = len(a)
    if len(a[0]) != n:
        raise InputError("El determinante requiere una matriz cuadrada.")
    rows = [row[:] for row in a]
    sign, product = 1, Q(1)
    steps = ["Partir de A y triangular sin escalar filas:\n" + display(a)]
    for j in range(n):
        pivot_row = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot_row is None:
            steps.append(f"No hay pivote en la columna {j+1}; det(A) = 0.")
            return Q(0), steps
        if pivot_row != j:
            rows[j], rows[pivot_row] = rows[pivot_row], rows[j]
            sign *= -1
            steps.append(f"Intercambiar F{j+1} ↔ F{pivot_row+1}: cambia el signo del determinante.\n{display(rows)}")
        pivot = rows[j][j]
        product *= pivot
        for i in range(j+1, n):
            factor = rows[i][j] / pivot
            if factor:
                rows[i] = [x - factor*y for x, y in zip(rows[i], rows[j])]
                steps.append(f"F{i+1} ← F{i+1} − ({fmt(factor)})·F{j+1}; no cambia el determinante.\n{display(rows)}")
    value = sign * product
    steps.append(f"det(A) = ({sign})·" + "·".join(f"({fmt(rows[i][i])})" for i in range(n)) + f" = {fmt(value)}.")
    return value, steps


def calculate(operation, data):
    """Recibe identificador de operación y campos de texto; devuelve un Result."""
    steps = []
    if operation == "eigen":
        from .spectral import eigen_result
        return eigen_result(matrix(data["a"]))
    if operation == "orthogonality":
        a, b = vector(data["a"]), vector(data["b"])
        same_vectors(a, b)
        dot = sum((x*y for x, y in zip(a, b)), Q(0))
        steps = ["Evaluar a·b = " + " + ".join(f"({fmt(x)})·({fmt(y)})" for x, y in zip(a, b)) + f" = {fmt(dot)}.",
                 "Comparar exactamente con cero: " + ("a·b = 0." if dot == 0 else "a·b ≠ 0.")]
        zero = not any(a) or not any(b)
        interpretation = ("El vector cero es ortogonal a todo vector según el producto punto, pero no define una dirección ni un ángulo. No puede pertenecer a una base." if zero else
                          "Los vectores son perpendiculares: su ángulo es 90°. Ser ortogonales no implica tener longitud uno." if dot == 0 else
                          "Estos vectores no son perpendiculares; no forman un par ortogonal.")
        return Result("Sí, son ortogonales" if dot == 0 else "No son ortogonales", "Ortogonalidad · comprobación exacta", steps, interpretation)
    if operation in {"rank", "nullspace", "span_basis", "span_membership"}:
        a = matrix(data["a"])
        m, n = len(a), len(a[0])
        if operation == "span_membership":
            b = vector(data["b"])
            if len(b) != m:
                raise InputError("El vector objetivo debe tener una componente por fila de A; los generadores son sus columnas.")
            augmented = [row + [target] for row, target in zip(a, b)]
            reduced, pivots, elimination = rref(augmented, n)
            steps = ["Buscar coeficientes c tales que Ac = b. Cada columna de A es un generador.\n" + display(augmented)] + elimination
            if any(not any(row[:n]) and row[n] for row in reduced):
                return Result("No pertenece al espacio generado", "Pertenencia a span(A)", steps + ["Una fila 0 = c con c ≠ 0 impide representar b."],
                              "Ninguna combinación lineal de los generadores produce este objetivo. Agregar este vector ampliaría el espacio generado.")
            coefficients = [Q(0)] * n
            for i, j in enumerate(pivots):
                coefficients[j] = reduced[i][n]
            kernel = null_basis(reduced, pivots, n)
            steps.append("Una representación, fijando las variables libres en cero: c = " + display(coefficients))
            steps.append("Verificar Ac = b:\n" + display([row[0] for row in multiply(a, [[x] for x in coefficients])]))
            if kernel:
                steps.append("Todas las representaciones: c = c₀ + Σ tᵢvᵢ, con tᵢ reales y:\n" + basis_text(kernel))
            return Result(coefficients, "Sí pertenece · coeficientes de la combinación", steps,
                          "Cada coeficiente multiplica la columna correspondiente de A. " + ("La representación no es única; consulta la familia completa en los pasos." if kernel else "La representación es única porque los generadores son independientes."))
        reduced, pivots, elimination = rref(a, n)
        rank = len(pivots)
        steps = ["Reducir A con Gauss–Jordan:\n" + display(a)] + elimination
        steps.append("Columnas con pivote (numeradas desde 1): " + (", ".join(str(j+1) for j in pivots) or "ninguna") + f". Rango = {rank}.")
        if operation == "rank":
            steps.append(f"Rango + nulidad = número de columnas: {rank} + {n-rank} = {n}.")
            return Result(rank, "Rango de A · dimensión de su imagen", steps,
                          f"Hay {rank} direcciones de salida independientes en ℝ^{m}. " + ("Las columnas son linealmente independientes." if rank == n else "Las columnas son linealmente dependientes; algunas no aportan direcciones nuevas."))
        if operation == "span_basis":
            basis = [[row[j] for row in a] for j in pivots]
            steps.append("Tomar las columnas con pivote de la matriz ORIGINAL, no de la reducida:\n" + basis_text(basis))
            return Result(basis, f"Base del espacio generado · dimensión {rank}", steps,
                          "Cada fila del resultado muestra un vector de la base. " + ("La base es vacía: el espacio generado es {0}. " if not basis else "") +
                          ("Los generadores son independientes. " if rank == n else "Los generadores son dependientes. ") +
                          (f"Generan todo ℝ^{m}." if rank == m else f"Generan un subespacio propio de ℝ^{m}."))
        basis = null_basis(reduced, pivots, n)
        steps.append("Resolver Ax = 0: elegir una variable libre igual a 1 y las otras a 0 para cada vector de la base.\n" + basis_text(basis))
        for i, v in enumerate(basis, 1):
            steps.append(f"Comprobar A·v{i} = " + display([row[0] for row in multiply(a, [[x] for x in v])]))
        steps.append(f"Rango + nulidad = {rank} + {len(basis)} = {n}.")
        if basis:
            steps.append("Todo x del espacio nulo se expresa como x = " + " + ".join(f"t{i+1}·v{i+1}" for i in range(len(basis))) + ", con parámetros reales.")
        return Result(basis, f"Base del espacio nulo · nulidad {len(basis)}", steps,
                      "Cada fila del resultado representa un vector de la base del núcleo. " + ("Son direcciones de entrada que A transforma en cero. Si Ax = b tiene una solución x₀, todas son x₀ más un vector de este núcleo." if basis else "La base vacía no contiene al vector cero: el espacio nulo es {0} y tiene dimensión cero."))
    if operation == "determinant":
        value, steps = determinant(matrix(data["a"]))
        return Result(value, "Determinante · cálculo exacto", steps,
                      "El valor absoluto es el factor de escala de volumen de la transformación. " + ("Al ser cero, A colapsa alguna dirección y no es invertible." if value == 0 else "Al ser distinto de cero, A es invertible. " + ("El signo negativo indica inversión de orientación." if value < 0 else "El signo positivo indica que conserva la orientación.")))
    if operation.startswith("v_"):
        a = vector(data["a"])
        if operation in {"v_add", "v_sub", "v_dot"}:
            b = vector(data["b"])
            same_vectors(a, b)
        if operation in {"v_add", "v_sub"}:
            sign = 1 if operation == "v_add" else -1
            symbol = "+" if sign == 1 else "−"
            result = [x + sign * y for x, y in zip(a, b)]
            steps = [f"Componente {i + 1}: ({fmt(x)}) {symbol} ({fmt(y)}) = {fmt(result[i])}" for i, (x, y) in enumerate(zip(a, b))]
            return Result(result, f"Vector de {len(a)} componentes", steps,
                          "Cada componente conserva su significado. Solo combina características que estén alineadas y expresadas en unidades compatibles.")
        if operation == "v_scale":
            k = number(data["k"])
            result = [k * x for x in a]
            steps = [f"Componente {i + 1}: ({fmt(k)})·({fmt(x)}) = {fmt(result[i])}" for i, x in enumerate(a)]
            return Result(result, "Vector escalado", steps,
                          f"La longitud se multiplica por |{fmt(k)}|. Un factor negativo invierte el sentido; cero produce el vector cero.")
        if operation == "v_dot":
            products = [x * y for x, y in zip(a, b)]
            steps = [f"Par {i + 1}: ({fmt(x)})·({fmt(y)}) = {fmt(products[i])}" for i, (x, y) in enumerate(zip(a, b))]
            value = sum(products, Q(0))
            steps.append("Sumar productos: " + " + ".join(f"({fmt(p)})" for p in products) + f" = {fmt(value)}")
            return Result(value, "Producto punto · resultado escalar", steps,
                          "Si a contiene características y b pesos, este escalar es la suma ponderada. No es automáticamente una probabilidad ni una similitud normalizada.")
        if operation == "v_norm":
            squared = sum((x * x for x in a), Q(0))
            from math import isqrt
            num, den = isqrt(squared.numerator), isqrt(squared.denominator)
            exact = num * num == squared.numerator and den * den == squared.denominator
            value = Q(num, den) if exact else sqrt(squared)
            return Result(value, "Norma L₂" + (" · exacta" if exact else " · aproximada"),
                          [f"Sumar cuadrados: " + " + ".join(f"({fmt(x)})²" for x in a) + f" = {fmt(squared)}",
                           f"Extraer raíz: √({fmt(squared)}) {'=' if exact else '≈'} {fmt(value)}"],
                          "La norma mide magnitud. Para obtener distancia entre dos observaciones se calcula ‖a − b‖₂; para normalizar, divide entre la norma solo si es distinta de cero.")
    if operation == "m_identity":
        n = number(data["n"])
        if n.denominator != 1 or not 1 <= n <= MAX_DIM:
            raise InputError(f"El orden n debe ser un entero entre 1 y {MAX_DIM}.")
        return Result(identity(int(n)), f"Identidad de orden {n}",
                      ["Construir una matriz cuadrada de n filas y n columnas.", "Colocar 1 si i = j y 0 en el resto de las entradas."],
                      "Aplicar I a un vector conserva todas sus componentes: Ix = x.")
    if operation.startswith("m_"):
        a = matrix(data["a"])
        m, n = len(a), len(a[0])
        if operation == "m_dimensions":
            return Result(f"{m} × {n}", "Filas × columnas", [f"Contar filas: m = {m}.", f"Contar columnas: n = {n}.", f"A pertenece a ℝ^({m}×{n})."],
                          f"Si A es una tabla de datos, representa {m} observaciones con {n} características cada una. " + ("La matriz es cuadrada." if m == n else "La matriz es rectangular no cuadrada."))
        if operation in {"m_add", "m_sub", "m_combo", "m_product"}:
            b = matrix(data["b"])
            if operation != "m_product":
                same_matrices(a, b)
        if operation in {"m_add", "m_sub", "m_combo", "m_scale"}:
            if operation == "m_scale":
                alpha, beta, b = number(data["k"]), Q(0), [[Q(0)] * n for _ in range(m)]
            elif operation == "m_combo":
                alpha, beta = number(data["alpha"]), number(data["beta"])
            else:
                alpha, beta = Q(1), Q(1 if operation == "m_add" else -1)
            result = [[alpha * a[i][j] + beta * b[i][j] for j in range(n)] for i in range(m)]
            for i in range(m):
                for j in range(n):
                    expression = f"({fmt(alpha)})·({fmt(a[i][j])})"
                    if operation != "m_scale":
                        expression += f" + ({fmt(beta)})·({fmt(b[i][j])})"
                    steps.append(f"C[{i+1},{j+1}] = {expression} = {fmt(result[i][j])}")
            return Result(result, f"Matriz de {m} × {n}", steps,
                          "Las posiciones mantienen su correspondencia. En IA, combinar matrices de parámetros exige que representen las mismas características y arquitectura.")
        if operation == "m_product":
            result = multiply(a, b)
            steps.append(f"Dimensiones: ({m}×{n})·({len(b)}×{len(b[0])}) → ({m}×{len(b[0])}).")
            for i in range(m):
                for j in range(len(b[0])):
                    terms = " + ".join(f"({fmt(a[i][k])})·({fmt(b[k][j])})" for k in range(n))
                    steps.append(f"C[{i+1},{j+1}] = {terms} = {fmt(result[i][j])}")
            return Result(result, f"Producto de {m} × {len(b[0])}", steps,
                          f"Interpretando A como datos y B como pesos: {m} observaciones, {n} características de entrada y {len(b[0])} salidas por observación. Esto calcula la parte lineal de una capa; faltan el sesgo y la activación si el modelo los utiliza.")
        if operation == "m_transpose":
            result = [list(col) for col in zip(*a)]
            return Result(result, f"Transpuesta de {n} × {m}",
                          [f"Mover A[{i+1},{j+1}] = {fmt(a[i][j])} a Aᵀ[{j+1},{i+1}]." for i in range(m) for j in range(n)],
                          "Las filas pasan a columnas. La transpuesta permite formar XᵀX, una matriz de productos entre columnas; no es una inversa.")
        if operation == "m_inverse":
            if m != n:
                raise InputError("La inversa ordinaria requiere una matriz cuadrada: igual número de filas y columnas.")
            augmented = [row + unit for row, unit in zip(a, identity(n))]
            reduced, pivots, elimination = rref(augmented, n)
            steps = ["Construir [A | I]:\n" + display(augmented)] + elimination
            if len(pivots) < n:
                return Result("La matriz no tiene inversa", "Matriz singular", steps,
                              "Hay columnas linealmente dependientes. La transformación pierde información y no puede deshacerse mediante una inversa ordinaria.")
            result = [row[n:] for row in reduced]
            steps.append("Al obtener [I | A⁻¹], extraer el bloque derecho.")
            steps.append("Comprobar A·A⁻¹ = I:\n" + display(multiply(a, result)))
            return Result(result, "Matriz inversa · cálculo exacto", steps,
                          "Permite deshacer una transformación lineal invertible. En modelos de IA con datos decimales, normalmente se resuelve el sistema directamente en vez de construir una inversa.")
    if operation == "system":
        a, b = matrix(data["a"]), vector(data["b"])
        if len(a) != len(b):
            raise InputError("El vector b debe tener una componente por cada fila (ecuación) de A.")
        n = len(a[0])
        augmented = [row + [target] for row, target in zip(a, b)]
        reduced, pivots, elimination = rref(augmented, n)
        steps = ["Construir [A | b]:\n" + display(augmented)] + elimination
        if any(all(x == 0 for x in row[:n]) and row[n] != 0 for row in reduced):
            steps.append("Aparece una fila 0 = c con c ≠ 0: contradicción.")
            return Result("No existe solución", "Sistema incompatible", steps,
                          "Ningún vector de pesos reproduce exactamente estos objetivos. En regresión con ruido se busca minimizar el error mediante mínimos cuadrados.")
        if len(pivots) < n:
            free = [j for j in range(n) if j not in pivots]
            lines = [f"x{j+1} = t{idx+1} (parámetro libre)" for idx, j in enumerate(free)]
            for i, col in enumerate(pivots):
                expression = fmt(reduced[i][n])
                for idx, j in enumerate(free):
                    if reduced[i][j]:
                        expression += f" + ({fmt(-reduced[i][j])})·t{idx+1}"
                lines.append(f"x{col+1} = {expression}")
            return Result("\n".join(lines), "Infinitas soluciones", steps + ["Las columnas sin pivote corresponden a variables libres."],
                          "Distintos pesos producen los mismos objetivos. Para elegir una solución de aprendizaje pueden hacer falta más datos o un criterio adicional, como regularización.")
        solution = [Q(0)] * n
        for i, col in enumerate(pivots):
            solution[col] = reduced[i][n]
        steps.append("Comprobar A·x = b:\n" + display([row[0] for row in multiply(a, [[x] for x in solution])]))
        return Result(solution, "Solución única · orden x₁, x₂, …", steps,
                      "Si A contiene características y b objetivos, este vector de pesos reproduce exactamente esos datos. Ajustar los datos disponibles no garantiza predecir bien datos nuevos.")
    if operation == "prediction":
        x, w, bias = vector(data["x"]), vector(data["w"]), number(data["bias"])
        same_vectors(x, w)
        terms = [a * b for a, b in zip(x, w)]
        result = sum(terms, Q(0)) + bias
        steps = [f"Característica {i+1}: ({fmt(a)})·({fmt(b)}) = {fmt(terms[i])}" for i, (a, b) in enumerate(zip(x, w))]
        steps.append(f"Suma ponderada = {fmt(sum(terms, Q(0)))}; agregar sesgo {fmt(bias)} → {fmt(result)}.")
        return Result(result, "Predicción lineal ŷ", steps,
                      f"Con tus {len(x)} características y los pesos proporcionados, la salida es {fmt(result)}. Su unidad depende del objetivo del modelo. Aquí los pesos ya se conocen: no se entrenó una regresión ni se aplicó una activación.")
    if operation == "regression":
        x, y = vector(data["x"]), vector(data["y"])
        same_vectors(x, y)
        if len(x) < 2:
            raise InputError("Se necesitan al menos dos observaciones para ajustar una recta.")
        mean_x, mean_y = sum(x, Q(0)) / len(x), sum(y, Q(0)) / len(y)
        denominator = sum(((v - mean_x)**2 for v in x), Q(0))
        if denominator == 0:
            raise InputError("Todos los valores de x son iguales. No se puede identificar una pendiente única.")
        numerator = sum(((a - mean_x) * (b - mean_y) for a, b in zip(x, y)), Q(0))
        slope = numerator / denominator
        bias = mean_y - slope * mean_x
        predicted = [slope * v + bias for v in x]
        mse = sum(((a-b)**2 for a, b in zip(y, predicted)), Q(0)) / len(x)
        steps = [f"Medias: x̄ = {fmt(mean_x)}, ȳ = {fmt(mean_y)}.",
                 f"Σ(xᵢ − x̄)(yᵢ − ȳ) = {fmt(numerator)}; Σ(xᵢ − x̄)² = {fmt(denominator)}.",
                 f"Pendiente w = {fmt(numerator)} / ({fmt(denominator)}) = {fmt(slope)}.",
                 f"Sesgo b = ȳ − w·x̄ = {fmt(bias)}.",
                 "Predicciones sobre los datos de ajuste: " + display(predicted),
                 f"Error cuadrático medio de ajuste = {fmt(mse)}."]
        return Result(f"ŷ = ({fmt(slope)})·x + ({fmt(bias)})", "Regresión lineal simple · mínimos cuadrados", steps,
                      "La pendiente indica cuánto cambia la predicción por unidad de x. Por ejemplo, x puede ser superficie de una casa e y su precio. El error mostrado corresponde a los datos de ajuste; evalúa con datos separados antes de afirmar capacidad predictiva.")
    raise InputError("Selecciona una operación válida.")
