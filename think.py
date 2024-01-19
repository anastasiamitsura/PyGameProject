import sqlite3 as sl


class DataBase:
    con = sl.connect('records.db')

    with con:
        data = con.execute("select count(*) from sqlite_master \
        where type='table' and name='records'")
        for row in data:
            if row[0] == 0:
                con.execute("""
                            CREATE TABLE records (
                                id INTEGER PRIMARY KEY,
                                name STRING,
                                score INTEGER
                            );
                        """)
    sqlite_insert_score = """ INSERT INTO records
                                             (id, name, score) VALUES (?, ?, ?)"""

