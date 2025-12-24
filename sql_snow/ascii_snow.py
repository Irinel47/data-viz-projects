import sqlite3, os, time

c = sqlite3.connect(":memory:").cursor()

q = """
WITH RECURSIVE r(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM r WHERE x < 50),
               c(y) AS (SELECT 1 UNION ALL SELECT y + 1 FROM c WHERE y < 70)
SELECT group_concat(CASE WHEN abs(random()) % 100 < 15 THEN '*' ELSE '.' END,'')
FROM r CROSS JOIN c GROUP BY x ORDER BY x;
"""

def run(n = 200, fps = 5):
    for _ in range(n):
        os.system("cls" if os.name=="nt" else "clear")
        print("\n".join(l[0] for l in c.execute(q)))
        time.sleep(1 / fps)

run()