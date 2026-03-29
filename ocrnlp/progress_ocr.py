import pytesseract as pt 
from PIL import Image
from patterns import patterns
import numpy as np
import re
import pandas as pd

import json


def ocr_with_confidence(img):
    df = pt.image_to_data(img, output_type = pt.Output.DATAFRAME)
    df = df[df["conf"] != -1]
    return df["conf"].mean(), pt.image_to_string(img, lang = "rus+eng")




replacements = {
    "A":"А", "B":"В", "E":"Е", "K":"К", "M":"М",
    "H":"Н", "O":"О", "P":"Р", "C":"С", "T":"Т",
    "Y":"У", "X":"Х", "a":"а", "e":"е", "o":"о",
    "p":"р", "c":"с", "y":"у", "x":"х"
}

def replace_chars(text, mapping):
    """замена слов по словарю"""
    for old_char, new_char in mapping.items():
        text = text.replace(old_char, new_char)
    return text

def normalize_text(text):
    prepro = replace_chars(text, replacements)
    prepro = re.sub(r"(?<=[\d-])О|О(?=[\d-])", "0", prepro)
    return prepro

def get_pattern(doc_type, feild, pattern_index=0):
    pattern_key = patterns["doc_schemas"][doc_type][feild][pattern_index]
    return patterns["pattern_lib"][pattern_key]

print(get_pattern("doc_type2", "reg_num"))

def get_full_name(text):
    """получение фио"""
    if not isinstance(text, str):
        return None
    match = re.search(
        r"что\s([А-ЯЁ][а-яё]+)\s([А-ЯЁ][а-яё]+)\s([А-ЯЁ][а-яё]+)",
        text,
        re.IGNORECASE
        )
    return " ".join(match.groups()) if match else None

def get_reg_num(text):
    """получение регистрационного номера"""
    if not isinstance(text, str):
        return None
    match = re.search(
        r"Регистрационный\s+номер\s+(\d+-\d+)",
        text,
        re.IGNORECASE
        )
    return match.group(1) if match else None

def get_own_date(text):
    """получение даты получения"""
    if not isinstance(text, str):
        return None
    match = re.search(
        r"выдачи\s+(\d{2}\.\d{2}\.\d{4})",
        text,
        re.IGNORECASE
        )
    return match.group(1) if match else None
        

def get_doc_num(text):
    """получение номера документа"""
    if not isinstance(text, str):
        return None
    match = re.search(
        r"О\s+ПОВЫШЕНИИ\s+КВАЛИФИКАЦИИ\s+(\d+)",
        text,
        re.IGNORECASE
        )
    return match.group(1) if match else None

def get_date_from_to(text, flg):
    """получение даты от/до"""
    if flg not in (0,1):
        raise ValueError("1 или 0 надо")
    if not isinstance(text, str):
        return None
    match = re.search(
        r"с\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)\sпо\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)",
        text,
        re.IGNORECASE
        )
    if flg == 0:
        return match.group(1) if match else None 
    else: 
        return match.group(2) if match else None 
    

def get_city_name(text):
    """получение названия города"""
    if not isinstance(text, str):
        return None
    match = re.search(
        r"Город\s([А-ЯЁ][а-яё]+)",
        text,
        re.IGNORECASE
        )
    return match.group(1) if match else None


def get_new_spec(text):
    """получение обученой специальности"""
    if not isinstance(text, str):
        return None
    match = re.search(
        r"программе\s+«([^»]+)»",
        text,
        re.IGNORECASE
        )
    return match.group(1) if match else None

def get_hours_num(text):
    if not isinstance(text, str):
        return None
    match = re.search(
        r"объеме\s+(\d+)",
        text,
        re.IGNORECASE
        )
    return match.group(1) if match else None
    
def build_json(text,save_file=False):
    text = normalize_text(text)
    jsonn = {
        "full_name":get_full_name(text),
        "own_date":get_own_date(text),
        "reg_num": get_reg_num(text),
        "doc_num": get_doc_num(text),
        "date_from": get_date_from_to(text,0),
        "date_to": get_date_from_to(text,1),
        "city_name": get_city_name(text),
        "new_spec": get_new_spec(text),
        "hours_num": get_hours_num(text)
    }
    if save_file:
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(jsonn, f, ensure_ascii=False, indent=4)
    return jsonn

def process_image(img):
    orig_conf, orig_text = ocr_with_confidence(img)
    text = orig_text
    return build_json(text)
