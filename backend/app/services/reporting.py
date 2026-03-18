from __future__ import annotations

from io import StringIO
import csv

from app.schemas.prediction import CsvAiData, PredictionResult


CSV_COLUMNS = [
    "Name/Source",
    "Diagnosis",
    "Why",
    "Immediate Actions",
    "Prevention",
    "Errors",
]


def build_csv_report(
    predictions: list[PredictionResult],
    ai_data: dict[str, CsvAiData] | None = None,
) -> str:
    out = StringIO()
    writer = csv.DictWriter(out, fieldnames=CSV_COLUMNS)
    writer.writeheader()

    for item in predictions:
        ai = (ai_data or {}).get(item.id, CsvAiData())
        writer.writerow(
            {
                "Name/Source": item.source_name,
                "Diagnosis": ai.diagnosis,
                "Why": ai.why,
                "Immediate Actions": "; ".join(ai.immediate_actions),
                "Prevention": "; ".join(ai.prevention),
                "Errors": " | ".join(item.errors) if item.errors else "",
            }
        )

    return out.getvalue()
