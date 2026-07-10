from __future__ import annotations

from typing import TYPE_CHECKING

from dinpro.domain.linear_referencing.station import Station

if TYPE_CHECKING:
    pass


class StationParser:
    def __init__(
        self,
        decimal_sep: str = ".",
        pk_sep: str = "+",
        prefix: str = "",
        min_kilometer_len: int = 2,
    ) -> None:
        if decimal_sep == pk_sep:
            raise ValueError("decimal_sep and pk_sep must differ")
        self._decimal_sep = decimal_sep
        self._pk_sep = pk_sep
        self._prefix = prefix
        self._min_kilometer_len = min_kilometer_len

    def parse(self, text: str) -> Station:
        s = text.strip()
        if not s:
            raise ValueError("Cannot parse empty string as Station")

        s = self._remove_prefix(s)
        s = self._normalize_separator(s)
        value = self._to_float(s)
        return Station(value)

    def _remove_prefix(self, text: str) -> str:
        s = text.strip()
        prefixes = ["PK", "P.K.", "pk", "p.k.", "Pk", "pK"]
        if self._prefix:
            prefixes = [self._prefix] + [p for p in prefixes if p != self._prefix]
        for pfx in prefixes:
            if s.upper().startswith(pfx.upper()):
                s = s[len(pfx):].strip()
                break
        return s

    def _normalize_separator(self, text: str) -> str:
        s = text.strip()
        if self._pk_sep != "+":
            s = s.replace(self._pk_sep, "\x00")
        s = s.replace(" ", "")
        s = s.replace("\x00", "+")
        return s

    def _to_float(self, text: str) -> float:
        s = text.strip()
        if not s:
            raise ValueError("Empty station value")

        has_sign = s[0] in ("-", "+")
        sign = -1.0 if has_sign and s[0] == "-" else 1.0
        if has_sign:
            s = s[1:].strip()

        has_pk_sep = self._pk_sep in s or "+" in s
        if has_pk_sep and self._pk_sep != self._decimal_sep:
            sep = "+" if "+" in s else self._pk_sep
            parts = s.split(sep, maxsplit=1)
            if len(parts) != 2:
                raise ValueError(f"Invalid station format: {text}")
            km_str, m_str = parts
            if not km_str or not km_str.lstrip("-"):
                raise ValueError(f"Missing kilometer value: {text}")
            km = float(km_str.replace(self._decimal_sep, "."))
            m_raw = m_str.replace(self._decimal_sep, ".")
            if not m_raw:
                raise ValueError(f"Missing meter value: {text}")
            m = float(m_raw)
            if km < 0:
                value = km * 1000.0 - m
            else:
                value = km * 1000.0 + m
        else:
            normalized = s.replace(self._decimal_sep, ".")
            try:
                value = float(normalized)
            except ValueError:
                raise ValueError(f"Invalid station numeric value: {text}")
            if not (0 <= value < 1000):
                pass

        return sign * value

    @property
    def decimal_sep(self) -> str:
        return self._decimal_sep

    @property
    def pk_sep(self) -> str:
        return self._pk_sep
