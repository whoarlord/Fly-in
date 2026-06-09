*Este proyecto ha sido creado como parte del currículo de 42 por [iarrien-].*

# Fly-in — Planificación de Rutas Multi-Dron (MAPF)

## Descripción

Fly-in es un simulador de planificación de rutas para múltiples drones autónomos que deben desplazarse simultáneamente desde un punto de origen hasta un destino final dentro de un mapa de nodos interconectados (hubs). El objetivo principal es encontrar rutas libres de colisiones para todos los drones minimizando el tiempo total de viaje.

El proyecto aborda el problema conocido como **Multi-Agent Pathfinding (MAPF)**, un campo de investigación con aplicaciones reales en almacenes automatizados, gestión de tráfico aéreo de drones, robótica colaborativa y logística de última milla.

El mapa se define mediante un archivo de texto que especifica hubs (nodos), conexiones entre ellos, capacidades máximas de tráfico y zonas con propiedades especiales. Una vez resuelto el problema, el resultado se muestra en una ventana gráfica animada donde se puede observar el movimiento de los drones en tiempo real paso a paso.

## Estructura del Proyecto

```
Fly-in/
├── main.py          # Punto de entrada del programa
├── Map.py           # Lógica principal del mapa y el algoritmo CBS
├── Hub.py           # Definición de hubs, conexiones, zonas y drones
├── CT.py            # Árbol de restricciones (Constraint Tree)
├── Parser.py        # Parseo del archivo de mapa
├── Graphics.py      # Representación visual con tkinter
├── maps/            # Directorio con mapas de ejemplo
├── test2.txt        # Mapa de prueba avanzado ("The Impossible Dream")
├── drone.png        # Imagen del dron usada en la visualización
├── requirements.txt # Dependencias del proyecto
└── Makefile         # Reglas de compilación/ejecución
```

## Instrucciones

### Requisitos previos

- Python 3.10 o superior
- `tkinter` (incluido en la mayoría de distribuciones de Python estándar; en algunos sistemas Linux puede requerir instalación adicional)
- `pytest` (para ejecutar los tests)

```bash
pip install -r requirements.txt
```

En sistemas basados en Debian/Ubuntu, si `tkinter` no está disponible:

```bash
sudo apt-get install python3-tk
```

### Ejecución

```bash
python3 main.py <archivo_de_mapa>
```

**Ejemplo:**

```bash
python3 main.py test2.txt
```

También es posible usar el `Makefile` si está configurado para ello:

```bash
make run MAP=test2.txt
```

### Tests

```bash
pytest
```

### Formato del archivo de mapa

El archivo de mapa es un fichero de texto plano con la siguiente sintaxis:

```
nb_drones: <número>

start_hub: <nombre> <x> <y> [color=<color> max_drones=<n>]
hub: <nombre> <x> <y> [zone=<zona> color=<color> max_drones=<n>]
end_hub: <nombre> <x> <y> [color=<color> max_drones=<n>]

connection: <hub1>-<hub2> [max_link_capacity=<n>]
```

Las zonas disponibles son `normal`, `blocked`, `restricted` y `priority`. Los hubs `blocked` son intransitables. Los hubs `restricted` tienen un coste de movimiento de 2 turnos y fuerzan restricciones temporales adicionales. Los hubs `priority` dan prioridad en la selección de ruta.

## Algoritmo: Conflict-Based Search (CBS)

### Visión general

El algoritmo central del proyecto es **Conflict-Based Search (CBS)**, un método óptimo de dos niveles para resolver MAPF publicado originalmente por Sharon et al. (2015).

### Nivel bajo: búsqueda individual con restricciones

Cada dron calcula su ruta de forma independiente mediante una búsqueda greedy guiada por heurística (implementada en `Hub.calculate_route`). La heurística se precalcula para todos los nodos con una búsqueda en anchura inversa desde el hub final (`Map.update_heuristic`), asignando a cada hub el coste mínimo estimado para llegar al destino.

En cada paso, el dron evalúa todos sus vecinos y avanza al nodo con menor valor de `f = g + h`, donde `g` es el coste acumulado hasta el momento y `h` es la heurística. Si ningún vecino es válido (por restricciones o bloqueos), el dron espera un turno en el hub virtual `Wait`.

Las restricciones consisten en tuplas `(dron, posición, tiempo)` que prohíben a un dron específico estar en una posición concreta en un instante dado. Los hubs `restricted` añaden automáticamente restricciones en `t+1` para modelar el mayor tiempo de ocupación.

### Nivel alto: árbol de restricciones (CT)

El nivel alto mantiene un árbol de restricciones representado por la clase `CT`. El algoritmo funciona así:

1. Se calculan rutas iniciales sin restricciones para todos los drones.
2. Se comprueba si existen conflictos: dos drones en el mismo hub o conexión en el mismo instante, superando la capacidad máxima de dicho hub o conexión.
3. Si hay un conflicto, se generan dos ramas del árbol: una que restringe al primer dron implicado y otra que restringe al segundo, en el lugar y tiempo del conflicto.
4. De las dos ramas, se elige la de menor coste (makespan: instante en que el último dron llega al destino) y se continúa expandiendo desde ella.
5. El proceso se repite hasta que no se detectan conflictos o se alcanza el límite de iteraciones (2000 por defecto).

Esta estrategia es greedy (no se guarda una frontera completa de nodos abiertos), lo cual sacrifica completitud óptima a cambio de eficiencia en escenarios complejos.

### Gestión de conflictos

La detección de conflictos se realiza en `Map.check_conflicts`, que itera sobre todas las soluciones y registra en un diccionario las posiciones de cada dron en cada turno. Si el número de drones en un hub supera `max_drones`, o en una conexión supera `max_link_capacity`, se reporta un conflicto. Los hubs `restricted` registran también el turno `t+1`, simulando que el dron ocupa el nodo durante dos turnos.

### Coste y función de evaluación

El coste de una solución es el **makespan**: el máximo tiempo de llegada entre todos los drones. La rama con menor makespan tiene prioridad al expandir el árbol.

## Representación Visual

La visualización se implementa en `Graphics.py` usando la biblioteca estándar `tkinter`.

Al finalizar el cálculo de rutas, se abre una ventana que muestra:

- **Los hubs** como círculos coloreados según su tipo o zona: verde para el inicio, rojo para zonas de alta restricción, marrón para zonas `restricted`, dorado para zonas `priority`, etc. El color `rainbow` se muestra como rosa.
- **Las conexiones** como líneas entre hubs, con una etiqueta que indica la capacidad máxima del enlace.
- **Los drones** representados con la imagen `drone.png`, situados inicialmente todos en el hub de inicio.
- **El número de drones en cada hub** mostrado como texto en el centro del círculo del hub, actualizado en cada turno.
- **El identificador de cada dron** mostrado bajo su imagen para facilitar el seguimiento individual.
- **El turno actual** indicado en la parte superior de la ventana.

La animación avanza automáticamente un turno por segundo (`root.after(1000, ...)`), moviéndose según la solución calculada por CBS. Cada dron se desplaza al hub indicado en su checkpoint correspondiente al turno actual.

Esta representación visual permite:
- Verificar intuitivamente que no se producen colisiones.
- Detectar cuellos de botella en el mapa.
- Observar el comportamiento del algoritmo ante zonas restringidas o de capacidad limitada.
- Comprobar que drones con distintos caminos convergen correctamente al destino.

## Ejemplo de Uso

Dado el mapa `test2.txt` ("The Impossible Dream"), que incluye 25 drones, múltiples zonas restringidas, puertas de capacidad 1 y más de 60 hubs, el programa intenta calcular rutas válidas para todos los drones. Es un mapa de estrés diseñado para explorar los límites del algoritmo.

```bash
python3 main.py test2.txt
```

La salida por consola mostrará los conflictos detectados en cada iteración y la heurística calculada. Al terminar, se abre la ventana de animación.

## Recursos

### Documentación y referencias académicas

- **Artículo original de CBS**: Sharon, G., Stern, R., Felner, A., & Sturtevant, N. R. (2015). *Conflict-based search for optimal multi-agent pathfinding*. Artificial Intelligence, 219, 40–66.
  [https://www.sciencedirect.com/science/article/pii/S0004370214001386](https://www.sciencedirect.com/science/article/pii/S0004370214001386)

- **Introducción a MAPF**: Stern, R. et al. (2019). *Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks*. SOCS 2019.
  [https://arxiv.org/abs/1906.08291](https://arxiv.org/abs/1906.08291)

- **Documentación de tkinter** (visualización):
  [https://docs.python.org/3/library/tkinter.html](https://docs.python.org/3/library/tkinter.html)

- **Documentación oficial de Python** (tipos, typing, enums):
  [https://docs.python.org/3/library/typing.html](https://docs.python.org/3/library/typing.html)

- **Algoritmo A\* (base conceptual para la búsqueda de bajo nivel)**:
  [https://en.wikipedia.org/wiki/A*_search_algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)

### Uso de inteligencia artificial

Durante el desarrollo del proyecto se empleó IA (Claude de Anthropic) en las siguientes tareas:

- **Depuración del algoritmo CBS**: diagnóstico de errores en la propagación de restricciones y en la detección de conflictos en hubs `restricted`, que requerían lógica especial en `t+1`.
- **Resolución de bugs en la búsqueda de rutas individuales**: análisis de casos donde drones quedaban atrapados en bucles o el hub `Wait` no se gestionaba correctamente.
- **Discusión de estrategias de implementación**: evaluación de alternativas para la selección de rama en el árbol de restricciones (greedy vs. expansión completa con lista abierta).
- **Revisión de lógica en `Map.py` y `Hub.py`**: validación de la coherencia entre la detección de conflictos, el registro de estados ocupados y el cálculo del makespan.

La IA se usó como herramienta de análisis y discusión técnica, no para generar código de forma automática. Todas las decisiones de diseño y la implementación final son obra del autor.
