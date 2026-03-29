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

def get_full_name(text, pattern):
    """получение фио"""
    if not isinstance(text, str):
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    return " ".join(match.groups()) if match else None

def get_reg_num(text, pattern):
    """получение регистрационного номера"""
    if not isinstance(text, str):
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None

def get_own_date(text, pattern):
    """получение даты получения"""
    if not isinstance(text, str):
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None
        

def get_doc_num(text, pattern):
    """получение номера документа"""
    if not isinstance(text, str):
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None

def get_date_from_to(text, pattern, flg):
    """получение даты от/до"""
    if flg not in (0,1):
        raise ValueError("1 или 0 надо")
    if not isinstance(text, str):
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    if flg == 0:
        return match.group(1) if match else None 
    else: 
        return match.group(2) if match else None 
    

def get_city_name(text, pattern):
    """получение названия города"""
    if not isinstance(text, str):
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None


def get_new_spec(text, pattern):
    """получение обученой специальности"""
    if not isinstance(text, str):
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None

def get_hours_num(text,pattern):
    if not isinstance(text, str):
        return None
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1) if match else None

def get_organization(text, pattern):
    if not isinstance(text,str):
        return None
    match = re.search(pattern,text, re.IGNORECASE)
    return match.group(1) if match else None
    
def build_json(text,save_file=False):
    text = normalize_text(text)
    jsonn = {
        "full_name":get_full_name(text,get_pattern("doc_type1", "full_name")),
        "own_date":get_own_date(text,get_pattern("doc_type1", "own_date")),
        "reg_num": get_reg_num(text,get_pattern("doc_type1", "reg_num")),
        "doc_num": get_doc_num(text,get_pattern("doc_type1", "doc_num")),
        "date_from": get_date_from_to(text,get_pattern("doc_type1", "date_from_to"), 0),
        "date_to": get_date_from_to(text,get_pattern("doc_type1", "date_from_to"), 1),
        "city_name": get_city_name(text,get_pattern("doc_type1", "city_name")),
        "new_spec": get_new_spec(text,get_pattern("doc_type1", "new_spec")),
        "hours_num": get_hours_num(text,get_pattern("doc_type1", "hours_num")),
        "organization" : get_organization(text, get_pattern("doc_type1", "organization"))
    }
    if save_file:
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(jsonn, f, ensure_ascii=False, indent=4)
    return jsonn

def process_image(img):
    orig_conf, orig_text = ocr_with_confidence(img)
    text = orig_text
    return build_json(text)
