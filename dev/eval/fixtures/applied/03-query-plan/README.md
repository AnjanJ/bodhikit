# Exercise 3 — Does the planner use the index?

SQLite's `EXPLAIN QUERY PLAN <query>` returns one row per step of the plan. The
fourth column, `detail`, says how each table is read: `SEARCH ... USING INDEX ...`
when the planner looks rows up through an index, `SCAN ...` when it reads every row.

Write `uses_index(conn, sql)` in `solution.py`: it returns `True` when SQLite's plan
for `sql` reads any table through an index, and `False` otherwise.

Run `python3 check.py` in this folder to check it.
