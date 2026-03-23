import pytesseract as pt 
from PIL import Image
import cv2
import numpy as np
import re
import pandas as pd
from pdf2image import convert_from_path
import json

def load_image(pdf_path):
    pages = convert_from_path(pdf_path)
    img_pill = pages[0]
    img = np.array(img_pill)
    return img

def ocr_with_confidence(img):
    df = pt.image_to_data(img, output_type = pt.Output.DATAFRAME)
    df = df[df["conf"] != -1]
    return df["conf"].mean(), pt.image_to_string(img, lang = "rus+eng")

def preprocess(img):
    big_img = cv2.resize(img, None, fx=2, fy=2)
    gray = cv2.cvtColor(big_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh



replacements = {
    "A":"А",
    "B":"В",
    "E":"Е",
    "K":"К",
    "M":"М",
    "H":"Н",
    "O":"О",
    "P":"Р",
    "C":"С",
    "T":"Т",
    "Y":"У",
    "X":"Х",
    "a":"а",
    "e":"е",
    "o":"о",
    "p":"р",
    "c":"с",
    "y":"у",
    "x":"х",
}

def rure_place(text, dict):
    for e, r in dict.items():
        text = text.replace(e,r)
    return text

def normalize_text(text):
    prepro = rure_place(text, replacements)
    prepro = re.sub(r"(?<=[\d-])О|О(?=[\d-])", "0", prepro)
    return prepro

def get_full_name(text):
    if isinstance(text, str):
        matchh = re.search(r"что\s([А-ЯЁ][а-яё]+)\s([А-ЯЁ][а-яё]+)\s([А-ЯЁ][а-яё]+)", text, re.IGNORECASE)
        if matchh:
            full_name = matchh.group(1,2,3)
            return " ".join(full_name)
    return None

def get_reg_num(text):
    
    if isinstance(text, str):
        matchh = re.search(r"Регистрационный\s+номер\s+(\d+-\d+)", text, re.IGNORECASE)
        if matchh:
            reg_num = matchh.group(1)
            return reg_num
    return None

def get_own_date(text):
    if isinstance(text, str):
        matchh = re.search(r"выдачи\s+(\d{2}\.\d{2}\.\d{4})", text, re.IGNORECASE)
        if matchh:
            own_date = matchh.group(1)
            return own_date
    return None

def get_doc_num(text):
    if isinstance(text, str):
        matchh = re.search(r"О\s+ПОВЫШЕНИИ\s+КВАЛИФИКАЦИИ\s+(\d+)", text, re.IGNORECASE)
        if matchh:
            doc_num = matchh.group(1)
            return doc_num
    return None

def get_date_from(text):
    if isinstance(text, str):
        matchh = re.search(r"с\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)\sпо\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)", text, re.IGNORECASE)
        if matchh:
            date_from = matchh.group(1)
            return date_from
    return None

def get_date_to(text):
    if isinstance(text, str):
        matchh = re.search(r"с\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)\sпо\s+(\d{2}\s+[а-яё]+\s+\d{4}\s+г\.)", text, re.IGNORECASE)
        if matchh:
            date_to = matchh.group(2)
            return date_to
    return None

def get_city_name(text):
    if isinstance(text, str):
        matchh = re.search(r"Город\s([А-ЯЁ][а-яё]+)", text, re.IGNORECASE)
        if matchh:
            city_name = matchh.group(1)
            return city_name
    return None

def get_new_spec(text):
    if isinstance(text, str):
        matchh = re.search(r"программе\s+«([^»]+)»", text, re.IGNORECASE)
        if matchh:
            new_spec = matchh.group(1)
            return new_spec
    return None

def get_hours_num(text):
    if isinstance(text, str):
        matchh = re.search(r"объеме\s+(\d+)",text, re.IGNORECASE)
        if matchh:
            hours_num = matchh.group(1)
            return hours_num
    return None
    
def build_json(text,save_file=False):
    text = normalize_text(text)
    jsonn = {
        "full_name":get_full_name(text),
        "own_date":get_own_date(text),
        "reg_num": get_reg_num(text),
        "doc_num": get_doc_num(text),
        "date_from": get_date_from(text),
        "date_to": get_date_to(text),
        "city_name": get_city_name(text),
        "new_spec": get_new_spec(text),
        "hours_num": get_hours_num(text)
    }
    if save_file:
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(jsonn, f, ensure_ascii=False, indent=4)
    return jsonn

def process_document(pdf_path):
    img = load_image(pdf_path)
    processed = preprocess(img)
    orig_conf, orig_text = ocr_with_confidence(img)
    proc_conf, proc_text = ocr_with_confidence(processed)
    text = proc_text
    return build_json(text)
print(process_document("тессеракт/скан9тип1(?).pdf"))