# Data Processing at Scale

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Analytics-informational)
![Docker](https://img.shields.io/badge/Docker-Environment-2496ED?logo=docker&logoColor=white)

Coursework for **CSE 511: Data Processing at Scale** at Arizona State University. The assignments work with a large Reddit dataset (over 18 million rows) and cover database design, bulk data loading, partitioning, and query processing with PostgreSQL, SQL, and Python. This repository is updated as new assignments are completed.

**Topics covered so far:** `postgresql` · `sql` · `python` · `bulk loading` · `partitioning` · `query processing`

## Assignments

Early assignments build on one another, from raw CSV files to a relational database, then to partitioned tables and a query processor.

| # | Assignment | Focus | Tools |
|---|---|---|---|
| 0 | [Database Creation & Loading](Assignment%200/) | Schema design, bulk loading with `COPY`, constraints, analytical SQL | PostgreSQL, SQL, Docker |
| 1 | [Data Fragmentation](Assignment%201/) | Range and round-robin partitioning, triggers, table inheritance | PostgreSQL, Python, psycopg2 |
| 2 | [Query Processing](Assignment%202/) | Range and point queries over partitioned tables | PostgreSQL, Python, psycopg2 |

## Dataset

A curated subset of the Pushshift Reddit archive:

| Table | Rows |
|---|---:|
| `comments` | 10,557,466 |
| `authors` | 6,158,212 |
| `submissions` | 1,263,937 |
| `subreddits` | 914,067 |

The CSV files are provided by the course and are not stored in this repository.

## Repository Structure

```text
Data-Processing-at-Scale/
├── README.md
├── Assignment 0/        # Database creation & loading
│   ├── README.md
│   └── Assignment_Database Creation & Loading.pdf
├── Assignment 1/        # Data fragmentation
│   ├── README.md
│   └── Assignment_ Data Fragmentation.pdf
└── Assignment 2/        # Query processing
    ├── README.md
    └── Assignment_ Query Processing.pdf
```

Each assignment folder has its own README covering the problem, approach, how to run it, and what is verified.

## Key Concepts

- **Bulk ingestion.** Loading millions of rows with `COPY`, and adding constraints afterwards for speed.
- **Relational modelling.** Primary keys, unique constraints and foreign keys across four related tables.
- **Horizontal partitioning.** Declarative range partitioning versus round-robin simulated with inheritance and a `BEFORE INSERT` trigger.
- **Query processing.** Range and point lookups against a partitioned layout, with results persisted to new tables.

## Getting Started

All assignments target **PostgreSQL 14**. The course supplies Docker images that include the database and data, which is the simplest way to reproduce the work.

```bash
# Assignment 0
docker pull change1472/cse511-database-creation:latest

# Assignment 2 (includes the partitioned database from Assignment 1)
docker pull change1472/cse511-query-processing:latest
```
See each assignment's README for the exact commands.

## Author

**Siddhartha Mettu**
M.S. Data Science, Arizona State University

[LinkedIn](https://linkedin.com/in/siddhartha-mettu/) · [GitHub](https://github.com/Siddhartha80)

---

*Assignment handouts are course material credited to their author, Zhichao Cao, Ph.D.*
