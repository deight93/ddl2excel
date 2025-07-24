from pathlib import Path

import typer
from excel_writer import write_excel_spec
from parser import parse_ddl_file

app = typer.Typer(help="DDL → Excel 테이블 스펙 변환기")


def collect_sql_files(
    ddl_file_paths: list[Path] | None, sql_directory: Path | None
) -> list[Path]:
    """
    DDL 파일 리스트와 디렉토리에서 .sql 파일 경로를 모두 수집
    """
    sql_file_list: list[Path] = []
    if sql_directory:
        sql_file_list.extend(sql_directory.glob("*.sql"))
    if ddl_file_paths:
        sql_file_list.extend(Path(file_path) for file_path in ddl_file_paths)
    return sql_file_list


@app.command()
def main(
    ddl_file_paths: list[Path] = typer.Argument(
        None, help="변환할 DDL .sql 파일 리스트", exists=False
    ),
    output_excel_path: Path = typer.Argument(
        ..., help="생성할 엑셀 파일명 (예: output.xlsx)"
    ),
    sql_directory: Path = typer.Option(
        None, "--dir", "-d", help="폴더 전체 변환 (모든 .sql)"
    ),
):
    """
    여러 DDL(.sql) → 단일 Excel로 각 파일별 시트로 변환
    """
    sql_file_list = collect_sql_files(ddl_file_paths, sql_directory)
    if not sql_file_list:
        typer.echo("*.sql 파일을 지정하거나 --dir 옵션으로 폴더를 입력하세요.")
        raise typer.Exit(1)

    table_spec_dict: dict[str, list] = {}
    for sql_file_path in sql_file_list:
        table_list = parse_ddl_file(sql_file_path)
        sheet_name = sql_file_path.stem
        table_spec_dict[sheet_name] = table_list

    write_excel_spec(table_spec_dict, output_excel_path)
    typer.echo(f"[+] 변환 완료 → {output_excel_path}")


if __name__ == "__main__":
    app()
