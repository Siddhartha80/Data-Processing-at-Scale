import psycopg2

username = "postgres"
password = "postgres"
dbname = "fragmentation"
host = "127.0.0.1"


def point_query(parent_partition_table_name, utc_val, save_table_name, connection):
    cur = connection.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {save_table_name}")
    cur.execute(
        f"CREATE TABLE {save_table_name} AS "
        f"SELECT * FROM {parent_partition_table_name} "
        f"WHERE created_utc = %s ORDER BY created_utc ASC",
        (utc_val,),
    )
    connection.commit()
    cur.close()


def range_query(parent_partition_table_name, utc_min_val, utc_max_val, save_table_name, connection):
    cur = connection.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {save_table_name}")
    cur.execute(
        f"CREATE TABLE {save_table_name} AS "
        f"SELECT * FROM {parent_partition_table_name} "
        f"WHERE created_utc > %s AND created_utc <= %s ORDER BY created_utc ASC",
        (utc_min_val, utc_max_val),
    )
    connection.commit()
    cur.close()