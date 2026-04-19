import re
import json
import logging
import time
import uuid

import pytesseract as pt

from ocrnlp.normalizer import normalize
from ocrnlp.patterns import patterns
from ocrnlp.log_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def ocr_with_confidence(img) -> tuple[float | None, str]:
    """Прогоняет изображение через Tesseract, возвращает (уверенность, текст).
    Уверенность — среднее значение conf по всем словам (0–100).
    Возвращает (None, "") если Tesseract упал.
    """
    run_id = str(uuid.uuid4())[:8]
    logger.info(f"[{run_id}] ocr start")

    try:
        t0 = time.perf_counter()
        df = pt.image_to_data(img, output_type=pt.Output.DATAFRAME)
        df = df[df["conf"] != -1]
        mean_conf = df["conf"].mean()
        t1 = time.perf_counter()

        text = pt.image_to_string(img, lang="rus+eng")
        t2 = time.perf_counter()

        logger.info(f"[{run_id}] tesseract: data={t1-t0:.3f}s  string={t2-t1:.3f}s  total={t2-t0:.3f}s")

        if mean_conf is not None and mean_conf < 50:
            logger.warning(f"[{run_id}] low confidence: {mean_conf:.1f}")
        else:
            logger.debug(f"[{run_id}] conf={mean_conf:.1f}  text_len={len(text)}")

        return mean_conf, text

    except Exception:
        logger.exception(f"[{run_id}] ocr failed")
        return None, ""


def get_pattern(doc_type: str, field: str, pattern_index: int = 0) -> str:
    """Достаёт regex-паттерн из patterns.py по типу документа и названию поля."""
    pattern_key = patterns["doc_schemas"][doc_type][field][pattern_index]
    return patterns["pattern_lib"][pattern_key]


def extract_field(text: str, doc_type: str, field: str, pattern_index: int = 0) -> str | None:
    """Извлекает одно поле из текста по паттерну.
    Возвращает строку с результатом или None если паттерн не сработал.
    """
    pattern = get_pattern(doc_type, field, pattern_index)
    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        logger.warning(f"  {field}: NOT FOUND")
        return None

    result = " ".join(match.groups()) if len(match.groups()) > 1 else match.group(1)
    logger.debug(f"  {field}: {result}")
    return result


def build_json(text: str, save_file: bool = False) -> dict:
    """Нормализует текст и извлекает все поля документа.
    Если save_file=True — дополнительно сохраняет результат в result.json.
    """
    text = normalize(text)
    logger.info("extracting fields")

    fields = [
        "full_name", "own_date", "reg_num", "doc_num",
        "date_from", "date_to", "city_name", "new_spec",
        "hours_num", "organization",
    ]
    result = {field: extract_field(text, "doc_type1", field) for field in fields}

    found = sum(1 for v in result.values() if v is not None)
    logger.info(f"fields parsed: {found}/{len(result)}")

    if save_file:
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

    return result


def process_image(img) -> dict | None:
    """Основная точка входа. Принимает изображение, возвращает словарь с полями документа.
    Возвращает None если OCR упал или произошла непредвиденная ошибка.
    """
    logger.info("process_image start")

    try:
        conf, text = ocr_with_confidence(img)
        if conf is None:
            logger.error("ocr returned nothing, aborting")
            return None

        result = build_json(text)
        logger.info("process_image done")
        logger.info(f"scanned text:\n{text}")
        return result

    except Exception:
        logger.exception("process_image failed")
        return None
