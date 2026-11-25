#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 1. Верификация ИИ-сгенерированной сортировки — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-01 (Cases) и методикой верификации по шагам 1–4
(docs/ai-verification.md). Проверяемый код лежит рядом, в dz01-ai-code.py;
исправлять его до завершения верификации запрещено.

Запуск: python dz01-verification-starter.py --variant N
"""
from __future__ import annotations

import argparse
import importlib.util
import random
import statistics
import time
from pathlib import Path
from collections import Counter

# ---------------------------------------------------------------------------
# 0. Загрузка проверяемого кода
# ---------------------------------------------------------------------------
# Имя файла содержит дефисы, поэтому обычный import не подходит —
# модуль загружается по пути через importlib.

AI_CODE_PATH = Path(__file__).with_name("dz01-ai-code.py")


def load_quicksort():
    """Загружает функцию quicksort из соседнего файла dz01-ai-code.py."""
    spec = importlib.util.spec_from_file_location("dz01_ai_code", AI_CODE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.quicksort


quicksort = load_quicksort()

# ---------------------------------------------------------------------------
# 1. Шаг 1 методики: инварианты сортировки
# ---------------------------------------------------------------------------


def is_sorted(a: list[int]) -> bool:
    """Инвариант 1: последовательность упорядочена по неубыванию."""
    for i in range(len(a) - 1):
        if a[i] > a[i + 1]:
            return False
    return True


def same_multiset(a: list[int], b: list[int]) -> bool:
    """Инвариант 2: b — перестановка a (мультимножества элементов совпадают)."""
    return Counter(a) == Counter(b)


def check_invariants(original: list[int], result: list[int]) -> list[str]:
    """Возвращает список нарушенных инвариантов (пустой список — нарушений нет)."""
    violations = []
    if not is_sorted(result):
        violations.append("РЕЗУЛЬТАТ НЕ УПОРЯДОЧЕН")
    if not same_multiset(original, result):
        violations.append("РЕЗУЛЬТАТ НЕ ПЕРЕСТАНОВКА ВХОДА (потеряны элементы)")
    return violations

# ---------------------------------------------------------------------------
# 2. Шаг 2 методики: репрезентативные тесты
# ---------------------------------------------------------------------------


def representative_cases(rng: random.Random) -> list[tuple[str, list[int]]]:
    """Именованные тестовые входы по классам методики.

    Обязательные классы: граничные (пустой, один, два элемента);
    вырожденные (все элементы равны, уже отсортированный, обратно
    отсортированный); типовые случайные с дубликатами и отрицательными
    числами (генерируются через rng — seed по варианту).
    """
    return [
        ("empty", []),
        ("single", [42]),
        ("two_elements", [2, 1]),
        ("two_equal", [5, 5]),
        ("all_equal", [7, 7, 7, 7, 7]),
        ("already_sorted", [1, 2, 3, 4, 5]),
        ("reversed", [5, 4, 3, 2, 1]),
        ("random_with_duplicates", [rng.randint(-5, 5) for _ in range(20)]),
        ("random_with_negatives", [rng.randint(-100, 100) for _ in range(30)]),
    ]


def run_representative_tests(rng: random.Random) -> None:
    """Прогоняет quicksort по всем классам входов и печатает нарушения инвариантов."""
    print("=" * 60)
    print("ШАГ 1-2: Инварианты + репрезентативные тесты")
    print("=" * 60)
    for name, data in representative_cases(rng):
        result = quicksort(list(data))
        violations = check_invariants(data, result)
        if violations:
            print(f"   [{name}] {'; '.join(violations)}")
            print(f"     вход:      {data}")
            print(f"     результат: {result}")
        else:
            print(f"   [{name}] OK")

# ---------------------------------------------------------------------------
# 3. Шаг 3 методики: сравнение с эталоном sorted()
# ---------------------------------------------------------------------------


def compare_with_reference(rng: random.Random, runs: int = 300) -> None:
    """Сверка quicksort с sorted() на сотнях случайных входов.

    Генерируйте входы разных размеров (включая маленькие: именно на них
    удобно локализовать расхождение), обязательно с дубликатами и
    отрицательными числами. Каждое расхождение печатайте вместе со входом,
    чтобы затем свести его к минимальному контрпримеру.
    """
    print("\n" + "=" * 60)
    print("ШАГ 3: Сверка с эталоном sorted()")
    print("=" * 60)
    mismatches = 0
    min_example = None
    for _ in range(runs):
        n = rng.randint(0, 50)
        data = [rng.randint(-20, 20) for _ in range(n)]
        result = quicksort(list(data))
        expected = sorted(data)
        if result != expected:
            mismatches += 1
            if min_example is None or len(data) < len(min_example[0]):
                min_example = (data, result, expected)
    print(f"  Тестов: {runs}, расхождений с sorted(): {mismatches}")
    if min_example is not None:
        data, got, expected = min_example
        print(f"  Минимальный контрпример:")
        print(f"    вход:      {data}")
        print(f"    quicksort: {got}")
        print(f"    sorted():  {expected}")


# ---------------------------------------------------------------------------
# 4. Шаг 4 методики: бенчмарк на трёх классах входов
# (методика — docs/reproducibility.md: прогрев, >=5 повторов, медиана)
# ---------------------------------------------------------------------------

SIZES = [500, 1_000, 2_000, 4_000, 8_000]
REPEATS = 5
INPUT_KINDS = ("random", "sorted", "reversed")


def make_input(rng: random.Random, n: int, kind: str) -> list[int]:
    """Вход размера n одного из трёх классов: random / sorted / reversed."""
    a = [rng.randint(-1000, 1000) for _ in range(n)]
    if kind == "sorted":
        a.sort()
    elif kind == "reversed":
        a.sort(reverse=True)
    return a


def bench(fn, data: list[int]) -> float:
    """Медиана времени выполнения fn(data) по REPEATS запускам, с прогревом."""
    fn(data)  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        fn(data)
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_benchmarks(seed: int) -> None:
    """Замеры quicksort на трёх классах входов; аварийные завершения фиксируются."""
    rng = random.Random(seed)
    for kind in INPUT_KINDS:
        print(f"\nкласс входа: {kind}")
        for n in SIZES:
            data = make_input(rng, n, kind)
            try:
                print(f"  n={n:>6}  t={bench(quicksort, data):.6f} c")
            except RecursionError:
                # Аварийное завершение — тоже результат верификации:
                # зафиксируйте его в отчёте вместе с размером входа.
                print(f"  n={n:>6}  RecursionError")
    print("\n" + "=" * 60)
    print("ВЫВОД по шагу 4:")
    print("=" * 60)
    print("  На 'random' рост времени близок к O(n log n).")
    print("  На 'sorted' и 'reversed' — RecursionError, т.к. pivot = data[0]")
    print("  всегда крайний элемент → глубина рекурсии = n → O(n²).")


# ---------------------------------------------------------------------------
# 5. Самопроверка каркаса (граничные случаи + сверка с эталоном stdlib)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Проверяет вспомогательные функции до основной верификации."""
    assert is_sorted([]) and is_sorted([7]) and is_sorted([1, 2, 2, 3])
    assert not is_sorted([3, 1, 2])
    assert same_multiset([], []) and same_multiset([2, 1, 2], [1, 2, 2])
    assert not same_multiset([1, 1, 2], [1, 2, 2])
    rng = random.Random(0)
    for _ in range(100):  # сверка помощников с эталоном стандартной библиотеки
        a = [rng.randint(-20, 20) for _ in range(rng.randint(0, 30))]
        assert is_sorted(sorted(a))          # эталон sorted() упорядочен
        assert same_multiset(a, sorted(a))   # эталон — перестановка входа
    print("self_check: OK")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant  # вариантность — см. docs/reproducibility.md
    random.seed(seed)
    self_check()
    rng = random.Random(seed)
    run_representative_tests(rng)          # шаги 1–2
    compare_with_reference(rng, runs=300)  # шаг 3
    run_benchmarks(seed)                   # шаг 4
    # TODO: по итогам шагов 1–4 сформулировать в отчёте вердикт о применимости
    # TODO: (принять / принять с доработкой / отклонить), исправить дефекты в копии
    # TODO: файла и подтвердить исправление повторной полной верификацией.


if __name__ == "__main__":
    main()
