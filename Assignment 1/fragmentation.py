# Code by ~Siddhartha Mettu - 1241917160

# Step 0: Environment Setup
# Import required libraries
# Do not install/import any additional libraries
import psycopg2
import psycopg2.extras
import json
import csv
import math


# Lets define some of the essentials
# We'll define these as global variables to keep it simple
username = "postgres"
password = "postgres"
dbname = "fragmentation"
host = "127.0.0.1"


def get_open_connection():
    """
    Connect to the database and return connection object

    Returns:
        connection: The database connection object.
    """

    return psycopg2.connect(f"dbname='{dbname}' user='{username}' host='{host}' password='{password}'")
# End of Step 0: Environment Setup


def load_data(table_name, csv_path, connection, header_file):
    """
    Create a table with the given name and load data from the CSV file located at the given path.

    Args:
        table_name (str): The name of the table where data is to be loaded.
        csv_path (str): The path to the CSV file containing the data to be loaded.
        connection: The database connection object.
        header_file (str): The path to where the header file is located
    """

    cursor = connection.cursor()

    # Creating the table
    with open(header_file) as json_data:
        header_dict = json.load(json_data)

    table_rows_formatted = (", ".join(f"{header} {header_type}" for header, header_type in header_dict.items()))
    create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            {table_rows_formatted}
            )'''

    cursor.execute(create_table_query)
    connection.commit()

    # Step 1: Loading the data
    with open(csv_path, 'r') as f:
        cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
    connection.commit()
    # End of Step 1: Loading the data

    cursor.close()


def range_partition(data_table_name, partition_table_name, num_partitions, header_file, column_to_partition, connection):
    """
    Use this function to partition the data in the given table using a range partitioning approach.

    Args:
        data_table_name (str): The name of the table that contains the data loaded during load_data phase.
        partition_table_name (str): The name of the table to be created for partitioning.
        num_partitions (int): The number of partitions to create.
        header_file (str): path to the header file that contains column headers and their data types
        column_to_partition (str): The column based on which we are creating the partition.
        connection: The database connection object.
    """

    # Step 2: Range Partition
    cursor = connection.cursor()

    with open(header_file) as json_data:
        header_dict = json.load(json_data)
    columns = ", ".join(f"{header} {header_type}" for header, header_type in header_dict.items())

    # Parent table
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {partition_table_name} ({columns})
        PARTITION BY RANGE ({column_to_partition})''')

    # Uniform range size
    cursor.execute(f"SELECT MIN({column_to_partition}), MAX({column_to_partition}) FROM {data_table_name}")
    min_val, max_val = (int(v) for v in cursor.fetchone())
    gap = math.ceil((max_val - min_val) / num_partitions)

    # Child partitions (upper bound is exclusive)
    for i in range(num_partitions):
        cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS {partition_table_name}{i}
            PARTITION OF {partition_table_name}
            FOR VALUES FROM ({min_val + i * gap}) TO ({min_val + (i + 1) * gap})''')

    # Route existing rows into the children
    cursor.execute(f"INSERT INTO {partition_table_name} SELECT * FROM {data_table_name}")
    connection.commit()
    cursor.close()
    # End of Step 2: Range Partition


def round_robin_partition(data_table_name, partition_table_name, num_partitions, header_file, connection):
    """
    Use this function to partition the data in the given table using a round-robin approach.

    Args:
        data_table_name (str): The name of the table that contains the data loaded during load_data phase.
        partition_table_name (str): The name of the table to be created for partitioning.
        num_partitions (int): The number of partitions to create.
        header_file (str): path to the header file that contains column headers and their data types
        connection: The database connection object.
    """

    # Step 3: Round Robin Partition
    cursor = connection.cursor()

    with open(header_file) as json_data:
        header_dict = json.load(json_data)
    columns = ", ".join(f"{header} {header_type}" for header, header_type in header_dict.items())

    # Parent table and children that inherit from it
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {partition_table_name} ({columns})")
    for i in range(num_partitions):
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {partition_table_name}{i} () INHERITS ({partition_table_name})")
    connection.commit()

    # Initial load: row i (0-indexed) goes to child i % num_partitions
    for i in range(num_partitions):
        cursor.execute(f'''
            INSERT INTO {partition_table_name}{i}
            SELECT {", ".join(header_dict)} FROM (
                SELECT *, ROW_NUMBER() OVER () AS rn FROM {data_table_name}
            ) sub
            WHERE (rn - 1) % {num_partitions} = {i}''')
    connection.commit()

    # Trigger: send each new row to the least-filled child (smallest suffix wins ties)
    cursor.execute(f'''
        CREATE OR REPLACE FUNCTION {partition_table_name}_rr_insert() RETURNS TRIGGER AS $$
        DECLARE
            target TEXT;
            min_count BIGINT;
            cnt BIGINT;
        BEGIN
            FOR i IN 0..{num_partitions - 1} LOOP
                EXECUTE format('SELECT COUNT(*) FROM %I', '{partition_table_name}' || i) INTO cnt;
                IF min_count IS NULL OR cnt < min_count THEN
                    min_count := cnt;
                    target := '{partition_table_name}' || i;
                END IF;
            END LOOP;
            EXECUTE format('INSERT INTO %I SELECT ($1).*', target) USING NEW;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql''')
    cursor.execute(f'''
        CREATE OR REPLACE TRIGGER {partition_table_name}_rr_trigger
        BEFORE INSERT ON {partition_table_name}
        FOR EACH ROW EXECUTE FUNCTION {partition_table_name}_rr_insert()''')
    connection.commit()
    cursor.close()
    # End of Step 3: Round Robin Partition


def delete_partitions(table_name, num_partitions, connection):
    """
    This function in NOT graded and for your own testing convinience.
    Use this function to delete all the partitions that are created by you.

    Args:
        table_name (str): The name of the table containing the partitions to be deleted.
        num_partitions (int): The number of partitions to be deleted.
        connection: The database connection object.
    """

    cursor = connection.cursor()

    # Drop trigger + function if they exist (round-robin case)
    trigger_name = f"{table_name}_rr_trigger"
    trigger_function_name = f"{table_name}_rr_insert"
    cursor.execute(f'DROP TRIGGER IF EXISTS {trigger_name} ON {table_name}')
    cursor.execute(f'DROP FUNCTION IF EXISTS {trigger_function_name}()')

    # Drop child partitions
    for i in range(num_partitions):
        cursor.execute(f'DROP TABLE IF EXISTS {table_name}{i} CASCADE')

    # Drop the parent table
    cursor.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE')

    connection.commit()
    cursor.close()

# Code by ~Siddhartha Mettu - 1241917160
