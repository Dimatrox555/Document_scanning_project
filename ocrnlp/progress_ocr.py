import pytesseract as pt 
from ocrnlp.patterns import patterns
import re
import json
import logging
from OpenCV_proj.main import *
from log_config import setup_logging
from WITHOWT_NIKITA_TESTS import preprocess_local

import cv2 as cv
#Запуск логирования 
setup_logging()
logger = logging.getLogger(__name__)


#Подсчет среднего значения(mean_conf) уверенности и сканирование текста(text)
def ocr_with_confidence(img):
    logger.info("ocr start")
    
    try:
        df = pt.image_to_data(img, output_type = pt.Output.DATAFRAME)
        df = df[df["conf"] != -1]
        mean_conf = df["conf"].mean()
        text = pt.image_to_string(img, lang = "rus+eng")
        if mean_conf is not None and mean_conf < 50:
            logger.warning(f"LOW OCR CONF: {mean_conf}")
        else:
            logger.debug(f"mean_conf={mean_conf}")
        logger.debug(f"len={len(text)}")
        return mean_conf, text
    except Exception:
        logger.exception("ocr falied")
        return None, ""
        

#TODO временный словарь замен(переедет в changes
replacements = {
    "A":"А", "B":"В", "E":"Е", "K":"К", "M":"М",
    "H":"Н", "O":"О", "P":"Р", "C":"С", "T":"Т",
    "Y":"У", "X":"Х", "a":"а", "e":"е", "o":"о",
    "p":"р", "c":"с", "y":"у", "x":"х"
}


#TODO временная функция замены слов по словарю
def replace_chars(text, mapping):
    """замена слов по словарю"""
    for old_char, new_char in mapping.items():
        text = text.replace(old_char, new_char)
    return text

#TODO доделать с 6 б и тд (переедет в chages)
def normalize_text(text):
    prepro = replace_chars(text, replacements)
    prepro = re.sub(r"(?<=[\d-])О|О(?=[\d-])", "0", prepro)
    return prepro

#функция получения паттерна (возможно переедет в patterns)
def get_pattern(doc_type, field, pattern_index=0):
    pattern_key = patterns["doc_schemas"][doc_type][field][pattern_index]
    return patterns["pattern_lib"][pattern_key]

#экстраткеры на все случаи жизни, служат универсальной заменой геттеров
def extract_document(text,doc_type,field, pattern_index=0):
    pattern = get_pattern(doc_type, field, pattern_index)

    logger.debug(f"field={field}, pattern={pattern}")

    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        logger.warning(f"{field} NOT FOUND")
        return None
    if len(match.groups()) > 1 :
        res = " ".join(match.groups())
    else:
        res = match.group(1)

    logger.debug(f"{field} FOUND: {res}")
    return res

#построение json с вариативным сохранением(нуждается в доработке TODO (имеется ввиду сохранение файла))
def build_json(text,save_file=False):
    logger.info("build_json start")
    text = normalize_text(text)
    jsonn = {
        "full_name":extract_document(text,"doc_type1", "full_name"),
        "own_date":extract_document(text,"doc_type1", "own_date"),
        "reg_num": extract_document(text,"doc_type1", "reg_num"),
        "doc_num": extract_document(text,"doc_type1", "doc_num"),
        "date_from": extract_document(text,"doc_type1", "date_from"),
        "date_to": extract_document(text,"doc_type1", "date_to"),
        "city_name": extract_document(text,"doc_type1", "city_name"),
        "new_spec": extract_document(text,"doc_type1", "new_spec"),
        "hours_num": extract_document(text, "doc_type1", "hours_num"),
        "organization" : extract_document(text, "doc_type1", "organization")
    }

    found = sum(1 for v in jsonn.values() if v is not None)
    logger.info(f"fields parsed: {found}/{len(jsonn)}")

    if save_file:
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(jsonn, f, ensure_ascii=False, indent=4)
    return jsonn

# функция процессинга (итоговая) (структура нуждается в доработке и согласовании с командой)
def process_image():
    logger.info("process_image start")
    #img2 = preprocess_local(img)
    
    try:
        img2 = preprocess()
        logger.debug(f"img type={type(img2)}")

        orig_conf, orig_text = ocr_with_confidence(img2)
        if orig_conf is None:
            logger.error("OCR returned None")
            return None
        
        logger.info(f"OCR done, conf={orig_conf}")

        result = build_json(orig_text)

        logger.info("process_image done")
        return result

    except Exception:
        logger.exception("process_image failed")
        return None
