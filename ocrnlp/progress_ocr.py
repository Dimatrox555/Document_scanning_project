import pytesseract as pt 
from patterns import patterns
import re
import json
from OpenCV_proj.main import grayscale
import cv2 as cv


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
#TODO доделать с 6 б и тд
def normalize_text(text):
    prepro = replace_chars(text, replacements)
    prepro = re.sub(r"(?<=[\d-])О|О(?=[\d-])", "0", prepro)
    return prepro

def get_pattern(doc_type, field, pattern_index=0):
    pattern_key = patterns["doc_schemas"][doc_type][field][pattern_index]
    return patterns["pattern_lib"][pattern_key]
    
def extract_document(text,doc_type,field, pattern_index=0):
    pattern = get_pattern(doc_type, field, pattern_index)
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None
    if len(match.groups()) > 1 :
        return " ".join(match.groups())
    else:
        return match.group(1)


def build_json(text,save_file=False):
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
    if save_file:
        with open("result.json", "w", encoding="utf-8") as f:
            json.dump(jsonn, f, ensure_ascii=False, indent=4)
    return jsonn

def process_image(img):
    img1 = cv.imread(img)
    img2 = grayscale(img1)
    orig_conf, orig_text = ocr_with_confidence(img2)
    text = orig_text
    return build_json(text)
