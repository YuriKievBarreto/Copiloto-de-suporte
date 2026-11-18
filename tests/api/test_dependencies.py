from unittest.mock import patch


def test_get_compiled_planner_graph_e_singleton():
    """Verifica que o grafo é compilado apenas uma vez (Singleton via lru_cache)."""
    from app.dependencies import get_compiled_planner_graph
    get_compiled_planner_graph.cache_clear()  # garante estado limpo entre execuções

    with patch("app.dependencies.get_planner_graph") as mock_build:
        mock_graph = object()
        mock_build.return_value = mock_graph

        g1 = get_compiled_planner_graph()
        g2 = get_compiled_planner_graph()

    assert g1 is g2, "O grafo deveria ser a mesma instância (Singleton)"
    assert mock_build.call_count == 1, "get_planner_graph deveria ter sido chamado apenas uma vez"
    get_compiled_planner_graph.cache_clear()  # limpeza após o teste
