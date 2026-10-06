# Project Notes

## What is ETL?

ETL means:

Extract
Transform
Load

### Extract

Get data from an external source.

In this project:

YouTube Data API → Python

### Transform

Clean and structure the extracted data.

In this project:

Raw YouTube JSON → validated Python records

### Load

Store the transformed data.

In this project:

Python records → PostgreSQL

---

## Why PostgreSQL?

PostgreSQL is a relational database suitable for storing
structured historical data.

---

## Why historical snapshots?

YouTube statistics such as views, likes and comments change
over time.

If only the latest value is stored, previous values are lost.

Therefore, the project stores daily snapshots.

---

## Why separate videos and daily statistics?

Video metadata is relatively stable.

Statistics change daily.

Separating them reduces unnecessary duplication and makes
the database structure easier to understand.

---

## Why use an API key?

The project only needs access to public YouTube information.
An API key identifies the application making the request.

---

## Why .env?

The .env file keeps credentials outside the source code.

---

## Why GitHub?

GitHub provides version control and allows the development
history and source code to be maintained in one repository.

Sensitive credentials are excluded.

---

## Why logging?

Logging provides a record of what happened during each ETL run.

It helps identify:

- API errors
- database errors
- data processing problems
- successful runs
- execution duration

---

## Main architecture

YouTube
    ↓
API
    ↓
Extract
    ↓
Transform
    ↓
Load
    ↓
PostgreSQL