import json
from pathlib import Path

try:
    from .metrics import field_scores
except ImportError:
    from metrics import field_scores

_IMAGE_EXT = {".png", ".tiff", ".tif", ".jpg", ".jpeg"}


def load_image_paths(images_dir):
    """Файлы 0.png, 1.tiff, … — тот же порядок номеров, что у eval/gold/*.json."""
    images_dir = Path(images_dir)
    if not images_dir.is_dir():
        raise FileNotFoundError(images_dir)

    paths = [
        p
        for p in images_dir.iterdir()
        if p.is_file() and p.suffix.lower() in _IMAGE_EXT and p.stem.isdigit()
    ]
    paths.sort(key=lambda p: int(p.stem))
    return [str(p) for p in paths]


def load_gold_dir(gold_dir):
    gold_dir = Path(gold_dir)
    if not gold_dir.is_dir():
        raise FileNotFoundError(gold_dir)

    paths = [p for p in gold_dir.glob("*.json") if p.stem.isdigit()]
    paths.sort(key=lambda p: int(p.stem))

    out = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            out.append(json.load(f))
    return out


def compare_document(prediction, gold, fields=None):
    if fields:
        keys = list(fields)
    else:
        keys = sorted(set(gold) | set(prediction or []))

    per_field = {}
    exact = 0
    cer_sum = 0.0
    cer_count = 0

    for key in keys:
        gv = gold.get(key)
        pv = prediction.get(key) if prediction else None
        row = field_scores(gv, pv)
        per_field[key] = row
        if row["exact"]:
            exact += 1
        if row["cer"] is not None:
            cer_sum += row["cer"]
            cer_count += 1

    return {
        "fields": per_field,
        "field_exact_acc": exact / len(keys) if keys else 0.0,
        "mean_cer": cer_sum / cer_count if cer_count else None,
        "prediction_ok": prediction is not None,
    }


def compare_run(predictions, gold_documents, fields=None):
    n = min(len(predictions), len(gold_documents))
    per_doc = []
    for i in range(n):
        per_doc.append(compare_document(predictions[i], gold_documents[i], fields))

    ok = sum(1 for d in per_doc if d["prediction_ok"])
    accs = [d["field_exact_acc"] for d in per_doc if d["prediction_ok"]]
    cers = [d["mean_cer"] for d in per_doc if d["mean_cer"] is not None]

    return {
        "documents_compared": n,
        "predictions_total": len(predictions),
        "gold_total": len(gold_documents),
        "predictions_ok": ok,
        "per_document": per_doc,
        "macro_field_exact_acc": sum(accs) / len(accs) if accs else None,
        "macro_mean_cer": sum(cers) / len(cers) if cers else None,
    }
