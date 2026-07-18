
"""
Color Panel Tool for Maya Control Rigs

Author: Bárbara Amado Camuñas
Copyright (C) 2026 Bárbara Amado Camuñas

Features:
    - Assign indexed or custom RGB colors to control curves
    - Save and load color presets via JSON
    - Apply Arnold render settings to control curves
    - Automatically manage ramp and place2dTexture nodes
    - Persistent UI workspace panel

Compatible with Maya 2026 (Windows). Other versions not tested.

This program is licensed under the GNU General Public License v3.0.

You may use, modify, and distribute this software under the terms of the GPL-3.0 license.
You must give appropriate credit to the original author.

https://www.gnu.org/licenses/gpl-3.0.html
"""

import maya.cmds as cmds
import json
import os
import re
import uuid


# ============================================================
# CONSTANTS
# ============================================================

INDEXED_COLORS = {
    0: "Gray", 1: "Black", 2: "Dark Gray", 3: "Light Gray", 4: "Red", 5: "Dark Blue",
    6: "Bright Blue", 7: "Green 1", 8: "Dark Purple", 9: "Pink", 10: "Brown", 11: "Dark Brown",
    12: "Dark Red", 13: "Bright Red", 14: "Bright Green", 15: "Blue 1", 16: "White",
    17: "Yellow", 18: "Light Blue", 19: "Light Green", 20: "Light Pink", 21: "Light Orange",
    22: "Light Yellow", 23: "Green 2", 24: "Dark Orange", 25: "Dark Yellow",
    26: "Green 3", 27: "Green 4", 28: "Blue 2", 29: "Blue 3", 30: "Purple", 31: "Dark Pink"
}

# Default control color groups
BLOCK_GROUPS = {"MAIN CONTROLS":[17,17,17], "SIDE CONTROLS":[13,13], "SECONDARY CONTROLS":[6,6]}

curve_width = None
sample_rate = None
PANEL_NAME = "ColorPanelWorkspace"
_color_ui_blocks = None     
_color_ui_scroll = None   


try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = cmds.internalVar(userScriptDir=True)

CONFIG_PATH = os.path.join(SCRIPT_DIR, "color_config.json")



# ============================================================
# UTILITIES
# ============================================================

def safe_name(name):
    # Return a safe Maya node name containing only letters, numbers and underscores
    return re.sub(r'[^0-9A-Za-z_]', '_', name.split('|')[-1])

def read_json_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def write_json_config(data):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=4)
        cmds.inViewMessage(amg="Configuration Saved", pos="midCenter", fade=True, backColor=(0.2,0.2,0.2))
    except Exception as e:
        cmds.warning("Configuration saved error: {}".format(e))




# ============================================================
# COLOR OPERATIONS
# ============================================================

def change_color_by_index(sel, index):
    # Apply Maya indexed color override to selected control shapes
    if not sel:
        return
    for ctl in sel:
        for s in cmds.listRelatives(ctl, shapes=True, fullPath=True) or []:
            try:
                cmds.setAttr(s + ".overrideEnabled", 1)
                cmds.setAttr(s + ".overrideRGBColors", 0)
                cmds.setAttr(s + ".overrideColor", index)
            except Exception:
                pass

def change_color_by_rgb(sel, rgb):
    # Apply custom RGB color override to selected control shapes
    if not sel:
        return
    for ctl in sel:
        for s in cmds.listRelatives(ctl, shapes=True, fullPath=True) or []:
            try:
                cmds.setAttr(s + ".overrideEnabled", 1)
                cmds.setAttr(s + ".overrideRGBColors", 1)
                cmds.setAttr(s + ".overrideColorRGB", *rgb)
            except Exception:
                pass

def get_current_color_of_shape(shape):
    try:
        if not cmds.getAttr(shape + ".overrideEnabled"):
            return [1.0, 1.0, 1.0]
    except Exception:
        return [1.0, 1.0, 1.0]

    try:
        if cmds.getAttr(shape + ".overrideRGBColors"):
            val = cmds.getAttr(shape + ".overrideColorRGB")
            if isinstance(val, (list, tuple)) and len(val) > 0:
                return [float(x) for x in val[0]]
            return [1.0, 1.0, 1.0]
        else:
            idx = int(cmds.getAttr(shape + ".overrideColor"))
            try:
                rgb = cmds.colorIndex(idx, q=True)
                if rgb:
                    return [float(x) for x in rgb]
            except Exception:
                return [1.0, 1.0, 1.0]
    except Exception:
        return [1.0, 1.0, 1.0]
    return [1.0, 1.0, 1.0]




# ============================================================
# UI HELPERS
# ============================================================

def update_color_block(slider, label, swatch, blocks_dict, title):
    idx = int(cmds.intSlider(slider, q=True, value=True))
    block = blocks_dict[title]

    if idx == -1:
        custom_rgb = block.get("rgb")

        if not custom_rgb:
            cmds.intSlider(slider, e=True, value=block["lastIndex"])
            return

        cmds.canvas(swatch, e=True, rgbValue=custom_rgb)
        cmds.text(label, e=True, label="Selected: Custom RGB")
        return

    block["lastIndex"] = idx

    try:
        rgb = cmds.colorIndex(idx, q=True)
    except Exception:
        rgb = [0.0, 0.0, 0.0]

    cmds.canvas(swatch, e=True, rgbValue=rgb)
    cmds.text(label, e=True,
              label=f"Selected: {INDEXED_COLORS.get(idx, f'Index {idx}')}")


def apply_color_button(slider, swatch, blocks_dict, title):
    sel = cmds.ls(sl=True)
    idx = int(cmds.intSlider(slider, q=True, value=True))
    rgb = cmds.canvas(swatch, q=True, rgbValue=True)
    if idx >= 0:
        change_color_by_index(sel, idx)
    else:
        change_color_by_rgb(sel, rgb)

def create_custom_color(title, slider, blocks_dict, label, swatch):
    cmds.colorEditor()
    if cmds.colorEditor(query=True, result=True):
        rgb = list(cmds.colorEditor(query=True, rgb=True))

        blocks_dict[title]["rgb"] = rgb

        cmds.intSlider(slider, e=True, value=-1)
        cmds.canvas(swatch, e=True, rgbValue=rgb)
        cmds.text(label, e=True, label="Selected: Custom RGB")

        cmds.inViewMessage(
            amg="Custom color created",
            pos="midCenter",
            fade=True,
            backColor=(0.2, 0.2, 0.2)
        )

def add_color_index_block(title, default_index=17, saved_data=None, blocks_dict=None, parent=None):
    if parent:
        cmds.setParent(parent)
    saved_idx = saved_data.get("index", default_index) if saved_data else default_index
    saved_rgb = saved_data.get("rgb") if saved_data else None

    form = cmds.formLayout(parent=parent)
    slider = cmds.intSlider(min=-1, max=31, value=saved_idx, step=1, height=25)
    swatch = cmds.canvas(height=30)
    cmds.formLayout(form, e=True,
                    attachForm=[(slider, "top", 0), (slider, "bottom", 0), (swatch, "top", 0), (swatch, "bottom", 0)],
                    attachPosition=[(slider, "left", 0, 0), (slider, "right", 5, 70),
                                    (swatch, "left", 5, 70), (swatch, "right", 0, 100)])
    cmds.setParent("..")

    if saved_idx == -1 and saved_rgb:
        rgb = saved_rgb
        label_text = "Selected: Custom RGB"
        last_index = default_index
    else:
        try:
            rgb = cmds.colorIndex(saved_idx, q=True)
        except Exception:
            rgb = [0.0, 0.0, 0.0]
        label_text = "Selected: " + INDEXED_COLORS.get(saved_idx, f"Index {saved_idx}")
        last_index = saved_idx

    label = cmds.text(label=label_text, height=20, align="center")
    cmds.canvas(swatch, e=True, rgbValue=rgb)

    cmds.separator(height=5, style="none")
    btn_form = cmds.formLayout(parent=parent)
    btn1 = cmds.button(label="Apply Color", height=28, bgc=(0.4,0.4,0.4),
                       command=lambda *_: apply_color_button(slider, swatch, blocks_dict, title))
    btn2 = cmds.button(label="Create Custom Color", height=28, bgc=(0.4,0.4,0.4),
                       command=lambda *_: create_custom_color(title, slider, blocks_dict, label, swatch))
    cmds.formLayout(btn_form, e=True,
                    attachForm=[(btn1, 'top', 0), (btn2, 'top', 0)],
                    attachPosition=[(btn1, 'left', 0, 0), (btn1, 'right', 0, 48),
                                    (btn2, 'left', 0, 52), (btn2, 'right', 0, 100)])
    cmds.setParent("..")
    cmds.intSlider(slider, e=True, dragCommand=lambda *_: update_color_block(slider, label, swatch, blocks_dict, title))

    if blocks_dict is not None:
        blocks_dict[title] = {
            "slider": slider,
            "rgb": saved_rgb if saved_idx == -1 else None,
            "lastIndex": last_index,
            "label": label,
            "swatch": swatch}




# ============================================================
# RENDER / ARNOLD HELPERS
# ============================================================
def get_curve_width():
    if curve_width:
        return cmds.floatField(curve_width, q=True, value=True)
    return 0.0

def get_sample_rate():
    if sample_rate:
        return cmds.intField(sample_rate, q=True, value=True)
    return 1

def ensure_place2d_and_ramp(ramp_name, texture_name, curve_shader_attr):
    try:
        if not cmds.objExists(ramp_name):
            cmds.createNode('ramp', name=ramp_name)
    except Exception:
        pass

    try:
        if not cmds.objExists(texture_name):
            cmds.createNode('place2dTexture', name=texture_name)
    except Exception:
        pass

    try:
        if not cmds.isConnected(texture_name + '.outUV', ramp_name + '.uv'):
            cmds.connectAttr(texture_name + '.outUV', ramp_name + '.uv', force=False)
    except Exception:
        pass

    try:
        if not cmds.isConnected(texture_name + '.outUvFilterSize', ramp_name + '.uvFilterSize'):
            cmds.connectAttr(texture_name + '.outUvFilterSize', ramp_name + '.uvFilterSize', force=False)
    except Exception:
        pass

    try:
        if not cmds.isConnected(ramp_name + '.outColor', curve_shader_attr):
            cmds.connectAttr(ramp_name + '.outColor', curve_shader_attr, force=True)
    except Exception:
        pass

def set_ramp_color(ramp_name, rgb):
    try:
        cmds.setAttr(ramp_name + '.type', 0)
    except Exception:
        pass

    try:
        size = cmds.getAttr(ramp_name + ".colorEntryList", size=True)
        for i in reversed(range(size)):
            cmds.removeMultiInstance(f"{ramp_name}.colorEntryList[{i}]", b=True)
    except Exception:
        pass

    try:
        cmds.setAttr(f"{ramp_name}.colorEntryList[0].color",
                     rgb[0], rgb[1], rgb[2], type="double3")
        cmds.setAttr(f"{ramp_name}.colorEntryList[0].position", 0.0)

        cmds.setAttr(f"{ramp_name}.colorEntryList[1].color",
                     rgb[0], rgb[1], rgb[2], type="double3")
        cmds.setAttr(f"{ramp_name}.colorEntryList[1].position", 1.0)
    except Exception:
        pass

def unique_node_name(base_name):
    short_uuid = str(uuid.uuid4())[:8]
    return "{}_{}".format(base_name, short_uuid)




# ============================================================
# RENDER SELECTED CONTROLS
# ============================================================

def cleanup_unused_ramps_and_textures(created_ramps, created_textures):
    # Delete unused ramp and place2dTexture nodes with no outgoing connections
    for ramp in created_ramps:
        if cmds.objExists(ramp):
            conns = cmds.listConnections(ramp, source=False, destination=True) or []
            if not conns:
                try:
                    cmds.delete(ramp)
                except Exception:
                    pass

    for tex in created_textures:
        if cmds.objExists(tex):
            conns = cmds.listConnections(tex, source=False, destination=True) or []
            if not conns:
                try:
                    cmds.delete(tex)
                except Exception:
                    pass


def render_selected_controls():
    """
    Apply Arnold render settings and color ramps to selected control curves.

    Handles:
        - Referenced and local nodes
        - Curve width and sample rate
        - Ramp shader creation and cleanup
    """
    selection = cmds.ls(sl=True, long=True) or []
    if not selection:
        cmds.inViewMessage(amg="No objects selected for render", pos="midCenter", fade=True, backColor=(0.25,0.25,0.25))
        return

    created_ramps = []
    created_textures = []

    for obj in selection:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        if not shapes:
            continue

        base_name = safe_name(obj)

        try:
            is_any_referenced = any(cmds.referenceQuery(s, isNodeReferenced=True) for s in shapes)
        except Exception:
            is_any_referenced = False

        if is_any_referenced:
            ramp_name = unique_node_name("ramp_" + base_name)
            texture_name = unique_node_name("place2dTexture_" + base_name)
        else:
            ramp_name = "ramp_" + base_name
            texture_name = "place2dTexture_" + base_name

        if shapes:
            ensure_place2d_and_ramp(ramp_name, texture_name, shapes[0] + ".aiCurveShader")

        created_ramps.append(ramp_name)
        created_textures.append(texture_name)

        for shape in shapes:
            try:
                if cmds.nodeType(shape) != "nurbsCurve":
                    continue
            except Exception:
                continue

            curve_shader_attr = shape + ".aiCurveShader"

            existing = cmds.listConnections(curve_shader_attr, plugs=True, source=True, destination=False) or []
            for old in existing:
                try:
                    cmds.disconnectAttr(old, curve_shader_attr)
                except Exception:
                    pass

            ensure_place2d_and_ramp(ramp_name, texture_name, curve_shader_attr)

            rgb = get_current_color_of_shape(shape)
            set_ramp_color(ramp_name, rgb)

            try:
                if cmds.attributeQuery('aiRenderCurve', node=shape, exists=True):
                    cmds.setAttr(shape + '.aiRenderCurve', 1)
            except Exception:
                pass

            try:
                if cmds.attributeQuery('aiCurveWidth', node=shape, exists=True):
                    cmds.setAttr(shape + '.aiCurveWidth', get_curve_width())
            except Exception:
                pass

            try:
                if cmds.attributeQuery('aiSampleRate', node=shape, exists=True):
                    cmds.setAttr(shape + '.aiSampleRate', get_sample_rate())
            except Exception:
                pass

            for attr in [
                'castsShadows', 'aiVisibleInDiffuseReflection', 'aiVisibleInSpecularReflection',
                'aiVisibleInDiffuseTransmission', 'aiVisibleInSpecularTransmission', 'aiVisibleInVolume',
                'aiSelfShadows'
            ]:
                try:
                    if cmds.attributeQuery(attr, node=shape, exists=True):
                        cmds.setAttr(shape + '.' + attr, 0)
                except Exception:
                    pass

    cleanup_unused_ramps_and_textures(created_ramps, created_textures)

    cmds.inViewMessage(amg="Render settings applied to selected controls", pos="midCenter", fade=True, backColor=(0.2,0.2,0.2))
    



# ============================================================
# SAVE / COMPARE CONFIGURATION
# ============================================================

# Save current color and render settings to JSON config file
def save_config(blocks):
    data = {}
    for title, info in blocks.items():
        slider = info["slider"]
        idx = int(cmds.intSlider(slider, q=True, value=True))
        if idx >= 0:
            data[title] = {"index": idx, "name": INDEXED_COLORS.get(idx, f"Index {idx}")}
        else:
            data[title] = {"index": -1, "rgb": info.get("rgb")}
    data["RenderRigControls"] = {
        "curveWidth": cmds.floatField(curve_width, q=True, value=True),
        "sampleRate": cmds.intField(sample_rate, q=True, value=True)
    }
    write_json_config(data)

def normalize_saved_block(block):
    if not block:
        return None
    idx = block.get("index")
    if idx is None:
        return None
    if idx >= 0:
        return {"index": int(idx)}
    else:
        rgb = block.get("rgb")
        if rgb is None:
            return {"index": -1}
        return {"index": -1, "rgb": [float(rgb[0]), float(rgb[1]), float(rgb[2])]}

# Check if current UI settings differ from saved config
def has_unsaved_changes(blocks):
    saved_config = read_json_config()
    current = {}
    for title, info in blocks.items():
        slider_val = int(cmds.intSlider(info["slider"], q=True, value=True))
        if slider_val >= 0:
            current[title] = {"index": slider_val}
        else:
            current[title] = {"index": -1, "rgb": info.get("rgb")}

    current["RenderRigControls"] = {
        "curveWidth": float(cmds.floatField(curve_width, q=True, value=True)),
        "sampleRate": int(cmds.intField(sample_rate, q=True, value=True))
    }

    if not saved_config:
        return True

    saved_rig = saved_config.get("RenderRigControls", {})
    if float(saved_rig.get("curveWidth", 0.0)) != current["RenderRigControls"]["curveWidth"]:
        return True
    
    if int(saved_rig.get("sampleRate", 1)) != current["RenderRigControls"]["sampleRate"]:
        return True

    for k, v in current.items():
        if k == "RenderRigControls":
            continue
        saved_block = saved_config.get(k, {})
        saved_norm = normalize_saved_block(saved_block)
        if saved_norm is None:
            return True
        
        if v.get("index") != saved_norm.get("index"):
            return True
        
        if v.get("index") == -1:
            saved_rgb = saved_norm.get("rgb")
            cur_rgb = v.get("rgb")
            if saved_rgb is None and cur_rgb is None:
                continue

            if saved_rgb != cur_rgb:
                return True
            
    return False




# ============================================================
# CLOSE PANEL
# ============================================================

# Close panel after confirming unsaved changes
def close_panel(blocks):
    if has_unsaved_changes(_color_ui_blocks):
        result = cmds.confirmDialog(
            title="Exit without saving?",
            message="Do you want to exit without saving the color and render settings?",
            button=["Yes", "No"],
            defaultButton="No",
            cancelButton="No",
            dismissString="No"
        )
        if result != "Yes":
            return

    try:
        if cmds.workspaceControl(PANEL_NAME, exists=True):
            cmds.deleteUI(PANEL_NAME)

    except Exception:
        pass



# ============================================================
# MAIN COLOR PANEL
# ============================================================

# Build the main color panel UI inside the given Maya workspace control
def build_ui(parent=None):
    global _color_ui_blocks, _color_ui_scroll, curve_width, sample_rate

    if _color_ui_scroll and cmds.scrollLayout(_color_ui_scroll, exists=True):
        cmds.deleteUI(_color_ui_scroll)
        _color_ui_scroll = None  # reset

    _color_ui_scroll = cmds.scrollLayout(
        horizontalScrollBarThickness=0,
        verticalScrollBarThickness=16,
        childResizable=True,
        parent=parent
    )

    main_layout = cmds.columnLayout(adjustableColumn=True, rowSpacing=10,
                                    columnAttach=("both",10), parent=_color_ui_scroll)
    
    cmds.separator(height=15, style='none')
    cmds.text(label='<h1>SELECT A COLOR FOR YOUR CONTROL</h1>', height=30, align='center')
    cmds.separator(height=10, style='none')

    saved_config = read_json_config()
    _color_ui_blocks = {}

    for group_name, defaults in BLOCK_GROUPS.items():
        frame = cmds.frameLayout(label=group_name, collapsable=True, collapse=False, marginHeight=10, marginWidth=10,
                                 borderVisible=True, parent=main_layout, bgc=(0.15,0.15,0.15))
        cmds.columnLayout(adjustableColumn=True, rowSpacing=5, parent=frame)

        for i, default_index in enumerate(defaults, start=1):
            cmds.separator(height=10, style='none')
            block_title = f"{group_name} {i}"
            saved_data = saved_config.get(block_title, {})
            add_color_index_block(block_title, default_index, saved_data, _color_ui_blocks, frame)

    cmds.separator(height=20, style='none')

    frame_render = cmds.frameLayout(label="Render Rig Controls", collapsable=True, collapse=False, marginHeight=10,
                                    marginWidth=10, borderVisible=True, parent=main_layout, bgc=(0.15,0.15,0.15))
    cmds.columnLayout(adjustableColumn=True, rowSpacing=6, parent=frame_render)
    saved_rig = saved_config.get("RenderRigControls", {})
    cw_default = saved_rig.get("curveWidth", 1.0)
    sr_default = saved_rig.get("sampleRate", 1)

    cmds.rowLayout(nc=2, columnWidth2=[150,300], adjustableColumn=2, columnAttach=[(1,'both',0),(2,'both',0)])
    cmds.text(label="Curve Width:", align='right')
    curve_width = cmds.floatField(precision=3, minValue=0.0, maxValue=100.0, value=cw_default)
    cmds.setParent('..')

    cmds.rowLayout(nc=2, columnWidth2=[150,300], adjustableColumn=2, columnAttach=[(1,'both',0),(2,'both',0)])
    cmds.text(label="Sample Rate:", align='right')
    sample_rate = cmds.intField(minValue=1, maxValue=100, value=sr_default)
    cmds.setParent('..')

    cmds.separator(height=8, style='none')
    cmds.button(label="Render Selected Controls", height=34, bgc=(0.4,0.4,0.4), command=lambda *_: render_selected_controls())

    cmds.setParent(main_layout)
    cmds.separator(height=18, style='none')

    cmds.rowLayout(nc=2, columnWidth2=[250,250], adjustableColumn=1, columnAttach=[(1,'both',5),(2,'both',5)])
    cmds.button(label="Save Config", height=32, bgc=(0.4,0.4,0.4), command=lambda *_: save_config(_color_ui_blocks))
    cmds.button(label="Close", height=32, bgc=(0.4,0.4,0.4), command=lambda *_: close_panel(_color_ui_blocks))
    cmds.setParent('..')



def show_color_panel():
    # Create or restore the color panel workspace control
    if cmds.workspaceControl(PANEL_NAME, exists=True):
        cmds.workspaceControl(PANEL_NAME, e=True, restore=True)
        return

    cmds.workspaceControl(
        PANEL_NAME,
        label="Color Panel",
        retain=True,
        initialWidth=520,
        initialHeight=900,
        minimumWidth=400,
        uiScript='import color_panel; import maya.cmds as cmds; cmds.evalDeferred(lambda: color_panel.build_ui(parent="{}"))'.format(PANEL_NAME)
    )





# ============================================================
# MAIN
# ============================================================

show_color_panel()

