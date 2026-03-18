import csv
import io
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def normalize_headers(fieldnames: list[str]) -> list[str]:
    return [header.strip().lower() if header else "" for header in fieldnames]


def parse_semicolon_csv(content: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(content), delimiter=";")
    if not reader.fieldnames:
        raise ValueError("Arquivo sem cabeçalhos")
    reader.fieldnames = normalize_headers(reader.fieldnames)
    rows = []
    for row in reader:
        normalized = {str(k).strip().lower(): (v or "").strip() for k, v in row.items()}
        if any(value for value in normalized.values()):
            rows.append(normalized)
    return rows


def parse_decimal(value: str) -> Decimal:
    if value is None:
        raise ValueError("Valor numérico ausente")
    cleaned = value.strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except (InvalidOperation, AttributeError) as exc:
        raise ValueError(f"Valor numérico inválido: {value}") from exc


def parse_date_br(value: str):
    try:
        return datetime.strptime(value.strip(), "%d/%m/%Y").date()
    except Exception as exc:
        raise ValueError(f"Data inválida: {value}") from exc


def _format_xlsx_cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, date):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, float):
        # round antes de converter para evitar lixo de ponto flutuante do Excel
        # (ex: 400.00000000000006 vindo de fórmulas =debito-credito)
        d = Decimal(repr(round(value, 2)))
        s = str(d)
        return s.replace(".", ",") if "." in s else s
    if isinstance(value, int):
        return str(value)
    return str(value).strip()


def parse_xlsx_to_csv_text(raw: bytes) -> str:
    try:
        import openpyxl
    except ImportError as exc:
        raise RuntimeError("openpyxl não instalado. Adicione 'openpyxl' ao requirements.txt.") from exc
    wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    ws = wb.active
    out = io.StringIO()
    writer = csv.writer(out, delimiter=";")
    for row in ws.iter_rows(values_only=True):
        cells = [_format_xlsx_cell(c) for c in row]
        if any(cells):
            writer.writerow(cells)
    wb.close()
    return out.getvalue()
