from __future__ import annotations
import math
from typing import Optional
from .vector3 import Vec3

__all__ = ["Plane"]


class Plane:
    __slots__ = ("normal", "d")

    def __init__(self, normal: Vec3, d: float) -> None:
        self.normal = normal.normalized()
        self.d = d

    @classmethod
    def from_point_normal(cls, point: Vec3, normal: Vec3) -> "Plane":
        n = normal.normalized()
        return cls(n, -n.dot(point))

    @classmethod
    def from_three_points(cls, p0: Vec3, p1: Vec3, p2: Vec3) -> "Plane":
        n = (p1 - p0).cross(p2 - p0)
        return cls.from_point_normal(p0, n)

    @classmethod
    def xy(cls) -> "Plane":
        return cls(Vec3(0, 0, 1), 0)

    @classmethod
    def xz(cls) -> "Plane":
        return cls(Vec3(0, 1, 0), 0)

    @classmethod
    def yz(cls) -> "Plane":
        return cls(Vec3(1, 0, 0), 0)

    def signed_distance(self, p: Vec3) -> float:
        return self.normal.dot(p) + self.d

    def distance(self, p: Vec3) -> float:
        return abs(self.signed_distance(p))

    def side(self, p: Vec3, eps: float = 1e-9) -> int:
        sd = self.signed_distance(p)
        if sd > eps:
            return 1
        if sd < -eps:
            return -1
        return 0

    def project_point(self, p: Vec3) -> Vec3:
        return p - self.normal * self.signed_distance(p)

    def mirror_point(self, p: Vec3) -> Vec3:
        return p - self.normal * (2.0 * self.signed_distance(p))

    def intersect_ray(self, origin: Vec3, direction: Vec3
                      ) -> Optional[Vec3]:
        denom = self.normal.dot(direction)
        if abs(denom) < 1e-12:
            return None
        t = -(self.normal.dot(origin) + self.d) / denom
        if t < 0:
            return None
        return origin + direction * t

    def intersect_segment(self, a: Vec3, b: Vec3
                           ) -> Optional[Vec3]:
        da = self.signed_distance(a)
        db = self.signed_distance(b)
        if da * db > 0:
            return None   # оба по одну сторону
        if abs(da - db) < 1e-12:
            return None
        t = da / (da - db)
        return a.lerp(b, t)

    def __repr__(self) -> str:
        n = self.normal
        return f"Plane(normal={n}, d={self.d:.6g})"
