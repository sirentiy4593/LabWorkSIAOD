#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ДЗ 2. Эксперимент: высота BST и деградация операций — стартовая заготовка.

Заготовка — это каркас, а не решение: заполните все TODO самостоятельно
в соответствии с КИМ-02 (Cases) и правилами использования генеративного ИИ
(docs/ai-verification.md). Класс BST из ЛР 5 рекомендуется подключить как
модуль; ниже дан минимальный узел и сигнатуры на случай автономного запуска.

Запуск: python dz02-bst-height-starter.py --variant N
"""
from __future__ import annotations

import argparse
import random
import statistics
import time

# ---------------------------------------------------------------------------
# 1. Узел и итеративная вставка
#    Внимание: на упорядоченном потоке дерево вырождается в список глубиной
#    до 10^4, поэтому вставка и обходы должны быть итеративными —
#    рекурсивные варианты вызовут RecursionError.
# ---------------------------------------------------------------------------


class Node:
    """Узел BST: ключ и ссылки на левое и правое поддеревья."""

    __slots__ = ("key", "left", "right")

    def __init__(self, key: int) -> None:
        self.key = key
        self.left: Node | None = None
        self.right: Node | None = None


def insert_iter(root: Node | None, key: int) -> Node:
    """Итеративная вставка ключа в BST; возвращает корень дерева.

    Дубликаты игнорируются (ключи в эксперименте уникальны).
    """
    if root is None:
        return Node(key)
    current = root
    while True:
        if key < current.key:
            if current.left is None:
                current.left = Node(key)
                break
            current = current.left
        elif key > current.key:
            if current.right is None:
                current.right = Node(key)
                break
            current = current.right
        else:
            break
    return root


def build_bst(keys: list[int]) -> Node | None:
    """Строит BST последовательной итеративной вставкой ключей."""
    root: Node | None = None
    for key in keys:
        root = insert_iter(root, key)
    return root


# ---------------------------------------------------------------------------
# 2. Измеряемые величины: высота и средняя глубина узла
# ---------------------------------------------------------------------------


def tree_height(root: Node | None) -> int:
    """Высота дерева: число рёбер на самом длинном пути от корня до листа.

    Пустое дерево: -1; один узел: 0. Реализовать итеративно
    (обход в ширину или в глубину с явным стеком/очередью).
    """
    if root is None:
        return -1
    max_depth = -1
    queue = [(root, 0)]
    while queue:
        node, depth = queue.pop(0)
        if depth > max_depth:
            max_depth = depth
        if node.left is not None:
            queue.append((node.left, depth + 1))
        if node.right is not None:
            queue.append((node.right, depth + 1))
    return max_depth


def sum_depths(root: Node | None) -> int:
    """Сумма глубин всех узлов (глубина корня — 0). Итеративно."""
    if root is None:
        return 0
    total = 0
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        total += depth
        if node.left is not None:
            stack.append((node.left, depth + 1))
        if node.right is not None:
            stack.append((node.right, depth + 1))
    return total


def count_nodes(root: Node | None) -> int:
    """Число узлов дерева. Итеративно."""
    if root is None:
        return 0
    count = 0
    stack = [root]
    while stack:
        node = stack.pop()
        count += 1
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    return count


def avg_depth(root: Node | None) -> float:
    """Средняя глубина узла: sum_depths / count_nodes (0.0 для пустого)."""
    n = count_nodes(root)
    if n == 0:
        return 0.0
    return sum_depths(root) / n


def inorder_keys(root: Node | None) -> list[int]:
    """Ключи in-order-обхода (итеративно, с явным стеком) — для верификации."""
    result = []
    stack = []
    current = root
    while current is not None or stack:
        while current is not None:
            stack.append(current)
            current = current.left
        current = stack.pop()
        result.append(current.key)
        current = current.right
    return result

# ---------------------------------------------------------------------------
# 3. Верификация (шаги 1–3 методики docs/ai-verification.md)
# ---------------------------------------------------------------------------


def self_check() -> None:
    """Граничные деревья, аналитические значения, сверка с эталоном sorted()."""
    # Граничные случаи: пустое дерево и один узел
    assert tree_height(None) == -1
    assert avg_depth(None) == 0.0
    single = build_bst([42])
    assert tree_height(single) == 0
    assert count_nodes(single) == 1

    # Типовой случай: [2, 1, 3] — идеально сбалансированное дерево из 3 узлов
    small = build_bst([2, 1, 3])
    assert tree_height(small) == 1
    assert sum_depths(small) == 2  # 0 (корень) + 1 + 1

    # Вырожденный случай: упорядоченные ключи 1..n дают "список"
    n = 100
    degenerate = build_bst(list(range(1, n + 1)))
    assert tree_height(degenerate) == n - 1
    assert avg_depth(degenerate) == (n - 1) / 2  # (0+1+...+(n-1)) / n

    # Сверка с эталоном стандартной библиотеки: инвариант BST —
    # in-order-обход совпадает с sorted() на случайных наборах ключей
    rng = random.Random(0)
    for _ in range(200):
        keys = rng.sample(range(-1000, 1000), rng.randint(1, 60))
        root = build_bst(keys)
        assert inorder_keys(root) == sorted(keys)
        assert count_nodes(root) == len(keys)
    print("self_check: OK")


# ---------------------------------------------------------------------------
# 4. Эксперимент и каркас замеров (методика — docs/reproducibility.md)
# ---------------------------------------------------------------------------

SIZES = [100, 300, 1_000, 3_000, 10_000]  # геометрический шаг, n до 10^4
REPEATS = 5


def random_keys(n: int, rng: random.Random) -> list[int]:
    """n уникальных случайных ключей (детерминированно по seed варианта)."""
    return rng.sample(range(10 * n), n)


def ordered_keys(n: int) -> list[int]:
    """n упорядоченных ключей 1..n — худший поток вставок для BST."""
    return list(range(1, n + 1))


def bench_search(root: Node | None, queries: list[int]) -> float:
    """Медиана времени поиска всех ключей queries по REPEATS запускам."""

    def run() -> None:
        for q in queries:
            node = root
            while node is not None and node.key != q:
                node = node.left if q < node.key else node.right

    run()  # прогрев — не учитывается
    times = []
    for _ in range(REPEATS):
        t0 = time.perf_counter()
        run()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


def run_experiment(seed: int) -> None:
    """Таблица: n, высота и средняя глубина для двух потоков, опорные величины."""
    rng = random.Random(seed)
    header = (f"{'n':>7} {'h_случ':>8} {'d_случ':>8} "
              f"{'h_упор':>8} {'d_упор':>8} {'log2(n)':>8}")
    print(header)
    import math

    ns_list = []
    h_rand_list = []
    h_ord_list = []
    log2_list = []

    for n in SIZES:
        root_rand = build_bst(random_keys(n, rng))
        root_ord = build_bst(ordered_keys(n))

        h_r = tree_height(root_rand)
        h_o = tree_height(root_ord)
        d_r = avg_depth(root_rand)
        d_o = avg_depth(root_ord)
        l2 = math.log2(n)

        print(f"{n:>7} {h_r:>8} {d_r:>8.1f} {h_o:>8} {d_o:>8.1f} {l2:>8.1f}")

        queries = random_keys(n, random.Random(seed + n))
        t_rand = bench_search(root_rand, queries)
        t_ord = bench_search(root_ord, queries)
        print(f"         t_случ={t_rand:.6f} c  t_упор={t_ord:.6f} c")

        ns_list.append(n)
        h_rand_list.append(h_r)
        h_ord_list.append(h_o)
        log2_list.append(l2)


    # Построение графиков
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib не установлен — графики не построены")
        return

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.loglog(ns_list, h_rand_list, 'o-', label='h случайное BST')
    ax.loglog(ns_list, h_ord_list, 's-', label='h упорядоченное (вырождение)')
    ax.loglog(ns_list, log2_list, '^-', label='log₂(n) (идеал)')
    ax.loglog(ns_list, ns_list, 'x-', label='n (линейная деградация)')
    ax.set_xlabel('n (число узлов)')
    ax.set_ylabel('Высота дерева h')
    ax.set_title('Высота BST: случайные vs упорядоченные данные')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig('dz02_bst_height.png', dpi=150)
    print("График сохранён: dz02_bst_height.png")

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", type=int, required=True, help="номер варианта")
    args = ap.parse_args()
    seed = 30 + args.variant
    random.seed(seed)
    self_check()
    run_experiment(seed)


if __name__ == "__main__":
    main()
