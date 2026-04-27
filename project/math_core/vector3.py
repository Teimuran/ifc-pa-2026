from __future__ import annotations
import math
from typing import Iterator, Tuple

__all__ = ["Vec3"]


class Vec3:
    __slots__ = ("x", "y", "z")

    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    @classmethod
    def from_sequence(cls, seq) -> "Vec3":
        x, y, z = seq
        return cls(x, y, z)

    @classmethod
    def zero(cls) -> "Vec3":
        return cls(0, 0, 0)

    @classmethod
    def ones(cls) -> "Vec3":
        return cls(1, 1, 1)

    def __add__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: "Vec3") -> "Vec3":
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> "Vec3":
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> "Vec3":
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> "Vec3":
        inv = 1.0 / scalar
        return Vec3(self.x * inv, self.y * inv, self.z * inv)

    def __neg__(self) -> "Vec3":
        return Vec3(-self.x, -self.y, -self.z)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vec3):
            return NotImplemented
        return (math.isclose(self.x, other.x) and
                math.isclose(self.y, other.y) and
                math.isclose(self.z, other.z))

    def dot(self, other: "Vec3") -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: "Vec3") -> "Vec3":
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def length_sq(self) -> float:
        return self.x * self.x + self.y * self.y + self.z * self.z

    def length(self) -> float:
        return math.sqrt(self.length_sq())

    def normalized(self) -> "Vec3":
        lng = self.length()
        if lng < 1e-12:
            return Vec3(self.x, self.y, self.z)
        return self / lng

    def lerp(self, other: "Vec3", t: float) -> "Vec3":
        return Vec3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
        )

    def distance_to(self, other: "Vec3") -> float:
        return (other - self).length()

    def angle_to(self, other: "Vec3") -> float:
        denom = self.length() * other.length()
        if denom < 1e-12:
            return 0.0
        cos_a = max(-1.0, min(1.0, self.dot(other) / denom))
        return math.acos(cos_a)

    def reflect(self, normal: "Vec3") -> "Vec3":
        n = normal.normalized()
        return self - n * (2.0 * self.dot(n))

    def is_zero(self, eps: float = 1e-9) -> bool:
        return self.length_sq() < eps * eps

    def is_unit(self, eps: float = 1e-6) -> bool:
        return abs(self.length_sq() - 1.0) < eps

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    def to_list(self):
        return [self.x, self.y, self.z]

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y
        yield self.z

    def __getitem__(self, index: int) -> float:
        return (self.x, self.y, self.z)[index]

    def __repr__(self) -> str:
        return f"Vec3({self.x:.6g}, {self.y:.6g}, {self.z:.6g})"
