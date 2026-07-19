# Color Panel Tool for Maya

Professional color and render settings tool for Maya control rigs, designed for animation and game production workflows.

---

## Overview

The Color Panel Tool is a Maya workspace tool that allows Riggers and Rigging TDs to quickly assign viewport colors and Arnold render settings to control curves.

It is designed to improve rig readability, standardize control colors and automate render curve setup in production environments.

This tool is suitable for:

- Rigging TD workflows  
- Animation rigs  
- Game-ready rigs  
- Pipeline integration

---

## Features

### Color Management

- Assign Maya indexed colors  
- Assign custom RGB colors  
- Organized color blocks (Main, Side, Secondary controls)  
- Visual color preview  
- Save and load color presets (JSON)  

### Arnold Render Setup

- Apply Arnold curve render settings  
- Automatic ramp shader creation  
- Automatic place2dTexture connection  
- Curve width control  
- Sample rate control  
- Automatic cleanup of unused nodes  

### UI Integration

- Dockable workspace panel  
- Persistent settings  
- Production-friendly interface  

---

## Installation

1. Download the file: color_panel.py
2. Move it to your Maya scripts folder:

    - **Windows:** Documents/maya/2026/scripts/
    - **Mac / Linux:**  ~/maya/scripts/
      
3. Run in Maya Script Editor:

```python
import color_panel
color_panel.show_color_panel()
```

---

## Usage

**Open the tool:**
1. Select controls
2. Choose color
3. Click **Apply Color**

**For rendering:**
1. Select controls
2. Adjust render settings
3. Click **Render Selected Controls**

---

## Code Features

This tool follows professional Python and Maya standards:

- Organized in functional sections (UI, Color Ops, Render Ops, Config)
- Clear naming conventions
- Safe node handling
- JSON configuration system
- Production-ready logic

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



