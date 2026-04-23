from __future__ import annotations
import math
from typing import Iterable, Optional, Tuple
from .vector3 import Vec3

__all__ = ["BBox"]


class BBox:
    __slots__ = ("min", "max")

    def __init__(self, min_pt: Vec3 | None = None, max_pt: Vec3 | None = None) -> None:
        _INF = math.inf
        self.min = min_pt if min_pt is not None else Vec3( _INF,  _INF,  _INF)
        self.max = max_pt if max_pt is not None else Vec3(-_INF, -_INF, -_INF)

    @classmethod
    def empty(cls) -> "BBox":
        return cls()

    @classmethod
    def from_points(cls, points: Iterable[Vec3]) -> "BBox":
        bb = cls()
        for p in points:
            bb.expand(p)
        return bb

    @classmethod
    def from_min_max(cls, min_pt: Vec3, max_pt: Vec3) -> "BBox":
        return cls(min_pt, max_pt)

    @classmethod
    def from_center_size(cls, center: Vec3, size: Vec3) -> "BBox":
        half = size * 0.5
        return cls(center - half, center + half)

    def expand(self, p: Vec3) -> None:
        self.min = Vec3(min(self.min.x, p.x),
                        min(self.min.y, p.y),
                        min(self.min.z, p.z))
        self.max = Vec3(max(self.max.x, p.x),
                        max(self.max.y, p.y),
                        max(self.max.z, p.z))

    def expand_bbox(self, other: "BBox") -> None:
        if other.is_valid():
            self.expand(other.min)
            self.expand(other.max)

    def expand_by(self, delta: float) -> None:
        d = Vec3(delta, delta, delta)
        self.min = self.min - d
        self.max = self.max + d

    def merged(self, other: "BBox") -> "BBox":
        result = BBox(self.min, self.max)
        result.expand_bbox(other)
        return result

    def intersection(self, other: "BBox") -> Optional["BBox"]:
        mn = Vec3(max(self.min.x, other.min.x),
                  max(self.min.y, other.min.y),
                  max(self.min.z, other.min.z))
        mx = Vec3(min(self.max.x, other.max.x),
                  min(self.max.y, other.max.y),
                  min(self.max.z, other.max.z))
        if mn.x <= mx.x and mn.y <= mx.y and mn.z <= mx.z:
            return BBox(mn, mx)
        return None

    def transformed(self, matrix) -> "BBox":
        corners = self.corners()
        return BBox.from_points(matrix.transform_point(c) for c in corners)

    def is_valid(self) -> bool:
        return (self.min.x <= self.max.x and
                self.min.y <= self.max.y and
                self.min.z <= self.max.z)

    def contains_point(self, p: Vec3) -> bool:
        return (self.min.x <= p.x <= self.max.x and
                self.min.y <= p.y <= self.max.y and
                self.min.z <= p.z <= self.max.z)

    def intersects(self, other: "BBox") -> bool:
        return (self.min.x <= other.max.x and self.max.x >= other.min.x and
                self.min.y <= other.max.y and self.max.y >= other.min.y and
                self.min.z <= other.max.z and self.max.z >= other.min.z)

    def intersects_ray(self, origin: Vec3, direction: Vec3
                       ) -> Tuple[bool, float, float]:
        t_min, t_max = -math.inf, math.inf
        for axis in range(3):
            d = direction[axis]
            o = origin[axis]
            lo = self.min[axis]
            hi = self.max[axis]
            if abs(d) < 1e-12:
                if o < lo or o > hi:
                    return False, 0.0, 0.0
            else:
                t1 = (lo - o) / d
                t2 = (hi - o) / d
                if t1 > t2:
                    t1, t2 = t2, t1
                t_min = max(t_min, t1)
                t_max = min(t_max, t2)
                if t_min > t_max:
                    return False, 0.0, 0.0
        return True, t_min, t_max

    def size(self) -> Vec3:
        return self.max - self.min

    def center(self) -> Vec3:
        return (self.min + self.max) * 0.5

    def volume(self) -> float:
        s = self.size()
        return max(0.0, s.x) * max(0.0, s.y) * max(0.0, s.z)

    def surface_area(self) -> float:
        s = self.size()
        return 2.0 * (s.x*s.y + s.y*s.z + s.z*s.x)

    def diagonal(self) -> float:
        return self.size().length()

    def corners(self):
        mn, mx = self.min, self.max
        for x in (mn.x, mx.x):
            for y in (mn.y, mx.y):
                for z in (mn.z, mx.z):
                    yield Vec3(x, y, z)

    def longest_axis(self) -> int:
        s = self.size()
        if s.x >= s.y and s.x >= s.z:
            return 0
        return 1 if s.y >= s.z else 2

    def __repr__(self) -> str:
        return f"BBox(min={self.min}, max={self.max})"
