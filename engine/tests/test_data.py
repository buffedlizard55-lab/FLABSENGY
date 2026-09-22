"""Data loader tests (CSV guards, P2-style validation)."""

import textwrap
from pathlib import Path

import pytest

from fantasylab_engine.data import load_players_csv


def _write(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "pool.csv"
    p.write_text(textwrap.dedent(body), encoding="utf-8")
    return p


def test_load_ok(tmp_path):
    p = _write(tmp_path, """\
        id,name,team,opp,position,salary,projection,ownership,game
        qb1,QB One,AAA,BBB,QB,7000,21.5,12.5,AAAxBBB
        rb1,RB One,CCC,DDD,RB,6000,15.0,,CCCxDD
        """)
    rows = load_players_csv(p)
    assert len(rows) == 2
    assert rows[0]["projection"] == pytest.approx(21.5)
    assert rows[0]["ownership"] == pytest.approx(12.5)
    assert rows[1]["ownership"] is None
    assert "RB" in rows[1]["flex_positions"]


def test_missing_columns(tmp_path):
    p = _write(tmp_path, """\
        id,name,team,opp,position,salary
        qb1,Q,AAA,BBB,QB,7000
        """)
    with pytest.raises(ValueError, match="missing columns"):
        load_players_csv(p)


def test_bad_salary(tmp_path):
    p = _write(tmp_path, """\
        id,name,team,opp,position,salary,projection
        qb1,Q,AAA,BBB,QB,abc,20
        """)
    with pytest.raises(ValueError, match="bad numeric"):
        load_players_csv(p)


def test_nonpositive_salary(tmp_path):
    p = _write(tmp_path, """\
        id,name,team,opp,position,salary,projection
        qb1,Q,AAA,BBB,QB,0,20
        """)
    with pytest.raises(ValueError, match="positive"):
        load_players_csv(p)


def test_missing_file():
    with pytest.raises(FileNotFoundError):
        load_players_csv("/no/such/file.csv")


def test_empty_csv(tmp_path):
    p = _write(tmp_path, """\
        id,name,team,opp,position,salary,projection
        """)
    with pytest.raises(ValueError, match="no player rows"):
        load_players_csv(p)
