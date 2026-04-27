import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import math
from math_core.vector3 import Vec3
from math_core.matrix4 import Mat4
from math_core.bbox import BBox
from math_core.plane import Plane
from math_core.mesh import Mesh
from math_core.mesh_editor import MeshEditor
from math_core.transform import (
    mat4_from_axes, triangulate_face, compute_face_normal
)

def run_visual_tests():
    print("="*50)
    print("🚀 ЗАПУСК ТЕСТОВ МАТЕМАТИЧЕСКОГО ЯДРА")
    print("="*50)

    # --- ТЕСТ 1: БАЗОВЫЙ MESH ---
    print("\n[1/3] Создание базовой сетки (треугольник)...")
    m = Mesh([Vec3(0,0,0), Vec3(1,0,0), Vec3(0,1,0)], [(0, 1, 2)])
    print(f"  -> Вершин: {len(m.vertices)}, Граней: {len(m.indices)}")
    print(f"  -> BBox: {m.bounds().min} to {m.bounds().max}")

    # --- ТЕСТ 2: РЕДАКТИРОВАНИЕ ---
    print("\n[2/3] Работа с MeshEditor (Перемещение и Экструзия)...")
    editor = MeshEditor(m)
    
    print("  -> Сдвигаем вершину [0] на +5 по Z")
    editor.move_vertex(0, Vec3(0, 0, 5))
    print(f"     Новая позиция v[0]: {m.vertices[0]}")

    print("  -> Выполняем экструзию грани [0] на расстояние 2.0")
    editor.extrude_face(0, 2.0)
    print(f"     После экструзии: {len(m.vertices)} вершин, {len(m.indices)} граней")
    
    # --- ТЕСТ 3: ОЧИСТКА ---
    print("\n[3/3] Тест топологии (Удаление и Cleanup)...")
    last_idx = len(m.indices) - 1
    print(f"  -> Удаляем последнюю грань (ID: {last_idx})")
    editor.delete_face(last_idx)
    
    print("  -> Запуск cleanup_unreferenced_vertices()...")
    removed = editor.cleanup_unreferenced_vertices()
    print(f"     Удалено мусорных вершин: {removed}")
    print(f"     Итоговая сетка: {len(m.vertices)} вершин, {len(m.indices)} граней")

    print("\n" + "="*50)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО")
    print("="*50)

if __name__ == "__main__":
    try:
        run_visual_tests()
    except Exception as e:
        print(f"\n❌ ОШИБКА ПРИ ТЕСТИРОВАНИИ: {e}")
        sys.exit(1)

class MeshEditor:
    """Утилита для прямого редактирования вершин и граней объекта Mesh."""

    def __init__(self, mesh: Mesh) -> None:
        self.mesh = mesh

    # ------------------------------------------------------------------ #
    #  Вершинные операции                                                  #
    # ------------------------------------------------------------------ #

    def move_vertex(self, vertex_idx: int, delta: Vec3) -> None:
        """Смещает указанную вершину на вектор delta."""
        if 0 <= vertex_idx < len(self.mesh.vertices):
            self.mesh.vertices[vertex_idx] = self.mesh.vertices[vertex_idx] + delta
        else:
            raise IndexError(f"Вершина {vertex_idx} вне диапазона.")

    def set_vertex(self, vertex_idx: int, position: Vec3) -> None:
        """Устанавливает новые абсолютные координаты для вершины."""
        if 0 <= vertex_idx < len(self.mesh.vertices):
            self.mesh.vertices[vertex_idx] = position

    # ------------------------------------------------------------------ #
    #  Топологические операции                                             #
    # ------------------------------------------------------------------ #

    def delete_face(self, face_idx: int) -> None:
        """
        Удаляет треугольник из списка индексов по его ID.
        Примечание: не удаляет сами вершины. Для очистки висячих вершин 
        нужно вызвать cleanup_unreferenced_vertices().
        """
        if 0 <= face_idx < len(self.mesh.indices):
            self.mesh.indices.pop(face_idx)
        else:
            raise IndexError(f"Грань {face_idx} вне диапазона.")

    def cleanup_unreferenced_vertices(self) -> int:
        """
        Удаляет вершины, которые больше не принадлежат ни одному треугольнику.
        Перестраивает индексы (O(N) по количеству вершин и граней).
        Возвращает количество удаленных вершин.
        """
        used_indices: Set[int] = set()
        for i0, i1, i2 in self.mesh.indices:
            used_indices.update((i0, i1, i2))

        original_count = len(self.mesh.vertices)
        if len(used_indices) == original_count:
            return 0  # Все вершины используются

        new_vertices = []
        old_to_new: Dict[int, int] = {}
        
        for old_idx, vertex in enumerate(self.mesh.vertices):
            if old_idx in used_indices:
                old_to_new[old_idx] = len(new_vertices)
                new_vertices.append(vertex)

        new_indices = [
            (old_to_new[i0], old_to_new[i1], old_to_new[i2])
            for i0, i1, i2 in self.mesh.indices
        ]

        self.mesh.vertices = new_vertices
        self.mesh.indices = new_indices

        return original_count - len(self.mesh.vertices)

    def extrude_face(self, face_idx: int, distance: float) -> None:
        """
        Базовая экструзия отдельного треугольника вдоль его нормали.
        Превращает грань в треугольную призму: исходная грань удаляется,
        создается новая "крышка" и 3 боковые стенки (6 новых треугольников).
        """
        if not (0 <= face_idx < len(self.mesh.indices)):
            raise IndexError("Неверный индекс грани.")

        i0, i1, i2 = self.mesh.indices[face_idx]
        v0, v1, v2 = self.mesh.vertices[i0], self.mesh.vertices[i1], self.mesh.vertices[i2]

        normal = self.mesh.triangle_normal(v0, v1, v2)
        offset = normal * distance

        # 1. Создаем новые вершины для "крышки"
        n0_idx = len(self.mesh.vertices)
        n1_idx = n0_idx + 1
        n2_idx = n0_idx + 2
        self.mesh.vertices.extend([v0 + offset, v1 + offset, v2 + offset])

        # 2. Удаляем оригинальную грань (она оказывается внутри новой фигуры)
        # Удаляем через pop, чтобы не оставлять дыр в массиве индексов
        self.mesh.indices.pop(face_idx)

        # 3. Добавляем новую "крышку" (направление обхода сохраняем)
        self.mesh.indices.append((n0_idx, n1_idx, n2_idx))

        # 4. Сшиваем боковые стенки (каждая стенка состоит из двух треугольников)
        
        # Стенка 1 (ребро v0 -> v1)
        self.mesh.indices.append((i0, i1, n1_idx))
        self.mesh.indices.append((i0, n1_idx, n0_idx))

        # Стенка 2 (ребро v1 -> v2)
        self.mesh.indices.append((i1, i2, n2_idx))
        self.mesh.indices.append((i1, n2_idx, n1_idx))

        # Стенка 3 (ребро v2 -> v0)
        self.mesh.indices.append((i2, i0, n0_idx))
        self.mesh.indices.append((i2, n0_idx, n2_idx))

        