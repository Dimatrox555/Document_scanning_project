"""
Утилиты для пост-обработки OCR: система правил замены и нормализации текста.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable, List, Union
import re

Replacement = Union[str, Callable[[re.Match[str]], str]]

@dataclass
class ReplacementRule:
    pattern: re.Pattern[str]
    replace: Replacement
    note: str = ""
    enabled: bool = True

    def apply(self, text: str) -> str:
        if not self.enabled:
            return text
        return self.pattern.sub(self.replace, text)


class TextCleaner:
    def __init__(self) -> None:
        self.rules: List[ReplacementRule] = []

    def add_rule(self, pattern: str, replace: Replacement, note: str = "") -> None:
        compiled = re.compile(pattern, re.IGNORECASE)
        self.rules.append(ReplacementRule(compiled, replace, note=note))

    def apply(self, text: str) -> str:
        for rule in self.rules:
            text = rule.apply(text)
        return re.sub(r"\s+", " ", text).strip()


cleaner = TextCleaner()