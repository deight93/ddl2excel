# ddl2excel

[README in Korean (한국어 안내)](./README.ko.md)

A CLI tool that converts SQL DDL files to structured Excel table specification sheets.

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (recommended for venv and dependency management)

## Quickstart (No Build/Install Needed)

```bash
# 1. Create a virtual environment with uv
uv venv

# 2. Install all dependencies (from pyproject.toml/requirements.txt)
uv sync

# 3. Run directly (no build step needed)
uv run python -m app.main --help

# Example usage:
uv run python -m app.main DDL.sql output.xlsx
uv run python -m app.main --dir ./ddls output.xlsx --lang en
````

## Why uv?

* Fast, reproducible dependency installation (`uv sync`)
* venv isolation, zero global pollution
* No build or install step required—just manage dependencies and run

## Usage

```bash
# Convert a single .sql file to Excel
uv run python -m app.main DDL.sql output.xlsx

# Convert multiple .sql files to Excel (each as a sheet)
uv run python -m app.main table1.sql table2.sql output.xlsx

# Convert all .sql files in a directory
uv run python -m app.main --dir ./ddls output.xlsx

# Select header language (default: Korean, options: ko, en)
uv run python -m app.main DDL.sql output.xlsx --lang en
```

**Note:**
You cannot specify file arguments and `--dir` option at the same time.

## Options

| Option     | Description                                                                 |
| ---------- | --------------------------------------------------------------------------- |
| FILES      | List of DDL .sql files to convert                                           |
| --dir, -d  | Directory containing .sql files (all files will be processed)               |
| --lang, -l | Excel sheet header/title language: `ko` (Korean, default) or `en` (English) |
| OUTPUT     | Output Excel file path                                                      |

## Project Structure

```
app/
  ├── main.py           # Command-line interface (entrypoint)
  ├── const.py          # All style/label constants (multi-language)
  ├── excel_writer.py   # Excel writing logic
  ├── parser.py         # DDL parser logic
  └── utils.py          # Excel style/merge helpers
```
