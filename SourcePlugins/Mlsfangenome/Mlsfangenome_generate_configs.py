# pylint: disable=line-too-long, too-many-lines

"""
Generates MLS Fan Genome derived configuration and SQL files from a data dictionary Excel workbook
and Jinja templates, driven by metadata at:
    config/{feature}/templates/{version}/config_generator_metadata.json.

Behavior:
- Never modifies the input Excel file (opened read-only).
- Validates workbook sheet formats strictly; fails fast on any deviation.
- Skips hidden sheets and the sheet named exactly "Object Summary".
- Uses FileMatchText and MLSFanGenomeObjectName from the A:B key/value section of each sheet.
- Uses D:I field section for per-column definitions and validation (ColumnName required, Y/N flags, valid Snowflake data types, no duplicates).
- Renders templates listed in metadata; both template file paths and output paths are Jinja-rendered.
- Creates parent directories as needed; never overwrites existing files; supports --dry-run.
- Renders environment files for dev/qa/prod using additional_settings.json.
- Applies instance suffix rules to object names and filenames as specified (environment files excluded).
"""


from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from tqdm import tqdm
from openpyxl import load_workbook  # type: ignore # pylint: disable=import-error
from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    Template,
    TemplateNotFound,
)


# -----------------------------
# Utility and model structures
# -----------------------------

# -----------------------------
# Module constants (behavior-preserving)
# -----------------------------

# First worksheet must be one of these names (ignored during parsing)
FIRST_SHEET_ALLOWED = {"Worksheet List", "Object Summary"} # NOSONAR

# Non-entity sheet prefixes to skip during entity parsing
NON_ENTITY_PREFIXES = ("rawaudience", "standardization")

# Required keys in the A:B TableInfo map
REQUIRED_TABLEINFO_KEYS = ("MLSFanGenomeObjectName",)

# Per-entity generation exclusions (do not generate for these entry names/objects)
EXCLUDED_ENTRY_NAMES = {
    "stage_model_per_entity",
    "copy_into_stage_sql_per_entity",
    "flatten_sql_per_entity",
    "dedup_sql_per_entity",
}
EXCLUDED_OBJECT_NAMES = {
    "account",
    "accountcontactrelation",
    "asset",
    "campaign",
    "campaignmember",
    "case",
    "contract",
    "emailmessage",
    "event",
    "lead",
    "opportunity",
    "order",
    "product",
    "profile",
    "recordtype",
    "task",
    "user",
}

# Default DLP columns that should always be included in the DLP metadata output even when
# the source data dictionary does not explicitly flag them. Keys are MLS Fan Genome objects
# (lowercase) and values are lists of Snowflake column names.
DEFAULT_DLP_COLUMNS_BY_OBJECT = {
    "account": ["ACCOUNTDESCRIPTION", "DESCRIPTION"],
    "asset": ["DESCRIPTION", "PRODUCTDESCRIPTION"],
    "campaign": ["DESCRIPTION"],
    "campaignmember": ["DESCRIPTION"],
    "case": ["COMMENTS", "DESCRIPTION", "REASON", "SUBJECT", "TYPE"],
    "casecomment": ["COMMENTBODY"],
    "contact": ["DESCRIPTION"],
    "contract": ["DESCRIPTION"],
    "emailmessage": ["TEXTBODY"],
    "event": ["DESCRIPTION", "SUBJECT"],
    "individual": ["CONSUMERCREDITSCORE"],
    "lead": ["DESCRIPTION"],
    "opportunity": ["DESCRIPTION", "NAME"],
    "opportunitylineitem": ["DESCRIPTION", "NAME"],
    "opportunitystage": ["DESCRIPTION"],
    "order": ["DESCRIPTION"],
    "pricebook": ["DESCRIPTION"],
    "product": ["DESCRIPTION"],
    "product2": ["DESCRIPTION"],
    "profile": ["DESCRIPTION"],
    "recordtype": ["DESCRIPTION"],
    "socialpost": ["CONTENT"],
    "task": ["CALLDISPOSITION", "CALLOBJECT", "DESCRIPTION", "SUBJECT"],
    "user": ["ABOUTME", "EMAILENCODINGKEY", "OUTOFOFFICEMESSAGE", "STAYINTOUCHNOTE"],
    "userrole": ["ROLLUPDESCRIPTION"],
}


def err(msg: str) -> None:
    """Print an error message to stderr with ERROR prefix.

    Args:
        msg: The error message to display.
    """
    print(f"ERROR: {msg}", file=sys.stderr)


def terminate(msg: str, code: int = 2) -> None:
    """Print an error message to stderr and exit the program.

    Args:
        msg: The error message to display.
        code: The exit code to use (default: 2).
    """
    err(msg)
    sys.exit(code)


def read_json(path: Path) -> Any: # pylint: disable=inconsistent-return-statements
    """Read and parse a JSON file.

    Args:
        path: Path to the JSON file to read.

    Returns:
        The parsed JSON data structure.

    Raises:
        SystemExit: If the file is not found or contains invalid JSON.
    """
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        terminate(f"Required JSON file not found: {path}")
    except json.JSONDecodeError as e:
        terminate(f"Invalid JSON at {path}: {e}")


def jinja_env_for_paths() -> Environment:
    """Create a Jinja2 environment for path templating.

    Uses StrictUndefined to ensure missing variables cause errors.

    Returns:
        A Jinja2 Environment configured for path rendering.
    """
    # For path templating (and content), make missing variables an error.
    return Environment(undefined=StrictUndefined, autoescape=False)


def jinja_env_for_content(loader_root: Path) -> Environment:
    """Create a Jinja2 environment for content templating.

    Args:
        loader_root: Root directory for template file loading.

    Returns:
        A Jinja2 Environment with FileSystemLoader configured for content rendering.
    """
    env = Environment(
        loader=FileSystemLoader(str(loader_root)),
        undefined=StrictUndefined,
        autoescape=False,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    # Utility filter used by some templates (e.g., matching_options)
    env.filters["tojson"] = json.dumps
    return env


def _print_progress(current: int, total: int, label: str = "Progress", width: int = 40) -> None:
    """Render a simple in-place progress bar without external deps.

    Prints a single-line bar like: "Progress [#####.....] 12/34" and uses carriage return
    so it updates in place. Call with current from 1..total.
    """
    if total <= 0:
        return
    ratio = max(0.0, min(1.0, current / float(total)))
    filled = int(width * ratio)
    progress_bar = "#" * filled + "." * (width - filled)
    msg = f"\r{label} [{progress_bar}] {current}/{total}"
    sys.stderr.write(msg)
    sys.stderr.flush()


def build_instance_suffixes(instance: Optional[str]) -> Tuple[str, str]:
    """Return (lower, upper) instance suffix values including leading underscore or empty strings."""
    if not instance:
        return "", ""
    return f"_{instance.lower()}", f"_{instance.upper()}"


def add_instance_ctx(ctx: Dict[str, Any], instance: Optional[str]) -> None:
    """Augment context with instance suffix variables."""
    low, up = build_instance_suffixes(instance)
    ctx["instance_suffix"] = low
    ctx["instance_suffix_upper"] = up


def to_bool_yn(v: str) -> Optional[bool]:
    """Convert Y/N string values to boolean.

    Args:
        v: String value to convert, typically 'Y' or 'N'.

    Returns:
        True if 'Y', False if 'N', None if neither (case-insensitive).
    """
    if v is None:
        return None
    s = str(v).strip().upper()
    if s == "Y":
        return True
    if s == "N":
        return False
    return None


def is_blank(value: Any) -> bool:
    """Check if a value is considered blank.

    Args:
        value: Value to check for blankness.

    Returns:
        True if value is None or empty/whitespace-only string, False otherwise.
    """
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def normalize_ws_header_value(v: Any) -> str:
    """Normalize worksheet header values to strings.

    Args:
        v: Header value from worksheet cell.

    Returns:
        Stripped string representation of the value, empty string if None.
    """
    return str(v).strip() if v is not None else ""


# Reserved words that must not be used as bare column names (case-insensitive)
_RESERVED_WORDS = {
    "ACCOUNT",
    "ALL",
    "ALTER",
    "AND",
    "ANY",
    "AS",
    "BETWEEN",
    "BY",
    "CASE",
    "CAST",
    "CHECK",
    "COLUMN",
    "CONNECT",
    "CONNECTION",
    "CONSTRAINT",
    "CREATE",
    "CROSS",
    "CURRENT",
    "CURRENT_DATE",
    "CURRENT_TIME",
    "CURRENT_TIMESTAMP",
    "CURRENT_USER",
    "DATABASE",
    "DELETE",
    "DISTINCT",
    "DROP",
    "ELSE",
    "EXISTS",
    "FALSE",
    "FOLLOWING",
    "FOR",
    "FROM",
    "FULL",
    "GRANT",
    "GROUP",
    "GSCLUSTER",
    "HAVING",
    "ILIKE",
    "IN",
    "INCREMENT",
    "INNER",
    "INSERT",
    "INTERSECT",
    "INTO",
    "IS",
    "ISSUE",
    "JOIN",
    "LATERAL",
    "LEFT",
    "LIKE",
    "LOCALTIME",
    "LOCALTIMESTAMP",
    "MINUS",
    "NATURAL",
    "NOT",
    "NULL",
    "OF",
    "ON",
    "OR",
    "ORDER",
    "ORGANIZATION",
    "QUALIFY",
    "REGEXP",
    "REVOKE",
    "RIGHT",
    "RLIKE",
    "ROW",
    "ROWS",
    "SAMPLE",
    "SCHEMA",
    "SELECT",
    "SET",
    "SOME",
    "START",
    "TABLE",
    "TABLESAMPLE",
    "THEN",
    "TO",
    "TRIGGER",
    "TRUE",
    "TRY_CAST",
    "UNION",
    "UNIQUE",
    "UPDATE",
    "USING",
    "VALUES",
    "VIEW",
    "WHEN",
    "WHENEVER",
    "WHERE",
    "WINDOW",
    "WITH",
}


def make_safe_column_name(name: str) -> str:
    """Return a safe column name by prepending 'DW_' when the name is a reserved word.

    Comparison is case-insensitive and must match exactly; substrings do not qualify.
    """
    try:
        n = (name or "").strip()
    except Exception:
        n = str(name)
    return f"DW_{n}" if n.upper() in _RESERVED_WORDS else n


_SNOWFLAKE_SIMPLE_TYPES = {
    "BOOLEAN",
    "DATE",
    "REAL",
    "DOUBLE",
    "DOUBLE PRECISION",
    "FLOAT",
    "FLOAT4",
    "FLOAT8",
    "INT",
    "INTEGER",
    "BIGINT",
    "SMALLINT",
    "TINYINT",
    "BYTEINT",
    "VARIANT",
    "OBJECT",
    "ARRAY",
    "GEOGRAPHY",
    # String/text without size
    "VARCHAR",
    "STRING",
    "TEXT",
    "CHAR",
    "CHARACTER",
    # Timestamp base types (without variants)
    "TIMESTAMP",
    "TIMESTAMP_NTZ",
    "TIMESTAMP_LTZ",
    "TIMESTAMP_TZ",
}


def is_valid_snowflake_datatype(dt: Any) -> bool:
    """Validate Snowflake data type syntax permissively but safely.

    Accepts typical aliases and optional parameters. Case-insensitive.
    """
    if dt is None:
        return False
    s = str(dt).strip().upper()
    if s == "":
        return False

    # Normalize multiple spaces; unify TIMESTAMP suffix forms
    s = re.sub(r"\s+", " ", s)
    s = s.replace("TIMESTAMP ", "TIMESTAMP_")

    # Simple, no params
    if s in _SNOWFLAKE_SIMPLE_TYPES:
        return True

    # Character/binary with optional (n)
    if re.fullmatch(
        r"(VARCHAR|STRING|TEXT|CHAR|CHARACTER|BINARY|VARBINARY)\s*\(\s*\d+\s*\)", s
    ):
        return True

    # NUMBER/DECIMAL/NUMERIC with (p[,s])
    if re.fullmatch(r"(NUMBER|DECIMAL|NUMERIC)\s*\(\s*\d+\s*(,\s*\d+\s*)?\)", s):
        return True

    # TIME[(p)]
    if re.fullmatch(r"TIME(\s*\(\s*\d+\s*\))?", s):
        return True

    # TIMESTAMP family with optional precision
    if re.fullmatch(
        r"(TIMESTAMP|TIMESTAMP_NTZ|TIMESTAMP_LTZ|TIMESTAMP_TZ)\s*\(\s*\d+\s*\)", s
    ):
        return True

    return False


class JinjaSourceName:
    """Helper object for Jinja that behaves like a string for sourcename,
    while also exposing attributes like FileMatchText and methods like upper/lower.
    """

    def __init__(self, value: str, **attrs: Any) -> None:
        self.value = value
        for k, v in attrs.items():
            setattr(self, k, v)

    def __str__(self) -> str:  # Jinja will string-coerce the object
        return self.value

    def upper(self) -> str:
        """Return the uppercase version of the sourcename value."""
        return self.value.upper()

    def lower(self) -> str:
        """Return the lowercase version of the sourcename value."""
        return self.value.lower()


@dataclass
class Field:
    """Representation of a single field/column from the data dictionary used by templates.

    Holds the source column name (MLS Fan Genome share name), canonical column name, Snowflake data
    type and boolean flags used by generation templates (primary key, phone indicator, DLP).
    """

    source_column_name: str
    column_name: str
    data_type: str
    primary_key: bool
    is_phone: bool
    is_dlp: bool

    # Derived/convenience for templates
    @property
    def name(self) -> str:
        """Canonical column name used by templates (reserved-safe)."""
        return make_safe_column_name(self.column_name)

    @property
    def snowflake_name(self) -> str:
        """Column name formatted for Snowflake usage (same as canonical name, reserved-safe)."""
        return make_safe_column_name(self.column_name)

    @property
    def snowflake_type(self) -> str:
        """Snowflake data type string for the column."""
        return self.data_type

    @property
    def nullable(self) -> bool:
        """Indicate whether the column is nullable; default is True when unspecified."""
        # No explicit nullable flag provided; treat columns as nullable by default.
        return True

    @property
    def dlp(self) -> bool:
        """Whether this column is subject to data loss prevention (DLP) rules."""
        return self.is_dlp

    @property
    def path(self) -> str:
        """Path/key used in JSON/ingest — the MLS Fan Genome share name for the field."""
        # Path in JSON/ingest — use MLS Fan Genome share name
        return self.source_column_name


@dataclass
class Entity:
    """Representation of a MLS Fan Genome entity parsed from the data dictionary.

    This dataclass holds the original MLS Fan Genome object name, canonical Snowflake
    naming bases, the file match text used to identify source files, and the list
    of Field definitions for the entity; it also exposes derived properties that
    templates expect (columns and primary_key).

    Attributes:
        entity_name: MLS Fan Genome object (e.g., Account).
        snowflake_table_base: e.g., MLSFANGENOMEACCOUNT (no instance suffix).
        sourcename_base: e.g., mlsfangenomeaccount (no instance suffix).
        file_match_text: Text used to match input files for this entity.
        fields: List of Field objects describing the entity's columns.
    """

    entity_name: str  # MLS Fan Genome object (e.g., Account)
    snowflake_table_base: str  # e.g., MLSFANGENOMEACCOUNT (no instance suffix)
    sourcename_base: str  # e.g., mlsfangenomeaccount (no instance suffix)
    file_match_text: str
    fields: List[Field]
    # Store ColumnName values from cells E4 and E6 (uppercased), when available
    fullname_first_col: Optional[str] = None
    fullname_last_col: Optional[str] = None

    # Derived
    @property
    def columns(self) -> List[Dict[str, Any]]:
        """Generate a list of column definitions for templates.

        Returns:
            A list of dictionaries, each representing a column with its attributes.
        """
        # Structure expected by many templates
        cols: List[Dict[str, Any]] = []
        for f in self.fields:
            cols.append(
                {
                    "name": f.name,
                    "snowflake_name": f.snowflake_name,
                    "snowflake_type": f.data_type,
                    "data_type": f.data_type,
                    "tags": None,
                    "nullable": f.nullable,
                    "primary_key": f.primary_key,
                    "dlp": f.is_dlp,
                    "path": f.source_column_name,
                }
            )
        return cols

    @property
    def primary_key(self) -> List[str]:
        """Retrieve the list of primary key column names.

        Returns:
            A list of column names marked as primary keys in the entity.
        """
        return [f.name for f in self.fields if f.primary_key]


@dataclass
class ParsedWorkbook:
    """Parsed workbook container holding validated Entity objects.

    Attributes:
        entities: List of Entity instances parsed from the Excel workbook.
    """
    entities: List[Entity]
    # Map of lowercased MLS Fan Genome object name -> list of standardization mappings
    standardization_map: Dict[str, List[Dict[str, str]]]
    # Per-object info (A:B key/value from STANDARDIZATION tabs), keys lowercased
    standardization_info_map: Dict[str, Dict[str, str]]


def _read_standardization_sheet(ws, sheet_name: str) -> List[Dict[str, str]]: # NOSONAR
    """Parse a STANDARDIZATION.* worksheet for field mappings.

    Expected headers (row 1): columns D..G = Field, PrimaryField, SecondaryField, TertiaryField
    Returns a list of dicts with keys: field, primary, secondary, tertiary
    """
    # Validate A/B/C and D..G headers
    a1 = normalize_ws_header_value(ws.cell(row=1, column=1).value)
    b1 = normalize_ws_header_value(ws.cell(row=1, column=2).value)
    c1 = normalize_ws_header_value(ws.cell(row=1, column=3).value)
    if a1 != "InfoKey":
        terminate(
            f"Sheet '{sheet_name}': header mismatch at column A — expected 'InfoKey', got '{a1}'"
        )
    if b1 != "InfoValue":
        terminate(
            f"Sheet '{sheet_name}': header mismatch at column B — expected 'InfoValue', got '{b1}'"
        )
    if c1 != "":
        terminate(
            f"Sheet '{sheet_name}': Column C header must be blank; found '{c1}'"
        )

    expected = ["Field", "PrimaryField", "SecondaryField", "TertiaryField"]
    for idx, name in enumerate(expected, start=4):
        val = normalize_ws_header_value(ws.cell(row=1, column=idx).value)
        if val != name:
            terminate(
                f"Sheet '{sheet_name}': header mismatch at column {idx} — expected '{name}', got '{val}'"
            )
    mappings: List[Dict[str, str]] = []
    for r in range(2, ws.max_row + 1):
        field = ws.cell(row=r, column=4).value
        prim = ws.cell(row=r, column=5).value
        sec = ws.cell(row=r, column=6).value
        ter = ws.cell(row=r, column=7).value
        if is_blank(field) and is_blank(prim) and is_blank(sec) and is_blank(ter):
            continue
        if is_blank(field):
            terminate(
                f"Sheet '{sheet_name}' row {r}: 'Field' (D) is required for standardization mapping"
            )
        mappings.append(
            {
                "field": str(field).strip(),
                "primary": str(prim).strip() if not is_blank(prim) else "",
                "secondary": str(sec).strip() if not is_blank(sec) else "",
                "tertiary": str(ter).strip() if not is_blank(ter) else "",
            }
        )
    return mappings


def _read_standardization_info(ws) -> Dict[str, str]:
    """Read InfoKey/InfoValue pairs from columns A:B of a STANDARDIZATION worksheet."""
    info: Dict[str, str] = {}
    r = 2
    while r <= ws.max_row:
        key = ws.cell(row=r, column=1).value
        val = ws.cell(row=r, column=2).value
        if is_blank(key) and is_blank(val):
            break
        key_s = str(key).strip().lower() if key is not None else ""
        val_s = str(val).strip() if val is not None else ""
        if key_s:
            info[key_s] = val_s
        r += 1
    return info


# ---------------------------------
# Excel parsing and strict validation
# ---------------------------------


EXPECTED_HEADERS = [
    (1, "TableInfo"),
    (2, "InfoValue"),
    (3, ""),
    (4, "SourceColumnName"),
    (5, "ColumnName"),
    #(6, "SourceDataType"),  # present but ignored by logic
    (6, "DataType"),        # Snowflake target type (validated)
    (7, "PrimaryKey"),
    (8, "IsPhone"),
    (9, "IsDLP"),
]


def _sheet_is_hidden(ws) -> bool:
    """Check if a worksheet is hidden from view.

    Args:
        ws: Worksheet object to check.

    Returns:
        True if worksheet state is 'hidden' or 'veryHidden', False otherwise.
    """
    state = getattr(ws, "sheet_state", "visible")
    return state in ("hidden", "veryHidden")


def _validate_headers(ws, sheet_name: str) -> None:  # NOSONAR
    """Validate that worksheet has the expected header structure.

    Checks:
    - Row 1 headers match expected values exactly
    - Column C is empty for all rows
    - No non-empty cells beyond column J

    Args:
        ws: Worksheet object to validate.
        sheet_name: Name of the sheet for error reporting.

    Raises:
        SystemExit: If validation fails on any check.
    """
    # Row 1 headers exact
    for idx, expected in EXPECTED_HEADERS:
        cell_value = normalize_ws_header_value(ws.cell(row=1, column=idx).value)
        if cell_value != expected:
            terminate(
                f"Sheet '{sheet_name}': header mismatch at column {idx} — expected '{expected}', got '{cell_value}'"
            )

    # Column C must be empty for all rows (whitespace allowed)
    for row in ws.iter_rows(
        min_row=1, max_row=ws.max_row, min_col=3, max_col=3, values_only=True
    ):
        v = row[0]
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        terminate(
            f"Sheet '{sheet_name}': Column C must be empty; found non-empty value '{v}'"
        )

    # No non-empty cells beyond column J
    if ws.max_column > 10:
        for row_cells in ws.iter_rows(
            min_row=1, max_row=ws.max_row, min_col=11, max_col=ws.max_column, values_only=True,
        ):
            for v in row_cells:
                if not is_blank(v):
                    terminate(f"Sheet '{sheet_name}': Found non-empty cell beyond column J")


def _read_table_info(ws, sheet_name: str) -> Dict[str, str]:
    """Read key-value table information from columns A:B of worksheet.

    Reads from row 2 downward until both A and B cells are blank.
    Validates presence of required keys.

    Args:
        ws: Worksheet object to read from.
        sheet_name: Name of the sheet for error reporting.

    Returns:
        Dictionary mapping TableInfo keys to their values.

    Raises:
        SystemExit: If required keys are missing or blank.
    """
    info: Dict[str, str] = {}
    # Start reading at row 2 until both A and B are blank
    r = 2
    while r <= ws.max_row:
        key = ws.cell(row=r, column=1).value
        val = ws.cell(row=r, column=2).value
        if is_blank(key) and is_blank(val):
            # stop when we hit the first fully blank row for A/B
            break
        key_s = str(key).strip() if key is not None else ""
        val_s = str(val).strip() if val is not None else ""
        if key_s != "":
            info[key_s] = val_s
        r += 1
    # Required keys
    for required in REQUIRED_TABLEINFO_KEYS:
        if required not in info or str(info[required]).strip() == "":
            terminate(
                f"Sheet '{sheet_name}': Missing required TableInfo '{required}' in columns A:B"
            )
    return info


def _read_fields(ws, sheet_name: str) -> List[Field]:  # NOSONAR
    """Read field definitions from columns D:J of worksheet.

    Validates:
    - SourceColumnName and ColumnName are both present
    - ColumnName uniqueness (case-insensitive)
    - Y/N flags are exactly 'Y' or 'N'
    - Data types are valid Snowflake types
    - At least one data row exists

    Args:
        ws: Worksheet object to read from.
        sheet_name: Name of the sheet for error reporting.

    Returns:
        List of Field objects parsed from the worksheet.

    Raises:
        SystemExit: If validation fails on any field definition.
    """
    fields: List[Field] = []
    # Start at row 2 for fields (D..J)
    seen_columns_lower = set()
    any_data_rows = False
    for r in range(2, ws.max_row + 1):
        d = ws.cell(row=r, column=4).value  # SourceColumnName
        e = ws.cell(row=r, column=5).value  # ColumnName
        #f_src = ws.cell(row=r, column=6).value  # SourceDataType (ignored for generation)
        f = ws.cell(row=r, column=6).value      # DataType (Snowflake target)
        g = ws.cell(row=r, column=7).value      # PrimaryKey
        h = ws.cell(row=r, column=8).value      # IsPhone
        i = ws.cell(row=r, column=9).value     # IsDLP

        row_blank = (
            is_blank(d)
            and is_blank(e)
            and is_blank(f)
            and is_blank(g)
            and is_blank(h)
            and is_blank(i)
        )
        if row_blank:
            continue
        any_data_rows = True

        if is_blank(d) or is_blank(e):
            terminate(
                f"Sheet '{sheet_name}' row {r}: Both SourceColumnName (D) and ColumnName (E) must be present; found blank"
            )

        # ColumnName uniqueness (case-insensitive)
        col_lower = str(e).strip().lower()
        if col_lower in seen_columns_lower:
            terminate(
                f"Sheet '{sheet_name}' row {r}: Duplicate ColumnName '{e}' (case-insensitive)"
            )
        seen_columns_lower.add(col_lower)

        # Validate flags exactly Y/N
        for name, val in [("PrimaryKey", g), ("IsPhone", h), ("IsDLP", i)]:
            b = to_bool_yn(str(val).strip() if val is not None else "")
            if b is None:
                terminate(
                    f"Sheet '{sheet_name}' row {r}: Column '{name}' must be exactly 'Y' or 'N' (whitespace allowed). Found '{val}'"
                )

        # Validate data type
        if not is_valid_snowflake_datatype(f):
            terminate(f"Sheet '{sheet_name}' row {r}: Invalid Snowflake data type '{f}'")

        # Cross-validate SourceDataType vs DataType for booleans
        # if f_src is not None and str(f_src).strip().lower() == "boolean":
        #     if str(f).strip().upper() != "BOOLEAN":
        #         terminate(
        #             f"Sheet '{sheet_name}' row {r}: SourceDataType is 'boolean' but DataType is '{f}'. Expected 'BOOLEAN'."
        #         )

        fields.append(
            Field(
                source_column_name=str(d).strip(),
                column_name=str(e).strip(),
                data_type=str(f).strip().upper(),
                primary_key=to_bool_yn(g) is True,
                is_phone=to_bool_yn(h) is True,
                is_dlp=to_bool_yn(i) is True,
            )
        )

    if not any_data_rows:
        terminate(
            f"Sheet '{sheet_name}': Headers present but no field rows found — sheet must not be empty"
        )

    return fields


def parse_workbook(path: Path) -> ParsedWorkbook: # NOSONAR
    """Parse Excel workbook into validated entities.

    Processes all non-hidden sheets except 'Object Summary'.
    Validates each sheet's header structure and field definitions.
    Applies MLS Fan Genome table naming conventions.

    Args:
        path: Path to the Excel workbook file.

    Returns:
        ParsedWorkbook containing validated Entity objects.

    Raises:
        SystemExit: If workbook not found, validation fails, or no entities found.
    """
    if not path.exists():
        terminate(f"Input workbook not found: {path}")

    # Open read-only; do not modify
    wb = load_workbook(filename=str(path), read_only=True, data_only=True)

    entities: List[Entity] = []

    sheetnames = wb.sheetnames
    if not sheetnames:
        terminate("Workbook has no worksheets")

    # The first worksheet must be named either 'Worksheet List' or 'Object Summary'. Always ignore it.
    first_sheet = sheetnames[0]
    if first_sheet not in FIRST_SHEET_ALLOWED:
        terminate(
            f"First worksheet must be named 'Worksheet List' or 'Object Summary'; found '{first_sheet}'"
        )

    # Require at least one standardization* worksheet (rawaudience* is optional)
    has_standardization = any(s.strip().lower().startswith("standardization") for s in sheetnames[1:])
    if not has_standardization:
        terminate(
            "Workbook is missing required sheet type: 'standardization*'. "
            "Expected at least one 'standardization*' worksheet (case-insensitive)."
        )

    # Build set of candidate entity sheet names (visible, not first sheet, not non-entity)
    entity_sheet_names_lower: set[str] = set()
    for idx, sn in enumerate(sheetnames, start=1):
        if idx == 1:
            continue
        if sn == "Object Summary":
            continue
        ws_ = wb[sn]
        if _sheet_is_hidden(ws_):
            continue
        low = sn.strip().lower()
        if any(low.startswith(p) for p in NON_ENTITY_PREFIXES):
            continue
        entity_sheet_names_lower.add(low)

    # Validate rawaudience*/standardization* naming and referenced object existence
    for sn in iter_progress(
        sheetnames[1:],
        label="Validating sheet names",
        total=len(sheetnames) - 1,
        mode="auto",
    ):
        low = sn.strip().lower()
        if any(low.startswith(p) for p in ("rawaudience", "standardization")):
            parts = sn.strip().split()
            if len(parts) != 2:
                # Fallback: allow a lone 'STANDARDIZATION' sheet name and derive object from cell B2
                if low.startswith("standardization") and len(parts) == 1:
                    ws_std = wb[sn]
                    # Attempt to read the Snowflake table name from B2 (InfoValue under InfoKey)
                    b2_val = ws_std.cell(row=2, column=2).value
                    table_hint = str(b2_val).strip() if b2_val is not None else ""
                    if table_hint == "":
                        terminate(
                            f"Sheet '{sn}': could not determine object from name or cell B2 (expected Snowflake table name like 'MLSFanGenomeContact')"
                        )
                    # Remove 'MLSFanGenome' prefix (case-insensitive) to get the object name
                    th_lower = table_hint.lower()
                    if th_lower.startswith("mlsfangenome"):
                        obj = table_hint[len("MLSFanGenome") :].strip()
                    else:
                        obj = table_hint.strip()
                else:
                    terminate(
                        f"Sheet '{sn}': invalid name format. Expected 'RAWAUDIENCE <Object>' or 'STANDARDIZATION <Object>' (exactly 2 words)."
                    )
            else:
                obj = parts[1].strip()
            if obj.lower() not in entity_sheet_names_lower:
                terminate(
                    f"Sheet '{sn}': references object '{obj}', but no corresponding worksheet named '{obj}' was found."
                )

    # Collect standardization mappings first (may exist for some entities)
    standardization_map: Dict[str, List[Dict[str, str]]] = {}
    standardization_info_map: Dict[str, Dict[str, str]] = {}
    for sheet_name in iter_progress(
        sheetnames,
        label="Reading standardization sheets",
        total=len(sheetnames),
        mode="auto",
    ):
        lower = sheet_name.strip().lower()
        if lower.startswith("standardization"):
            ws = wb[sheet_name]
            if _sheet_is_hidden(ws):
                continue
            mappings = _read_standardization_sheet(ws, sheet_name)
            info_kv = _read_standardization_info(ws)
            # Extract object name suffix after the first space following 'STANDARDIZATION'
            parts = sheet_name.split(None, 1)
            obj_name = parts[1].strip() if len(parts) > 1 else ""
            if obj_name == "":
                # Fallback: derive from cell B2 (Snowflake table name like 'MLSFanGenomeContact')
                b2_val = ws.cell(row=2, column=2).value
                table_hint = str(b2_val).strip() if b2_val is not None else ""
                if table_hint == "":
                    terminate(
                        f"Sheet '{sheet_name}': could not determine object from name or cell B2 (expected Snowflake table name like 'MLSFanGenomeContact')"
                    )
                th_lower = table_hint.lower()
                if th_lower.startswith("mlsfangenome"):
                    obj_name = table_hint[len("MLSFanGenome") :].strip()
                else:
                    obj_name = table_hint.strip()
            standardization_map[obj_name.lower()] = mappings
            standardization_info_map[obj_name.lower()] = info_kv

    for idx, sheet_name in enumerate(
        iter_progress(
            sheetnames, label="Parsing entities", total=len(sheetnames), mode="auto"
        ),
        start=1,
    ):
        # Skip first sheet per spec
        if idx == 1:
            continue
        # Skip known non-entity sheets
        lower = sheet_name.strip().lower()
        if any(lower.startswith(p) for p in NON_ENTITY_PREFIXES):
            continue
        if sheet_name == "Object Summary":
            continue
        ws = wb[sheet_name]
        if _sheet_is_hidden(ws):
            continue

        _validate_headers(ws, sheet_name)

        info = _read_table_info(ws, sheet_name)
        mlsfangenome_object_name = str(info["MLSFanGenomeObjectName"]).strip()
        file_match_text = str(info["FileMatchText"]).strip()

        fields = _read_fields(ws, sheet_name)

        # Table naming rule
        if mlsfangenome_object_name.strip().lower().startswith("mlsfangenome"):
            base_table = mlsfangenome_object_name.strip().upper()
        else:
            base_table = f"MLSFANGENOME{mlsfangenome_object_name.strip().upper()}"

        sourcename_base = base_table.lower()

        # Read ColumnName values from E4 and E6 for FULLNAME generation (defaults if blank)
        e4_val = ws.cell(row=4, column=5).value  # E4
        e6_val = ws.cell(row=6, column=5).value  # E6
        first_col = str(e4_val).strip().upper() if not is_blank(e4_val) else "FIRSTNAME"
        last_col = str(e6_val).strip().upper() if not is_blank(e6_val) else "LASTNAME"

        entities.append(
            Entity(
                entity_name=mlsfangenome_object_name,
                snowflake_table_base=base_table,
                sourcename_base=sourcename_base,
                file_match_text=file_match_text,
                fields=fields,
                fullname_first_col=first_col,
                fullname_last_col=last_col,
            )
        )

    if not entities:
        terminate(
            "No valid entities found in workbook (after skipping hidden and 'Object Summary')"
        )

    return ParsedWorkbook(entities=entities, standardization_map=standardization_map, standardization_info_map=standardization_info_map)


# -----------------------------
# Rendering helpers
# -----------------------------


def dedupe_preserve_case_insensitive(values: List[str]) -> List[str]:
    """Remove duplicate strings preserving original case, case-insensitive comparison.

    Args:
        values: List of strings that may contain duplicates.

    Returns:
        List with duplicates removed, preserving first occurrence case.
    """
    seen = set()
    out: List[str] = []
    for v in values:
        key = v.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
    return out


def apply_default_dlp_columns(
    entity_name: str, dlp_columns: List[str], available_columns: Optional[Iterable[str]] = None
) -> List[str]:
    """Ensure default DLP columns are present only when defined for the entity."""
    defaults = DEFAULT_DLP_COLUMNS_BY_OBJECT.get(entity_name.lower())
    if not defaults:
        return dlp_columns
    available_lower = (
        {col.lower() for col in available_columns} if available_columns is not None else None
    )
    seen = {col.lower() for col in dlp_columns}
    for default_col in defaults:
        safe_default = make_safe_column_name(default_col)
        key = safe_default.lower()
        if key in seen:
            continue
        if available_lower is not None and key not in available_lower:
            continue
        dlp_columns.append(safe_default)
        seen.add(key)
    return dlp_columns


def override_fullname_from_field_mappings(ctx: Dict[str, Any], field_mappings: Dict[str, List[str]]) -> None:
    """Override fullname_first_col/lastname using PrimaryField from STANDARDIZATION mappings."""
    try:
        first_vals = field_mappings.get("RAWFIRSTNAME", [])
        last_vals = field_mappings.get("RAWLASTNAME", [])
        if first_vals and first_vals[0]:
            ctx["fullname_first_col"] = make_safe_column_name(str(first_vals[0]).strip().upper())
        if last_vals and last_vals[0]:
            ctx["fullname_last_col"] = make_safe_column_name(str(last_vals[0]).strip().upper())
    except Exception:  # pylint: disable=broad-exception-caught
        # Non-fatal: fall back to defaults already in ctx
        pass


def compute_entity_runtime(entity: Entity, instance: Optional[str]) -> Dict[str, Any]:
    """Prepare the per-entity context structure expected by templates.

    Args:
        entity: Entity object to build context for.
        instance: Optional instance name for suffix computation.

    Returns:
        Dictionary containing template context variables including:
        - sourcename: SourcenameString with FileMatchText attribute
        - entity: Entity dictionary structure for templates
        - dlp_columns: Deduplicated list of DLP column names
        - instance_suffix: Lowercase instance suffix
        - instance_suffix_upper: Uppercase instance suffix
        - entity_slug: Lowercase entity name
    """
    instance_suffix = f"_{instance.lower()}" if instance else ""
    instance_suffix_upper = f"_{instance.upper()}" if instance else ""

    # sourcename helper used by SQL templates (supports attributes + string coercion)
    sourcename_attr = JinjaSourceName(
        entity.sourcename_base, FileMatchText=entity.file_match_text
    )

    # dlp columns list in sheet order (case-insensitive de-dupe), using safe column names
    dlp_cols = [f.name for f in entity.fields if f.is_dlp]
    dlp_cols = dedupe_preserve_case_insensitive(dlp_cols)

    # entity dict structure for various templates
    entity_dict: Dict[str, Any] = {
        "entity_name": entity.entity_name,
        "name": entity.entity_name,  # for templates expecting 'name'
        "snowflake_table": entity.snowflake_table_base,
        "columns": entity.columns,
        "primary_key": entity.primary_key,
        "unique_sort": None,
        # Used by prefect_source_metadata and soql
        "fields": [f.source_column_name for f in entity.fields],
        "mlsfangenome_object": entity.entity_name,
        # Standardization flag: default false unless specified otherwise later
        "standardization_source": False,
    }

    return {
        "sourcename": sourcename_attr,
        "entity": entity_dict,
        "dlp_columns": dlp_cols,
        "instance_suffix": instance_suffix,
        "instance_suffix_upper": instance_suffix_upper,
        # Convenience slug (lowercase MLS Fan Genome object name)
        "entity_slug": entity.entity_name.lower(),
        # Names used for FULLNAME expression in Melissa model YAML
        "fullname_first_col": make_safe_column_name((entity.fullname_first_col or "FIRSTNAME").strip().upper()),
        "fullname_last_col": make_safe_column_name((entity.fullname_last_col or "LASTNAME").strip().upper()),
    }


def has_last_modified_date_field(entity: Entity) -> bool:
    """Return True if the entity defines a LastModifiedDate column."""
    for field in entity.fields:
        source_name = str(field.source_column_name).strip().lower()
        if source_name == "lastmodifieddate":
            return True
        column_name = str(field.column_name).strip().lower()
        if column_name.replace("_", "") == "lastmodifieddate":
            return True
    return False


def build_sources_list(
    entities: List[Entity], instance: Optional[str], standardization_map: Dict[str, List[Dict[str, str]]]
) -> List[Dict[str, Any]]:
    """Construct the global sources list used by some templates (behavior preserved)."""
    _, up = build_instance_suffixes(instance)
    _ = up  # not used directly here, but kept for clarity
    sources: List[Dict[str, Any]] = []
    for e in entities:
        dlp_columns = [f.name for f in e.fields if f.is_dlp]
        dlp_columns = dedupe_preserve_case_insensitive(dlp_columns)
        available_columns = [f.name for f in e.fields]
        dlp_columns = apply_default_dlp_columns(e.entity_name, dlp_columns, available_columns)
        sources.append(
            {
                "name": e.entity_name,
                "fileMatchPattern": e.file_match_text,
                "snowflake_table": f"{e.snowflake_table_base}{up}" if up else e.snowflake_table_base,
                "isStandardizationSource": bool(standardization_map.get(e.entity_name.lower())),
                "dlpColumns": dlp_columns,
                "primaryKeyColumns": [f.name for f in e.fields if f.primary_key],
                # Provide an empty structure so nested lookups like
                # source.getLastDateProperties.lastDateColumn | default('LastModifiedDate')
                # resolve without raising UndefinedError
                "getLastDateProperties": {},
                # Flag used by templates to disable last-date based extraction when missing
                "getLastDateIndicator": has_last_modified_date_field(e),
            }
        )
    return sources


def build_entity_ctx( # NOSONAR # pylint: disable=too-many-locals
    e: Entity,
    global_ctx: Dict[str, Any],
    instance: Optional[str],
    standardization_map: Dict[str, List[Dict[str, str]]],
) -> Dict[str, Any]:
    """Assemble per-entity context (behavior-preserving consolidation)."""
    ctx = dict(global_ctx)
    ctx.update(compute_entity_runtime(e, instance=None))
    add_instance_ctx(ctx, instance)

    # Compute standardization info (available to templates)
    std = standardization_map.get(e.entity_name.lower())
    mappings_render: List[Dict[str, str]] = []
    field_mappings: Dict[str, List[str]] = {}
    if std:
        for m in std:
            field = m.get("field", "").strip()
            p = m.get("primary", "").strip()
            s = m.get("secondary", "").strip()
            t = m.get("tertiary", "").strip()
            # Build expression for SQL
            if p == "":
                expr = "''"
            else:
                cols = [c for c in [p, s, t] if c]
                if len(cols) == 1:
                    expr = cols[0].upper()
                else:
                    expr = "COALESCE(" + ", ".join(c.upper() for c in cols) + ")"
            mappings_render.append(
                {
                    "field": field.upper(),
                    "primary": p.upper(),
                    "secondary": s.upper(),
                    "tertiary": t.upper(),
                    "expression": expr,
                }
            )
            # Build fieldMappings list for YAML
            key = field.upper()
            vals: List[str] = []
            if p:
                vals.append(p.upper())
            if s:
                vals.append(s.upper())
            if t:
                vals.append(t.upper())
            field_mappings[key] = vals
    if mappings_render:
        ctx["standardization_mappings"] = mappings_render

    # Override FULLNAME columns using PrimaryField from STANDARDIZATION
    override_fullname_from_field_mappings(ctx, field_mappings)

    # entityName and entities structure expected by YAML template
    entity_name_upper = e.snowflake_table_base
    ctx["entityName"] = entity_name_upper
    ctx["entities"] = {
        "entityName": {
            entity_name_upper: {
                "standardizationSettings": {
                    "fieldMappings": field_mappings,
                }
            }
        }
    }
    return ctx


def append_instance_to_filename(
    path: Path, instance: Optional[str], is_environment_file: bool
) -> Path:
    """Append instance suffix to filename unless it's an environment file.

    Args:
        path: Original file path.
        instance: Optional instance name to append.
        is_environment_file: If True, skip instance appending.

    Returns:
        Path with instance suffix appended to stem (if applicable).
    """
    if not instance or is_environment_file:
        return path
    base = path.stem
    suf = f"_{instance.lower()}"
    # Avoid double-appending if already present anywhere in the stem
    # (handles cases where metadata embeds the suffix before other tokens like _RAW)
    if suf in base.lower():
        return path
    return path.with_name(f"{base}{suf}{path.suffix}")


def build_global_context(
    client: str, feature: str, version: str, feature_settings: Dict[str, Any]
) -> Dict[str, Any]:
    """Build global template context with required defaults.

    Args:
        client: Client code (e.g., 'KROENKE').
        feature: Feature name (e.g., 'mlsfangenome').
        version: Template version (e.g., 'v1_0_0').
        feature_settings: Feature-specific settings dictionary.

    Returns:
        Global context dictionary with client, feature, version, and featureSettings.
    """
    # Ensure required defaults
    fs = dict(feature_settings or {})
    fs.setdefault("ddl_stage_schema", "STAGE")
    return {
        "client": client,
        "feature": feature,
        "version": version,
        "featureSettings": fs,
    }


def load_additional_settings(client: str, feature: str) -> Dict[str, Any]:
    """Load and validate additional_settings.json for client/feature.

    Args:
        client: Client code to load settings for.
        feature: Feature name to load settings for.

    Returns:
        Parsed additional_settings.json content.

    Raises:
        SystemExit: If file not found, invalid JSON, or missing required structure.
    """
    # New layout: config/client-config/{CLIENT}/{feature}/additional_settings.json
    settings_path = Path(f"config/client-config/{client}/{feature}/additional_settings.json")
    settings = read_json(settings_path)
    # Validate environment structure
    try:
        envs = settings["featureSettings"]["environments"]
    except KeyError:
        terminate(
            f"additional_settings.json missing 'featureSettings.environments' at {settings_path}"
        )
    for env in ("dev", "qa", "prod"):
        if env not in envs:
            terminate(
                f"additional_settings.json missing environment '{env}' in featureSettings.environments"
            )
    return settings


def load_metadata(feature: str, version: str) -> Dict[str, Any]:
    """Load and validate config_generator_metadata.json for feature/version.

    Args:
        feature: Feature name to load metadata for.
        version: Template version to load metadata for.

    Returns:
        Parsed metadata.json content.

    Raises:
        SystemExit: If file not found, invalid JSON, or missing 'filesToGenerate'.
    """
    # New layout: config/product-config/{feature}/{version}/config_generator_metadata.json
    meta_path = Path(
        f"config/product-config/{feature}/{version}/config_generator_metadata.json"
    )
    meta = read_json(meta_path)
    if "filesToGenerate" not in meta or not isinstance(meta["filesToGenerate"], list):
        terminate(f"Metadata file missing 'filesToGenerate' list: {meta_path}")
    # Basic sanity: feature and version match (optional)
    return meta


def render_string(s: str, ctx: Dict[str, Any]) -> str:
    """Render a Jinja2 template string with given context.

    Args:
        s: Template string to render.
        ctx: Context variables for template rendering.

    Returns:
        Rendered string.
    """
    return jinja_env_for_paths().from_string(s).render(**ctx)


def plan_outputs(  # NOSONAR
    meta: Dict[str, Any],
    repo_root: Path,
    global_ctx: Dict[str, Any],
    entities: List[Entity],
    instance: Optional[str],
    standardization_map: Dict[str, List[Dict[str, str]]],
    standardization_info_map: Dict[str, Dict[str, str]],
) -> List[Dict[str, Any]]:
    """Plan all output files to be generated based on metadata configuration.

    Processes metadata filesToGenerate list and creates generation plans for:
    - Environment files (dev/qa/prod) using additional_settings
    - Per-entity files using entity-specific context
    - Global files using aggregate entity lists

    Args:
        meta: Loaded config_generator_metadata.json content.
        repo_root: Repository root path for resolving template and output paths.
        global_ctx: Global template context variables.
        entities: List of parsed Entity objects.
        instance: Optional instance name for suffix handling.

    Returns:
        List of generation plan dictionaries containing entry, context,
        template_path, output_path, and is_environment_file keys.

    Raises:
        SystemExit: If metadata entries are missing required keys.
    """
    plans: List[Dict[str, Any]] = []

    files = meta["filesToGenerate"]

    # Build aggregate lists used by some global templates
    all_sources = build_sources_list(entities, instance, standardization_map)
    all_entities = [
        {
            "name": e.entity_name,
            "raw_table_name": e.snowflake_table_base,
            "snowflake_table": e.snowflake_table_base,
        }
        for e in entities
    ]

    for entry in iter_progress(files, label="Planning outputs", total=len(files), mode="auto"):
        # Require both keys per spec
        for key in ("jinjaTemplateForGeneration", "outputPath"):
            if key not in entry or not entry[key]:
                terminate(
                    f"Metadata entry missing required key '{key}': {json.dumps(entry, indent=2)}"
                )

        is_env = bool(entry.get("isEnvironmentFile", False))
        per_entity = bool(entry.get("appliesToEachEntity", False))
        only_for_std = bool(entry.get("onlyForStandardizationSource", False))

        template_path_tpl = entry["jinjaTemplateForGeneration"]
        output_path_tpl = entry["outputPath"]

        if is_env:
            # Render for each environment without additional_settings.json
            for env in ("dev", "qa", "prod"):
                ctx = dict(global_ctx)
                ctx.update(
                    {
                        "env": env,
                        "environment": env,
                        "environmentName": env.upper(),
                        # No featureSettings from additional_settings.json
                        "featureSettings": {},
                    }
                )
                add_instance_ctx(ctx, instance)

                # Treat template path as a literal path (do not Jinja-render)
                template_path = template_path_tpl
                output_path = render_string(output_path_tpl, ctx)
                # Per specification: environment files SHOULD NOT be appended with instance
                final_output = repo_root / output_path

                plans.append(
                    {
                        "entry": entry,
                        "context": ctx,
                        "template_path": repo_root / template_path,
                        "output_path": final_output,
                        "is_environment_file": True,
                    }
                )
            continue

        if per_entity:
            for e in entities:
                if entry.get("name") in EXCLUDED_ENTRY_NAMES and e.entity_name.lower() in EXCLUDED_OBJECT_NAMES:
                    continue
                runtime = compute_entity_runtime(
                    e, instance=None
                )  # content templates handle suffix via vars
                ctx = dict(global_ctx)
                ctx.update(runtime)
                ctx.update(
                    {
                        "instance_suffix": f"_{instance.lower()}" if instance else "",
                        "instance_suffix_upper": (f"_{instance.upper()}" if instance else ""),
                        "instance": instance or "",
                    }
                )

                # Remove optional per-object SOQL where clause from additional_settings
                # Compute standardization info (available to templates)
                std = standardization_map.get(e.entity_name.lower())
                mappings_render: List[Dict[str, str]] = []
                field_mappings: Dict[str, List[str]] = {}
                if std:
                    for m in std:
                        field = m.get("field", "").strip()
                        p = m.get("primary", "").strip()
                        s = m.get("secondary", "").strip()
                        t = m.get("tertiary", "").strip()
                        # Build expression for SQL
                        if p == "":
                            expr = "''"
                        else:
                            cols = [c for c in [p, s, t] if c]
                            if len(cols) == 1:
                                expr = cols[0].upper()
                            else:
                                expr = "COALESCE(" + ", ".join(c.upper() for c in cols) + ")"
                        mappings_render.append(
                            {
                                "field": field.upper(),
                                "primary": p.upper(),
                                "secondary": s.upper(),
                                "tertiary": t.upper(),
                                "expression": expr,
                            }
                        )
                        # Build fieldMappings list for YAML
                        key = field.upper()
                        vals: List[str] = []
                        if p:
                            vals.append(p.upper())
                        if s:
                            vals.append(s.upper())
                        if t:
                            vals.append(t.upper())
                        field_mappings[key] = vals
                if mappings_render:
                    ctx["standardization_mappings"] = mappings_render

                # Inject entity_joins from STANDARDIZATION A:B info (JoinTable/JoinCondition)
                try:
                    info_kv = standardization_info_map.get(e.entity_name.lower(), {}) or {}
                    # keys are lowercased in the map
                    join_table = info_kv.get("jointable", "").strip()
                    join_condition = info_kv.get("joincondition", "").strip()
                    join_alias = info_kv.get("joinalias", "").strip()
                    if join_table and join_condition:
                        ctx["entity_joins"] = [
                            {
                                "join_type": "left",
                                "join_table": join_table,
                                "join_alias": join_alias,  # from STANDARDIZATION InfoKey=JoinAlias
                                "join_condition": join_condition,
                                "filter": "",
                            }
                        ]
                    else:
                        ctx["entity_joins"] = []
                except Exception:
                    ctx["entity_joins"] = []

                # Override FULLNAME columns using PrimaryField from STANDARDIZATION
                override_fullname_from_field_mappings(ctx, field_mappings)

                # entityName and entities structure expected by YAML template
                entity_name_upper = e.snowflake_table_base
                ctx["entityName"] = entity_name_upper
                ctx["entities"] = {
                    "entityName": {
                        entity_name_upper: {
                            "standardizationSettings": {
                                "fieldMappings": field_mappings,
                            }
                        }
                    }
                }

                # If rendering the stage DDL for a standardization source, prepend two columns
                # to the dynamic columns list as requested:
                #   RAWAUDIENCEID NUMBER(38, 0)
                #   STANDARDIZATIONROWID NUMBER(38, 0)
                is_stage_ddl_template = str(template_path_tpl).endswith(
                    "kagr-data/ddl_stage.sql.j2"
                ) or os.path.basename(str(template_path_tpl)) == "ddl_stage.sql.j2"
                if is_stage_ddl_template and std:
                    try:
                        cols = list(ctx.get("entity", {}).get("columns", []))
                        # Deduplicate safeguard: don't add if already present
                        existing = {str(c.get("snowflake_name", "")).strip().upper() for c in cols}
                        prepend_cols = []
                        if "RAWAUDIENCEID" not in existing:
                            prepend_cols.append(
                                {
                                    "name": "RAWAUDIENCEID",
                                    "snowflake_name": "RAWAUDIENCEID",
                                    "snowflake_type": "NUMBER(38, 0)",
                                    "data_type": "NUMBER(38, 0)",
                                    "tags": None,
                                    "nullable": True,
                                    "primary_key": False,
                                    "dlp": False,
                                    "path": "",
                                }
                            )
                        if "STANDARDIZATIONROWID" not in existing:
                            prepend_cols.append(
                                {
                                    "name": "STANDARDIZATIONROWID",
                                    "snowflake_name": "STANDARDIZATIONROWID",
                                    "snowflake_type": "NUMBER(38, 0)",
                                    "data_type": "NUMBER(38, 0)",
                                    "tags": None,
                                    "nullable": True,
                                    "primary_key": False,
                                    "dlp": False,
                                    "path": "",
                                }
                            )
                        if prepend_cols:
                            ctx["entity"]["columns"] = prepend_cols + cols
                    except Exception:
                        # Fail-safe: do not block generation if context mutation fails
                        pass

                is_kagr_yaml_template = (
                    str(template_path_tpl).endswith(
                        "kagr-data/{{sourcename}}.yml.j2"
                    )
                    or (
                        os.path.basename(str(template_path_tpl))
                        == "{{sourcename}}.yml.j2"
                        and "kagr-data" in str(template_path_tpl)
                    )
                )
                if is_kagr_yaml_template and std:
                    try:
                        cols = list(ctx.get("entity", {}).get("columns", []))
                        existing = {
                            str(c.get("name", "")).strip().upper() for c in cols
                        }
                        insert_cols: List[Dict[str, Any]] = []
                        if "STANDARDIZATIONROWID" not in existing:
                            insert_cols.append(
                                {
                                    "name": "STANDARDIZATIONROWID",
                                    "snowflake_name": "STANDARDIZATIONROWID",
                                    "snowflake_type": "NUMBER(38, 0)",
                                    "data_type": "NUMBER(38, 0)",
                                    "tags": None,
                                    "nullable": True,
                                    "primary_key": False,
                                    "dlp": False,
                                    "path": "",
                                }
                            )
                        if "RAWAUDIENCEID" not in existing:
                            insert_cols.append(
                                {
                                    "name": "RAWAUDIENCEID",
                                    "snowflake_name": "RAWAUDIENCEID",
                                    "snowflake_type": "NUMBER(38, 0)",
                                    "data_type": "NUMBER(38, 0)",
                                    "tags": None,
                                    "nullable": True,
                                    "primary_key": False,
                                    "dlp": False,
                                    "path": "",
                                }
                            )
                        if insert_cols:
                            ctx["entity"]["columns"] = insert_cols + cols
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass

                # For specific templates, override to use raw (unsafened) column names
                is_sf_soql_template = (
                    str(template_path_tpl).endswith(
                        "platform-configuration/{{sourcename}}-select.soql.j2"
                    )
                    or os.path.basename(str(template_path_tpl))
                    == "{{sourcename}}-select.soql.j2"
                )
                if is_sf_soql_template:
                    try:
                        raw_cols: List[Dict[str, Any]] = []
                        for fdef in e.fields:
                            raw_cols.append(
                                {
                                    "name": fdef.column_name,
                                    "snowflake_name": fdef.column_name,
                                    "snowflake_type": fdef.data_type,
                                    "data_type": fdef.data_type,
                                    "tags": None,
                                    "nullable": fdef.nullable,
                                    "primary_key": fdef.primary_key,
                                    "dlp": fdef.is_dlp,
                                    "path": fdef.source_column_name,
                                }
                            )
                        ctx["entity"]["columns"] = raw_cols
                        ctx["entity"]["primary_key"] = [
                            fdef.column_name for fdef in e.fields if fdef.primary_key
                        ]
                        ctx["dlp_columns"] = dedupe_preserve_case_insensitive(
                            [fdef.column_name for fdef in e.fields if fdef.is_dlp]
                        )
                    except Exception:  # pylint: disable=broad-exception-caught
                        pass

                # Optional filter: only for standardization sources
                if only_for_std:
                    # Generate only if a standardization sheet exists for this entity
                    if not std:
                        continue
                    # Also reflect in entity.standardization_source where expected
                    ctx["entity"]["standardization_source"] = True

                template_path = template_path_tpl
                output_path = render_string(output_path_tpl, ctx)

                out_path = repo_root / output_path
                out_path = append_instance_to_filename(
                    out_path, instance, is_environment_file=False
                )

                plans.append(
                    {
                        "entry": entry,
                        "context": ctx,
                        "template_path": repo_root / template_path,
                        "output_path": out_path,
                        "is_environment_file": False,
                    }
                )
            continue

        # Global, non-environment
        ctx = dict(global_ctx)
        ctx.update({"sources": all_sources, "entities": all_entities, "instance": instance or ""})
        add_instance_ctx(ctx, instance)

        template_path = template_path_tpl
        output_path = render_string(output_path_tpl, ctx)
        out_path = repo_root / output_path
        out_path = append_instance_to_filename(
            out_path, instance, is_environment_file=False
        )

        # For standardization request/response entries, copy verbatim (no Jinja rendering)
        no_render = entry.get("name") in ("standardization_request", "standardization_response", "standardization_response_new_records_inserted", "standardization_request_new_records_inserted", "standardization_final_unique", "standardization_final", "standardization_staging_table_upsert")

        plans.append(
            {
                "entry": entry,
                "context": ctx,
                "template_path": repo_root / template_path,
                "output_path": out_path,
                "is_environment_file": False,
                "no_render": no_render,
            }
        )

    return plans


def check_plans(plans: List[Dict[str, Any]]) -> Tuple[List[Path], List[str]]:
    """Validate generation plans for template existence and output conflicts.

    Args:
        plans: List of generation plan dictionaries.

    Returns:
        Tuple of (output_paths, error_messages).
    """
    outputs: List[Path] = []
    errors: List[str] = []
    for p in plans:
        t = p["template_path"]
        o = p["output_path"]
        if not t.exists():
            errors.append(f"Template not found: {t}")
        outputs.append(o)
    # Check for existing outputs (no overwrite allowed)
    conflicts = [str(o) for o in outputs if o.exists()]
    for c in conflicts:
        errors.append(f"Output already exists (will not overwrite): {c}")
    return outputs, errors


def iter_progress(iterable, label: str, total: Optional[int] = None, mode: str = "auto"):
    """Yield items with visible progress.

    mode: 'auto' (always use tqdm), 'simple' (line per item), 'none' (no progress).
    """
    if mode == "none":
        for item in iterable:
            yield item
        return
    # Always use tqdm unless explicitly set to simple mode
    if mode != "simple":
        yield from tqdm(
            iterable,
            desc=label,
            total=total,
            unit="file",
            file=sys.stderr,  # Use stderr instead of stdout for better compatibility
            disable=False,
            dynamic_ncols=True,
            miniters=1,
            mininterval=0,
            leave=True,
        )
        return
    # Simple: print a line per iteration
    count = 0
    # Resolve total into a concrete value without nested conditional expressions
    if total is not None:
        resolved_total = total
    elif hasattr(iterable, "__len__"):
        resolved_total = len(iterable)
    else:
        resolved_total = None
    for item in iterable:
        count += 1
        if resolved_total is not None:
            print(f"{label}: {count}/{resolved_total}")
        else:
            print(f"{label}: {count}")
        yield item


def render_and_write(plans: List[Dict[str, Any]], repo_root: Path, progress_mode: str = "auto") -> None: # NOSONAR
    """Execute generation plans by rendering templates and writing output files.

    Args:
        plans: List of validated generation plan dictionaries.
        repo_root: Repository root path for template loading.
    """
    # Single content environment for all templates with repo-root loader
    env = jinja_env_for_content(repo_root)
    for p in iter_progress(plans, label="Writing files", total=len(plans), mode=progress_mode):
        template_path = p["template_path"]
        output_path: Path = p["output_path"]
        ctx = p["context"]

        # Prepare parent dirs
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy verbatim when requested (no Jinja rendering)
        if p.get("no_render"):
            with template_path.open("rb") as src, output_path.open("xb") as dst:
                dst.write(src.read())
            continue

        content: str
        if str(template_path).endswith(".sql.j2"):
            # Decide handling based on the OUTPUT location, not the template path
            opath_norm = str(output_path).replace("\\", "/")
            if "/dbt/models/" in opath_norm:
                # For dbt SQL templates: only evaluate {{ sourcename ... }} and {{ entity ... }} expressions,
                # leave all other Jinja (dbt macros) untouched.
                with template_path.open("r", encoding="utf-8") as f:
                    raw = f.read()

                # Replace variable tags referencing 'sourcename' or 'entity' with simple lower/upper filters
                pattern = re.compile(
                    r"{{\s*((?:sourcename|entity)(?:\.[A-Za-z_]\w*(?:\(\))?)*(?:\s*\|\s*(?:lower|upper))?)\s*}}"
                )

                def replace_match(m: re.Match) -> str:
                    expr = m.group(1)
                    mini_env = Environment(undefined=StrictUndefined, autoescape=False)
                    try:
                        return mini_env.from_string("{{ " + expr + " }}").render(
                            sourcename=ctx.get("sourcename"),
                            entity=ctx.get("entity"),
                        )
                    except Exception:
                        return m.group(0)

                content = pattern.sub(replace_match, raw)
                # Also fill copy_into instance placeholder for dbt models
                try:
                    instance_val = ctx.get("instance") or "mlsfangenome"
                    content = content.replace("__COPYINTO_INSTANCE__", str(instance_val))
                except Exception:
                    pass

                # Force-resolve unique_key for specific sources (no dbt this.name available here)
                try:
                    sn = ctx.get("sourcename")
                    source_lower = sn.lower() if hasattr(sn, "lower") else str(sn).lower()
                    id_sources = {"mlsfangenometicketing", "mlsfangenomemerchandisea"}
                    chosen_key = "ID" if source_lower in id_sources else "MLS_ID"
                    # Replace single-quoted or double-quoted Jinja expressions
                    content = re.sub(r"(unique_key\s*=\s*)'{{[^}]+}}'", r"\1'" + chosen_key + "'", content)
                    content = re.sub(r'(unique_key\s*=\s*)"{{[^}]+}}"', r'\1"' + chosen_key + '"', content)
                except Exception:
                    pass
            elif "/kagr-data/ddl/" in opath_norm:
                # Fully render DDL SQL (no dbt macros), but keep {{database}} literal
                rel_path = os.path.relpath(str(template_path), str(repo_root))
                try:
                    tmpl = env.get_template(rel_path)
                except TemplateNotFound:
                    with template_path.open("r", encoding="utf-8") as f:
                        tmpl = Template(f.read())
                ctx2 = dict(ctx)
                ctx2.setdefault("database", "{{database}}")
                # Ensure table_name remains a literal placeholder for downstream Jinja
                ctx2.setdefault("table_name", "{{table_name}}")
                content = tmpl.render(**ctx2)
                # Resolve only {{ sourcename | upper }} occurrences in header blocks
                try:
                    sn = ctx.get("sourcename")
                    sn_upper = sn.upper() if hasattr(sn, "upper") else str(sn).upper()
                    content = re.sub(r"{{\s*sourcename\s*\|\s*upper\s*}}", sn_upper, content)
                except Exception:  # pylint: disable=broad-exception-caught
                    pass
            else:
                # Default: leave unchanged (safety)
                with template_path.open("r", encoding="utf-8") as f:
                    content = f.read()
        else:
            # Load template as a file path relative to repo root.
            rel_path = os.path.relpath(str(template_path), str(repo_root))
            # Special-case .env files: render with whitespace trimming disabled to avoid
            # concatenating lines when using inline conditionals.
            if str(template_path).endswith(".env.j2"):
                local_env = Environment(
                    loader=FileSystemLoader(str(repo_root)),
                    undefined=StrictUndefined,
                    autoescape=False,
                    trim_blocks=False,
                    lstrip_blocks=False,
                )
                try:
                    tmpl = local_env.get_template(rel_path)
                except TemplateNotFound:
                    with template_path.open("r", encoding="utf-8") as f:
                        tmpl = Template(f.read())
                content = tmpl.render(**ctx)
            else:
                try:
                    tmpl = env.get_template(rel_path)
                except TemplateNotFound:
                    # Fallback: load directly from file if the loader couldn't locate the template
                    with template_path.open("r", encoding="utf-8") as f:
                        tmpl = Template(f.read())
                content = tmpl.render(**ctx)

        # Write file (we already checked for collisions)
        with output_path.open("x", encoding="utf-8") as f:
            f.write(content)
    # Progress handling done by iterator


# --------------
# Main CLI entry
# --------------


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point for the MLS Fan Genome configuration generator.

    Parses command line arguments, loads and validates input data,
    plans output files, and generates them (unless --dry-run).

    Args:
        argv: Optional command line arguments (defaults to sys.argv).

    Returns:
        Exit code: 0 for success, 2 for validation errors.
    """
    parser = argparse.ArgumentParser(
        description="Generate MLS Fan Genome configs from Excel data dictionary and Jinja templates"
    )
    parser.add_argument(
        "--input", required=True, help="Path to Excel workbook (data dictionary)"
    )
    parser.add_argument("--client", required=True, help="Client code (e.g., KROENKE)")
    parser.add_argument(
        "--feature", required=True, help="Feature name (e.g., mlsfangenome)"
    )
    parser.add_argument(
        "--version", required=True, help="Template version (e.g., v1_0_0)"
    )
    parser.add_argument(
        "--instance",
        required=False,
        help="Optional instance name; will suffix object names and filenames",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and print planned outputs without writing files",
    )

    args = parser.parse_args(argv)

    repo_root = Path.cwd()
    workbook_path = Path(args.input)
    client = args.client
    feature = args.feature
    version = args.version
    instance = args.instance
    dry_run = args.dry_run

    # Load auxiliary data and metadata
    feature_settings = {}  # Do not use additional_settings.json
    global_ctx = build_global_context(
        client=client,
        feature=feature,
        version=version,
        feature_settings=feature_settings,
    )

    meta = load_metadata(feature=feature, version=version)

    # Parse and validate workbook (strict)
    parsed = parse_workbook(workbook_path)

    # Plan outputs
    plans = plan_outputs(
        meta=meta,
        repo_root=repo_root,
        global_ctx=global_ctx,
        entities=parsed.entities,
        instance=instance,
        standardization_map=parsed.standardization_map,
        standardization_info_map=parsed.standardization_info_map,
    )

    _, errors = check_plans(plans)

    if errors:
        print("Validation errors:")
        for e in errors:
            print(f" - {e}")
        return 2

    if dry_run:
        # Write planned outputs to a dry-run results file instead of printing
        results_path = repo_root / f"mlsfangenome_{client}_dry_run_results.txt"
        lines: List[str] = ["Planned outputs (no files written):\n"]
        for p in iter_progress(plans, label="Planning outputs", total=len(plans), mode="auto"):
            tpl_rel = os.path.relpath(str(p["template_path"]), str(repo_root))
            out_rel = os.path.relpath(str(p["output_path"]), str(repo_root))
            lines.append(f" - TEMPLATE: {tpl_rel}\n")
            lines.append(f"   OUTPUT  : {out_rel}\n")
        with results_path.open("w", encoding="utf-8") as f:
            f.writelines(lines)
        print(f"Dry-run results written to: {results_path.resolve()}")
        print("Reminder: delete this temporary file after review.")
        return 0

    # Write files
    render_and_write(plans, repo_root)

    print(f"Generated {len(plans)} files.")

    # Post-run reminder to review Melissa model YAML outputs
    melissa_paths = [
        str(p["output_path"]) for p in plans if p.get("entry", {}).get("name") == "melissa_model_yaml_per_entity"
    ]
    if melissa_paths:
        print("********************")
        print("Manual review recommended for Melissa model YAML files:")
        for mp in melissa_paths:
            print(f" - {mp}")
        print("********************")
    if not melissa_paths:
        print("")
        print("WARNING: No Melissa model YAML files were generated. Please check your data dictionary to confirm that the standardization mapping is filled out.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
