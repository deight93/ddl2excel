import re
from pathlib import Path

# 테이블/컬럼 COMMENT 정규식
TABLE_COMMENT_REGEX = re.compile(
    r"comment\s+on\s+table\s+([a-zA-Z0-9_\"\.]+)\s+is\s+'(.*?)';", re.IGNORECASE
)
COLUMN_COMMENT_REGEX = re.compile(
    r"comment\s+on\s+column\s+([a-zA-Z0-9_\"\.]+)\.([a-zA-Z0-9_\"\.]+)\s+is\s+'(.*?)';",
    re.IGNORECASE,
)


def split_statements(sql: str) -> list[str]:
    """
    세미콜론(;) 기준으로 쿼리를 분리, 문자열 리터럴('') 내부는 예외 처리
    """
    statements = []
    current_statement = ""
    in_single_quote = 0
    for char in sql:
        current_statement += char
        if char == "'":
            in_single_quote = 1 - in_single_quote
        if char == ";" and in_single_quote == 0:
            statements.append(current_statement.strip())
            current_statement = ""
    if current_statement.strip():
        statements.append(current_statement.strip())
    return [stmt for stmt in statements if stmt]


def parse_create_table(statement: str):
    """
    CREATE TABLE 구문에서 테이블명, 컬럼 스펙 추출
    """
    table_match = re.match(
        r"create\s+table\s+(?:if\s+not\s+exists\s+)?([a-zA-Z0-9_\"\.]+)\s*\((.+)\)",
        statement,
        re.IGNORECASE | re.DOTALL,
    )
    if not table_match:
        return None
    table_name = table_match.group(1).replace('"', "")
    table_body = table_match.group(2)

    column_block_list = []
    current_block = ""
    paren_depth = 0
    for char in table_body:
        if char == "(":
            paren_depth += 1
        elif char == ")" and paren_depth > 0:
            paren_depth -= 1
        if char == "," and paren_depth == 0:
            if current_block.strip():
                column_block_list.append(current_block.strip())
            current_block = ""
        else:
            current_block += char
    if current_block.strip():
        column_block_list.append(current_block.strip())

    columns = []
    primary_key_columns = set()
    foreign_key_columns = set()

    for column_def in column_block_list:
        column_def = column_def.replace("\n", " ").strip()
        pk_match = re.match(r"primary key\s*\((.+?)\)\s*$", column_def, re.IGNORECASE)
        if pk_match:
            for pk_col in pk_match.group(1).split(","):
                primary_key_columns.add(pk_col.strip().replace('"', ""))
            continue

        column_match = re.match(r"^([a-zA-Z0-9_\"\.]+)\s+(.+)$", column_def)
        if not column_match:
            continue
        column_name, rest = column_match.group(1), column_match.group(2)
        type_match = re.match(
            r"([a-zA-Z0-9_\[\]\"\.]+(\s*\(\s*\d+(?:\s*,\s*\d+)?\s*\))?(\[\])?)", rest
        )
        if not type_match:
            continue
        column_type = type_match.group(1)
        rest_attrs = rest[type_match.end() :].strip()
        default_value = None
        default_match = re.search(
            r"default\s+(.+?)(?=\s+(not\s+null|null|constraint|,|$))",
            rest_attrs,
            re.IGNORECASE,
        )
        if default_match:
            default_value = default_match.group(1).strip()
        is_not_null = bool(re.search(r"\bnot\s+null\b", rest_attrs, re.IGNORECASE))
        is_primary_key = bool(
            re.search(r"\bprimary\s+key\b", rest_attrs, re.IGNORECASE)
        )
        fk_constraint_match = re.match(
            r'constraint\s+[a-zA-Z0-9_"]*\s*foreign\s+key\s*\(([^)]+)\)\s*references\s+([a-zA-Z0-9_"]+)\s*\(([^)]+)\)',
            column_def,
            re.IGNORECASE,
        )
        if fk_constraint_match:
            fk_columns = [
                c.strip().replace('"', "")
                for c in fk_constraint_match.group(1).split(",")
            ]
            ref_table = fk_constraint_match.group(2).replace('"', "")
            ref_columns = [
                c.strip().replace('"', "")
                for c in fk_constraint_match.group(3).split(",")
            ]
            for fk_col, ref_col in zip(fk_columns, ref_columns, strict=False):
                foreign_key_columns.add((fk_col, ref_table, ref_col))
            continue

        ref_table = ref_column = None

        columns.append(
            {
                "column_name": column_name,
                "type": column_type,
                "pk": is_primary_key,
                "nn": is_not_null,
                "default": default_value,
                "attrs": rest_attrs,
                "ref_table": ref_table,
                "ref_column": ref_column,
            }
        )

    for fk_col, ref_table, ref_col in foreign_key_columns:
        for col in columns:
            if col["column_name"] == fk_col:
                col["ref_table"] = ref_table
                col["ref_column"] = ref_col

    for col in columns:
        if col["column_name"] in primary_key_columns:
            col["pk"] = True
        if col["pk"]:
            col["nn"] = True

    return table_name, columns


def parse_ddl_file(ddl_file_path: Path):
    """
    DDL 파일을 파싱하여 테이블 구조 및 코멘트 정보를 추출
    """
    file_content = ddl_file_path.read_text(encoding="utf-8")
    table_comments = {
        match.group(1).replace('"', ""): match.group(2)
        for match in TABLE_COMMENT_REGEX.finditer(file_content)
    }
    column_comments = {}
    for match in COLUMN_COMMENT_REGEX.finditer(file_content):
        table, column, comment = match.group(1), match.group(2), match.group(3)
        table = table.replace('"', "")
        column = column.replace('"', "")
        column_comments[(table, column)] = comment

    statements = split_statements(file_content)
    table_list = []
    for statement in statements:
        if statement.lower().startswith("create table"):
            parsed = parse_create_table(statement)
            if parsed:
                table_name, columns = parsed
                # 컬럼별 코멘트 할당
                for column in columns:
                    column["comment"] = column_comments.get(
                        (table_name, column["column_name"]), ""
                    )
                table_list.append(
                    {
                        "table_name": table_name,
                        "columns": columns,
                        "table_comment": table_comments.get(table_name, ""),
                    }
                )
    return table_list
