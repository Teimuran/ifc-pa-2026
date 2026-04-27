import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.placement
import ifcopenshell.util.unit


def move_ifc_element(model: ifcopenshell.file, guid: str, dx: float, dy: float, dz: float) -> dict:
    try:
        element = model.by_guid(guid)
        if not element:
            return {"success": False, "error": f"Элемент с GUID {guid} не найден."}

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(model)

        dx_proj = dx / unit_scale
        dy_proj = dy / unit_scale
        dz_proj = dz / unit_scale

        matrix = ifcopenshell.util.placement.get_local_placement(element)

        matrix[0][3] += dx_proj
        matrix[1][3] += dy_proj
        matrix[2][3] += dz_proj

        matrix_list = matrix.tolist()

        ifcopenshell.api.run(
            "geometry.edit_object_placement",
            model,
            product=element,
            matrix=matrix_list
        )

        return {
            "success": True,
            "message": f"Смещение элемента {guid} выполнено на вектор: [{dx_proj:.2f}, {dy_proj:.2f}, {dz_proj:.2f}]"
        }

    except Exception as e:
        return {"success": False, "error": f"Ошибка обновления координат: {str(e)}"}