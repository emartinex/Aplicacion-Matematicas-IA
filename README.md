# Álgebra para IA

Aplicación educativa de escritorio en **Python**, en español. Permite seleccionar una operación, comprender su definición y parámetros, introducir valores, calcular y consultar los pasos y un escenario de aplicación en inteligencia artificial.

## Abrir en Windows

Haz doble clic en **`iniciar.bat`**. El lanzador busca Python instalado y, en este equipo, también puede utilizar el Python incluido con Codex.

O ejecuta desde esta carpeta:

```powershell
python app.py
```

Se requiere **Python 3.10 o superior con Tkinter/Tcl-Tk**, incluido en la instalación habitual de Python para Windows. No se necesitan paquetes de `pip`, claves de API, conexión a Internet ni servicios de IA. Si Python no está en el PATH, el lanzador también busca `py -3`.

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
    catalog.py             Definiciones, parámetros, ejemplos y escenarios
    ui.py                  Interfaz de escritorio Tkinter
tests/
    test_core.py           Casos de apuntes, álgebra y validación
    smoke_ui.py            Verificación de interfaz y flujo de todas las operaciones
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
