# CURRENTLY NONFUNCTIONAL

# dbdiff

A small Python tool for comparing SQLite and SQLCipher databases.

## Installation

Clone the repo:

```bash
git clone https://github.com/DesmondN1ckl/dbdiff.git
cd dbdiff
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Basic run:

```bash
python3 dbscan.py db1.sqlite db2.sqlite --values old_value new_value
```
