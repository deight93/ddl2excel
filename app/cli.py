from pathlib import Path

import typer
from excel_writer import write_excel_spec
from parser import parse_ddl_file

app = typer.Typer(
    help="DDL → Excel Table Specification Converter (DDL → 엑셀 테이블 스펙 변환기)"
)


def collect_sql_files(
    ddl_file_paths: list[Path] | None, sql_directory: Path | None
) -> list[Path]:
    """
    Collect DDL .sql files from list and/or directory.
    DDL 파일 리스트와 디렉토리에서 .sql 파일 경로를 모두 수집합니다.
    """
    sql_file_list: list[Path] = []

    # 디렉토리 모드
    if sql_directory:
        if not sql_directory.exists() or not sql_directory.is_dir():
            typer.echo(f"[ERROR] --dir: '{sql_directory}' is not a valid directory.")
            raise typer.Exit(1)
        sql_file_list.extend([p for p in sql_directory.glob("*.sql") if p.is_file()])

    # 파일 인자 모드
    if ddl_file_paths:
        for file_path in ddl_file_paths:
            path = Path(file_path)
            if path.is_dir():
                typer.echo(
                    f"[ERROR] '{file_path}' is a directory. Use --dir for directories."
                )
                raise typer.Exit(1)
            if not path.is_file():
                typer.echo(f"[ERROR] '{file_path}' does not exist or is not a file.")
                raise typer.Exit(1)
            sql_file_list.append(path)

    return sql_file_list


@app.command()
def main(
    ddl_file_paths: list[Path] = typer.Argument(
        None,
        help="List of DDL .sql files to convert (변환할 DDL .sql 파일 리스트)",
        exists=False,
    ),
    output_excel_path: Path = typer.Argument(
        ..., help="Output Excel file name (생성할 엑셀 파일명, 예: output.xlsx)"
    ),
    sql_directory: Path = typer.Option(
        None,
        "--dir",
        "-d",
        help="Directory to convert all .sql files (폴더 전체 변환, 모든 .sql 파일 처리)",
    ),
    lang: str = typer.Option(
        "ko",
        "--lang",
        "-l",
        help="Excel header language: ko (Korean, 기본값), en (English) | 엑셀 시트 타이틀/헤더 언어 (ko: 한글, en: 영어)",
        show_default=True,
    ),
):
    """
    Convert multiple DDL(.sql) files to a single Excel file, each as a sheet.
    여러 DDL(.sql) 파일을 하나의 Excel 파일로 변환 (파일별 시트 생성)
    """
    # --- lang validation
    if lang not in {"ko", "en"}:
        typer.echo(
            f"[ERROR] --lang option supports only 'ko' or 'en'. (입력값: {lang})\n--lang 옵션에는 'ko' 또는 'en'만 입력할 수 있습니다."
        )
        raise typer.Exit(1)

    # --- 인자와 옵션 동시 입력 방지
    if ddl_file_paths and sql_directory:
        typer.echo(
            "[ERROR] Specify either .sql files *or* --dir option, not both.\n파일 인자와 --dir 옵션을 동시에 지정할 수 없습니다."
        )
        raise typer.Exit(1)

    sql_file_list = collect_sql_files(ddl_file_paths, sql_directory)
    if not sql_file_list:
        typer.echo(
            "Specify one or more .sql files, or use --dir to provide a folder.\n*.sql 파일을 지정하거나 --dir 옵션으로 폴더를 입력하세요."
        )
        raise typer.Exit(1)

    table_spec_dict: dict[str, list] = {}
    for sql_file_path in sql_file_list:
        try:
            table_list = parse_ddl_file(sql_file_path)
        except Exception as e:
            typer.echo(f"[ERROR] Failed to parse file: {sql_file_path}\n{e}")
            raise typer.Exit(1)
        sheet_name = sql_file_path.stem
        table_spec_dict[sheet_name] = table_list

    try:
        write_excel_spec(table_spec_dict, output_excel_path, lang=lang)
    except Exception as e:
        typer.echo(f"[ERROR] Failed to write Excel file: {output_excel_path}\n{e}")
        raise typer.Exit(1)

    typer.echo(f"[+] Conversion complete → {output_excel_path} (Language: {lang})")


if __name__ == "__main__":
    app()
