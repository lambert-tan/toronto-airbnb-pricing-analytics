"""Run the DuckDB SQL pipeline in sql/ end to end.

    python scripts/run_sql_pipeline.py                       # steps 01-03
    python scripts/run_sql_pipeline.py --check-known-totals  # real Inside Airbnb file

Steps
    01  clean the raw snapshot and engineer the model features -> listings_clean, listing_features
    02  data-quality checks (the run fails if a check fails)
    03  descriptive market cuts

Each query in 01-03 tagged "-- name: <result_name>" is printed and written to
<out-dir>/<result_name>.csv. Needs data/raw/toronto_listings_detail_nov.csv (see data/README.md).
The regression is not done in SQL: it stays in src/modeling.py and the notebook.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import duckdb
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
SQL_DIR = REPO / "sql"
STEP_FILES = {
    "01": "01_clean_and_engineer.sql",
    "02": "02_quality_checks.sql",
    "03": "03_market_exploration.sql",
}
NAME_MARKER = re.compile(r"^-- name:\s*(\w+)\s*$", re.MULTILINE)


def split_named_queries(sql: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (preamble, [(name, sql_chunk), ...]) split on '-- name:' markers."""
    marks = list(NAME_MARKER.finditer(sql))
    if not marks:
        return sql, []
    preamble = sql[: marks[0].start()]
    chunks = []
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(sql)
        chunks.append((m.group(1), sql[m.end():end]))
    return preamble, chunks


def run_statements(con: duckdb.DuckDBPyConnection, sql: str) -> pd.DataFrame | None:
    """Execute every statement in `sql`; return the last result set (if any)."""
    result = None
    for stmt in con.extract_statements(sql):
        cur = con.execute(stmt.query)
        if stmt.type == duckdb.StatementType.SELECT:
            result = cur.df()
    return result


def run_step(con, step: str, out_dir: Path) -> bool:
    """Run one SQL file. Returns False if a data-quality check failed."""
    path = SQL_DIR / STEP_FILES[step]
    print(f"\n=== step {step}: {path.name}")
    preamble, chunks = split_named_queries(path.read_text())
    run_statements(con, preamble)
    ok = True
    for name, chunk in chunks:
        df = run_statements(con, chunk)
        if df is None:
            continue
        out_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_dir / f"{name}.csv", index=False)
        print(f"\n-- {name}  ({len(df)} rows -> {out_dir.relative_to(REPO) if out_dir.is_relative_to(REPO) else out_dir}/{name}.csv)")
        print(df.head(12).to_string(index=False))
        if name == "quality_checks":
            failed = df[~df["passed"]]
            if len(failed):
                ok = False
                print("\nFAILED CHECKS:\n" + failed.to_string(index=False))
            else:
                print(f"\nAll {len(df)} quality checks passed.")
    if step == "01":
        n = con.execute("SELECT COUNT(*) FROM listing_features").fetchone()[0]
        print(f"listing_features built: {n:,} listings")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw-file", default=str(REPO / "data" / "raw" / "toronto_listings_detail_nov.csv"),
                    help="raw Inside Airbnb detailed-listings CSV")
    ap.add_argument("--out-dir", default=str(REPO / "outputs" / "sql_results"), help="where result CSVs are written")
    ap.add_argument("--steps", nargs="+", default=list(STEP_FILES), choices=list(STEP_FILES))
    ap.add_argument("--db", default=":memory:", help="DuckDB file (default: in memory)")
    ap.add_argument("--check-known-totals", action="store_true",
                    help="also assert the README sample sizes (21,468 raw / 15,332 final listings)")
    ap.add_argument("--export-features", metavar="CSV",
                    help="write listing_features to this CSV after step 01 (same columns as engineer_features)")
    args = ap.parse_args()

    # relative paths in the SQL (outputs/..., data/raw) resolve from the repo root
    import os
    os.chdir(REPO)

    con = duckdb.connect(args.db)
    con.execute("SET VARIABLE raw_file = ?", [args.raw_file])
    con.execute("SET VARIABLE check_known_totals = ?", [bool(args.check_known_totals)])

    all_ok = True
    for step in sorted(args.steps):
        all_ok &= run_step(con, step, Path(args.out_dir))
        if step == "01" and args.export_features:
            con.execute(f"COPY listing_features TO '{args.export_features}' (HEADER, DELIMITER ',')")
    if not all_ok:
        print("\nPipeline finished with failed data-quality checks.", file=sys.stderr)
        return 1
    print("\nPipeline finished OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
