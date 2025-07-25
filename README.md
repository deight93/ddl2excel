# ddl2excel

[한국어 안내(README in Korean)](./README.ko.md)

A CLI tool that converts SQL DDL files to structured Excel table specification sheets.

## Features

- Supports multiple `.sql` files and directory input
- Each file is output as a separate Excel sheet
- Column/metadata/index headers in both Korean and English (selectable with `--lang`)
- Clean, maintainable Python codebase (no star imports)
- CLI with helpful error messages, English-by-default
- Extensible, production-ready code structure

## Requirements

- Python 3.12+
- [openpyxl](https://openpyxl.readthedocs.io/)
- [typer](https://typer.tiangolo.com/)

Install dependencies:
```bash
pip install -r requirements.txt
````

## Usage

```bash
# Convert a single .sql file to Excel
python app/cli.py DDL.sql output.xlsx

# Convert multiple .sql files to Excel (each as a sheet)
python app/cli.py table1.sql table2.sql output.xlsx

# Convert all .sql files in a directory
python app/cli.py --dir ./ddls output.xlsx

# Select header language (default: Korean, options: ko, en)
python app/cli.py DDL.sql output.xlsx --lang en
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

## Error Handling

* If both file arguments and `--dir` are given, the tool will exit with an error.
* If any file or directory does not exist, or if a directory is passed as a file, a helpful error message is shown.
* Only `.sql` files are processed.

## Example Output

* Each Excel sheet includes:

    * Table specification title
    * Metadata (system/service, author, project, etc.)
    * Column definitions
    * Index info (PK example)
    * All headers and field names in your selected language

## Project Structure

```
app/
  ├── cli.py           # Command-line interface
  ├── const.py         # All style/label constants (multi-language)
  ├── excel_writer.py  # Excel writing logic
  ├── parser.py        # DDL parser logic
  └── utils.py         # Excel style/merge helpers
```
