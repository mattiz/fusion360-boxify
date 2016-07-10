#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam


UP = 1
DOWN = 2
RIGHT = 3
LEFT = 4


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


def createFrontAndBackFingerJointsWall(component, plane, width, height, offset, thickness, name):
    center = adsk.core.Point3D.create(0, 0, 0)
    
    topPlane = createOffsetPlane( component, plane, offset, name )
    sketch = createSketch( component, topPlane, name )
    
    startPoint = adsk.core.Point3D.create(center.x - (width/2), center.y + (height/2))
    
    # Top
    last = squarePattern( sketch, startPoint, 1, abs(thickness), 17, [RIGHT, DOWN, RIGHT, UP] )
    
    # Right
    last = squarePattern( sketch, last, abs(thickness), 1, 9, [DOWN, LEFT, DOWN, RIGHT] )
    
    # Bottom
    last = squarePattern( sketch, last, 1, abs(thickness), 17, [LEFT, UP, LEFT, DOWN] )
    
    # Left
    squarePattern( sketch, last, abs(thickness), 1, 9, [UP, RIGHT, UP, LEFT] )
    
    extrudeSketch( component, sketch, thickness, name )


def createLeftAndRightFingerJointsWall(component, plane, width, height, offset, thickness, name):
    center = adsk.core.Point3D.create(0, 0, 0)
    
    topPlane = createOffsetPlane( component, plane, offset, name )
    sketch = createSketch( component, topPlane, name )
    
    startPoint = adsk.core.Point3D.create(center.x - (width/2), center.y + (height/2))
    
    # Top
    last = squarePattern( sketch, startPoint, 1.24, abs(thickness), 9, [RIGHT, DOWN, RIGHT, UP] )
    
    # Right
    last = squarePattern( sketch, last, abs(thickness), 1, 9, [DOWN, RIGHT, DOWN, LEFT] )
    
    # Bottom
    last = squarePattern( sketch, last, 1.24, abs(thickness), 9, [LEFT, UP, LEFT, DOWN] )
    
    # Left
    squarePattern( sketch, last, abs(thickness), 1, 9, [UP, LEFT, UP, RIGHT] )
    
    extrudeSketch( component, sketch, thickness, name )


def createTopAndBottomFingerJointsWall(component, plane, width, height, offset, thickness, name):
    center = adsk.core.Point3D.create(0, 0, 0)
    
    topPlane = createOffsetPlane( component, plane, offset, name )
    sketch = createSketch( component, topPlane, name )
    
    startPoint = adsk.core.Point3D.create(center.x - (width/2) + thickness, center.y + (height/2) - thickness)
    
    # Top
    last = squarePattern( sketch, startPoint, 1, abs(thickness), 17, [RIGHT, UP, RIGHT, DOWN], 0.6 )
    
    # Right
    last = squarePattern( sketch, last, abs(thickness), 1.24, 9, [DOWN, RIGHT, DOWN, LEFT] )
    
    # Bottom
    last = squarePattern( sketch, last, 1, abs(thickness), 17, [LEFT, DOWN, LEFT, UP], 0.6 )
    
    # Left
    squarePattern( sketch, last, abs(thickness), 1.24, 9, [UP, LEFT, UP, RIGHT] )
    
    extrudeSketch( component, sketch, thickness, name )


def squarePattern(sketch, startPoint, width, height, number, pattern, firstAndLastWidth = 0):
    points = []
    index = 0
    last = startPoint
    points.append( startPoint )
    
    for i in range(number):
        if firstAndLastWidth > 0 and (i == 0 or i == number-1):
            w = firstAndLastWidth
        else:
            w = width
        
        if index > len(pattern)-1:
            index = 0
        
        p = pattern[index]
        index += 1
        
        if p == UP:
            last = adsk.core.Point3D.create( last.x, last.y+height )
            points.append( last )
        
        if p == DOWN:
            last = adsk.core.Point3D.create( last.x, last.y-height )
            points.append( last )
        
        if p == RIGHT:
            last = adsk.core.Point3D.create( last.x+w, last.y )
            points.append( last )
        
        if p == LEFT:
            last = adsk.core.Point3D.create( last.x-w, last.y )
            points.append( last )
    
    for i in range(0, len(points)-1):
        sketch.sketchCurves.sketchLines.addByTwoPoints( points[i], points[i+1] )
    
    return last


def run(context):
    boxWidth = 9
    boxHeight = 5
    boxDepth = 7
    wallThickness = 0.4
    
    
    deleteAllComponents()
    
    
    newComp = createComponent( "Box" )
    xyPlane = newComp.xYConstructionPlane
    yzPlane = newComp.yZConstructionPlane
    xzPlane = newComp.xZConstructionPlane
    
    
    createFrontAndBackFingerJointsWall(newComp, xyPlane, boxWidth, boxHeight, (boxDepth/2)-wallThickness, wallThickness, "Front wall")
    createFrontAndBackFingerJointsWall(newComp, xyPlane, boxWidth, boxHeight, -(boxDepth/2)+wallThickness, -wallThickness, "Back wall")
    
    createLeftAndRightFingerJointsWall(newComp, yzPlane, boxDepth-(wallThickness*2), boxHeight, (boxWidth/2)-wallThickness, wallThickness, "Right wall")
    createLeftAndRightFingerJointsWall(newComp, yzPlane, boxDepth-(wallThickness*2), boxHeight, -(boxWidth/2)+wallThickness, -wallThickness, "Left wall")
    
    createTopAndBottomFingerJointsWall(newComp, xzPlane, boxWidth, boxDepth, (boxHeight/2)-wallThickness, wallThickness, "Top wall")   
    createTopAndBottomFingerJointsWall(newComp, xzPlane, boxWidth-(wallThickness*4), boxDepth-(wallThickness*4), -(boxHeight/2)+wallThickness, -wallThickness, "Bottom wall")
    
    
    
    
    #createWall(newComp, xyPlane, boxWidth, boxHeight, boxDepth/2, wallThickness, "Front wall")
    #createWall(newComp, xyPlane, boxWidth, boxHeight, -(boxDepth/2), -wallThickness, "Back wall")
    
    #createWall(newComp, yzPlane, boxDepth, boxHeight-(wallThickness*2), (boxWidth/2)-wallThickness, wallThickness, "Right wall")
    #createWall(newComp, yzPlane, boxDepth, boxHeight-(wallThickness*2), -(boxWidth/2)+wallThickness, -wallThickness, "Left wall")
    
    #createWall(newComp, xzPlane, boxWidth, boxDepth, (boxHeight/2)-wallThickness, wallThickness, "Top wall")
    #createWall(newComp, xzPlane, boxWidth, boxDepth, -(boxHeight/2)+wallThickness, -wallThickness, "Bottom wall")
    
    
    
    
    
    
    