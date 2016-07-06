#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam



def deleteAllComponents():
    app = adsk.core.Application.get()
    product = app.activeProduct
    design = adsk.fusion.Design.cast(product)   
    
    for comp in design.allComponents:
        for occ in comp.allOccurrences:
            print("Deleting " + occ.name + " in " + comp.name)
            occ.deleteMe()
            

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


def createFingerJointsWall(component, plane, width, height, offset, thickness, name):
    center = adsk.core.Point3D.create(0, 0, 0)
    
    topPlane = createOffsetPlane( component, plane, offset, name )
    sketch = createSketch( component, topPlane, name )
    
    c1 = adsk.core.Point3D.create(center.x - (width/2), center.y + (height/2))
    c2 = adsk.core.Point3D.create(center.x + (width/2), center.y + (height/2))
    c3 = adsk.core.Point3D.create(center.x + (width/2), center.y - (height/2))
    c4 = adsk.core.Point3D.create(center.x - (width/2), center.y - (height/2))
    
    tabWidth = 2
    startPoint = adsk.core.Point3D.create(c1.x, c1.y-thickness)
    createTopTabbedLine(sketch, startPoint, tabWidth, thickness)
    
    createBottomTabbedLine(sketch, c4, tabWidth, thickness)

    tabWidth = 1
    createLeftTabbedLine(sketch, c1, tabWidth, thickness)
    
    startPoint = adsk.core.Point3D.create(c2.x-thickness, c2.y)
    createRightTabbedLine(sketch, startPoint, tabWidth, thickness)

    
    #extrudeSketch( component, sketch, thickness, name )


def createTopTabbedLine(sketch, startPoint, tabWidth, thickness):
    last = createHorizontalTab(sketch, startPoint, tabWidth, thickness, includeFirst = False)
    
    for i in range(3):
        if i % 2:
            last = createHorizontalTab(sketch, last, tabWidth, thickness)
        else:
            last = createHorizontalLine(sketch, last, tabWidth)
    
    last = createHorizontalTab(sketch, last, tabWidth, thickness, includeLast = False)


def createBottomTabbedLine(sketch, startPoint, tabWidth, thickness):
    last = createHorizontalLine(sketch, startPoint, tabWidth)
    
    for i in range(3):
        if i % 2:
            last = createHorizontalLine(sketch, last, tabWidth)
        else:
            last = createHorizontalTab(sketch, last, tabWidth, thickness)
    
    last = createHorizontalLine(sketch, last, tabWidth)


def createLeftTabbedLine(sketch, startPoint, tabWidth, thickness):
    last = createVerticalLine(sketch, startPoint, tabWidth)
    
    for i in range(3):
        if i % 2:
            last = createVerticalLine(sketch, last, tabWidth)
        else:
            last = createVerticalTab(sketch, last, tabWidth, thickness)
    
    last = createVerticalLine(sketch, last, tabWidth)


def createRightTabbedLine(sketch, startPoint, tabWidth, thickness):
    last = createVerticalTab(sketch, startPoint, tabWidth, thickness, includeFirst = False)
    
    for i in range(3):
        if i % 2:
            last = createVerticalTab(sketch, last, tabWidth, thickness)
        else:
            last = createVerticalLine(sketch, last, tabWidth)
    
    last = createVerticalTab(sketch, last, tabWidth, thickness, includeLast = False)
    

def createHorizontalTab(sketch, startPoint, tabWidth, tabHeight, includeFirst = True, includeLast = True):
    p1 = adsk.core.Point3D.create(startPoint.x, startPoint.y)
    p2 = adsk.core.Point3D.create(p1.x, p1.y+tabHeight)
    p3 = adsk.core.Point3D.create(p2.x+tabWidth, p2.y)
    p4 = adsk.core.Point3D.create(p3.x, p3.y-tabHeight)
    
    if includeFirst:
        sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
    
    sketch.sketchCurves.sketchLines.addByTwoPoints(p2, p3)
    
    if includeLast:
        sketch.sketchCurves.sketchLines.addByTwoPoints(p3, p4)
    
    return p4


def createVerticalTab(sketch, startPoint, tabWidth, tabHeight, includeFirst = True, includeLast = True):
    p1 = adsk.core.Point3D.create(startPoint.x, startPoint.y)
    p2 = adsk.core.Point3D.create(p1.x+tabHeight, p1.y)
    p3 = adsk.core.Point3D.create(p2.x, p2.y-tabWidth)
    p4 = adsk.core.Point3D.create(p3.x-tabHeight, p3.y)
    
    if includeFirst:
        sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
    
    sketch.sketchCurves.sketchLines.addByTwoPoints(p2, p3)
    
    if includeLast:
        sketch.sketchCurves.sketchLines.addByTwoPoints(p3, p4)
    
    return p4


def createHorizontalLine(sketch, startPoint, tabWidth):
    p1 = adsk.core.Point3D.create(startPoint.x, startPoint.y)
    p2 = adsk.core.Point3D.create(p1.x+tabWidth, p1.y)
    
    sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
    
    return p2


def createVerticalLine(sketch, startPoint, tabWidth):
    p1 = adsk.core.Point3D.create(startPoint.x, startPoint.y)
    p2 = adsk.core.Point3D.create(p1.x, p1.y-tabWidth)
    
    sketch.sketchCurves.sketchLines.addByTwoPoints(p1, p2)
    
    return p2


def run(context):
    boxWidth = 10
    boxHeight = 5
    boxDepth = 5
    wallThickness = 0.4
    
    
    deleteAllComponents()
    
    
    newComp = createComponent( "Box" )
    xyPlane = newComp.xYConstructionPlane
    yzPlane = newComp.yZConstructionPlane
    xzPlane = newComp.xZConstructionPlane
    
    
    
    createFingerJointsWall(newComp, xyPlane, boxWidth, boxHeight, boxDepth/2, wallThickness, "Front wall")
    
    #createWall(newComp, xyPlane, boxWidth, boxHeight, boxDepth/2, wallThickness, "Front wall")
    #createWall(newComp, xyPlane, boxWidth, boxHeight, -(boxDepth/2), -wallThickness, "Back wall")
    
    #createWall(newComp, yzPlane, boxDepth, boxHeight-(wallThickness*2), (boxWidth/2)-wallThickness, wallThickness, "Right wall")
    #createWall(newComp, yzPlane, boxDepth, boxHeight-(wallThickness*2), -(boxWidth/2)+wallThickness, -wallThickness, "Left wall")
    
    #createWall(newComp, xzPlane, boxWidth, boxDepth, (boxHeight/2)-wallThickness, wallThickness, "Top wall")
    #createWall(newComp, xzPlane, boxWidth, boxDepth, -(boxHeight/2)+wallThickness, -wallThickness, "Bottom wall")
    
    
    
    
    
    
    