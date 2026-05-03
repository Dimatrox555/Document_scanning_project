import re
import unicodedata


def normalize_for_compare(value):
    if value is None:
        return ""
    s = str(value).strip().lower()
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s)
    return s


def levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        cur = [i]
        for j, cb in enumerate(b, start=1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def cer(reference, hypothesis):
    ref = normalize_for_compare(reference)
    hyp = normalize_for_compare(hypothesis)
    if not ref:
        return None
    return levenshtein(ref, hyp) / len(ref)


def field_scores(gold, pred):
    g = normalize_for_compare(gold)
    p = normalize_for_compare(pred)
    dist = levenshtein(g, p)
    if not g:
        c = None if p else 0.0
    else:
        c = dist / len(g)
    return {"exact": g == p, "levenshtein": dist, "cer": c}


def fulltext_metrics(gold_text, pred_text):
    g = normalize_for_compare(gold_text)
    p = normalize_for_compare(pred_text)
    c = cer(gold_text, pred_text)
    return {"chars_ref": len(g), "chars_hyp": len(p), "levenshtein": levenshtein(g, p), "cer": c}
