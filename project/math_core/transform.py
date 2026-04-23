from __future__ import annotations
import math
from typing import List, Optional, Sequence
from .vector3 import Vec3
from .matrix4 import Mat4

__all__ = [
    "placement_to_mat4",
    "axis2placement3d_to_mat4",
    "mat4_from_axes",
    "ifc_cartesian_transform",
]


def mat4_from_axes(
    origin: Vec3,
    axis_z: Vec3,
    axis_x: Vec3,
) -> Mat4:
    z = axis_z.normalized()
    x = axis_x.normalized()
    # ортогонализация Грама-Шмидта: убрать проекцию z из x
    x = (x - z * z.dot(x)).normalized()
    y = z.cross(x)

    return Mat4([
        x.x, y.x, z.x, origin.x,
        x.y, y.y, z.y, origin.y,
        x.z, y.z, z.z, origin.z,
        0,   0,   0,   1,
    ])


def axis2placement3d_to_mat4(
    location: Sequence[float],
    axis: Optional[Sequence[float]] = None,
    ref_direction: Optional[Sequence[float]] = None,
) -> Mat4:
    origin = Vec3(*location[:3])
    axis_z = Vec3(*(axis[:3] if axis else (0, 0, 1)))
    axis_x = Vec3(*(ref_direction[:3] if ref_direction else (1, 0, 0)))
    return mat4_from_axes(origin, axis_z, axis_x)


def placement_to_mat4(placement) -> Mat4:
    if placement is None:
        return Mat4.identity()

    parent_mat = placement_to_mat4(
        getattr(placement, "PlacementRelTo", None)
    )

    rel = getattr(placement, "RelativePlacement", None)
    if rel is None:
        return parent_mat

    # IfcAxis2Placement3D
    loc = getattr(rel, "Location", None)
    if loc is None:
        return parent_mat

    location = loc.Coordinates if hasattr(loc, "Coordinates") else loc
    axis_attr = getattr(rel, "Axis", None)
    refdir_attr = getattr(rel, "RefDirection", None)

    axis = (axis_attr.DirectionRatios
            if axis_attr and hasattr(axis_attr, "DirectionRatios")
            else None)
    ref_dir = (refdir_attr.DirectionRatios
               if refdir_attr and hasattr(refdir_attr, "DirectionRatios")
               else None)

    local_mat = axis2placement3d_to_mat4(location, axis, ref_dir)
    return parent_mat @ local_mat


def ifc_cartesian_transform(
    operator_origin: Sequence[float],
    operator_axis: Optional[Sequence[float]],
    operator_ref: Optional[Sequence[float]],
    scale: float = 1.0,
) -> Mat4:
    base = axis2placement3d_to_mat4(operator_origin, operator_axis, operator_ref)
    if abs(scale - 1.0) > 1e-9:
        base = base @ Mat4.from_scale(scale, scale, scale)
    return base


def triangulate_face(coords: List[Sequence[float]]) -> List[Vec3]:
    if len(coords) < 3:
        return []
    pts = [Vec3(*c[:3]) for c in coords]
    result: List[Vec3] = []
    for i in range(1, len(pts) - 1):
        result.extend([pts[0], pts[i], pts[i + 1]])
    return result


def compute_face_normal(coords: List[Sequence[float]]) -> Vec3:
    n = Vec3()
    count = len(coords)
    for i in range(count):
        cur = coords[i]
        nxt = coords[(i + 1) % count]
        n = Vec3(
            n.x + (cur[1] - nxt[1]) * (cur[2] + nxt[2]),
            n.y + (cur[2] - nxt[2]) * (cur[0] + nxt[0]),
            n.z + (cur[0] - nxt[0]) * (cur[1] + nxt[1]),
        )
    return n.normalized()
