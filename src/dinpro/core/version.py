from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    major: int = 0
    minor: int = 1
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def label(self) -> str:
        return f"DINPRO Professional v{self}"

    @classmethod
    def from_string(cls, version_str: str) -> "Version":
        parts = version_str.strip().split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version string: {version_str}")
        return cls(major=int(parts[0]), minor=int(parts[1]), patch=int(parts[2]))
