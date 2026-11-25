#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ЛР 6. Линейный, бинарный и интерполяционный поиск — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-06 и правилами использования генеративного ИИ
(docs/ai-verification.md).

Каждая функция поиска работает с отсортированным по неубыванию массивом
и возвращает пару (индекс найденного элемента или -1, число сравнений ключей).

Запуск: python lab06-search-starter.py --variant N
"""
from __future__ import annotations

import argparse
import bisect
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Алгоритмы поиска (реализуются вручную, без in/index/bisect в основной части)
# ---------------------------------------------------------------------------


def linear_search(a: list[int], key: int) -> tuple[int, int]:
    """Линейный поиск первого вхождения key.

    Возвращает (индекс первого вхождения или -1, число сравнений ключей).
    Ожидаемая сложность: TODO (обосновать в отчёте).
    """
    comparisons = 0
    for i, val in enumerate(a):
        comparisons += 1
        if val == key:
            return i, comparisons
    return -1, comparisons


def binary_search(a: list[int], key: int) -> tuple[int, int]:
    """Бинарный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений ключей).
    Аккуратно поддерживайте инвариант обеих границ lo и hi: искомый элемент,
    если он есть, всегда лежит в текущем отрезке; цикл обязан завершаться.
    Ожидаемая сложность: TODO.
    """
    lo, hi = 0, len(a) - 1
    comparisons = 0
    while lo <= hi:
        comparisons += 1
        mid = lo + (hi - lo) // 2
        if a[mid] == key:
            return mid, comparisons
        elif a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, comparisons

def interpolation_search(a: list[int], key: int) -> tuple[int, int]:
    """Интерполяционный поиск key в отсортированном массиве.

    Возвращает (индекс любого вхождения или -1, число сравнений ключей).
    Позиция зонда: mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo]).
    Обязательно защититься от деления на ноль при a[hi] == a[lo] и от выхода
    key за пределы [a[lo], a[hi]]. Средняя сложность на равномерных данных: TODO.
    """
    lo, hi = 0, len(a) - 1
    comparisons = 0
    while lo <= hi:
        comparisons += 1
        if key < a[lo]:
            return -1, comparisons
        comparisons += 1
        if key > a[hi]:
            return -1, comparisons
        if a[lo] == a[hi]:
            comparisons += 1
            if a[lo] == key:
                return lo, comparisons
            return -1, comparisons
        mid = lo + (key - a[lo]) * (hi - lo) // (a[hi] - a[lo])

        comparisons += 1
        if a[mid] == key:
            return mid, comparisons
        elif a[mid] < key:
            lo = mid + 1
        else:
            hi = mid - 1

    return -1, comparisons


# ---------------------------------------------------------------------------
# 2. Данные по варианту: два распределения, присутствующие/отсутствующие ключи
# ---------------------------------------------------------------------------


def make_dataset(n: int, distribution: str, rng: random.Random) -> list[int]:
    """Отсортированный массив n ключей: 'uniform' — равномерное распределение,
    'exponential' — неравномерное (экспоненциальное, значения сгущаются у нуля)."""
    if distribution == "uniform":
        return sorted(rng.randint(0, 10 * n) for _ in range(n))
    if distribution == "exponential":
        return sorted(int(rng.expovariate(1.0 / 1000.0)) for _ in range(n))
    raise ValueError(f"неизвестное распределение: {distribution!r}")


def pick_keys(a: list[int], rng: random.Random, count: int,
              present: bool) -> list[int]:
    """count ключей для серии поисков: присутствующие берутся из массива,
    отсутствующие подбираются вне множества его значений."""
    if present:
        return [a[rng.randrange(len(a))] for _ in range(count)]
    have = set(a)
    hi = (a[-1] if a else 0) + 2
    keys: list[int] = []
    while len(keys) < count:
        k = rng.randint(-hi, hi)
        if k not in have:
            keys.append(k)
    return keys


# ---------------------------------------------------------------------------
# 3. Репрезентативные тесты и инварианты (шаги 1–3 методики верификации)
# ---------------------------------------------------------------------------

ALGORITHMS = [
    ("linear", linear_search),
    ("binary", binary_search),
    ("interpolation", interpolation_search),
]


def self_check() -> None:
    """Граничные случаи + сверка с эталоном (оператор in, list.index, bisect)."""
    for name, fn in ALGORITHMS:
        # Пустой массив: элемент не найден, сравнений нет.
        assert fn([], 1) == (-1, 0), f"{name}: пустой массив"
        # Один элемент: найден / не найден.
        assert fn([7], 7)[0] == 0, f"{name}: один элемент, ключ найден"
        assert fn([7], 3)[0] == -1, f"{name}: один элемент, ключ отсутствует"
        # Первый, последний и отсутствующие ключи (внутри и вне диапазона).
        a = [1, 3, 3, 5, 8, 13, 21]
        assert fn(a, 1)[0] == 0, f"{name}: первый элемент"
        assert fn(a, 21)[0] == len(a) - 1, f"{name}: последний элемент"
        assert fn(a, 4)[0] == -1, f"{name}: отсутствующий ключ внутри диапазона"
        assert fn(a, 100)[0] == -1, f"{name}: ключ вне диапазона"

    # Сверка с эталоном стандартной библиотеки на случайных массивах.
    rng = random.Random(0)
    for _ in range(300):
        a = sorted(rng.randint(0, 60) for _ in range(rng.randint(1, 40)))
        key = rng.randint(-5, 65)
        # Эталон присутствия ключа — bisect_left (и, эквивалентно, оператор in).
        j = bisect.bisect_left(a, key)
        present = j < len(a) and a[j] == key
        assert present == (key in a)
        for name, fn in ALGORITHMS:
            idx, cmp_count = fn(a, key)
            assert cmp_count >= 1, f"{name}: счётчик сравнений не ведётся"
            if present:
                # При дубликатах бинарный/интерполяционный могут вернуть
                # любое вхождение — проверяем значение по индексу.
                assert idx != -1 and a[idx] == key, f"{name}: ключ не найден"
            else:
                assert idx == -1, f"{name}: найден отсутствующий ключ"
        # Линейный поиск обязан возвращать первое вхождение — эталон list.index.
        if present:
            assert linear_search(a, key)[0] == a.index(key)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Бенчмарк: сравнения и время от n (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [1_000, 3_000, 10_000, 30_000, 100_000]
REPEATS = 5      # число повторов серии замеров (берётся медиана)
N_KEYS = 200     # число ключей в одной серии поисков


def bench(fn, a: list[int], keys: list[int]) -> float:
    """Медиана времени одной серии поисков по REPEATS запускам, с прогревом."""
    for k in keys:  # прогрев — не учитывается
        fn(a, k)
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        for k in keys:
            fn(a, k)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def mean_comparisons(fn, a: list[int], keys: list[int]) -> float:
    """Среднее число сравнений ключей на один поиск."""
    return statistics.mean(fn(a, k)[1] for k in keys)


def run_benchmarks(seed: int) -> None:
    rng = random.Random(seed)
    for distribution in ("uniform", "exponential"):
        print(f"\nРаспределение: {distribution}")
        for n in SIZES:
            a = make_dataset(n, distribution, rng)
            for present in (True, False):
                keys = pick_keys(a, rng, N_KEYS, present)
                label = "есть" if present else "нет"
                for name, fn in ALGORITHMS:
                    if name == "linear" and n > 30_000:
                        continue  # линейный поиск: большие n занимают минуты
                    print(f"  n={n:>7}  ключ {label:<4}  {name:<13}"
                          f"  сравнений={mean_comparisons(fn, a, keys):>10.1f}"
                          f"  t={bench(fn, a, keys):.6f} c")
    # TODO: построить графики «среднее число сравнений от n» и «время от n»
    # TODO: (matplotlib, отдельно для каждого распределения) и включить в отчёт;
    # TODO: объяснить, когда интерполяционный поиск превосходит бинарный
    # TODO: и на каких данных он деградирует к O(n).


def plot_benchmarks(seed: int) -> None:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — графики не построены")
        return

    rng = random.Random(seed)
    distributions = ["uniform", "exponential"]

    for dist in distributions:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        data = {
            "bin_pres": {"sizes": [], "comps": [], "times": []},
            "bin_abs": {"sizes": [], "comps": [], "times": []},
            "int_pres": {"sizes": [], "comps": [], "times": []},
            "int_abs": {"sizes": [], "comps": [], "times": []},
            "lin_pres": {"sizes": [], "comps": [], "times": []},
            "lin_abs": {"sizes": [], "comps": [], "times": []},
        }

        for n in SIZES:
            a = make_dataset(n, dist, rng)
            for present in (True, False):
                keys = pick_keys(a, rng, N_KEYS, present)
                suffix = "pres" if present else "abs"

                data[f"bin_{suffix}"]["sizes"].append(n)
                data[f"int_{suffix}"]["sizes"].append(n)

                data[f"bin_{suffix}"]["comps"].append(mean_comparisons(binary_search, a, keys))
                data[f"bin_{suffix}"]["times"].append(bench(binary_search, a, keys))

                data[f"int_{suffix}"]["comps"].append(mean_comparisons(interpolation_search, a, keys))
                data[f"int_{suffix}"]["times"].append(bench(interpolation_search, a, keys))

                if n <= 30_000:
                    data[f"lin_{suffix}"]["sizes"].append(n)
                    data[f"lin_{suffix}"]["comps"].append(mean_comparisons(linear_search, a, keys))
                    data[f"lin_{suffix}"]["times"].append(bench(linear_search, a, keys))

        # График сравнений
        for suffix, label, style in [("pres", "Ключ есть", "-o"), ("abs", "Ключа нет", "--s")]:
            ax1.plot(data[f"bin_{suffix}"]["sizes"], data[f"bin_{suffix}"]["comps"], style, label=f"Бинарный ({label})")
            ax1.plot(data[f"int_{suffix}"]["sizes"], data[f"int_{suffix}"]["comps"], style,
                     label=f"Интерполяционный ({label})")
            if data[f"lin_{suffix}"]["sizes"]:
                ax1.plot(data[f"lin_{suffix}"]["sizes"], data[f"lin_{suffix}"]["comps"], style,
                         label=f"Линейный ({label})")

        ax1.set_xlabel("n (размер массива)")
        ax1.set_ylabel("Среднее число сравнений")
        ax1.set_title(f"Число сравнений: {dist}")
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # График времени
        for suffix, label, style in [("pres", "Ключ есть", "-o"), ("abs", "Ключа нет", "--s")]:
            ax2.plot(data[f"bin_{suffix}"]["sizes"], data[f"bin_{suffix}"]["times"], style, label=f"Бинарный ({label})")
            ax2.plot(data[f"int_{suffix}"]["sizes"], data[f"int_{suffix}"]["times"], style,
                     label=f"Интерполяционный ({label})")
            if data[f"lin_{suffix}"]["sizes"]:
                ax2.plot(data[f"lin_{suffix}"]["sizes"], data[f"lin_{suffix}"]["times"], style,
                         label=f"Линейный ({label})")

        ax2.set_xlabel("n (размер массива)")
        ax2.set_ylabel("Время, с")
        ax2.set_title(f"Время поиска: {dist}")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(f"lab06_search_{dist}.png", dpi=150)
        print(f"Графики для {dist} сохранены: lab06_search_{dist}.png")


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


