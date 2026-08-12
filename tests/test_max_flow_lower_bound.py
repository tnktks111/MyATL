"""下限制約付き最大流の全列挙差分テスト。"""

from itertools import product
import random

import pytest

from max_flow import FlowLowerBound


def _naive_circulation(
    n: int,
    edges: list[tuple[int, int, int, int]],
) -> tuple[int, ...] | None:
    """全辺流量を列挙し、実行可能循環流を1つ返す。"""
    ranges = [range(lower, upper + 1) for _, _, lower, upper in edges]
    for flows in product(*ranges):
        net_outflow = [0] * n
        for (from_vertex, to_vertex, _, _), flow in zip(edges, flows):
            net_outflow[from_vertex] += flow
            net_outflow[to_vertex] -= flow
        if all(value == 0 for value in net_outflow):
            return flows
    return None


def _naive_max_flow_lower_bound(
    n: int,
    edges: list[tuple[int, int, int, int]],
    source: int,
    sink: int,
) -> tuple[int, tuple[int, ...]] | None:
    """全辺流量を列挙し、0以上の最大フローと割当を返す。"""
    best: tuple[int, tuple[int, ...]] | None = None
    ranges = [range(lower, upper + 1) for _, _, lower, upper in edges]
    for flows in product(*ranges):
        net_outflow = [0] * n
        for (from_vertex, to_vertex, _, _), flow in zip(edges, flows):
            net_outflow[from_vertex] += flow
            net_outflow[to_vertex] -= flow
        value = net_outflow[source]
        if value < 0 or net_outflow[sink] != -value:
            continue
        if any(
            net_outflow[vertex] != 0
            for vertex in range(n)
            if vertex not in (source, sink)
        ):
            continue
        if best is None or value > best[0]:
            best = value, flows
    return best


def _assert_returned_flow_is_valid(
    n: int,
    edges: list[tuple[int, int, int, int]],
    flows: list[int],
    source: int,
    sink: int,
    expected_value: int,
) -> None:
    net_outflow = [0] * n
    for (from_vertex, to_vertex, lower, upper), flow in zip(edges, flows):
        assert lower <= flow <= upper
        net_outflow[from_vertex] += flow
        net_outflow[to_vertex] -= flow
    assert net_outflow[source] == expected_value
    assert net_outflow[sink] == -expected_value
    assert all(
        net_outflow[vertex] == 0
        for vertex in range(n)
        if vertex not in (source, sink)
    )


def test_lower_bound_max_flow_matches_exhaustive_enumeration() -> None:
    rng = random.Random(20260812)
    for n in range(2, 6):
        source, sink = 0, n - 1
        for _ in range(100):
            edges = []
            for _ in range(rng.randrange(7)):
                from_vertex = rng.randrange(n)
                to_vertex = rng.randrange(n)
                lower = rng.randrange(3)
                upper = rng.randrange(lower, 3)
                edges.append((from_vertex, to_vertex, lower, upper))

            expected = _naive_max_flow_lower_bound(
                n, edges, source, sink
            )
            graph = FlowLowerBound(n)
            for edge in edges:
                graph.add_edge(*edge)

            result = graph.flow(source, sink)
            if expected is None:
                assert result == -1
                with pytest.raises(RuntimeError):
                    graph.edges()
            else:
                assert result == expected[0]
                returned_edges = graph.edges()
                assert [
                    (
                        edge.from_vertex,
                        edge.to_vertex,
                        edge.lower_bound,
                        edge.upper_bound,
                    )
                    for edge in returned_edges
                ] == edges
                _assert_returned_flow_is_valid(
                    n,
                    edges,
                    [edge.flow for edge in returned_edges],
                    source,
                    sink,
                    result,
                )


def test_lower_bound_max_flow_handles_zero_capacity_loops_and_parallel_edges() -> None:
    graph = FlowLowerBound(3)
    loop = graph.add_edge(0, 0, 2, 2)
    zero = graph.add_edge(0, 1, 0, 0)
    first = graph.add_edge(0, 1, 1, 3)
    second = graph.add_edge(0, 1, 0, 2)
    graph.add_edge(1, 2, 1, 5)

    assert graph.flow(0, 2) == 5
    assert graph.get_edge(loop).flow == 2
    assert graph.get_edge(zero).flow == 0
    assert graph.get_edge(first).flow + graph.get_edge(second).flow == 5


def test_lower_bound_max_flow_reports_infeasible_constraints() -> None:
    graph = FlowLowerBound(3)
    graph.add_edge(0, 1, 1, 1)
    assert graph.flow(0, 2) == -1
    with pytest.raises(RuntimeError):
        graph.get_edge(0)


def test_lower_bound_max_flow_is_single_use() -> None:
    graph = FlowLowerBound(2)
    graph.add_edge(0, 1, 1, 3)
    with pytest.raises(RuntimeError):
        graph.get_edge(0)
    assert graph.flow(0, 1) == 3
    with pytest.raises(RuntimeError):
        graph.flow(0, 1)
    with pytest.raises(RuntimeError):
        graph.add_edge(0, 1, 0, 1)


def test_lower_bound_max_flow_can_have_feasible_zero_value() -> None:
    graph = FlowLowerBound(2)
    graph.add_edge(1, 0, 1, 1)
    graph.add_edge(0, 1, 1, 1)
    assert graph.flow(0, 1) == 0
    assert [edge.flow for edge in graph.edges()] == [1, 1]


def test_lower_bound_circulation_matches_exhaustive_enumeration() -> None:
    rng = random.Random(20260813)
    for n in range(1, 6):
        for _ in range(100):
            edges = []
            for _ in range(rng.randrange(7)):
                from_vertex = rng.randrange(n)
                to_vertex = rng.randrange(n)
                lower = rng.randrange(3)
                upper = rng.randrange(lower, 3)
                edges.append((from_vertex, to_vertex, lower, upper))

            expected = _naive_circulation(n, edges)
            graph = FlowLowerBound(n)
            for edge in edges:
                graph.add_edge(*edge)

            assert graph.circulation() is (expected is not None)
            if expected is None:
                with pytest.raises(RuntimeError):
                    graph.edges()
                continue

            returned_edges = graph.edges()
            net_outflow = [0] * n
            for original, edge in zip(edges, returned_edges):
                from_vertex, to_vertex, lower, upper = original
                assert (
                    edge.from_vertex,
                    edge.to_vertex,
                    edge.lower_bound,
                    edge.upper_bound,
                ) == original
                assert lower <= edge.flow <= upper
                net_outflow[from_vertex] += edge.flow
                net_outflow[to_vertex] -= edge.flow
            assert net_outflow == [0] * n


def test_lower_bound_circulation_handles_empty_graph_and_fixed_cycle() -> None:
    empty = FlowLowerBound(0)
    assert empty.circulation() is True
    assert empty.edges() == []

    graph = FlowLowerBound(3)
    graph.add_edge(0, 1, 2, 2)
    graph.add_edge(1, 2, 2, 2)
    graph.add_edge(2, 0, 2, 2)
    assert graph.circulation() is True
    assert [edge.flow for edge in graph.edges()] == [2, 2, 2]


def test_lower_bound_circulation_reports_infeasible_constraints() -> None:
    graph = FlowLowerBound(2)
    graph.add_edge(0, 1, 1, 1)
    assert graph.circulation() is False
    with pytest.raises(RuntimeError):
        graph.get_edge(0)


def test_lower_bound_solver_modes_are_mutually_exclusive() -> None:
    circulation = FlowLowerBound(2)
    circulation.add_edge(0, 1, 0, 1)
    assert circulation.circulation() is True
    with pytest.raises(RuntimeError):
        circulation.flow(0, 1)
    with pytest.raises(RuntimeError):
        circulation.circulation()
    with pytest.raises(RuntimeError):
        circulation.add_edge(1, 0, 0, 1)
