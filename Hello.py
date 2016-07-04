#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, traceback





def createComponent( name ):
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)
    rootComp = design.rootComponent
    allOccs = rootComp.occurrences
    newOcc = allOccs.addNewComponent(adsk.core.Matrix3D.create())
    newOcc.component.name = name
    
    return newOcc.component


def createOffsetPlane(component, planarEntity, offset, name):
    planes = component.constructionPlanes
    offsetValue = adsk.core.ValueInput.createByReal(offset)
    planeInput = planes.createInput()
    planeInput.setByOffset(planarEntity, offsetValue)
    
    plane = planes.add(planeInput)
    plane.name = name
    
    return plane


def createSketch(component, planarEntity, name):
    sketches = component.sketches
    sketch = sketches.add(planarEntity)
    sketch.name = name
    
    return sketch


def extrudeSketch(component, sketch, depth, name):
    extrudes = component.features.extrudeFeatures
    extInput = extrudes.createInput( sketch.profiles[0], adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal( depth )
    extInput.setDistanceExtent(False, distance)
    headExt = extrudes.add(extInput)
    headExt.faces[0].body.name = name


def createWall(component, plane, width, height, offset, thickness, name):
    center = adsk.core.Point3D.create(0, 0, 0)
    
    topPlane = createOffsetPlane( component, plane, offset, name )
    sketch = createSketch( component, topPlane, name )
    
    c1 = adsk.core.Point3D.create(center.x - (width/2), center.y + (height/2))
    c2 = adsk.core.Point3D.create(center.x + (width/2), center.y + (height/2))
    c3 = adsk.core.Point3D.create(center.x + (width/2), center.y - (height/2))
    c4 = adsk.core.Point3D.create(center.x - (width/2), center.y - (height/2))
    
    sketch.sketchCurves.sketchLines.addByTwoPoints(c1, c2)
    sketch.sketchCurves.sketchLines.addByTwoPoints(c2, c3)
    sketch.sketchCurves.sketchLines.addByTwoPoints(c3, c4)
    sketch.sketchCurves.sketchLines.addByTwoPoints(c4, c1)
    
    extrudeSketch( component, sketch, thickness, name )


def run(context):
    boxWidth = 20
    boxHeight = 20
    boxDepth = 20
    wallThickness = 0.5
    
    
    
    newComp = createComponent( "Box" )
    xyPlane = newComp.xYConstructionPlane
    yzPlane = newComp.yZConstructionPlane
    xzPlane = newComp.xZConstructionPlane
    
    
    
    createWall(newComp, xyPlane, boxWidth, boxHeight, boxDepth/2, wallThickness, "Front wall")
    createWall(newComp, xyPlane, boxWidth, boxHeight, -(boxDepth/2), -wallThickness, "Back wall")
    
    createWall(newComp, yzPlane, boxDepth, boxHeight-(wallThickness*2), (boxWidth/2)-wallThickness, wallThickness, "Right wall")
    createWall(newComp, yzPlane, boxDepth, boxHeight-(wallThickness*2), -(boxWidth/2), wallThickness, "Left wall")
    
    createWall(newComp, xzPlane, boxWidth, boxDepth, (boxHeight/2)-wallThickness, wallThickness, "Top wall")
    createWall(newComp, xzPlane, boxWidth, boxDepth, -(boxHeight/2), wallThickness, "Bottom wall")

        
        
        
        
        
        
