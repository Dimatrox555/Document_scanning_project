# Только OCR+NLP

import json
from datetime import datetime
from pathlib import Path

from PIL import Image

try:
    from ocrnlp.progress_ocr import process_image
except ModuleNotFoundError:
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from ocrnlp.progress_ocr import process_image
try:
    from eval.compare import compare_run, load_gold_dir, load_image_paths
except ModuleNotFoundError:
    from compare import compare_run, load_gold_dir, load_image_paths


def run_eval(images_dir="eval/images", gold_dir="eval/gold", out=None):
    gold_docs = load_gold_dir(gold_dir)
    predictions = []
    for path in load_image_paths(images_dir):
        try:
            img = Image.open(path)
        except Exception:
            predictions.append(None)
        else:
            predictions.append(process_image(img))

    report = compare_run(predictions, gold_docs)

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)

    if out:
        out_path = Path(out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
    _append_results_log(report, images_dir, gold_dir)

    if report["documents_compared"] < report["gold_total"]:
        return 2
    if report["documents_compared"] < report["predictions_total"]:
        return 2
    return 0


def _append_results_log(report, images_dir, gold_dir):
    log_path = Path(__file__).resolve().parent / "results_log.txt"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = (
        f"[{ts}] "
        f"images_dir={images_dir} "
        f"gold_dir={gold_dir} "
        f"docs={report['documents_compared']}/{report['gold_total']} "
        f"pred_ok={report['predictions_ok']}/{report['predictions_total']} "
        f"macro_acc={report['macro_field_exact_acc']} "
        f"macro_cer={report['macro_mean_cer']}\n"
    )
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(line)


if __name__ == "__main__":
    raise SystemExit(run_eval())
