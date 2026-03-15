import csv
import io
from datetime import datetime
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
