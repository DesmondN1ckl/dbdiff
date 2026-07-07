import argparse
import pathlib

import sqlcipher3


def parse_args():
    parser = argparse.ArgumentParser(
                    prog='dbscan',
                    description='Scans differences between 2 or more sqlite/sqlcipher dbs, then offers to patch the results')

    key_group = parser.add_mutually_exclusive_group()

    key_group.add_argument(
        '-k', '--key',
        help='Specify key for sqlcipher dbs'
    )

    key_group.add_argument(
        '-kf', '--key-file',
        help='Specify file containing key for sqlcipher dbs'
    )


    parser.add_argument(
        'dbs',
        help='DB files to compare',
        nargs='+'
    )

    parser.add_argument(
        '-v', '--values',
        help='Values to scan for, in the same order as the databases',
        nargs='+',
        required=True
    )

    args = parser.parse_args()

    if len(args.values) != len(args.dbs):
        parser.error('Number of databases and values must be equal')

    return args

def read_key(path):
    return open(path).read().rstrip('\r\n')

def sanitize_key(key):
    return key.replace("'", "''")

def flatten_output(output):
    return [result[0] for result in output]

def open_db(db, key=None):
    con = sqlcipher3.connect(db)
    cur = con.cursor()

    if key is not None:
        key = sanitize_key(key)
        cur.execute(f'PRAGMA key = \'{key}\'')
        get_tables(con) # Attempt fetching something from the db to test the key, discards results.

    cur.close()
    return con

def execute_sql(con, sql, params=()):
    cur = con.cursor()
    result = cur.execute(sql, params).fetchall()
    cur.close()
    return result

def get_tables(con):
    result = execute_sql(con, "SELECT name FROM sqlite_master WHERE type='table'")
    return flatten_output(result)

def find_shared_tables(tables):
    shared_tables = set(tables[0])

    for table in tables.values():
        shared_tables &= set(table) # im aware it intersects the first entry with itself, but ill fix it later since it works

    shared_tables = list(shared_tables)
    return shared_tables

def get_columns(con, table):
    result = execute_sql(con, f'SELECT name FROM pragma_table_info(?)', params=(table,)) # trailing , needed to make it a tuple
    return flatten_output(result)

def find_shared_columns(conns, shared_tables):
    shared_columns_by_db = {}

    for table in shared_tables:
        columns_by_db = {}
        for i in range(len(conns)):
            columns_by_db[i] = set(get_columns(conns[i], table))
        
        if len(columns_by_db) == 0:
            break

        intersect_columns = columns_by_db[0]
        for i in range(len(columns_by_db)):
            intersect_columns &= columns_by_db[i]
        
        shared_columns_by_db[table] = intersect_columns

    return shared_columns_by_db

def main():
    args = parse_args()
    if args.key is not None:
        key = args.key
    elif args.key_file is not None:
        key = read_key(args.key_file)
    else:
        key = None


    connections = []
    for db_path in args.dbs:
        connections.append(open_db(pathlib.Path(db_path), key=key))

    tables_by_db = {}
    for i in range(len(connections)):
        tables_by_db[i] = (get_tables(connections[i]))

    print("Tables by db", tables_by_db)
    
    shared_tables = find_shared_tables(tables_by_db)
    print("Shared tables:", shared_tables)
    
    shared_columns = find_shared_columns(connections, shared_tables)
    print("Shared columns:", shared_columns)

    # print("Tables by db:", tables_by_db)    

    for con in connections:
        con.close()

if __name__ == "__main__":
    main()