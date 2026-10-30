# Data Processing at Scale

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14-336791?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3-3776AB?logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-Analytics-informational)
![Docker](https://img.shields.io/badge/Docker-Environment-2496ED?logo=docker&logoColor=white)

Coursework for **CSE 511: Data Processing at Scale** at Arizona State University. Three progressive assignments take a large Reddit dataset (over 18 million rows) from raw CSV files to a partitioned PostgreSQL database with a custom query processor.

## Course Progression

The assignments build on one another:

```text
 CSV files ──► Relational database ──► Partitioned tables ──► Query processor
 (Assignment 0)       (Assignment 0)       (Assignment 1)        (Assignment 2)
```

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

Assignments 1 and 2 also need Python 3 and `psycopg2`:

```bash
pip install psycopg2-binary
```

See each assignment's README for the exact commands.

## Author

**Siddhartha Mettu**
M.S. Data Science, Arizona State University

[LinkedIn](https://linkedin.com/in/siddhartha-mettu/) · [GitHub](https://github.com/Siddhartha80)

---

*Assignment handouts are course material credited to their author, Zhichao Cao, Ph.D.*
