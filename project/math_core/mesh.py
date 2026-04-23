from __future__ import annotations
import math
from typing import List, Tuple, Iterator
from .vector3 import Vec3
from .bbox import BBox

__all__ = ["Mesh"]

Triangle = Tuple[Vec3, Vec3, Vec3]


class Mesh:

    def __init__(self,
                 vertices: List[Vec3] | None = None,
                 indices: List[Tuple[int, int, int]] | None = None) -> None:
        self.vertices: List[Vec3] = vertices or []
        self.indices: List[Tuple[int, int, int]] = indices or []

    @classmethod
    def from_flat(cls, flat_coords: List[float],
                  flat_indices: List[int]) -> "Mesh":
        """
        flat_coords: [x0,y0,z0, x1,y1,z1, ...]
        flat_indices: [i0,i1,i2, i3,i4,i5, ...]  (тройки)
        """
        verts = [
            Vec3(flat_coords[i], flat_coords[i+1], flat_coords[i+2])
            for i in range(0, len(flat_coords), 3)
        ]
        tris = [
            (flat_indices[i], flat_indices[i+1], flat_indices[i+2])
            for i in range(0, len(flat_indices), 3)
        ]
        return cls(verts, tris)


    def triangle(self, tri_index: int) -> Triangle:
        i0, i1, i2 = self.indices[tri_index]
        return self.vertices[i0], self.vertices[i1], self.vertices[i2]

    def triangles(self) -> Iterator[Triangle]:
        for i in range(len(self.indices)):
            yield self.triangle(i)

    @staticmethod
    def triangle_normal(p0: Vec3, p1: Vec3, p2: Vec3) -> Vec3:
        return (p1 - p0).cross(p2 - p0).normalized()

    @staticmethod
    def triangle_area(p0: Vec3, p1: Vec3, p2: Vec3) -> float:
        return (p1 - p0).cross(p2 - p0).length() * 0.5

    @staticmethod
    def triangle_centroid(p0: Vec3, p1: Vec3, p2: Vec3) -> Vec3:
        return (p0 + p1 + p2) * (1.0 / 3.0)


    def face_normals(self) -> List[Vec3]:
        """Нормаль каждого треугольника."""
        return [self.triangle_normal(*self.triangle(i))
                for i in range(len(self.indices))]

    def vertex_normals(self) -> List[Vec3]:
        normals = [Vec3() for _ in self.vertices]
        for i0, i1, i2 in self.indices:
            p0 = self.vertices[i0]
            p1 = self.vertices[i1]
            p2 = self.vertices[i2]
            n = (p1 - p0).cross(p2 - p0)   # не нормировать — длина = 2*area
            normals[i0] = normals[i0] + n
            normals[i1] = normals[i1] + n
            normals[i2] = normals[i2] + n
        return [n.normalized() for n in normals]

    def surface_area(self) -> float:
        return sum(self.triangle_area(*self.triangle(i))
                   for i in range(len(self.indices)))

    def volume(self) -> float:
        vol = 0.0
        for p0, p1, p2 in self.triangles():
            vol += p0.dot(p1.cross(p2))
        return abs(vol) / 6.0

    def center_of_gravity(self) -> Vec3:
        total_area = 0.0
        weighted = Vec3()
        for p0, p1, p2 in self.triangles():
            area = self.triangle_area(p0, p1, p2)
            centroid = self.triangle_centroid(p0, p1, p2)
            weighted = weighted + centroid * area
            total_area += area
        if total_area < 1e-12:
            return Vec3()
        return weighted / total_area

    def bounding_box(self) -> BBox:
        return BBox.from_points(self.vertices)

    def transformed(self, matrix) -> "Mesh":
        new_verts = [matrix.transform_point(v) for v in self.vertices]
        return Mesh(new_verts, list(self.indices))

    def transform_inplace(self, matrix) -> None:
        for i, v in enumerate(self.vertices):
            self.vertices[i] = matrix.transform_point(v)

    def validate(self) -> List[str]:
        issues = []
        n_verts = len(self.vertices)
        for fi, (i0, i1, i2) in enumerate(self.indices):
            for idx in (i0, i1, i2):
                if idx < 0 or idx >= n_verts:
                    issues.append(f"Грань {fi}: индекс {idx} вне диапазона")
            p0, p1, p2 = self.vertices[i0], self.vertices[i1], self.vertices[i2]
            if self.triangle_area(p0, p1, p2) < 1e-12:
                issues.append(f"Грань {fi}: вырожденный треугольник")
        return issues

    def __repr__(self) -> str:
        return (f"Mesh(vertices={len(self.vertices)}, "
                f"triangles={len(self.indices)})")
    
    def bounds(self) -> BBox:
        if not self.vertices:
            return BBox.empty()
        return BBox.from_points(self.vertices)
    
    @staticmethod
    def triangle_normal(v0: Vec3, v1: Vec3, v2: Vec3) -> Vec3:
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = edge1.cross(edge2)
        return normal.normalized()
