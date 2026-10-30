# Assignment 2: Query Processing

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Environment-Docker-2496ED?logo=docker&logoColor=white)

Build a simplified query processor that runs **range queries** and **point queries** over the partitioned tables created in [Assignment 1](../Assignment%201/).

📄 [Assignment handout (PDF)](Assignment_%20Query%20Processing.pdf)

---

## Overview

Once data is fragmented, queries must be answered against the partitioned layout. This assignment extends the previous work with two query types that read from a parent partition table and persist their results to a new table.

The same two functions are tested against both partitioning schemes:

| Parent table | Partitioning scheme |
|---|---|
| `range_part` | Declarative range partitioning on `created_utc` |
| `rrobin_part` | Round-robin partitioning via inheritance and trigger |

## Implementation

### `range_query(parent_partition_table_name, utc_min_val, utc_max_val, save_table_name, connection)`

Selects every row whose `created_utc` falls in the half-open interval **(`utc_min_val`, `utc_max_val`]**, meaning strictly greater than the minimum and less than or equal to the maximum. All matching rows and columns are saved to `save_table_name`.

### `point_query(parent_partition_table_name, utc_val, save_table_name, connection)`

Selects every row where `created_utc = utc_val` and saves all matching rows and columns to `save_table_name`.

### Behaviour common to both

- Queries run against the **parent** partition table, so PostgreSQL resolves the underlying fragments.
- Results are written to a new table rather than returned from the Python function.
- Saved tables preserve the full column set of the source table.
- PostgreSQL does not guarantee row order without `ORDER BY`, so results are compared independent of physical order. Use `ORDER BY created_utc ASC` when reading a saved table in sorted order.

## Example

```sql
-- Rows with created_utc in (1300000000, 1400000000]
SELECT * FROM range_query_result ORDER BY created_utc ASC;
```

## Setup & Usage

The recommended setup is the course Docker image, which already contains the `fragmentation` database with `subreddits`, `range_part` and `rrobin_part` populated. Rerunning the Assignment 1 code is not required.

```bash
docker pull change1472/cse511-query-processing:latest
docker run --name cse511-query-processing -it change1472/cse511-query-processing:latest
python3 tester.py
```

Alternatively, use a local PostgreSQL 14 environment with the Assignment 1 database loaded.

## What the Tester Checks

| Part | Points | Coverage |
|---|---:|---|
| Point query | 50 | 10 tests × 5 pts, five on `range_part` and five on `rrobin_part` |
| Range query | 50 | 10 tests × 5 pts, five on `range_part` and five on `rrobin_part` |

Tests verify that the result table is created, that it contains the correct rows and columns, that the parent partition table is the one queried, and that range-partitioned and round-robin results agree.

## Repository Contents

```text
Assignment 2/
├── README.md
├── Assignment_ Query Processing.pdf   # assignment handout
└── query_processing.py                # range_query and point_query
```

> The grading harness (`tester.py`) and the partitioned database come from the course image and are not stored here.

## Skills Demonstrated

- Querying partitioned tables through a parent table
- Half-open range predicates and exact-match lookups
- Persisting query results with `CREATE TABLE AS`-style workflows from Python
- Validating that results are independent of the physical partitioning scheme

---

*CSE 511: Data Processing at Scale, Arizona State University. The assignment handout is course material and is credited to its author, Zhichao Cao, Ph.D.*
