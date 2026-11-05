def uses_index(conn, sql):
    """Ask SQLite for its plan and look for an index lookup in each step."""
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
    return any("USING INDEX" in row["detail"] for row in rows)
