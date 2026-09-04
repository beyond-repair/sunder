from sunder.aegis_bridge import session_graph
from sunder.portfolio import REPOS, build_priorities, by_cluster, gaps


def test_catalog_nonempty_and_clustered():
    assert len(REPOS) >= 8
    clusters = by_cluster()
    assert "agent-runtime" in clusters
    assert "integrity" in clusters
    assert any(r.name == "sunder" for r in REPOS)


def test_gaps_and_priorities():
    g = gaps()
    assert g
    pri = build_priorities()
    assert any("AEGIS" in p for p in pri)


def test_session_graph_referential_integrity():
    g = session_graph("inspect", "/tmp/ws", "abc123")
    assert g.valid()
    m = g.manifest()
    assert m["valid"] is True
    assert m["relationship_count"] == 2
