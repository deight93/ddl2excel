import re

from const import (
    BOLD_FONT,
    BOLD_LARGE_FONT,
    BORDER_THIN,
    CENTER_ALIGN,
    COLUMN_HEADERS,
    COLUMN_WIDTHS,
    FILL_GRAY,
    FILL_HEADER,
    FILL_YELLOW,
    LEFT_ALIGN,
    META_FIELDS,
)
from openpyxl import Workbook
from openpyxl.utils import get_column_letter


def extract_length_from_type(type_str: str) -> str:
    match = re.search(r"\((\d+)\)", type_str)
    return match.group(1) if match else "-"


def set_merged_cell_border(
    ws, border_style, start_row, start_column, end_row, end_column
):
    for row in range(start_row, end_row + 1):
        for col in range(start_column, end_column + 1):
            ws.cell(row=row, column=col).border = border_style


def write_excel_spec(table_spec_dict: dict, output_excel_path: str):
    wb = Workbook()
    wb.remove(wb.active)
    for sheet_name, table_list in table_spec_dict.items():
        for table_spec in table_list:
            ws = wb.create_sheet(title=f"{sheet_name}_{table_spec['table_name']}"[:31])
            ws.sheet_view.zoomScale = 85
            row_idx = 1

            # 1. Table Specification 제목
            ws.merge_cells(
                start_row=row_idx, start_column=1, end_row=row_idx, end_column=12
            )
            ws.cell(row_idx, 1, "Table Specification").font = BOLD_LARGE_FONT
            ws.cell(row_idx, 1).alignment = CENTER_ALIGN
            ws.cell(row_idx, 1).fill = FILL_HEADER
            set_merged_cell_border(ws, BORDER_THIN, row_idx, 1, row_idx, 12)
            row_idx += 1

            # 2. 상단 메타정보
            meta_values = [
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                table_spec["table_name"],
                table_spec["table_name"],
                table_spec["table_comment"],
            ]
            for meta_idx, (meta_field, meta_value) in enumerate(
                zip(META_FIELDS, meta_values, strict=False)
            ):
                ws.merge_cells(
                    start_row=row_idx, start_column=1, end_row=row_idx, end_column=2
                )
                set_merged_cell_border(ws, BORDER_THIN, row_idx, 1, row_idx, 2)
                ws.merge_cells(
                    start_row=row_idx, start_column=3, end_row=row_idx, end_column=12
                )
                set_merged_cell_border(ws, BORDER_THIN, row_idx, 3, row_idx, 12)
                ws.cell(row_idx, 1, meta_field).alignment = LEFT_ALIGN
                ws.cell(row_idx, 1).font = BOLD_FONT
                ws.cell(row_idx, 1).fill = (
                    FILL_YELLOW if 3 <= meta_idx <= 6 else FILL_GRAY
                )
                ws.cell(row_idx, 3, meta_value)
                ws.cell(row_idx, 3).alignment = LEFT_ALIGN
                row_idx += 1

            # 3. 데이터 건수/주기 등
            ws.merge_cells(
                start_row=row_idx, start_column=1, end_row=row_idx, end_column=3
            )
            set_merged_cell_border(
                ws,
                BORDER_THIN,
                start_row=row_idx,
                start_column=1,
                end_row=row_idx,
                end_column=3,
            )
            ws.merge_cells(
                start_row=row_idx, start_column=4, end_row=row_idx, end_column=5
            )
            set_merged_cell_border(
                ws,
                BORDER_THIN,
                start_row=row_idx,
                start_column=4,
                end_row=row_idx,
                end_column=5,
            )
            ws.merge_cells(
                start_row=row_idx, start_column=6, end_row=row_idx, end_column=7
            )
            set_merged_cell_border(
                ws,
                BORDER_THIN,
                start_row=row_idx,
                start_column=6,
                end_row=row_idx,
                end_column=7,
            )
            ws.merge_cells(
                start_row=row_idx, start_column=8, end_row=row_idx, end_column=9
            )
            set_merged_cell_border(
                ws,
                BORDER_THIN,
                start_row=row_idx,
                start_column=8,
                end_row=row_idx,
                end_column=9,
            )
            ws.merge_cells(
                start_row=row_idx, start_column=10, end_row=row_idx, end_column=12
            )
            set_merged_cell_border(
                ws,
                BORDER_THIN,
                start_row=row_idx,
                start_column=10,
                end_row=row_idx,
                end_column=12,
            )
            ws.cell(row_idx, 1, "초기 예상 건수").fill = FILL_HEADER
            ws.cell(row_idx, 4, "증가 예상 건수").fill = FILL_HEADER
            ws.cell(row_idx, 6, "최대 예상 건수").fill = FILL_HEADER
            ws.cell(row_idx, 8, "data 보존 기간").fill = FILL_HEADER
            ws.cell(row_idx, 10, "data 백업 주기").fill = FILL_HEADER
            for col_idx in [1, 4, 6, 8, 10]:
                ws.cell(row_idx, col_idx).alignment = CENTER_ALIGN
                ws.cell(row_idx, col_idx).font = BOLD_FONT
            row_idx += 1

            # 값 라인 병합 및 값 기입
            ws.merge_cells(
                start_row=row_idx, start_column=1, end_row=row_idx, end_column=3
            )
            ws.merge_cells(
                start_row=row_idx, start_column=4, end_row=row_idx, end_column=5
            )
            ws.merge_cells(
                start_row=row_idx, start_column=6, end_row=row_idx, end_column=7
            )
            ws.merge_cells(
                start_row=row_idx, start_column=8, end_row=row_idx, end_column=9
            )
            ws.merge_cells(
                start_row=row_idx, start_column=10, end_row=row_idx, end_column=12
            )
            ws.cell(row_idx, 1, "")  # 초기 예상 건수
            ws.cell(row_idx, 4, "")  # 증가 예상 건수
            ws.cell(row_idx, 6, "")  # 최대 예상 건수
            ws.cell(row_idx, 8, "5년")  # data 보존 기간
            ws.cell(row_idx, 10, "1년")  # data 백업 주기
            row_idx += 1

            # 4. 컬럼 스펙 테이블 헤더
            ws.append(COLUMN_HEADERS)
            ws.merge_cells(
                start_row=row_idx, start_column=8, end_row=row_idx, end_column=10
            )
            ws.cell(row_idx, 8).value = "정의/설명"
            for col_num in range(1, 13):
                cell = ws.cell(row_idx, col_num)
                cell.fill = FILL_HEADER
                cell.font = BOLD_FONT
                cell.alignment = CENTER_ALIGN
                cell.border = BORDER_THIN
            row_idx += 1

            # 5. 컬럼 데이터 (정의/설명 3칸 병합)
            for col_idx, column_spec in enumerate(table_spec["columns"], 1):
                ws.cell(row_idx, 1, col_idx)
                ws.cell(row_idx, 2, column_spec["column_name"])
                ws.cell(row_idx, 3, column_spec["type"].upper())
                ws.cell(row_idx, 4, extract_length_from_type(column_spec["type"]))
                ws.cell(row_idx, 5, "Y" if column_spec.get("pk") else "N")
                ws.cell(row_idx, 6, "Y" if column_spec.get("nn") else "N")
                ws.cell(row_idx, 7, column_spec.get("default") or "-")
                ws.merge_cells(
                    start_row=row_idx, start_column=8, end_row=row_idx, end_column=10
                )
                ws.cell(row_idx, 8, column_spec.get("comment", ""))
                ref_info = "-"
                if column_spec.get("ref_table") and column_spec.get("ref_column"):
                    ref_info = f"{column_spec['ref_table']}.{column_spec['ref_column']}"
                ws.cell(row_idx, 11, ref_info)
                ws.cell(row_idx, 12, "-")
                for col_num in range(1, 13):
                    ws.cell(row_idx, col_num).alignment = (
                        CENTER_ALIGN if col_num in [1, 5, 6] else LEFT_ALIGN
                    )
                    ws.cell(row_idx, col_num).border = BORDER_THIN
                row_idx += 1

            # 6. Index 스펙 (컬럼 데이터 직후 빈 줄 없이 바로)
            index_headers = [
                "no",
                "Index name",
                "",
                "",
                "Index type",
                "",
                "",
                "Unique",
                "",
                "구성 컬럼",
                "",
                "",
            ]
            ws.append(index_headers)
            ws.merge_cells(
                start_row=row_idx, start_column=2, end_row=row_idx, end_column=4
            )  # Index name
            ws.merge_cells(
                start_row=row_idx, start_column=5, end_row=row_idx, end_column=7
            )  # Index type
            ws.merge_cells(
                start_row=row_idx, start_column=8, end_row=row_idx, end_column=9
            )  # Unique
            ws.merge_cells(
                start_row=row_idx, start_column=10, end_row=row_idx, end_column=12
            )  # 구성 컬럼

            for col_num in range(1, 13):
                cell = ws.cell(row_idx, col_num)
                cell.fill = FILL_HEADER
                cell.font = BOLD_FONT
                cell.alignment = CENTER_ALIGN
                cell.border = BORDER_THIN
            row_idx += 1

            # 인덱스 데이터 (PK만 표기 예시)
            index_data = [1, "", "", "", "PK", "", "", "Y", "", "", "", ""]
            ws.append(index_data)
            ws.merge_cells(
                start_row=row_idx, start_column=2, end_row=row_idx, end_column=4
            )
            ws.merge_cells(
                start_row=row_idx, start_column=5, end_row=row_idx, end_column=7
            )
            ws.merge_cells(
                start_row=row_idx, start_column=8, end_row=row_idx, end_column=9
            )
            ws.merge_cells(
                start_row=row_idx, start_column=10, end_row=row_idx, end_column=12
            )
            for col_num in range(1, 13):
                cell = ws.cell(row_idx, col_num)
                cell.alignment = CENTER_ALIGN
                cell.border = BORDER_THIN

            # 열 너비 조정 (12칸)
            for col_num, width in enumerate(COLUMN_WIDTHS, 1):
                ws.column_dimensions[get_column_letter(col_num)].width = width

    wb.save(output_excel_path)
