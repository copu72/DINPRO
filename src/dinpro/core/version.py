from dataclasses import dataclass


from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    major: int = 0
    minor: int = 3
    patch: int = 1
    suffix: str = "-dev"

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}{self.suffix}"

    @property
    def label(self) -> str:
        return f"DINPRO Professional v{self}"

    @classmethod
    def from_string(cls, version_str: str) -> Version:
        parts = version_str.strip().split(".")
        if len(parts) < 2:
            raise ValueError(f"Invalid version string: {version_str}")
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2]) if len(parts) > 2 else 0
        suffix = version_str[len(f"{major}.{minor}.{patch}"):]
        return cls(major=major, minor=minor, patch=patch, suffix=suffix)
