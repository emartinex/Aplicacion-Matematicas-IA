"""Polinomio característico exacto y pares propios numéricos de matrices reales."""

from dataclasses import dataclass

from .core import InputError, Q, Result, fmt, identity, multiply


def characteristic_coefficients(a):
    """Faddeev–LeVerrier: coeficientes de det(λI − A), de mayor a menor grado."""
    n = len(a)
    b = identity(n)
    coefficients = [Q(1)]
    for k in range(1, n+1):
        b = multiply(a, b)
        c = -sum((b[i][i] for i in range(n)), Q(0)) / k
        coefficients.append(c)
        for i in range(n):
            b[i][i] += c
    return coefficients


def complex_text(value):
    value = complex(value)
    if value.imag == 0:
        return fmt(float(value.real))
    if value.real == 0:
        return f"{fmt(float(value.imag))}i"
    return f"({fmt(float(value.real))} {'+' if value.imag > 0 else '−'} {fmt(float(abs(value.imag)))}i)"


def vector_text(v):
    return "[ " + ", ".join(complex_text(x) for x in v) + " ]"


@dataclass
class EigenSolution:
    eigenvalues: list[complex]
    vectors: list[list[complex]]  # Un vector por lista; cada uno es una columna de V.
    residuals: list[float]

    def __str__(self):
        return "\n\n".join(f"λ{i+1} ≈ {complex_text(value)}\nv{i+1} ≈ {vector_text(v)}" for i, (value, v) in enumerate(zip(self.eigenvalues, self.vectors)))


def eigen_result(a):
    n = len(a)
    if len(a[0]) != n:
        raise InputError("Autovalores y autovectores requieren una matriz cuadrada.")
    try:
        import numpy as np
    except ImportError:
        raise InputError("Esta operación necesita NumPy. Instala las dependencias con el mismo Python que abre la aplicación: python -m pip install -r requirements.txt.") from None
    coefficients = characteristic_coefficients(a)
    polynomial = " + ".join(f"({fmt(c)})" + (f"·λ^{n-i}" if n-i else "") for i, c in enumerate(coefficients) if c)
    steps = ["Buscar un vector v ≠ 0 tal que Av = λv. Entonces (A − λI)v = 0.",
             "El polinomio característico exacto es p(λ) = det(λI − A) = " + polynomial + ". Sus raíces son los autovalores."]
    if n == 2:
        trace = a[0][0] + a[1][1]
        det = coefficients[-1]
        discriminant = trace**2 - 4*det
        steps.append(f"En 2 × 2: tr(A) = {fmt(trace)}, det(A) = {fmt(det)}, Δ = tr(A)² − 4·det(A) = {fmt(discriminant)}. λ = (tr(A) ± √Δ)/2.")
    else:
        steps.append("Coeficientes por Faddeev–LeVerrier: B₀ = I; cₖ = −tr(ABₖ₋₁)/k; Bₖ = ABₖ₋₁ + cₖI.\n" + "\n".join(f"c{k} = {fmt(c)}" for k, c in enumerate(coefficients[1:], 1)))
    array = np.array(a, dtype=float)
    scale = float(np.max(np.abs(array))) or 1.0
    scaled = array / scale
    symmetric = all(a[i][j] == a[j][i] for i in range(n) for j in range(n))
    try:
        values, vectors = np.linalg.eigh(scaled) if symmetric else np.linalg.eig(scaled)
        if not np.all(np.isfinite(values)) or not np.all(np.isfinite(vectors)):
            raise InputError("No se obtuvo un resultado numérico finito; revisa la escala de los datos.")
        condition = float(np.linalg.cond(vectors))
    except np.linalg.LinAlgError:
        raise InputError("El cálculo numérico no convergió. Revisa los valores y la escala de la matriz.") from None
    steps.append("A partir de aquí se usa aritmética aproximada de doble precisión. " + ("Como A es simétrica, se utiliza un método que obtiene autovectores ortonormales." if symmetric else "Se calculan autovalores y autovectores derechos; pueden aparecer pares complejos conjugados.") + " Los vectores se normalizan a longitud 1.")
    pairs, columns, residuals = [], [], []
    for j in sorted(range(n), key=lambda j: (complex(values[j]).real, complex(values[j]).imag)):
        eigenvalue = complex(values[j]) * scale
        v = vectors[:, j].astype(complex)
        # Fijar una fase para que los ejemplos tengan una representación reproducible.
        anchor = int(np.argmax(np.abs(v)))
        v *= np.conj(v[anchor]) / abs(v[anchor])
        v /= np.linalg.norm(v)
        residual = float(np.linalg.norm(scaled @ v - values[j]*v) / (np.linalg.norm(scaled) + abs(values[j]))) if np.any(scaled) else 0.0
        pairs.append(eigenvalue)
        columns.append([complex(x) for x in v])
        residuals.append(residual)
        steps.append(f"Par {len(pairs)}: λ ≈ {complex_text(eigenvalue)}; resolver (A − λI)v ≈ 0 y normalizar.\n"
                     f"v ≈ {vector_text(v)}\nAv ≈ {vector_text(array @ v)}\nλv ≈ {vector_text(eigenvalue*v)}\n"
                     f"Residuo relativo ‖Av − λv‖₂ / ((‖A‖F + |λ|)‖v‖₂) ≈ {residual:.3g}.")
    interpretation = "Los pares mostrados satisfacen Av ≈ λv. En un autovector real, λ escala la magnitud y puede invertir el sentido. i representa √(−1). Las cifras se redondean a ocho dígitos significativos. "
    if symmetric:
        interpretation += "Para una matriz de covarianza, los autovectores son direcciones principales y sus autovalores miden varianza en esas direcciones. "
    else:
        interpretation += "Los vectores devueltos pueden ser dependientes; la lista no certifica una base ni la multiplicidad exacta de los espacios propios. "
    if condition > 1e8:
        interpretation += "Atención: los autovectores son casi dependientes numéricamente; la matriz puede ser defectiva o estar cerca de serlo. "
        steps.append(f"Diagnóstico: condición de la matriz de autovectores ≈ {condition:.3g}. No se afirma que A sea diagonalizable.")
    if max(residuals) > 1e-10:
        interpretation += "El residuo relativo supera 10⁻¹⁰: toma el resultado con cautela. "
    interpretation += "Un residuo pequeño verifica la ecuación aproximadamente, pero no garantiza precisión en autovalores sensibles o casi repetidos."
    return Result(EigenSolution(pairs, columns, residuals), "Autovalores y autovectores · aproximados", steps, interpretation)
