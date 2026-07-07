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
    return open(path).read().strip()

def sanitize_key(key):
    return key.replace("'", "''")

def open_db(db, key=None):
    con = sqlcipher3.connect(db)
    cur = con.cursor()

    if key is not None:
        key = sanitize_key(key)
        cur.execute(f'PRAGMA key = \'{key}\'')
        get_tables(con) # Attempt fetching something from the db to test the key, discards results.

    cur.close()
    return con

def execute_sql(con, sql):
    cur = con.cursor()
    result = cur.execute(sql).fetchall()
    cur.close()
    return result

def get_tables(con):
    result = execute_sql(con, "SELECT name FROM sqlite_master WHERE type='table'")
    tables = [tables[0] for tables in result]
    return tables

def main():
    args = parse_args()
    if args.key is not None:
        key = args.key
    elif args.key_file is not None:
        key = read_key(args.key_file)
    else:
        key = None


    conns = []
    for db_path in args.dbs:
        conns.append(open_db(pathlib.Path(db_path), key=key))

    tables = []
    for con in conns:
        tables.append(get_tables(con))

    shared_tables = set(tables[0])
    for table in tables[1:]:
        shared_tables &= set(table)

    print(tables)    
    print(shared_tables)
    

if __name__ == "__main__":
    main()