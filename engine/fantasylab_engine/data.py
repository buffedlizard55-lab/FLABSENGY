"""Data loading helpers.

Design rule (research/data-sources): ONLY ingest from sources with clear
terms — open-licensed bundles (nflverse CC-BY-4.0 [S35][S36]), official league
APIs for personal analysis (MLB Stats API [S37]), or files the user exported
from DFS sites themselves (official contest CSVs). Never from fantasylabs.com
(I2/I3), never via DK/FD undocumented endpoints (I16).
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, List, Optional


def load_players_csv(path: str | Path) -> List[Dict[str, object]]:
    """Load a player pool CSV.

    Required columns:
      id, name, team, opp, position, salary, projection
    Optional:
      flex_positions (pipe-separated, default derived), ownership, game
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(path)
    rows: List[Dict[str, object]] = []
    with p.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        required = {"id", "name", "team", "opp", "position", "salary", "projection"}
        header = set(reader.fieldnames or [])
        missing = required - header
        if missing:
            raise ValueError(f"CSV missing columns: {sorted(missing)}")
        for i, r in enumerate(reader, start=2):
            try:
                salary = float(r["salary"])
                projection = float(r["projection"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"line {i}: bad numeric field") from exc
            if salary <= 0:
                raise ValueError(f"line {i}: salary must be positive")
            flex_raw = r.get("flex_positions") or ""
            if flex_raw:
                flex = frozenset(s.strip() for s in flex_raw.split("|") if s.strip())
            else:
                flex = _default_flex(r["position"])
            own: Optional[float]
            if r.get("ownership") in (None, ""):
                own = None
            else:
                own = float(r["ownership"])  # type: ignore[arg-type]
            rows.append({
                "id": r["id"],
                "name": r["name"],
                "team": r["team"],
                "opp": r["opp"],
                "position": r["position"],
                "flex_positions": flex,
                "salary": salary,
                "projection": projection,
                "ownership": own,
                "game": r.get("game") or f"{r['team']}@{r['opp']}",
            })
    if not rows:
        raise ValueError("CSV has no player rows")
    return rows


_DEFAULT_FLEX = {
    "RB": frozenset({"RB", "WR", "TE"}),
    "WR": frozenset({"RB", "WR", "TE"}),
    "TE": frozenset({"RB", "WR", "TE"}),
}


def _default_flex(position: str) -> frozenset:
    """FLEX eligibility ONLY (not primary-position eligibility).

    QB/DST/K get an empty set => never FLEX-eligible (fixes double-QB bug
    found in Pass 1).
    """
    pos = position.upper()
    return _DEFAULT_FLEX.get(pos, frozenset())
