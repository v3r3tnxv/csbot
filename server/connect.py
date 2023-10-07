import sqlite3 as sl

con = sl.connect('cityk.db')

with con:
    con.execute("""
        DROP TABLE district
    """)
    con.execute("""
        DROP TABLE street
    """)
    con.execute("""
        DROP TABLE location
    """)
    con.execute("""
        DROP TABLE outage
      """)
    con.execute("""
        DROP TABLE resource
    """)

    con.execute("""
        CREATE TABLE district (
            id_district INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name_district VARCHAR(150)
        )
    """)
    con.execute("""
        CREATE TABLE street (
            id_street INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            name_street VARCHAR(150),
            id_district INTEGER,
            FOREIGN KEY (id_district) REFERENCES district (id_district)
        )
    """)
    con.execute("""
        CREATE TABLE location (
            id_record INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            id_street INTEGER,
            id_outage INTEGER,
            FOREIGN KEY (id_street) REFERENCES street (id_street)
            FOREIGN KEY (id_outage) REFERENCES outage (id_outage)
        )
    """)
    con.execute("""
        CREATE TABLE outage (
            id_outage INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            date_start VARCHAR(150),
            date_end VARCHAR(150),
            note_outage VARCHAR(300),
            id_resource INTEGER,
            FOREIGN KEY (id_resource) REFERENCES resource (id_resource)
        )
    """)
    con.execute("""
        CREATE TABLE resource (
            id_resource INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            supplier_contacts VARCHAR(300),
            type_resource VARCHAR(150)
        )
    """)

district_data = [
    (1, 'Хостинский'),
    (2, 'Адлерский'),
    (3, 'Центральный'),
    (4, 'Лазаревский')
]
with con:
    con.executemany("INSERT INTO district (id_district, name_district) VALUES (?, ?)", district_data)
with con:
    data = con.execute("SELECT * FROM district")
    for row in data:
        print(row)

street_data = [
    (1, 'ул. Роз', 1),
    (2, 'ул. Победы', 2),
    (3, 'ул. Гагарина', 3),
    (4, 'ул. Ленина', 4)
]
with con:
    con.executemany("INSERT INTO street (id_street, name_district, id_district) VALUES (?, ?, ?)", street_data)
with con:
    data = con.execute("SELECT * FROM street")
    for row in data:
        print(row)

location_data = [
    (1, 1, 1),
    (2, 2, 2),
    (3, 3, 3)
]
with con:
    con.executemany("INSERT INTO location (id_location, id_street, id_outage) VALUES (?, ?, ?)", location_data)
with con:
    data = con.execute("SELECT * FROM location")
    for row in data:
        print(row)

outage_data = [
    (1, '10.10.2023', '12.12.2050', 'ТРУБУ ПОРВАЛО НА ЧАСТИ', 1),
    (2, '11.11.2024', '11.11.2040' 'Упало дерево на линию электропередачь', 2),
    (3, '12.12.2024', '10.10.2030' 'Плановые работы', 3)
]
with con:
    con.executemany("INSERT INTO outage (id_outage, date_start, date_end, note_outage, id_resource) VALUES (?, ?, ?, ?, ?)", outage_data)
with con:
    data = con.execute("SELECT * FROM outage")
    for row in data:
        print(row)

resource_data = [
    (1, '7 918 244 48 03', '12.12.2050', 'Вода', 1),
    (2, '7 918 244 48 03', '11.11.2040' 'Электричество', 2),
    (3, '7 918 244 48 03', '10.10.2030' 'Газ', 3)
]
with con:
    con.executemany("INSERT INTO resource (id_resource, supplier_contacts, type_resource) VALUES (?, ?, ?)", resource_data)
with con:
    data = con.execute("SELECT * FROM resource")
    for row in data:
        print(row)

