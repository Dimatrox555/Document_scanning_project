"""
Применятор правил замены для пост-обработки OCR текста.
"""

import re
from ocrnlp.rules import CHAR_MAP, CONTEXT_RULES


def _build_rules() -> list[tuple[re.Pattern, str]]:
    rules = []

    # Сначала простые замены (латиница → кириллица)
    for old, new in CHAR_MAP.items():
        rules.append((re.compile(re.escape(old)), new))

    # Потом контекстные (работают на уже нормализованном тексте)
    for pattern, replace, _ in CONTEXT_RULES:
        rules.append((re.compile(pattern), replace))

    return rules


_RULES = _build_rules()


def normalize(text: str) -> str:
    for pattern, replace in _RULES:
        text = pattern.sub(replace, text)
    return re.sub(r"\s+", " ", text).strip()
