from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

FILL_YELLOW = PatternFill("solid", fgColor="FFF000")
FILL_GRAY = PatternFill("solid", fgColor="E6E6E6")
FILL_HEADER = PatternFill("solid", fgColor="C0C0C0")
FILL_WHITE = PatternFill("solid", fgColor="FFFFFF")

BORDER_THIN = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)

CENTER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_ALIGN = Alignment(horizontal="left", vertical="center", wrap_text=True)
BOLD_FONT = Font(bold=True)
BOLD_LARGE_FONT = Font(bold=True, size=13)


META_FIELDS = [
    "시스템/서비스",
    "작성자",
    "작성일",
    "프로젝트명",
    "dbms",
    "db name",
    "schema name",
    "table name",
    "테이블명",
    "상세설명",
]

COLUMN_HEADERS = [
    "no",
    "column name",
    "type",
    "length",
    "PK",
    "NN",
    "Default",
    "정의/설명",
    "",
    "",
    "참조테이블",
    "비고",
]

COLUMN_WIDTHS = [5, 22, 14, 8, 6, 6, 12, 24, 2, 2, 16, 10]
