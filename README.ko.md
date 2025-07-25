# ddl2excel

SQL DDL 파일을 엑셀 테이블 명세서로 변환하는 Python CLI 도구입니다.

## 주요 특징

- 여러 개의 `.sql` 파일 또는 폴더 입력 지원
- 파일별로 엑셀 시트 자동 분리
- 컬럼/메타데이터/인덱스 헤더 한영 선택 가능 (`--lang` 옵션)
- 스타 임포트 없이 명확한 구조의 클린 코드
- 모든 메시지/에러는 영어가 기본, 옵션/도움말은 한영 병기

## 요구사항

- Python 3.12+
- [openpyxl](https://openpyxl.readthedocs.io/)
- [typer](https://typer.tiangolo.com/)

설치:
```bash
pip install -r requirements.txt
````

## 사용법

```bash
# 단일 .sql → 엑셀
python app/cli.py DDL.sql output.xlsx

# 여러 .sql → 엑셀 (각 파일별 시트)
python app/cli.py table1.sql table2.sql output.xlsx

# 폴더 내 모든 .sql → 엑셀
python app/cli.py --dir ./ddls output.xlsx

# 헤더/타이틀 언어 선택 (기본 한글, en: 영어)
python app/cli.py DDL.sql output.xlsx --lang en
```

**참고:**
파일 인자와 `--dir` 옵션은 동시에 사용할 수 없습니다.

## 주요 옵션

| 옵션         | 설명                                      |
| ---------- | --------------------------------------- |
| FILES      | 변환할 DDL .sql 파일 리스트                     |
| --dir, -d  | 폴더 전체의 .sql 파일 일괄 처리                    |
| --lang, -l | 엑셀 시트 헤더/타이틀 언어: `ko`(한글, 기본), `en`(영어) |
| OUTPUT     | 결과 엑셀 파일 경로                             |

## 에러/예외 처리

* 파일 인자와 `--dir` 옵션을 동시에 주면 에러 후 종료
* 파일/디렉토리 미존재, 잘못된 경로 입력 시 에러 메시지 안내
* `.sql` 확장자만 처리

## 엑셀 결과 예시

* 각 시트는 다음 영역으로 구성됩니다:

  * 테이블 명세서 타이틀
  * 시스템/작성자/프로젝트 등 메타정보
  * 컬럼 정의 테이블
  * 인덱스 정보(PK 예시)
  * 모든 헤더 및 필드명 한글/영어 선택 출력

## 프로젝트 구조

```
app/
  ├── cli.py           # 커맨드라인 실행부
  ├── const.py         # 스타일/라벨(다국어) 상수
  ├── excel_writer.py  # 엑셀 작성 로직
  ├── parser.py        # DDL 파싱 로직
  └── utils.py         # 스타일/병합 유틸리티
```
