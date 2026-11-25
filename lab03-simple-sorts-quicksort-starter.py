#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 3. Простые сортировки и QuickSort с рандомизацией — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-03 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Запуск: python lab03-simple-sorts-quicksort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Простые сортировки со счётчиками (сортируют КОПИЮ входа, вход не меняют)
#    Каждая функция возвращает кортеж: (отсортированный список,
#    число сравнений ключей, число обменов/перемещений элементов).
# ---------------------------------------------------------------------------


def bubble_sort(a: list) -> tuple[list, int, int]:
    a = list(a)
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            comparisons += 1
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swaps += 1
                swapped = True
        if not swapped:
            break
    return a, comparisons, swaps



def insertion_sort(a: list) -> tuple[list, int, int]:
    a = list(a)
    n = len(a)
    comparisons = 0
    shifts = 0
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0:
            comparisons += 1
            if a[j] > key:
                a[j + 1] = a[j]
                shifts += 1
                j -= 1
            else:
                break
        a[j + 1] = key
        if j + 1 != i:
            shifts += 1
    return a, comparisons, shifts




def selection_sort(a: list) -> tuple[list, int, int]:
    a = list(a)
    n = len(a)
    comparisons = 0
    swaps = 0
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            comparisons += 1
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            swaps += 1
    return a, comparisons, swaps



# ---------------------------------------------------------------------------
# 2. QuickSort с рандомизированным опорным элементом
# ---------------------------------------------------------------------------


def quick_sort(a: list, rng: random.Random | None = None) -> list:
    if rng is None:
        rng = random.Random()
    a = list(a)
    def _qs(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        pivot_idx = rng.randrange(lo, hi)
        a[lo], a[pivot_idx] = a[pivot_idx], a[lo]
        pivot = a[lo]
        i = lo
        for j in range(lo + 1, hi):
            if a[j] < pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[lo], a[i] = a[i], a[lo]
        _qs(lo, i)
        _qs(i + 1, hi)
    _qs(0, len(a))
    return a




# ---------------------------------------------------------------------------
# 3. Демонстрация стабильности на парах (ключ, метка)
# ---------------------------------------------------------------------------


def stability_demo() -> None:
    pairs = [(2, "a"), (1, "b"), (2, "c"), (1, "d")]
    print("Исходный массив пар:", pairs)
    print("  При ключе 1 исходный порядок меток: b, d")
    print("  При ключе 2 исходный порядок меток: a, c")
    print()

    a = list(pairs)
    n = len(a)
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            if a[j][0] > a[j + 1][0]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
        if not swapped:
            break
    print(f"bubble_sort:     {a}")
    print(f"  метки при ключе 1: {[p[1] for p in a if p[0]==1]}")
    print(f"  метки при ключе 2: {[p[1] for p in a if p[0]==2]}")

    a = list(pairs)
    n = len(a)
    for i in range(1, n):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j][0] > key[0]:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    print(f"insertion_sort:  {a}")
    print(f"  метки при ключе 1: {[p[1] for p in a if p[0]==1]}")
    print(f"  метки при ключе 2: {[p[1] for p in a if p[0]==2]}")

    a = list(pairs)
    n = len(a)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if a[j][0] < a[min_idx][0]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
    print(f"selection_sort:  {a}")
    print(f"  метки при ключе 1: {[p[1] for p in a if p[0]==1]}")
    print(f"  метки при ключе 2: {[p[1] for p in a if p[0]==2]}")

    a = list(pairs)
    rng = random.Random(0)
    def _qs(lo, hi):
        if lo >= hi:
            return
        pivot_idx = rng.randrange(lo, hi)
        a[lo], a[pivot_idx] = a[pivot_idx], a[lo]
        pivot = a[lo][0]
        i = lo
        for j in range(lo + 1, hi):
            if a[j][0] < pivot:
                i += 1
                a[i], a[j] = a[j], a[i]
        a[lo], a[i] = a[i], a[lo]
        _qs(lo, i)
        _qs(i + 1, hi)
    _qs(0, len(a))
    print(f"quick_sort:      {a}")
    print(f"  метки при ключе 1: {[p[1] for p in a if p[0]==1]}")
    print(f"  метки при ключе 2: {[p[1] for p in a if p[0]==2]}")

    print()
    print("Вывод: bubble_sort и insertion_sort — СТАБИЛЬНЫ (метки сохраняют исходный порядок).")
    print("       selection_sort и quick_sort — НЕСТАБИЛЬНЫ (порядок меток меняется).")



# ---------------------------------------------------------------------------
# 4. Классы входов (данные по варианту, детерминированно по seed)
# ---------------------------------------------------------------------------


def make_inputs(n: int, seed: int) -> dict[str, list[int]]:
    """Три класса входов размера n: упорядоченный, случайный, обратный."""
    rng = random.Random(seed + n)  # свой поток для каждого размера
    data = [rng.randint(-1_000_000, 1_000_000) for _ in range(n)]
    return {
        "упорядоченный": sorted(data),
        "случайный": data,
        "обратный": sorted(data, reverse=True),
    }


# ---------------------------------------------------------------------------
# 5. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------

ALGORITHMS = {
    "bubble_sort": lambda a: bubble_sort(a)[0],
    "insertion_sort": lambda a: insertion_sort(a)[0],
    "selection_sort": lambda a: selection_sort(a)[0],
    "quick_sort": lambda a: quick_sort(a, random.Random(0)),
}


def is_sorted(a: list) -> bool:
    """Инвариант 1: неубывающий порядок элементов."""
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))


def self_check() -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [5, 5, 5, 5],          # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for name, fn in ALGORITHMS.items():
        for a in boundary:
            res = fn(list(a))
            assert is_sorted(res), f"{name}: нарушен порядок на {a}"
            assert sorted(res) == sorted(a), f"{name}: не перестановка входа {a}"

    # Сверка с эталоном из стандартной библиотеки на сотнях случайных входов.
    rng = random.Random(0)
    for _ in range(300):
        a = [rng.randint(-100, 100) for _ in range(rng.randint(0, 80))]
        expected = sorted(a)
        for name, fn in ALGORITHMS.items():
            assert fn(list(a)) == expected, f"{name}: расходится с sorted() на {a}"

    # Счётчики: у сортировки выбором ровно n*(n-1)/2 сравнений на любом входе.
    _, comparisons, _ = selection_sort([3, 1, 2, 5, 4])
    assert comparisons == 10, "selection_sort: неверный счётчик сравнений"
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 6. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES_QUADRATIC = [500, 1_000, 2_000, 4_000, 8_000]     # для простых сортировок
SIZES_QUICK = [1_000, 3_000, 10_000, 30_000, 100_000]   # для QuickSort
REPEATS = 5


def bench(fn, data: list) -> float:
    """Медиана времени выполнения fn(копия data) по REPEATS запускам, с прогревом."""
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        arg = list(data)  # свежая копия: сортировка не должна получать свой результат
        t0 = time.perf_counter()
        fn(arg)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры всех алгоритмов на трёх классах входов; результат — таблица в stdout."""
    plans = [
        ("bubble_sort", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion_sort", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection_sort", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick_sort", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    for name, fn, sizes in plans:
        print(f"\n{name}:")
        for n in sizes:
            for cls, data in make_inputs(n, seed).items():
                print(f"  n={n:>7}  вход={cls:<13} t={bench(fn, data):.6f} c")


def plot_benchmarks(seed: int) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — графики не построены")
        return

    plans = [
        ("bubble", ALGORITHMS["bubble_sort"], SIZES_QUADRATIC),
        ("insertion", ALGORITHMS["insertion_sort"], SIZES_QUADRATIC),
        ("selection", ALGORITHMS["selection_sort"], SIZES_QUADRATIC),
        ("quick", lambda a: quick_sort(a, random.Random(seed)), SIZES_QUICK),
    ]
    class_names = ["упорядоченный", "случайный", "обратный"]
    colors = ["blue", "green", "red"]

    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    for cls_idx, cls in enumerate(class_names):
        ax = axes[cls_idx]
        for (name, fn, sizes), color in zip(plans, ["blue", "orange", "green", "red"]):
            times = []
            for n in sizes:
                data = make_inputs(n, seed)[cls]
                t = bench(fn, data)
                times.append(t)
            ax.loglog(sizes, times, marker='o', label=name, color=color)
        ax.set_xlabel("n (размер входа)")
        ax.set_ylabel("время, с")
        ax.set_title(f"Вход: {cls}")
        ax.legend()
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig("lab03_sorts.png", dpi=150)
    print("График сохранён: lab03_sorts.png")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    stability_demo()
    run_benchmarks(seed)
    plot_benchmarks(seed)


if __name__ == "__main__":
    main()


