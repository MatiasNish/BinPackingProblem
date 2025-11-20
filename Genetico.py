import math
import random
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt

# ==================== UTILIDADES DE SALIDA ====================

def minimo_teorico(capacidad: int, lista_de_objetos: List[int]) -> int:
    suma_total = sum(lista_de_objetos)
    return math.ceil(suma_total / capacidad)

def decodificar_bins(solution: List[int], items: List[int]) -> List[List[int]]:
    """
    Convierte un vector de asignacion (bin_id por objeto) en una lista de cajas (lista de listas de items).
    Recompacta los IDs de bin para que salgan 0..k-1 en el orden en el que aparecen.
    """
    orden_ids = []
    visto = set()
    for b in solution:
        if b not in visto:
            visto.add(b)
            orden_ids.append(b)
    id_map = {old: new for new, old in enumerate(orden_ids)}

    bins_dict: Dict[int, List[int]] = {}
    for i, bin_id in enumerate(solution):
        bid = id_map[bin_id]
        bins_dict.setdefault(bid, []).append(items[i])

    # devolver en orden 0..k-1
    k = len(bins_dict)
    return [bins_dict[i] for i in range(k)]

# ==================== ALGORITMO GENETICO (BPP) ====================

def fitness(solution: List[int], items: List[int], capacidad: int) -> int:
    # suma de pesos por bin
    bins_sum: Dict[int, int] = {}
    for i, bin_id in enumerate(solution):
        bins_sum[bin_id] = bins_sum.get(bin_id, 0) + items[i]
    # penalizacion por exceso
    penalty = sum(max(0, w - capacidad) for w in bins_sum.values())
    # objetivo: menos bins y menos exceso
    return len(bins_sum) + penalty * 10

def generate_population(n_items: int, population_size: int) -> List[List[int]]:
    # asigna cada objeto a un bin aleatorio (IDs entre 0 y n_items-1)
    return [[random.randint(0, n_items - 1) for _ in range(n_items)] for _ in range(population_size)]

def selection(pop: List[List[int]], items: List[int], capacidad: int, k: int = 3) -> List[int]:
    contenders = random.sample(pop, k)
    return min(contenders, key=lambda s: fitness(s, items, capacidad))

def crossover(parent1: List[int], parent2: List[int]) -> Tuple[List[int], List[int]]:
    if len(parent1) < 2:
        return parent1[:], parent2[:]
    point = random.randint(1, len(parent1) - 2)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(solution: List[int], mutation_rate: float) -> List[int]:
    if random.random() < mutation_rate:
        idx = random.randint(0, len(solution) - 1)
        solution[idx] = random.randint(0, len(solution) - 1)
    return solution

def genetic_algorithm_bpp(
    items: List[int],
    capacidad: int,
    population_size: int = 1000,
    generations: int = 500,
    mutation_rate: float = 0.1,
    seed: int | None = 42,
    patience_no_change: int = 50,  # corta si pasan N generaciones sin CAMBIO del mejor de la generacion
) -> Tuple[int, List[List[int]], List[int], List[int]]:
    """
    Devuelve (num_cajas, configuracion_de_cajas, mejor_solution_vector, historia_bins_por_gen)
    Early stopping: termina si pasan 'patience_no_change' generaciones sin CAMBIO del numero de bins
    del mejor individuo de la generacion (sea mejora o empeora). Si cambia, se resetea el contador.
    """
    if seed is not None:
        random.seed(seed)

    n = len(items)
    population = generate_population(n, population_size)

    history_bins: List[int] = []

    # mejor global (para devolver una buena solucion al final)
    best_overall = min(population, key=lambda s: fitness(s, items, capacidad))
    best_bins_overall = len(set(best_overall))

    # control de "sin cambios" respecto al mejor de CADA generacion
    last_best_bins: int | None = None
    gens_without_change = 0

    for _ in range(generations):
        new_population: List[List[int]] = []

        # elitismo
        elite = min(population, key=lambda s: fitness(s, items, capacidad))
        new_population.append(elite[:])

        # reproduccion
        while len(new_population) < population_size:
            p1 = selection(population, items, capacidad)
            p2 = selection(population, items, capacidad)
            c1, c2 = crossover(p1, p2)
            new_population.append(mutate(c1, mutation_rate))
            if len(new_population) < population_size:
                new_population.append(mutate(c2, mutation_rate))

        population = new_population

        # mejor de la generacion (en bins y por fitness)
        best_gen = min(population, key=lambda s: fitness(s, items, capacidad))
        best_bins_gen = len(set(best_gen))
        history_bins.append(best_bins_gen)

        # actualizar mejor global si hay mejora en bins (o igual bins pero mejor fitness)
        if (best_bins_gen < best_bins_overall) or (
            best_bins_gen == best_bins_overall and fitness(best_gen, items, capacidad) < fitness(best_overall, items, capacidad)
        ):
            best_overall = best_gen[:]
            best_bins_overall = best_bins_gen

        # EARLY STOPPING por "sin cambios" del mejor de la generacion
        if last_best_bins is None or best_bins_gen != last_best_bins:
            # hubo cambio (mejora o empeora) -> reset
            gens_without_change = 0
            last_best_bins = best_bins_gen
        else:
            gens_without_change += 1
            if gens_without_change >= patience_no_change:
                break

    # mejor final
    best = min([best_overall] + population, key=lambda s: fitness(s, items, capacidad))
    bins_list = decodificar_bins(best, items)
    return len(bins_list), bins_list, best, history_bins



# ==================== EJECUCION CON SALIDA "AL ESTILO" ====================

if __name__ == "__main__":
    # ---- Tus datos originales ----
    items = [27, 4, 19, 33, 8, 41, 12, 50, 6, 28, 15, 47, 22, 9, 35, 14, 2, 49, 31, 7,
            18, 43, 11, 25, 39, 5, 16, 34, 21, 46, 3, 20, 44, 10, 37, 1, 29, 42, 26, 13,
            48, 17, 32, 24, 40, 30, 23, 45, 36, 38, 11, 7, 28, 2, 49, 16, 33, 41, 12, 22,
            5, 47, 19, 8, 39, 31, 14, 46, 3, 25, 34, 10, 50, 29, 18, 44, 6, 37, 21, 40,
            32, 15, 48, 4, 43, 27, 24, 36, 9, 30]
    capacidad = 50

    # Hiperparametros GA (puedes ajustarlos)
    population_size = 1000
    generations = 500
    mutation_rate = 0.25
    seed = 1

    # ---- Encabezado estilo consola ----
    print("=" * 60)
    print("PROBLEMA DE BIN PACKING (Algoritmo Genetico)")
    print("=" * 60)
    print(f"Capacidad de cada caja: {capacidad}")
    print(f"Lista de objetos: {items}")
    print(f"Suma total: {sum(items)}")
    print("=" * 60)
    print()

    # 1) Minimo teorico
    minimo = minimo_teorico(capacidad, items)
    print("1) MINIMO TEORICO")
    print(f"   Calculo: {sum(items)}/{capacidad} = {sum(items)/capacidad:.2f}")
    print(f"   Minimo teorico: {minimo} cajas")
    print()

    # 2) Algoritmo Genetico (con salida formateada como los heuristicas)
    print("=" * 60)
    print("ALGORITMO GENETICO (BPP)")
    print("=" * 60)
    num_cajas, configuracion, _best_vec, history_bins = genetic_algorithm_bpp(
        items,
        capacidad,
        population_size=population_size,
        generations=generations,
        mutation_rate=mutation_rate,
        seed=seed,
    )
    print(f"   Numero de cajas: {num_cajas}")
    print(f"   Configuracion:")
    for i, caja in enumerate(configuracion, 1):
        print(f"      Caja {i}: {caja} (suma: {sum(caja)})")
    print()
    print("=" * 60)

    # ==================== GRAFICO DE EVOLUCION ====================
    # Se adapta al largo real de history_bins (por si generations cambia)
    x = list(range(1, len(history_bins) + 1))

    plt.figure()
    plt.plot(x, history_bins, marker="o", linewidth=1)
    plt.axhline(minimo, linestyle="--", label=f"Minimo teorico = {minimo}")

    # Limites y ticks dinamicos
    plt.xlim(1, len(x))
    if x:
        ymin, ymax = min(history_bins), max(history_bins)
        if ymin == ymax:
            ymin -= 1
            ymax += 1
        plt.ylim(ymin - 0.5, ymax + 0.5)

    # Paso de ticks en X segun cantidad de generaciones
    if len(x) <= 15:
        xticks = x
    else:
        step = max(1, len(x) // 10)
        xticks = list(range(1, len(x) + 1, step))
        if xticks[-1] != len(x):
            xticks.append(len(x))
    plt.xticks(xticks)

    plt.title("Evolucion del numero de bins (mejor por generacion)")
    plt.xlabel("Generacion")
    plt.ylabel("Numero de bins")
    plt.grid(True)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.show()

