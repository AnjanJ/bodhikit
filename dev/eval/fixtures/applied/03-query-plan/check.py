import sqlite3

from solution import uses_index

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE orders (id INTEGER PRIMARY KEY, customer TEXT, total REAL)")
conn.execute("CREATE INDEX idx_orders_customer ON orders(customer)")

assert uses_index(conn, "SELECT * FROM orders WHERE customer = 'ana'") is True, \
    "an equality on the indexed column should use the index"
assert uses_index(conn, "SELECT * FROM orders WHERE total > 10") is False, \
    "a filter on an unindexed column scans the table"
print("all checks passed")
