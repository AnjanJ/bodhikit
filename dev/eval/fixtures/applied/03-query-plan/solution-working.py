def uses_index(conn, sql):
    rows = conn.execute("EXPLAIN QUERY PLAN " + sql).fetchall()
    for row in rows:
        detail = row[3]
        if "USING INDEX" in detail or "USING COVERING INDEX" in detail:
            return True
    return False
