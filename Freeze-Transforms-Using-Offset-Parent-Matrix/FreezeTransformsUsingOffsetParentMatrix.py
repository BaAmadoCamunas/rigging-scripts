import maya.cmds as cmds
import maya.OpenMaya as om

def get_world_matrix(node):
    # Return the world transformation matrix of a scene object as an MMatrix.
    matrix_list = cmds.xform(node, query=True, matrix=True, worldSpace=True)
    
    # Convert the flat list returned by Maya into an MMatrix.
    matrix = om.MMatrix()
    om.MScriptUtil.createMatrixFromList(matrix_list, matrix)

    return matrix

def get_parent_matrix(node):
    # Return the parent's world matrix, or an identity matrix if no parent exists.
    parent = cmds.listRelatives(node, parent=True)
    if parent:
        return get_world_matrix(parent[0])  
    
    # Return an identity matrix for objects without a parent.
    return om.MMatrix()  

def set_offset_parent_matrix(node):
    # Apply the computed offset matrix and reset transform channels.
    world_matrix = get_world_matrix(node)
    parent_matrix = get_parent_matrix(node)
    
    # Compute the object's local transform relative to its parent.
    offset_matrix = world_matrix * parent_matrix.inverse()

    # Flatten the matrix so it can be assigned to offsetParentMatrix.
    matrix_list = [offset_matrix(i, j) for i in range(4) for j in range(4)]

    cmds.setAttr(f"{node}.offsetParentMatrix", matrix_list, type="matrix")

    # Reset transform channels after storing the offset matrix.
    for attr in ["translate", "rotate", "scale"]:
        for axis in "XYZ":
            full_attr = f"{node}.{attr}{axis}"
            if cmds.getAttr(full_attr, settable=True):
                cmds.setAttr(full_attr, 0 if attr != "scale" else 1)

def freeze_transforms_with_offset_matrix(objects):
    # Freeze transforms for multiple objects using offsetParentMatrix.
    for obj in objects:
        if not cmds.objExists(obj):
            om.MGlobal.displayWarning(f"Object {obj} does not exist.")
            continue
        
        set_offset_parent_matrix(obj)

    om.MGlobal.displayInfo("Transforms successfully frozen while preserving hierarchy.")

if __name__ == "__main__":
    selected_objects = cmds.ls(selection=True)
    freeze_transforms_with_offset_matrix(selected_objects)