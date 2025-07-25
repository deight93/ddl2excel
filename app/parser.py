import re
from pathlib import Path
from typing import Any


class DDLParser:
    """
    DDL 파싱 책임. 상태: 원본 텍스트, 코멘트 맵 등. 메서드로 분할.
    """

    TABLE_COMMENT_REGEX = re.compile(
        r"comment\s+on\s+table\s+([a-zA-Z0-9_\"\.]+)\s+is\s+'(.*?)';", re.IGNORECASE
    )
    COLUMN_COMMENT_REGEX = re.compile(
        r"comment\s+on\s+column\s+([a-zA-Z0-9_\"\.]+)\.([a-zA-Z0-9_\"\.]+)\s+is\s+'(.*?)';",
        re.IGNORECASE,
    )

    def __init__(self, ddl_text: str):
        self.ddl_text = ddl_text
        self.table_comments = self._parse_table_comments()
        self.column_comments = self._parse_column_comments()
        self.statements = self._split_statements()

    def _split_statements(self) -> list[str]:
        """; 기준으로 쿼리를 분리, 문자열 리터럴('') 예외 처리"""
        statements, current, in_quote = [], "", 0
        for char in self.ddl_text:
            current += char
            if char == "'":
                in_quote = 1 - in_quote
            if char == ";" and not in_quote:
                statements.append(current.strip())
                current = ""
        if current.strip():
            statements.append(current.strip())
        return [s for s in statements if s]

    def _parse_table_comments(self) -> dict[str, str]:
        return {
            m.group(1).replace('"', ""): m.group(2)
            for m in self.TABLE_COMMENT_REGEX.finditer(self.ddl_text)
        }

    def _parse_column_comments(self) -> dict[tuple, str]:
        out = {}
        for m in self.COLUMN_COMMENT_REGEX.finditer(self.ddl_text):
            table, col, comment = (
                m.group(1).replace('"', ""),
                m.group(2).replace('"', ""),
                m.group(3),
            )
            out[(table, col)] = comment
        return out

    def parse_tables(self) -> list[dict[str, Any]]:
        """
        CREATE TABLE 구문 기준 테이블/컬럼 파싱 및 코멘트 매핑
        """
        tables = []
        for stmt in self.statements:
            if not stmt.lower().startswith("create table"):
                continue
            parsed = self._parse_create_table(stmt)
            if parsed:
                table_name, columns = parsed
                # 컬럼별 코멘트 할당
                for col in columns:
                    col["comment"] = self.column_comments.get(
                        (table_name, col["column_name"]), ""
                    )
                tables.append(
                    {
                        "table_name": table_name,
                        "columns": columns,
                        "table_comment": self.table_comments.get(table_name, ""),
                    }
                )
        return tables

    def _parse_create_table(self, statement: str):
        """
        CREATE TABLE 구문에서 테이블명, 컬럼 스펙 추출 (기존 파싱 코드)
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

        column_block_list, current_block, paren_depth = [], "", 0
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

        columns, primary_key_columns, foreign_key_columns = [], set(), set()
        for column_def in column_block_list:
            column_def = column_def.replace("\n", " ").strip()
            pk_match = re.match(
                r"primary key\s*\((.+?)\)\s*$", column_def, re.IGNORECASE
            )
            if pk_match:
                for pk_col in pk_match.group(1).split(","):
                    primary_key_columns.add(pk_col.strip().replace('"', ""))
                continue
            if column_def.lower().startswith(("unique", "check")):
                continue
            column_match = re.match(r"^([a-zA-Z0-9_\"\.]+)\s+(.+)$", column_def)
            if not column_match:
                continue
            column_name, rest = column_match.group(1), column_match.group(2)
            type_match = re.match(
                r"([a-zA-Z0-9_\[\]\"\.]+(\s*\(\s*\d+(?:\s*,\s*\d+)?\s*\))?(\[\])?)",
                rest,
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
    parser = DDLParser(ddl_file_path.read_text(encoding="utf-8"))
    return parser.parse_tables()
