import math
from typing import List, Tuple

def minimo_teorico(capacidad: int, lista_de_objetos: List[int]) -> int:
    """
    Calcula el mínimo teórico de cajas necesarias.
    
    Args:
        capacidad: Capacidad máxima de cada caja
        lista_de_objetos: Lista con los tamaños de los objetos
    
    Returns:
        Número mínimo teórico de cajas (redondeado hacia arriba)
    """
    suma_total = sum(lista_de_objetos)
    minimo = math.ceil(suma_total / capacidad)
    return minimo


def resultado_optimo(capacidad: int, lista_de_objetos: List[int]) -> Tuple[int, List[List[int]]]:
    """
    Utiliza Branch and Bound para encontrar el número óptimo de cajas.
    
    Args:
        capacidad: Capacidad máxima de cada caja
        lista_de_objetos: Lista con los tamaños de los objetos
    
    Returns:
        Tupla con (número_mínimo_de_cajas, configuración_de_cajas)
    """
    n = len(lista_de_objetos)
    
    # Mejor solución encontrada
    mejor_num_cajas = float('inf')
    mejor_cajas = []
    
    def calcular_lower_bound(num_cajas_usadas, peso_restante):
        """Calcula una cota inferior del número de cajas necesarias"""
        return max(num_cajas_usadas, math.ceil(peso_restante / capacidad))
    
    def branch_and_bound(indice, cajas_actuales, peso_restante):
        nonlocal mejor_num_cajas, mejor_cajas
        
        # Caso base: todos los objetos han sido asignados
        if indice == n:
            num_cajas = len(cajas_actuales)
            if num_cajas < mejor_num_cajas:
                mejor_num_cajas = num_cajas
                mejor_cajas = [caja[:] for caja in cajas_actuales]
            return
        
        # Poda: calcular cota inferior
        lower_bound = calcular_lower_bound(len(cajas_actuales), peso_restante)
        if lower_bound >= mejor_num_cajas:
            return
        
        peso_objeto = lista_de_objetos[indice]
        nuevo_peso_restante = peso_restante - peso_objeto
        
        # Intentar colocar el objeto en cada caja existente
        for i, caja in enumerate(cajas_actuales):
            peso_caja = sum(caja)
            if peso_caja + peso_objeto <= capacidad:
                caja.append(peso_objeto)
                branch_and_bound(indice + 1, cajas_actuales, nuevo_peso_restante)
                caja.pop()
        
        # Intentar colocar el objeto en una nueva caja
        if len(cajas_actuales) < mejor_num_cajas - 1:
            cajas_actuales.append([peso_objeto])
            branch_and_bound(indice + 1, cajas_actuales, nuevo_peso_restante)
            cajas_actuales.pop()
    
    # Calcular peso total para la cota inferior
    peso_total = sum(lista_de_objetos)
    
    # Iniciar el algoritmo
    branch_and_bound(0, [], peso_total)
    
    return mejor_num_cajas, mejor_cajas


# ==================== ALGORITMOS HEURÍSTICOS ====================

def next_fit(capacidad: int, lista_de_objetos: List[int]) -> Tuple[int, List[List[int]]]:
    """
    Next Fit: Coloca cada objeto en la caja actual si cabe, 
    si no cabe abre una nueva caja.
    
    Args:
        capacidad: Capacidad máxima de cada caja
        lista_de_objetos: Lista con los tamaños de los objetos
    
    Returns:
        Tupla con (número_de_cajas, configuración_de_cajas)
    """
    if not lista_de_objetos:
        return 0, []
    
    cajas = [[lista_de_objetos[0]]]
    
    for objeto in lista_de_objetos[1:]:
        # Intentar colocar en la caja actual (la última)
        if sum(cajas[-1]) + objeto <= capacidad:
            cajas[-1].append(objeto)
        else:
            # Abrir una nueva caja
            cajas.append([objeto])
    
    return len(cajas), cajas


def first_fit(capacidad: int, lista_de_objetos: List[int]) -> Tuple[int, List[List[int]]]:
    """
    First Fit: Coloca cada objeto en la primera caja donde quepa.
    Si no cabe en ninguna, abre una nueva caja.
    
    Args:
        capacidad: Capacidad máxima de cada caja
        lista_de_objetos: Lista con los tamaños de los objetos
    
    Returns:
        Tupla con (número_de_cajas, configuración_de_cajas)
    """
    if not lista_de_objetos:
        return 0, []
    
    cajas = []
    
    for objeto in lista_de_objetos:
        colocado = False
        
        # Buscar la primera caja donde quepa
        for caja in cajas:
            if sum(caja) + objeto <= capacidad:
                caja.append(objeto)
                colocado = True
                break
        
        # Si no cabe en ninguna, abrir nueva caja
        if not colocado:
            cajas.append([objeto])
    
    return len(cajas), cajas


def best_fit(capacidad: int, lista_de_objetos: List[int]) -> Tuple[int, List[List[int]]]:
    """
    Best Fit: Coloca cada objeto en la caja con menor espacio restante
    donde quepa. Si no cabe en ninguna, abre una nueva caja.
    
    Args:
        capacidad: Capacidad máxima de cada caja
        lista_de_objetos: Lista con los tamaños de los objetos
    
    Returns:
        Tupla con (número_de_cajas, configuración_de_cajas)
    """
    if not lista_de_objetos:
        return 0, []
    
    cajas = []
    
    for objeto in lista_de_objetos:
        mejor_caja = -1
        menor_espacio = capacidad + 1
        
        # Buscar la caja con menor espacio restante donde quepa
        for i, caja in enumerate(cajas):
            peso_actual = sum(caja)
            espacio_restante = capacidad - peso_actual
            
            if objeto <= espacio_restante < menor_espacio:
                mejor_caja = i
                menor_espacio = espacio_restante
        
        # Si encontró una caja adecuada
        if mejor_caja != -1:
            cajas[mejor_caja].append(objeto)
        else:
            # Abrir nueva caja
            cajas.append([objeto])
    
    return len(cajas), cajas


def first_fit_decreasing(capacidad: int, lista_de_objetos: List[int]) -> Tuple[int, List[List[int]]]:
    """
    First Fit Decreasing: Ordena los objetos de mayor a menor y 
    aplica First Fit.
    
    Args:
        capacidad: Capacidad máxima de cada caja
        lista_de_objetos: Lista con los tamaños de los objetos
    
    Returns:
        Tupla con (número_de_cajas, configuración_de_cajas)
    """
    # Ordenar objetos de mayor a menor
    objetos_ordenados = sorted(lista_de_objetos, reverse=True)
    
    # Aplicar First Fit sobre la lista ordenada
    return first_fit(capacidad, objetos_ordenados)


def best_fit_decreasing(capacidad: int, lista_de_objetos: List[int]) -> Tuple[int, List[List[int]]]:
    """
    Best Fit Decreasing: Ordena los objetos de mayor a menor y 
    aplica Best Fit.
    
    Args:
        capacidad: Capacidad máxima de cada caja
        lista_de_objetos: Lista con los tamaños de los objetos
    
    Returns:
        Tupla con (número_de_cajas, configuración_de_cajas)
    """
    # Ordenar objetos de mayor a menor
    objetos_ordenados = sorted(lista_de_objetos, reverse=True)
    
    # Aplicar Best Fit sobre la lista ordenada
    return best_fit(capacidad, objetos_ordenados)


# Ejemplo de uso
if __name__ == "__main__":
    capacidad = 50
    lista_de_objetos = [27, 4, 19, 33, 8, 41, 12, 50, 6, 28, 15, 47, 22, 9, 35, 14, 2, 49, 31, 7,
                        18, 43, 11, 25, 39, 5, 16, 34, 21, 46, 3, 20, 44, 10, 37, 1, 29, 42, 26, 13,
                        48, 17, 32, 24, 40, 30, 23, 45, 36, 38, 11, 7, 28, 2, 49, 16, 33, 41, 12, 22,
                        5, 47, 19, 8, 39, 31, 14, 46, 3, 25, 34, 10, 50, 29, 18, 44, 6, 37, 21, 40,
                        32, 15, 48, 4, 43, 27, 24, 36, 9, 30]
    
    print("=" * 60)
    print("PROBLEMA DE BIN PACKING")
    print("=" * 60)
    print(f"Capacidad de cada caja: {capacidad}")
    print(f"Lista de objetos: {lista_de_objetos}")
    print(f"Suma total: {sum(lista_de_objetos)}")
    print("=" * 60)
    print()
    
    # Método 1: Mínimo teórico
    minimo = minimo_teorico(capacidad, lista_de_objetos)
    print(f"1) MINIMO TEORICO")
    print(f"   Calculo: {sum(lista_de_objetos)}/{capacidad} = {sum(lista_de_objetos)/capacidad:.2f}")
    print(f"   Minimo teorico: {minimo} cajas")
    print()
    '''
    # Método 2: Resultado óptimo (Branch and Bound)
    print("2) RESULTADO OPTIMO (Branch and Bound)")
    num_cajas, configuracion = resultado_optimo(capacidad, lista_de_objetos)
    print(f"   Número mínimo de cajas: {num_cajas}")
    print(f"   Configuración:")
    for i, caja in enumerate(configuracion, 1):
        print(f"      Caja {i}: {caja} (suma: {sum(caja)})")
    print()
    '''
    print("=" * 60)
    print("ALGORITMOS HEURISTICOS")
    print("=" * 60)
    print()
    
    # Método 3: Next Fit
    print("3) NEXT FIT (VORAZ)")
    num_cajas, configuracion = next_fit(capacidad, lista_de_objetos)
    print(f"   Numero de cajas: {num_cajas}")
    print(f"   Configuracion:")
    for i, caja in enumerate(configuracion, 1):
        print(f"      Caja {i}: {caja} (suma: {sum(caja)})")
    print()
    
    # Método 4: First Fit
    print("4) FIRST FIT")
    num_cajas, configuracion = first_fit(capacidad, lista_de_objetos)
    print(f"   Numero de cajas: {num_cajas}")
    print(f"   Configuracion:")
    for i, caja in enumerate(configuracion, 1):
        print(f"      Caja {i}: {caja} (suma: {sum(caja)})")
    print()
    
    # Método 5: Best Fit
    print("5) BEST FIT")
    num_cajas, configuracion = best_fit(capacidad, lista_de_objetos)
    print(f"   Número de cajas: {num_cajas}")
    print(f"   Configuración:")
    for i, caja in enumerate(configuracion, 1):
        print(f"      Caja {i}: {caja} (suma: {sum(caja)})")
    print()
    
    # Método 6: First Fit Decreasing
    print("6) FIRST FIT DECREASING")
    num_cajas, configuracion = first_fit_decreasing(capacidad, lista_de_objetos)
    print(f"   Numero de cajas: {num_cajas}")
    print(f"   Configuracion:")
    for i, caja in enumerate(configuracion, 1):
        print(f"      Caja {i}: {caja} (suma: {sum(caja)})")
    print()
    
    # Método 7: Best Fit Decreasing
    print("7) BEST FIT DECREASING")
    num_cajas, configuracion = best_fit_decreasing(capacidad, lista_de_objetos)
    print(f"   Número de cajas: {num_cajas}")
    print(f"   Configuración:")
    for i, caja in enumerate(configuracion, 1):
        print(f"      Caja {i}: {caja} (suma: {sum(caja)})")
    print()
    
    print("=" * 60)