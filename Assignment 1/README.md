# Assignment 1: Data Fragmentation

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![psycopg2](https://img.shields.io/badge/Driver-psycopg2-informational)

Implement horizontal data fragmentation over a single PostgreSQL base table using two strategies: **range partitioning** and **round-robin partitioning**.

📄 [Assignment handout (PDF)](Assignment_%20Data%20Fragmentation.pdf)

---

## Overview

Partitioning splits one large logical table into smaller physical fragments, which improves manageability and lets queries touch less data. This assignment implements both a declarative strategy (range) and a simulated one (round-robin) on the Reddit `subreddits` dataset, using the `created_utc` column.

| Step | Function | Technique |
|---|---|---|
| 1 | `load_data` | Bulk load a CSV with `COPY`, driven from Python |
| 2 | `range_partition` | PostgreSQL declarative `PARTITION BY RANGE` |
| 3 | `round_robin_partition` | Table inheritance plus a `BEFORE INSERT` trigger |

## Dataset

`subreddits.csv` (about 244 MB, 914,067 rows) with the column types described in `headers.json`. The loader builds the base table from this JSON header specification, so the schema always matches the CSV.

## Implementation

### 1. Loading: `load_data(table_name, csv_path, connection, header_file)`

Creates the base table from the header specification and loads the CSV using PostgreSQL `COPY`, executed from Python through `psycopg2`.

### 2. Range partition: `range_partition(data_table_name, partition_table_name, num_partitions, header_file, column_to_partition, connection)`

1. Create the parent table with `PARTITION BY RANGE (column_to_partition)`.
2. Compute `min_val` and `max_val` of the partition column.
3. Compute a uniform gap: `ceil((max_val - min_val) / num_partitions)`.
4. Create child tables `<name>0 … <name>N-1`, where child *i* covers `[min_val + i·gap, min_val + (i+1)·gap)`. The upper bound is exclusive.
5. `INSERT INTO parent SELECT * FROM base` so PostgreSQL routes every row to the right child.

Rounding the gap up guarantees the final range covers the maximum value. Rows are only ever stored in child partitions, never in the parent.

### 3. Round-robin partition: `round_robin_partition(data_table_name, partition_table_name, num_partitions, header_file, connection)`

PostgreSQL has no built-in round-robin partitioning, so it is simulated:

- **Structure.** An unpartitioned parent and `N` children created with `INHERITS`.
- **Initial load.** Rows are numbered with `ROW_NUMBER()` and row *k* goes to child `(k - 1) mod N`, so child row counts differ by at most one.
- **Ongoing inserts.** A PL/pgSQL `BEFORE INSERT` trigger on the parent counts the rows in each child, picks the child with the fewest rows (lowest numeric suffix wins ties), inserts the full `NEW` row there, and returns `NULL` so the row is not also stored in the parent.

## Design Highlights

| Concern | Decision |
|---|---|
| Even distribution | `ROW_NUMBER()` modulo `N` for the initial load; least-filled child for new rows |
| No duplicate storage | Trigger returns `NULL` so the parent stays empty |
| Deterministic ranges | Ceiling-rounded uniform gap, half-open intervals |
| Naming | Children are `<partition_table_name>0 … N-1` (for example `range_part0`, `rrobin_part2`) |

## Setup & Usage

Requirements: PostgreSQL 14, Python 3 and `psycopg2`.

```bash
pip install psycopg2-binary
python3 tester.py
```

A Docker image with PostgreSQL 14 preconfigured is also available from the course. The tester loads the data, builds both partitioned layouts, replays `insert1.json`, `insert2.json` and `insert3.json`, and reports a score out of 100.

## What the Tester Checks

| Area | Points | Verified |
|---|---:|---|
| Data loading | 20 | Row count in the table matches the CSV |
| Range partition | 40 | Parent creation, child tables, correct row routing, new inserts land in the right range |
| Round-robin partition | 40 | Parent creation, child tables, balanced distribution (max − min ≤ 1), trigger, new inserts go to the least-filled child |

## Repository Contents

```text
Assignment 1/
├── README.md
├── Assignment_ Data Fragmentation.pdf   # assignment handout
└── fragmentation.py                     # load_data, range_partition, round_robin_partition
```

> The provided support files (`tester.py`, `test_helper.py`, `headers.json`, `insert*.json`) and the 244 MB `subreddits.csv` are course material and are not stored here.

## Skills Demonstrated

- Horizontal partitioning strategies and their trade-offs
- PostgreSQL declarative partitioning and table inheritance
- PL/pgSQL functions and triggers
- Running SQL and `COPY` programmatically with `psycopg2`
- Verifying distribution and routing correctness

---

*CSE 511: Data Processing at Scale, Arizona State University. The assignment handout is course material and is credited to its author, Zhichao Cao, Ph.D.*
