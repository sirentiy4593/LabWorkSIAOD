#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 4. MergeSort, Counting, Radix и HeapSort: оценка производительности — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-04 и правилами использования генеративного ИИ
(docs/ai-verification.md). QuickSort перенесите из собственной ЛР 3.

Запуск: python lab04-mergesort-linear-heapsort-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import sys
import time
import traceback

# ---------------------------------------------------------------------------
# 1. Сортировки (реализуются вручную; sorted() используется только как эталон)
# ---------------------------------------------------------------------------


def merge(left: list, right: list, key) -> list:
    """Стабильное слияние двух отсортированных списков в новый список."""
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def merge_sort(a: list, key=lambda x: x) -> list:
    """MergeSort: возвращает новый отсортированный список. Сложность: O(n log n)."""
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid], key)
    right = merge_sort(a[mid:], key)
    return merge(left, right, key)


def counting_sort(a: list[int], key_max: int) -> list[int]:
    """Устойчивая сортировка подсчётом. Сложность и память: O(n + k), где k = key_max + 1."""
    if not a:
        return []
    k = key_max + 1
    count = [0] * k
    for x in a:
        count[x] += 1
    for i in range(1, k):
        count[i] += count[i - 1]
    output = [0] * len(a)
    for x in reversed(a):
        count[x] -= 1
        output[count[x]] = x
    return output


def radix_sort_lsd(a: list[int]) -> list[int]:
    """RadixSort LSD по десятичным разрядам. Сложность: O(d * (n + 10)), d - число разрядов."""
    if not a:
        return []
    max_val = max(a)
    exp = 1
    while max_val // exp > 0:
        count = [0] * 10
        output = [0] * len(a)
        for x in a:
            digit = (x // exp) % 10
            count[digit] += 1
        for i in range(1, 10):
            count[i] += count[i - 1]
        for x in reversed(a):
            digit = (x // exp) % 10
            count[digit] -= 1
            output[count[digit]] = x
        a = output
        exp *= 10
    return a


def sift_down(a: list[int], i: int, n: int) -> None:
    """Просейка вниз элемента i в куче a[0:n] (max-heap), на месте. Сложность: O(log n)."""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n and a[left] > a[largest]:
            largest = left
        if right < n and a[right] > a[largest]:
            largest = right
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            i = largest
        else:
            break


def heap_sort(a: list[int]) -> None:
    """HeapSort in-place. Сложность: O(n log n), дополнительная память: O(1)."""
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    for i in range(n - 1, 0, -1):
        a[0], a[i] = a[i], a[0]
        sift_down(a, 0, i)


def quick_sort(a: list[int]) -> list[int]:
    """QuickSort с рандомизацией и сортировкой вставками для малых подмассивов (из ЛР 3)."""
    rng = random.Random(0)

    def insertion_sort_small(arr: list, lo: int, hi: int) -> None:
        for i in range(lo + 1, hi):
            key = arr[i]
            j = i - 1
            while j >= lo and arr[j] > key:
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key

    def _qs(lo: int, hi: int) -> None:
        while lo < hi:
            if hi - lo < 16:
                insertion_sort_small(a, lo, hi)
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
            if i - lo < hi - i - 1:
                _qs(lo, i)
                lo = i + 1
            else:
                _qs(i + 1, hi)
                hi = i

    a = list(a)
    _qs(0, len(a))
    return a


# ---------------------------------------------------------------------------
# 2. Верификация: инварианты + сверка с эталоном sorted()
#    (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


class SelfCheckError(Exception):
    """Нарушен контракт или инвариант реализации."""


def expect(condition: bool, message: str) -> None:
    """Явная проверка вместо assert: assert-ы исчезают при запуске python -O."""
    if not condition:
        raise SelfCheckError(message)


def heap_sorted(a: list[int]) -> list[int]:
    """heap_sort сортирует на месте: проверяется тот список, который ему передали."""
    buf = list(a)
    heap_sort(buf)
    return buf


# Каждая функция возвращает отсортированный список; ключи — целые из [0, 999].
SORTS = {
    "merge_sort": lambda a: merge_sort(a),
    "counting_sort": lambda a: counting_sort(a, key_max=999),
    "radix_sort_lsd": lambda a: radix_sort_lsd(a),
    "heap_sort": lambda a: heap_sorted(a),
    "quick_sort": lambda a: quick_sort(a),
}


def check_sort(fn) -> None:
    """Граничные случаи, инварианты сортировки и сверка с эталоном sorted()."""
    boundary = [
        [],                    # пустой массив
        [7],                   # один элемент
        [0],                   # нулевой ключ
        [5, 5, 5],             # все элементы равны
        [1, 2, 3, 4, 5],       # уже отсортирован
        [5, 4, 3, 2, 1],       # обратный порядок
    ]
    for a in boundary:
        res = fn(list(a))
        expect(isinstance(res, list), f"на {a} возвращён {type(res).__name__}, а не список")
        expect(res == sorted(a), f"на {a} получено {res}, ожидалось {sorted(a)}")

    # Случайные тесты: инвариант перестановки + сверка с эталоном
    rng = random.Random(0)
    for _ in range(200):
        a = [rng.randint(0, 999) for _ in range(rng.randint(0, 60))]
        res = fn(list(a))
        expect(sorted(res) == sorted(a), f"не перестановка входа {a}: получено {res}")
        expect(res == sorted(a), f"расходится с sorted() на {a}: получено {res}")


def check_merge_stability() -> None:
    """Стабильность слияния на парах (ключ, порядковый номер): эталон sorted() стабилен,
    поэтому при равных ключах порядок номеров обязан совпасть."""
    rng = random.Random(0)
    pairs = [(rng.randint(0, 5), i) for i in range(100)]
    got = merge_sort(pairs, key=lambda p: p[0])
    expect(got == sorted(pairs, key=lambda p: p[0]),
           "merge_sort нестабилен: при равных ключах нарушен исходный порядок номеров")


def check_custom_properties() -> None:
    """Дополнительная проверка: свойство max-кучи после этапа построения (требование КИМ-04)."""
    test_arr = [3, 1, 4, 1, 5, 9, 2, 6]
    n = len(test_arr)
    # Строим кучу так же, как в heap_sort
    for i in range(n // 2 - 1, -1, -1):
        sift_down(test_arr, i, n)

    # Проверяем инвариант: родитель >= детей
    for i in range(n):
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n:
            expect(test_arr[i] >= test_arr[left],
                   f"Куча нарушена: родитель {test_arr[i]} < левого ребенка {test_arr[left]}")
        if right < n:
            expect(test_arr[i] >= test_arr[right],
                   f"Куча нарушена: родитель {test_arr[i]} < правого ребенка {test_arr[right]}")


def self_check() -> None:
    """Все проверки по разделам; при любой ошибке замеры не выполняются."""
    # fn=fn фиксирует функцию текущего шага цикла (иначе все лямбды увидят последнюю)
    checks = [(name, lambda fn=fn: check_sort(fn)) for name, fn in SORTS.items()]
    checks.append(("стабильность merge_sort", check_merge_stability))
    checks.append(("свойство кучи heap_sort", check_custom_properties))

    failed = 0
    print("self_check:")
    for name, check in checks:
        try:
            check()
        except NotImplementedError as err:
            where = traceback.extract_tb(err.__traceback__)[-1].name
            print(f"  {name}: не реализовано — {where} (TODO)")
            failed += 1
        except SelfCheckError as err:
            print(f"  {name}: ОШИБКА — {err}")
            failed += 1
        except Exception:  # noqa: BLE001 — падение реализации тоже результат проверки
            print(f"  {name}: ИСКЛЮЧЕНИЕ")
            traceback.print_exc(file=sys.stdout)
            failed += 1
        else:
            print(f"  {name}: OK")
    # TODO: добавить собственные проверки (свойство кучи после построения,
    #       устойчивость поразрядного прохода radix) и описать их в отчёте.
    if failed:
        raise SystemExit(f"self_check: не пройдено разделов — {failed}; "
                         f"замеры выполняются только после всех проверок.")
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 3. Бенчмарк (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5
SMALL_KEY_MAX = 100        # узкий диапазон: counting уместен
WIDE_KEY_MAX = 10**9       # широкий диапазон: counting теряет смысл (обсудить в отчёте)


def make_datasets(rng: random.Random, n: int) -> dict[str, list[int]]:
    """Массивы разных распределений и диапазонов ключей для размера n."""
    almost = list(range(n))
    for _ in range(max(1, n // 100)):  # ~1 % случайных обменов
        i, j = rng.randrange(n), rng.randrange(n)
        almost[i], almost[j] = almost[j], almost[i]
    return {
        "random_wide": [rng.randint(0, WIDE_KEY_MAX) for _ in range(n)],
        "random_small": [rng.randint(0, SMALL_KEY_MAX) for _ in range(n)],
        "sorted": list(range(n)),
        "reversed": list(range(n, 0, -1)),
        "almost_sorted": almost,
    }


def bench(fn, data: list[int]) -> float:
    """Медиана времени fn на копии data по REPEATS запускам, с прогревом.

    Каждый запуск получает свежую копию: сортировка на месте не должна
    превращать последующие запуски в сортировку уже отсортированного массива.
    """
    fn(list(data))  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        buf = list(data)
        t0 = time.perf_counter()
        fn(buf)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort (ЛР 3)", quick_sort),
        ("sorted() (эталон)", sorted),
    ]
    for n in SIZES:
        datasets = make_datasets(rng, n)
        print(f"\nn = {n}:")
        for dist_name, data in datasets.items():
            print(f"  распределение {dist_name}:")
            for algo_name, fn in algorithms:
                if algo_name == "counting_sort" and dist_name == "random_wide":
                    # счётчики размера ~10^9 не помещаются в память — граница
                    # применимости counting; зафиксировать в таблице свойств
                    print(f"    {algo_name:>18}: пропуск (диапазон ключей)")
                    continue
                print(f"    {algo_name:>18}: t = {bench(fn, data):.6f} c")
    # TODO: построить log-log графики (matplotlib) по каждому распределению;
    # TODO: заполнить таблицу свойств: время (лучший/средний/худший),
    #       память, стабильность, ограничения — для всех шести сортировок;
    # TODO: объяснить расхождения замеров с асимптотикой в отчёте.


def plot_benchmarks(seed: int) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — графики не построены")
        return

    local_algorithms = [
        ("merge_sort", merge_sort),
        ("counting_sort", lambda a: counting_sort(a, key_max=max(a, default=0))),
        ("radix_sort_lsd", radix_sort_lsd),
        ("heap_sort", heap_sort),
        ("quick_sort", quick_sort),
        ("sorted() (эталон)", sorted),
    ]

    dist_names = ["random_wide", "random_small", "sorted", "reversed", "almost_sorted"]

    fig, axes = plt.subplots(1, len(dist_names), figsize=(20, 4))
    if len(dist_names) == 1:
        axes = [axes]

    for idx, dist_name in enumerate(dist_names):
        ax = axes[idx]
        for algo_name, algo_fn in local_algorithms:
            sizes = []
            times = []
            for n in SIZES:
                rng = random.Random(seed + n)
                datasets = make_datasets(rng, n)
                if dist_name not in datasets:
                    continue
                data = datasets[dist_name]

                if algo_name == "counting_sort" and dist_name == "random_wide":
                    continue

                t = bench(algo_fn, data)
                sizes.append(n)
                times.append(t)

            if sizes:
                ax.loglog(sizes, times, marker='o', label=algo_name)

        ax.set_xlabel("n (размер входа)")
        ax.set_ylabel("время, с")
        ax.set_title(f"Распределение: {dist_name}")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig("lab04_sorts.png", dpi=150)
    print("График сохранён: lab04_sorts.png")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_benchmarks(seed)
    plot_benchmarks(seed)


if __name__ == "__main__":
    main()