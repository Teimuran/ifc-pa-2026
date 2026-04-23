from __future__ import annotations
import math
from typing import List, Sequence
from .vector3 import Vec3

__all__ = ["Mat4"]


class Mat4:
    __slots__ = ("_m",)

    def __init__(self, data: Sequence[float] | None = None) -> None:
        if data is None:
            self._m: List[float] = [
                1, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1, 0,
                0, 0, 0, 1,
            ]
        else:
            if len(data) != 16:
                raise ValueError("Mat4 требует ровно 16 элементов")
            self._m = list(map(float, data))

    @classmethod
    def identity(cls) -> "Mat4":
        return cls()

    @classmethod
    def from_translation(cls, v: Vec3) -> "Mat4":
        m = cls()
        m._m[3] = v.x
        m._m[7] = v.y
        m._m[11] = v.z
        return m

    @classmethod
    def from_scale(cls, sx: float, sy: float, sz: float) -> "Mat4":
        m = cls()
        m._m[0] = sx
        m._m[5] = sy
        m._m[10] = sz
        return m

    @classmethod
    def from_axis_angle(cls, axis: Vec3, angle_rad: float) -> "Mat4":
        n = axis.normalized()
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        t = 1.0 - c
        x, y, z = n.x, n.y, n.z
        return cls([
            t*x*x + c,   t*x*y - s*z, t*x*z + s*y, 0,
            t*x*y + s*z, t*y*y + c,   t*y*z - s*x, 0,
            t*x*z - s*y, t*y*z + s*x, t*z*z + c,   0,
            0,           0,           0,            1,
        ])

    @classmethod
    def from_euler_xyz(cls, rx: float, ry: float, rz: float) -> "Mat4":
        return (cls.from_axis_angle(Vec3(0, 0, 1), rz) @
                cls.from_axis_angle(Vec3(0, 1, 0), ry) @
                cls.from_axis_angle(Vec3(1, 0, 0), rx))

    @classmethod
    def from_trs(cls, t: Vec3, axis: Vec3, angle_rad: float,
                 s: Vec3 | None = None) -> "Mat4":
        m = cls.from_translation(t) @ cls.from_axis_angle(axis, angle_rad)
        if s is not None:
            m = m @ cls.from_scale(s.x, s.y, s.z)
        return m

    @classmethod
    def look_at(cls, eye: Vec3, target: Vec3, up: Vec3) -> "Mat4":
        f = (target - eye).normalized()
        r = f.cross(up).normalized()
        u = r.cross(f)
        return cls([
             r.x,  r.y,  r.z, -r.dot(eye),
             u.x,  u.y,  u.z, -u.dot(eye),
            -f.x, -f.y, -f.z,  f.dot(eye),
             0,    0,    0,    1,
        ])

    def __matmul__(self, other: "Mat4") -> "Mat4":
        a = self._m
        b = other._m
        result = [0.0] * 16
        for row in range(4):
            for col in range(4):
                s = 0.0
                for k in range(4):
                    s += a[row * 4 + k] * b[k * 4 + col]
                result[row * 4 + col] = s
        return Mat4(result)

    def transform_point(self, p: Vec3) -> Vec3:
        m = self._m
        x = m[0]*p.x + m[1]*p.y + m[2]*p.z + m[3]
        y = m[4]*p.x + m[5]*p.y + m[6]*p.z + m[7]
        z = m[8]*p.x + m[9]*p.y + m[10]*p.z + m[11]
        w = m[12]*p.x + m[13]*p.y + m[14]*p.z + m[15]
        if abs(w - 1.0) > 1e-9 and abs(w) > 1e-12:
            return Vec3(x / w, y / w, z / w)
        return Vec3(x, y, z)

    def transform_vector(self, v: Vec3) -> Vec3:
        m = self._m
        return Vec3(
            m[0]*v.x + m[1]*v.y + m[2]*v.z,
            m[4]*v.x + m[5]*v.y + m[6]*v.z,
            m[8]*v.x + m[9]*v.y + m[10]*v.z,
        )

    def transform_normal(self, n: Vec3) -> Vec3:
        inv = self.inverse()
        m = inv._m
        # transpose of inverse linear part
        return Vec3(
            m[0]*n.x + m[4]*n.y + m[8]*n.z,
            m[1]*n.x + m[5]*n.y + m[9]*n.z,
            m[2]*n.x + m[6]*n.y + m[10]*n.z,
        ).normalized()

    def determinant(self) -> float:
        m = self._m
        def det3(a, b, c, d, e, f, g, h, i):
            return a*(e*i - f*h) - b*(d*i - f*g) + c*(d*h - e*g)
        return (m[0] * det3(m[5],m[6],m[7],m[9],m[10],m[11],m[13],m[14],m[15])
              - m[1] * det3(m[4],m[6],m[7],m[8],m[10],m[11],m[12],m[14],m[15])
              + m[2] * det3(m[4],m[5],m[7],m[8],m[ 9],m[11],m[12],m[13],m[15])
              - m[3] * det3(m[4],m[5],m[6],m[8],m[ 9],m[10],m[12],m[13],m[14]))

    def is_identity(self, eps: float = 1e-9) -> bool:
        identity = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]
        return all(abs(a - b) < eps for a, b in zip(self._m, identity))

    def is_mirrored(self) -> bool:
        return self.determinant() < 0.0

    def inverse(self) -> "Mat4":
        m = list(self._m)
        inv = [1,0,0,0, 0,1,0,0, 0,0,1,0, 0,0,0,1]

        for col in range(4):
            # поиск ведущего элемента
            max_row = max(range(col, 4), key=lambda r: abs(m[r*4+col]))
            if abs(m[max_row*4+col]) < 1e-12:
                raise ValueError("Матрица вырождена, обратной не существует")
            # перестановка строк
            for j in range(4):
                m[col*4+j], m[max_row*4+j] = m[max_row*4+j], m[col*4+j]
                inv[col*4+j], inv[max_row*4+j] = inv[max_row*4+j], inv[col*4+j]
            pivot = m[col*4+col]
            for j in range(4):
                m[col*4+j] /= pivot
                inv[col*4+j] /= pivot
            for row in range(4):
                if row == col:
                    continue
                factor = m[row*4+col]
                for j in range(4):
                    m[row*4+j] -= factor * m[col*4+j]
                    inv[row*4+j] -= factor * inv[col*4+j]
        return Mat4(inv)

    def transposed(self) -> "Mat4":
        m = self._m
        return Mat4([
            m[0], m[4], m[8],  m[12],
            m[1], m[5], m[9],  m[13],
            m[2], m[6], m[10], m[14],
            m[3], m[7], m[11], m[15],
        ])

    def get_translation(self) -> Vec3:
        return Vec3(self._m[3], self._m[7], self._m[11])

    def get_scale(self) -> Vec3:
        m = self._m
        return Vec3(
            math.sqrt(m[0]**2 + m[4]**2 + m[8]**2),
            math.sqrt(m[1]**2 + m[5]**2 + m[9]**2),
            math.sqrt(m[2]**2 + m[6]**2 + m[10]**2),
        )

    def get_rotation_matrix(self) -> "Mat4":
        s = self.get_scale()
        m = self._m
        r = [
            m[0]/s.x, m[1]/s.y, m[2]/s.z,  0,
            m[4]/s.x, m[5]/s.y, m[6]/s.z,  0,
            m[8]/s.x, m[9]/s.y, m[10]/s.z, 0,
            0,        0,        0,           1,
        ]
        return Mat4(r)

    def to_list(self) -> List[float]:
        return list(self._m)

    def to_column_major(self) -> List[float]:
        m = self._m
        return [
            m[0], m[4], m[8],  m[12],
            m[1], m[5], m[9],  m[13],
            m[2], m[6], m[10], m[14],
            m[3], m[7], m[11], m[15],
        ]

    def __getitem__(self, idx):
        if isinstance(idx, tuple):
            row, col = idx
            return self._m[row * 4 + col]
        return self._m[idx]

    def __repr__(self) -> str:
        m = self._m
        rows = [
            f"  [{m[0]:8.4f} {m[1]:8.4f} {m[2]:8.4f} {m[3]:8.4f}]",
            f"  [{m[4]:8.4f} {m[5]:8.4f} {m[6]:8.4f} {m[7]:8.4f}]",
            f"  [{m[8]:8.4f} {m[9]:8.4f} {m[10]:8.4f} {m[11]:8.4f}]",
            f"  [{m[12]:8.4f} {m[13]:8.4f} {m[14]:8.4f} {m[15]:8.4f}]",
        ]
        return "Mat4(\n" + "\n".join(rows) + "\n)"
