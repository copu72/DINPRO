from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    major: int = 0
    minor: int = 3
    patch: int = 1
    suffix: str = ""

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}{self.suffix}"

    @property
    def label(self) -> str:
        return f"DINPRO Professional v{self}"

    @classmethod
    def from_string(cls, version_str: str) -> Version:
        s = version_str.strip()
        parts = s.split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid version string: {version_str}")
        major = int(parts[0])
        minor = int(parts[1])
        if len(parts) > 2:
            patch_str = "".join(c for c in parts[2] if c.isdigit())
            patch = int(patch_str) if patch_str else 0
            suffix = s[len(f"{major}.{minor}.{patch}"):]
        else:
            patch = 0
            suffix = ""
        return cls(major=major, minor=minor, patch=patch, suffix=suffix)
