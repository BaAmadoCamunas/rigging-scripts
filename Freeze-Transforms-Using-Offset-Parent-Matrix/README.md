# Freeze Transforms Using Offset Parent Matrix

A Python script for Autodesk Maya that freezes object transformations using `offsetParentMatrix` while preserving hierarchy and world-space transforms.

Unlike Maya's traditional **Freeze Transformations**, this script computes the correct offset matrix relative to each object's parent, allowing transform channels to be reset without affecting the object's position, orientation or hierarchy.

---

## Features

- [x] Freeze transforms using `offsetParentMatrix`
- [x] Preserve parent-child hierarchies
- [x] Maintain world-space position, rotation, and scale
- [x] Reset Translate, Rotate, and Scale channels
- [x] Support multiple selected objects

---

## Requirements

- Autodesk Maya 2020 or newer (supports `offsetParentMatrix`)
- Python
- `maya.cmds`
- `maya.OpenMaya`

---

## Usage

1. Open **Autodesk Maya**.
2. Select one or more objects.
3. Run the script from the **Script Editor**.

The script will automatically:

- Compute each object's world matrix.
- Calculate its local offset relative to its parent.
- Store the result in `offsetParentMatrix`.
- Reset the transform channels while preserving the object's current transform.

---

## How It Works

The script retrieves both the object's world transformation matrix and its parent's world matrix. It then computes the relative transformation and stores it in the `offsetParentMatrix` attribute.

This allows the object's **Translate**, **Rotate**, and **Scale** attributes to be reset without changing its final position in the scene or breaking the hierarchy.

---

## Author

**Bárbara Amado Camuñas**  
Rigging Artist | Character TD

---

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**.  

You may:  
- **Use**  
- **Modify**  
- **Share**  

Under the GPL-3.0 terms.  

Full license: [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html)

---

## Contact

- GitHub: [https://github.com/BaAmadoCamunas](https://github.com/BaAmadoCamunas)  
- LinkedIn: [https://www.linkedin.com/in/barbara-amado-camunas-riggingartist](https://www.linkedin.com/in/barbara-amado-camunas-riggingartist)

---

## Portfolio Note

This tool is part of a professional Rigging TD portfolio.

