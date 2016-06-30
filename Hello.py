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


def run(context):
    newComp = createComponent( "Box" )
    
    # construction plane
    #xyPlane = newComp.xYConstructionPlane
    xzPlane = newComp.xZConstructionPlane
    
    topPlane = createOffsetPlane( newComp, xzPlane, 5.0, "Top wall" )
    
    sketch = createSketch( newComp, topPlane, "Top wall" )
    
    # draw lines
    center = adsk.core.Point3D.create(0, 0, 0)
    p1 = adsk.core.Point3D.create(center.x + 10, center.y)
    p2 = adsk.core.Point3D.create(center.x + 10, center.y - 10)
    p3 = adsk.core.Point3D.create(center.x, center.y - 10)
    
    sketch.sketchCurves.sketchLines.addByTwoPoints(center, p1)
    sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
    sketch.sketchCurves.sketchLines.addByTwoPoints(p2, p3)
    sketch.sketchCurves.sketchLines.addByTwoPoints(p3, center)
    
    # extrude
    extrudes = newComp.features.extrudeFeatures
    prof = sketch.profiles[0]
    extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    distance = adsk.core.ValueInput.createByReal(0.4)
    extInput.setDistanceExtent(False, distance)
    headExt = extrudes.add(extInput)
    
    # give body name
    fc = headExt.faces[0]
    bd = fc.body
    bd.name = "Top wall"
        
        
        
        
        
        
        
