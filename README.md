# Pocket Ledger

A small command-line expense log using Python's standard library and a local CSV file. No packages or account required. Designed with Python 3.9-era syntax and APIs.

## Project context

Created in September 2026 as a reconstruction of a modest December 2020 learning project. Git author and committer dates are intentionally assigned to December 5, 7, 12, and 16, 2020; they do not establish that the code existed or was published then. The repository was created in 2026.

## Usage

```sh
python3 ledger.py add "Coffee" 3.50 --date 2020-12-05
```

The date defaults to today. Amounts must be positive, at most 999999.99, and have no more than two decimal places. Use a single currency per file. Data stays in `expenses.csv` in your current directory; that file is ignored by Git. Use `--file /path/to/log.csv` before the command to select another file in an existing directory. Invalid data produces an error instead of overwriting the file. Intended for one process at a time.

Show recorded expenses with `python3 ledger.py list`. An empty file list shows a helpful message.

Show all-time totals with `python3 ledger.py summary`, or filter a month with `python3 ledger.py summary --month 2020-12`. Decimal arithmetic keeps amounts exact.

## Checks

Run `python3 -m unittest -v`. The tests use temporary files and cover persistence, quoted descriptions, exact totals, invalid input, malformed files, and inaccessible paths. Verified on Python 3.9 and Python 3.13. The implementation uses only standard-library features available in Python 3.9; a currently supported Python version can also run it.
