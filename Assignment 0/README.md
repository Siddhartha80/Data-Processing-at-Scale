# Assignment 0: Database Creation & Loading

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql&logoColor=white)
![SQL](https://img.shields.io/badge/Language-SQL-informational)
![Docker](https://img.shields.io/badge/Environment-Docker-2496ED?logo=docker&logoColor=white)

Build a PostgreSQL database from four large Reddit CSV files: design the schema, bulk-load more than 18 million rows, add integrity constraints, and answer five analytical queries.

📄 [Assignment handout (PDF)](Assignment_Database%20Creation%20%26%20Loading.pdf)

---

## Overview

This assignment covers the core relational database workflow end to end:

1. Inspect the environment and the source data
2. Create the tables with appropriate data types
3. Bulk-load the CSV files
4. Add primary keys, unique constraints and foreign keys
5. Verify the load and run analytical queries

The emphasis is on ingesting a large dataset efficiently and understanding how bulk loading works, rather than on query tuning.

## Dataset

A curated subset of the Pushshift Reddit archive, split across four CSV files.

| Table | Rows | Description | Sample columns |
|---|---:|---|---|
| `authors` | 6,158,212 | Reddit user accounts | `id`, `name`, `created_utc`, `link_karma`, `comment_karma` |
| `subreddits` | 914,067 | Subreddit metadata | `id`, `name`, `display_name`, `subreddit_type`, `subscribers` |
| `submissions` | 1,263,937 | Posts submitted to subreddits | `id`, `author`, `subreddit_id`, `title`, `created_utc`, `ups` |
| `comments` | 10,557,466 | Comments on submissions | `id`, `author`, `subreddit_id`, `subreddit`, `body`, `score` |

Table and column names are lowercase and match the CSV headers exactly.

### Relationships

| Child column | References |
|---|---|
| `submissions.author` | `authors(name)` |
| `submissions.subreddit_id` | `subreddits(name)` |
| `comments.author` | `authors(name)` |
| `comments.subreddit_id` | `subreddits(name)` |
| `comments.subreddit` | `subreddits(display_name)` |

## Approach

**1. Schema creation.** Four empty tables are created with suitable PostgreSQL types for every CSV column.

**2. Bulk loading.** Each CSV is loaded into its matching table with PostgreSQL `COPY`, skipping the header row. `pg_bulkload` is an accepted alternative; only one loader is used on empty tables.

**3. Constraints after loading.** Primary keys, unique constraints and foreign keys are added *after* the data is loaded. This is considerably faster than maintaining constraints while millions of rows are inserted, because PostgreSQL can build each index once instead of updating it per row.

**4. Verification.** Exact row counts for all four tables are checked against the figures above.

## Queries

All queries live in `queries/queries.sql`.

| # | Task | Notes |
|---|---|---|
| 1 | Count the comments written by one specific author | Single value named `comments count` |
| 2 | Count subreddits per `subreddit_type` | Aggregation with `GROUP BY` |
| 3 | Top 10 subreddits by comment volume | Includes average score rounded to 2 decimals |
| 4 | Authors with average karma above 1,000,000 | Adds a label: `0` if link karma ≥ comment karma, otherwise `1`; sorted by average karma |
| 5 | Comments by subreddit type for the `[deleted_user]` author | Join between `comments` and `subreddits` |

Reference result sizes: Query 1 returns `18`; Queries 2 to 5 return 6, 10, 42 and 2 rows respectively.

## Environment

- PostgreSQL 14
- Docker image: [`change1472/cse511-database-creation`](https://hub.docker.com/r/change1472/cse511-database-creation)
- Connection: `postgres` / `postgres` on `127.0.0.1:5432`

```bash
docker pull change1472/cse511-database-creation:latest
docker run --name cse511-database-creation-loading -it change1472/cse511-database-creation:latest
```

PostgreSQL starts automatically with the container. To return to the same container later:

```bash
docker start -ai cse511-database-creation-loading
```

## How to Run

From `/root/cse511/database-creation-and-loading/` inside the container:

```bash
./database.sh reset --yes   # start from empty tables
./assignment.sh all         # create tables, load with COPY, add relationships
./run_queries.sh            # run Query 1-5, output saved to output/query_results.txt
./autograde.sh              # illustrative self-check
./database.sh counts        # exact row counts for all four tables
```

Individual stages are also available: `./assignment.sh tables`, `copy`, `pg_bulkload` and `relations`.

## Repository Contents

```text
Assignment 0/
├── README.md
├── Assignment_Database Creation & Loading.pdf   # assignment handout
├── schema/
│   ├── create_tables.sql                        # table definitions
│   └── create_relations.sql                     # keys and foreign keys
├── queries/
│   └── queries.sql                              # Query 1-5
└── output/
    └── query_results.txt                        # query output
```

> The source CSV files are large and provided by the course, so they are not stored in this repository.

## Skills Demonstrated

- Relational schema design and data type selection
- High-volume data ingestion with `COPY` and `pg_bulkload`
- Keys, constraints and referential integrity
- Aggregations, joins and ranking queries in SQL
- Reproducible database environments with Docker

---

*CSE 511: Data Processing at Scale, Arizona State University. The assignment handout is course material and is credited to its author, Zhichao Cao, Ph.D.*
