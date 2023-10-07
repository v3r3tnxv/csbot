import sqlite3 as sl

con = sl.connect('cityk.db')
with con:
    con.execute("""
        DROP TABLE vg_rn
    """)
    con.execute("""
        DROP TABLE street
    """)
    con.execute("""
        CREATE TABLE vg_rn (
            id_rn INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name_rn VARCHAR(150)
        )
    """)
    con.execute("""
        CREATE TABLE street (
            id_street INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name_street VARCHAR(150),
            id_rn INTEGER,
            FOREIGN KEY (id_rn) REFERENCES vg_rn (id_rn)
        )
    """)
data = [
    (1, 'Хостинский'),
    (2, 'Адлерский'),
    (3, 'Центральный')
]
with con:
    con.executemany("INSERT INTO vg_rn (id_rn, name_rn) VALUES (?, ?)", data)
with con:
    data = con.execute("SELECT * FROM vg_rn")
    for row in data:
        print(row)
