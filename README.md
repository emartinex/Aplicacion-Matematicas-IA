# Álgebra para IA

Aplicación educativa de escritorio en **Python**, en español. Permite seleccionar una operación, comprender su definición y parámetros, introducir valores, calcular y consultar los pasos y un escenario de aplicación en inteligencia artificial.

## Abrir en Windows

Haz doble clic en **`iniciar.bat`**. El lanzador busca Python instalado y, en este equipo, también puede utilizar el Python incluido con Codex.

O ejecuta desde esta carpeta:

```powershell
python app.py
```

Se requiere **Python 3.10 o superior con Tkinter/Tcl-Tk**, incluido en la instalación habitual de Python para Windows. El módulo de autovalores/autovectores requiere **NumPy**, ya disponible en el Python de Codex de este equipo. En otro intérprete, instala las dependencias una vez con el mismo Python que abrirá la aplicación:

```powershell
python -m pip install -r requirements.txt
```

La aplicación funciona localmente, sin claves de API ni servicios de IA. Solo la instalación de dependencias puede necesitar Internet. Si Python no está en el PATH, el lanzador también busca `py -3`. Si falta NumPy, la operación de autovalores muestra cómo instalarlo y las demás operaciones siguen disponibles.

## Flujo del alumno

1. Selecciona una operación en el menú izquierdo.
2. Lee la fórmula, la definición y la descripción de cada parámetro.
3. Escribe los valores o pulsa **Cargar ejemplo** para usar un ejercicio preparado.
4. Pulsa **Calcular y comprender** o **Ctrl + Enter**.
5. Explora las pestañas **Resultado**, **Paso a paso** y **Aplicación en IA**.
6. Opcionalmente, guarda la explicación completa como texto UTF-8.

La explicación exportada incluye los datos introducidos, el procedimiento, el resultado, la interpretación y una pregunta de reflexión. Al editar los datos se invalida el resultado anterior para evitar exportar una explicación desactualizada.

## Operaciones

| Grupo | Operaciones |
|---|---|
| Vectores | Suma, resta, multiplicación por escalar, producto punto, norma L₂ |
| Matrices | Dimensiones, suma, resta, multiplicación por escalar, combinación αA + βB, producto, identidad, transpuesta, inversa |
| Modelos lineales | Sistemas Ax = b, predicción w·x + b y ajuste de regresión lineal simple |
| Espacios vectoriales | Espacio generado y base; pertenencia a un espacio; espacio nulo |
| Ampliación en Matrices | Rango y determinante |
| Ampliación en Vectores | Ortogonalidad |
| Espectro de matrices | Autovalores y autovectores |

Los sistemas pueden ser cuadrados o rectangulares. Se identifican soluciones únicas, sistemas incompatibles e infinitas soluciones; estas últimas se expresan con parámetros libres. La inversa se comprueba con A·A⁻¹ = I.

## Formato de entrada

- Vectores: componentes separadas por espacios, por ejemplo `3 -2 4`.
- Matrices: una fila por línea y valores separados por espacios; también se pueden separar filas con `;`.
- Escalares: enteros, decimales con punto, fracciones o notación científica; por ejemplo `-2`, `0.5`, `1/3`, `2e-3`.
- No se evalúan expresiones de Python. No se admiten comas decimales, infinitos ni valores NaN.
- Límite didáctico: 8 componentes por vector y 8 × 8 por matriz. Cada número tiene hasta 32 caracteres; los valores no nulos deben estar entre 10⁻¹² y 10¹² en valor absoluto.

Ejemplo de matriz:

```text
2 1 0
1 3 2
```

El motor usa `fractions.Fraction` para conservar resultados racionales exactos, incluso con decimales de entrada. Por ejemplo, `0.1 + 0.2` produce `3/10`. Las normas con raíz no racional se muestran como aproximaciones de ocho cifras significativas.

## Ejercicios complementarios del temario

Se añadieron siete ejercicios con la misma secuencia de definición, parámetros, valores, resultado, pasos, aplicación en IA y pregunta de reflexión. El programa contiene **24 operaciones**; el menú permite desplazarse para acceder a todas.

| Ejercicio nuevo | Entrada de ejemplo | Resultado esperado |
|---|---|---|
| Espacio generado y base | A = `1 2 0; 0 0 1` | Base {(1,0), (0,1)}, dimensión 2; generadores dependientes |
| Pertenencia a un espacio | A = `1 0; 0 1; 1 1`, b = `2 3 5` | Pertenece; coeficientes (2,3) |
| Rango | A = `1 2 0; 2 4 1; 3 6 1` | Rango 2 |
| Espacio nulo | A = `1 2 3; 2 4 6` | Base {(-2,1,0), (-3,0,1)}, nulidad 2 |
| Determinante | A = `2 1 0; 1 3 2; 0 1 4` | Determinante 16 |
| Ortogonalidad | a = `1 2 -1`, b = `2 -1 0` | Sí; producto punto cero |
| Autovalores/autovectores | A = `2 1; 1 2` | λ ≈ 1 y 3, con vectores propios unitarios |

En los ejercicios de espacios generados, **cada columna de A es un generador**. Las bases de los resultados se muestran como listas de vectores, uno por fila. La base vacía corresponde al espacio {0}, de dimensión cero. No es una base que contenga el vector cero.

Rango, bases, pertenencia, núcleo, determinante y ortogonalidad se calculan exactamente. Se comprueban las ecuaciones de pertenencia y del núcleo. El determinante se obtiene por eliminación con seguimiento de intercambios de filas; no se confunde el producto de la diagonal de la matriz reducida con el determinante original.

Autovalores/autovectores admite matrices reales cuadradas de hasta 8 × 8. Se obtiene el polinomio característico con coeficientes exactos y se calculan pares propios aproximados en doble precisión. Se admiten salidas complejas y se informa el residuo relativo de cada ecuación Av ≈ λv. Las cifras mostradas se redondean a ocho dígitos significativos; dos valores muy próximos pueden verse iguales. Un residuo pequeño no certifica precisión de autovalores sensibles.

Para matrices simétricas se emplea `numpy.linalg.eigh`; para otras, `numpy.linalg.eig`. En matrices no simétricas, los vectores devueltos pueden ser dependientes y no se presentan como una base completa de cada espacio propio. Se advierte cuando son casi dependientes; no se certifica diagonalización ni multiplicidad exacta. Véanse las referencias oficiales de [eig](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eig.html) y [eigh](https://numpy.org/doc/stable/reference/generated/numpy.linalg.eigh.html).

## Base en los apuntes

Se utilizaron las ocho fotografías compartidas como material académico de referencia. Sus anotaciones de tarea no se interpretaron como instrucciones adicionales. No se copian las fotografías personales al proyecto ni se necesitan para ejecutarlo.

Ejemplos incluidos y verificados:

- `(3, −2, 4)·(1, 5, −2) = −15`.
- `‖(3, 4)‖₂ = 5`.
- `[[2, 1, 0], [1, 3, 2]] · [[1, 0], [2, 1], [0, 3]] = [[4, 1], [7, 9]]`.
- Para `A = [[3, −2], [4, 5]]` y `B = [[−1, 6], [2, −3]]`, `3A − 2B = [[11, −18], [8, 21]]`.
- `x + 2y = 3` y `4x + 5y = 6` tienen solución `x = −1`, `y = 2`.
- `(0.5, 0.3, 0.2)·(8, 7, 9) = 7.9`.

Se precisan algunos conceptos para evitar confusiones:

- Un vector de ℝⁿ es una colección ordenada de componentes reales; un espacio vectorial es una estructura con suma y multiplicación por escalares que satisfacen sus axiomas.
- La resta de vectores produce un desplazamiento. Su norma mide la distancia.
- Una inversa ordinaria requiere una matriz cuadrada no singular; transponer no equivale a invertir.
- Multiplicar matrices o calcular una suma ponderada utiliza pesos existentes. Entrenar una regresión requiere estimar esos pesos a partir de observaciones.
- La regresión lineal simple se incluye como **extensión didáctica**. El error de ajuste no mide por sí solo el desempeño sobre datos nuevos.
- Las redes neuronales usan transformaciones lineales y activaciones para representar funciones; no se afirma que resuelvan cualquier ecuación no lineal.

## Estructura del proyecto

```text
app.py                     Entrada de la aplicación
iniciar.bat                Lanzador Windows por doble clic
iniciar.ps1                Detección del intérprete Python
matematicas_ia/
    core.py                Validación y motor matemático independiente
    spectral.py            Polinomio característico exacto y pares propios numéricos
    catalog.py             Definiciones, parámetros, ejemplos y escenarios
    ui.py                  Interfaz de escritorio Tkinter
tests/
    test_core.py           Casos de apuntes, álgebra y validación
    test_topics.py         Nuevos temas, invariantes algebraicas y casos límite
    smoke_ui.py            Verificación de interfaz y flujo de todas las operaciones
requirements.txt           Dependencia del módulo de autovalores/autovectores
```

Para incorporar una operación nueva, agrega su definición en `catalog.py`, implementa el cálculo en `core.py` y añade una prueba con un resultado conocido. La interfaz construye los campos a partir del catálogo.

## Verificación

Desde la carpeta del proyecto:

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python tests/smoke_ui.py
```

La segunda verificación necesita un entorno con Tcl/Tk y comprueba el flujo de interfaz con ventanas ocultas. Las pruebas matemáticas no necesitan abrir la aplicación.

Esta herramienta está orientada al aprendizaje con matrices pequeñas. La aritmética exacta y el detalle de Gauss–Jordan priorizan la comprensión. Para conjuntos de datos grandes se necesita un motor numérico especializado y métodos adecuados al problema.
