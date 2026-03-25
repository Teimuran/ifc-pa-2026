import ifcopenshell
import ifcopenshell.geom
import numpy as np
import pyvista as pv
import tempfile
import multiprocessing
from pathlib import Path


def get_element_geometry(model: ifcopenshell.file) -> dict:
    try:
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True) 

        num_cores = multiprocessing.cpu_count()
        iterator = ifcopenshell.geom.iterator(settings, model, num_cores)

        if not iterator.initialize():
            return {"error": "The model has no 3D geometry or the file is corrupted."}

        multiblock = pv.MultiBlock()

        while True:
            shape = iterator.get()
            global_id = shape.guid

            verts_np = np.array(shape.geometry.verts).reshape((-1, 3))
            faces_np = np.array(shape.geometry.faces).reshape((-1, 3))

            faces_pv = np.empty((faces_np.shape[0], 4), dtype=int)
            faces_pv[:, 0] = 3
            faces_pv[:, 1:] = faces_np
            faces_pv = faces_pv.flatten()

            mesh = pv.PolyData(verts_np, faces_pv)

            multiblock[global_id] = mesh

            if not iterator.next():
                break

        temp_dir = Path(tempfile.gettempdir())
        file_path = temp_dir / "full_ifc_model.vtm"

        multiblock.save(str(file_path))

        return {
            "file_path": str(file_path),
            "elements_count": multiblock.n_blocks
        }

    except Exception as e:
        return {"error": f"Error generating full geometry: {str(e)}"}