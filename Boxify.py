#Author-
#Description-

import adsk.core, adsk.fusion, adsk.cam, math, traceback


UP = 1
DOWN = 2
RIGHT = 3
LEFT = 4



handlers = []
app = adsk.core.Application.get()
if app:
    ui = app.userInterface




def roundToNearestEOdd( n ):
	r = round( n )
	ceil = math.ceil( n )
	floor = math.floor( n )
	
	if r % 2 != 0:
		return r
	
	if ceil == floor:
		return ceil + 1
	
	if ceil % 2 != 0:
		return ceil
	else:
		return floor


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


def calculateTabLength( wantedTabLength, wallLength ):
    numTabs = wallLength / wantedTabLength
    numTabs = roundToNearestEOdd(numTabs)
    return numTabs, (wallLength / numTabs)


def calculateNumEdges( numTabs ):
    return (numTabs * 2) - 1


def createFrontAndBackFingerJointsWall(component, plane, width, height, offset, thickness, wantedTabLength, name):
    center = adsk.core.Point3D.create(0, 0, 0)
    
    topPlane = createOffsetPlane( component, plane, offset, name )
    sketch = createSketch( component, topPlane, name )
    
    startPoint = adsk.core.Point3D.create(center.x - (width/2), center.y + (height/2))
    
    
    numHorizontalTabs, horizontalTabWidth = calculateTabLength( wantedTabLength, width )
    numHorizontalEdges = calculateNumEdges( numHorizontalTabs )
    
    numVerticalTabs, verticalTabWidth = calculateTabLength( wantedTabLength, height )
    numVerticalEdges = calculateNumEdges( numVerticalTabs )
    
    
    # Top
    last = squarePattern( sketch, startPoint, horizontalTabWidth, abs(thickness), numHorizontalEdges, [RIGHT, DOWN, RIGHT, UP] )
    
    # Right
    last = squarePattern( sketch, last, abs(thickness), verticalTabWidth, numVerticalEdges, [DOWN, LEFT, DOWN, RIGHT] )
    
    # Bottom
    last = squarePattern( sketch, last, horizontalTabWidth, abs(thickness), numHorizontalEdges, [LEFT, UP, LEFT, DOWN] )
    
    # Left
    squarePattern( sketch, last, abs(thickness), verticalTabWidth, numVerticalEdges, [UP, RIGHT, UP, LEFT] )
    
    extrudeSketch( component, sketch, thickness, name )


def createLeftAndRightFingerJointsWall(component, plane, width, height, offset, thickness, wantedTabLength, name):
    center = adsk.core.Point3D.create(0, 0, 0)
    
    topPlane = createOffsetPlane( component, plane, offset, name )
    sketch = createSketch( component, topPlane, name )
    
    startPoint = adsk.core.Point3D.create(center.x - (width/2), center.y + (height/2))
    
    
    numHorizontalTabs, horizontalTabWidth = calculateTabLength( wantedTabLength, width )
    numHorizontalEdges = calculateNumEdges( numHorizontalTabs )
    
    numVerticalTabs, verticalTabWidth = calculateTabLength( wantedTabLength, height )
    numVerticalEdges = calculateNumEdges( numVerticalTabs )
    
    
    # Top
    last = squarePattern( sketch, startPoint, horizontalTabWidth, abs(thickness), numHorizontalEdges, [RIGHT, DOWN, RIGHT, UP] )
    
    # Right
    last = squarePattern( sketch, last, abs(thickness), verticalTabWidth, numVerticalEdges, [DOWN, RIGHT, DOWN, LEFT] )
    
    # Bottom
    last = squarePattern( sketch, last, horizontalTabWidth, abs(thickness), numHorizontalEdges, [LEFT, UP, LEFT, DOWN] )
    
    # Left
    squarePattern( sketch, last, abs(thickness), verticalTabWidth, numVerticalEdges, [UP, LEFT, UP, RIGHT] )
    
    extrudeSketch( component, sketch, thickness, name )


def createTopAndBottomFingerJointsWall(component, plane, width, height, offset, thickness, wantedTabLength, name):
    center = adsk.core.Point3D.create(0, 0, 0)
    
    topPlane = createOffsetPlane( component, plane, offset, name )
    sketch = createSketch( component, topPlane, name )
    
    startPoint = adsk.core.Point3D.create(center.x - (width/2), center.y + (height/2))
    
    
    numHorizontalTabs, horizontalTabWidth = calculateTabLength( wantedTabLength, width + (abs(thickness) * 2) )
    numHorizontalEdges = calculateNumEdges( numHorizontalTabs )
    
    numVerticalTabs, verticalTabWidth = calculateTabLength( wantedTabLength, height )
    numVerticalEdges = calculateNumEdges( numVerticalTabs )
    
    
    # Top
    last = squarePattern( sketch, startPoint, horizontalTabWidth, abs(thickness), numHorizontalEdges, [RIGHT, UP, RIGHT, DOWN], horizontalTabWidth - abs(thickness) )
    
    # Right
    last = squarePattern( sketch, last, abs(thickness), verticalTabWidth, numVerticalEdges, [DOWN, RIGHT, DOWN, LEFT] )
    
    # Bottom
    last = squarePattern( sketch, last, horizontalTabWidth, abs(thickness), numHorizontalEdges, [LEFT, DOWN, LEFT, UP], horizontalTabWidth - abs(thickness) )
    
    # Left
    squarePattern( sketch, last, abs(thickness), verticalTabWidth, numVerticalEdges, [UP, LEFT, UP, RIGHT] )
    
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








class BoxCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            boxName = 'Box'
            boxWidth = 0
            boxHeight = 0
            boxDepth = 0
            materialThickness = 0
            tabWidth = 0

            unitsMgr = app.activeProduct.unitsManager
            command = args.firingEvent.sender
            inputs = command.commandInputs

            for input in inputs:
                if input.id == 'boxName':
                    print(input.value)
                    boxName = input.value
                    
                elif input.id == 'boxWidth':
                    print(unitsMgr.evaluateExpression(input.expression, "mm"))
                    boxWidth = unitsMgr.evaluateExpression(input.expression, "mm")
                    
                elif input.id == 'boxHeight':
                    print(unitsMgr.evaluateExpression(input.expression, "mm"))
                    boxHeight = unitsMgr.evaluateExpression(input.expression, "mm")
                    
                elif input.id == 'boxDepth':
                    print(unitsMgr.evaluateExpression(input.expression, "mm"))
                    boxDepth = unitsMgr.evaluateExpression(input.expression, "mm")
                    
                elif input.id == 'materialThickness':
                    print(unitsMgr.evaluateExpression(input.expression, "mm"))
                    materialThickness = unitsMgr.evaluateExpression(input.expression, "mm")
                    
                elif input.id == 'tabWidth':
                    print(unitsMgr.evaluateExpression(input.expression, "mm"))
                    tabWidth = unitsMgr.evaluateExpression(input.expression, "mm")

            createTabbedBox(boxName, boxWidth, boxHeight, boxDepth, materialThickness, tabWidth)
            
            args.isValidResult = True

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class BoxCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class BoxCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):    
    def __init__(self):
        super().__init__()
        
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = True
            onExecute = BoxCommandExecuteHandler()
            cmd.execute.add(onExecute)
            #onExecutePreview = BoxCommandExecuteHandler()
            #cmd.executePreview.add(onExecutePreview)
            onDestroy = BoxCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            # keep the handler referenced beyond this function
            handlers.append(onExecute)
            #handlers.append(onExecutePreview)
            handlers.append(onDestroy)

            #define the inputs
            inputs = cmd.commandInputs
            inputs.addStringValueInput('boxName', 'Box Name', "Box")
            inputs.addValueInput('boxWidth', 'Box width', 'mm', adsk.core.ValueInput.createByReal(10) )
            inputs.addValueInput('boxHeight', 'Box height', 'mm', adsk.core.ValueInput.createByReal(5) )
            inputs.addValueInput('boxDepth', 'Box depth', 'mm', adsk.core.ValueInput.createByReal(5) )
            inputs.addValueInput('materialThickness', 'Material thickness', 'mm', adsk.core.ValueInput.createByReal(0.4) )
            inputs.addValueInput('tabWidth', 'Tab width', 'mm', adsk.core.ValueInput.createByReal(1) )

        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



def createTabbedBox(boxName, boxWidth, boxHeight, boxDepth, wallThickness, wantedTabLength):
    newComp = createComponent( boxName )
    xyPlane = newComp.xYConstructionPlane
    yzPlane = newComp.yZConstructionPlane
    xzPlane = newComp.xZConstructionPlane
    
    # width = 9 (9 tabs), height = 5 (5 tabs)
    createFrontAndBackFingerJointsWall(newComp, xyPlane, boxWidth, boxHeight, (boxDepth/2)-wallThickness, wallThickness, wantedTabLength, "Front wall")
    createFrontAndBackFingerJointsWall(newComp, xyPlane, boxWidth, boxHeight, -(boxDepth/2)+wallThickness, -wallThickness, wantedTabLength, "Back wall")
    
    # width = 6.2 (5 tabs), height = 5 (5 tabs)
    createLeftAndRightFingerJointsWall(newComp, yzPlane, boxDepth-(wallThickness*2), boxHeight, (boxWidth/2)-wallThickness, wallThickness, wantedTabLength, "Right wall")
    createLeftAndRightFingerJointsWall(newComp, yzPlane, boxDepth-(wallThickness*2), boxHeight, -(boxWidth/2)+wallThickness, -wallThickness, wantedTabLength, "Left wall")
    
    # width = 8.2 (9 tabs), height = 6.2 (5 tabs)
    createTopAndBottomFingerJointsWall(newComp, xzPlane, boxWidth-(wallThickness*2), boxDepth-(wallThickness*2), (boxHeight/2)-wallThickness, wallThickness, wantedTabLength, "Top wall")   
    createTopAndBottomFingerJointsWall(newComp, xzPlane, boxWidth-(wallThickness*2), boxDepth-(wallThickness*2), -(boxHeight/2)+wallThickness, -wallThickness, wantedTabLength, "Bottom wall")    
    
    



def run(context):
#    boxWidth = 15
#    boxHeight = 8
#    boxDepth = 8
#    
#    wantedTabLength = 1
#    wallThickness = 0.4
#    
#    
#    deleteAllComponents()
#    
#    
#    newComp = createComponent( "Box" )
#    xyPlane = newComp.xYConstructionPlane
#    yzPlane = newComp.yZConstructionPlane
#    xzPlane = newComp.xZConstructionPlane
#    
#    
#    # width = 9 (9 tabs), height = 5 (5 tabs)
#    createFrontAndBackFingerJointsWall(newComp, xyPlane, boxWidth, boxHeight, (boxDepth/2)-wallThickness, wallThickness, wantedTabLength, "Front wall")
#    createFrontAndBackFingerJointsWall(newComp, xyPlane, boxWidth, boxHeight, -(boxDepth/2)+wallThickness, -wallThickness, wantedTabLength, "Back wall")
#    
#    # width = 6.2 (5 tabs), height = 5 (5 tabs)
#    createLeftAndRightFingerJointsWall(newComp, yzPlane, boxDepth-(wallThickness*2), boxHeight, (boxWidth/2)-wallThickness, wallThickness, wantedTabLength, "Right wall")
#    createLeftAndRightFingerJointsWall(newComp, yzPlane, boxDepth-(wallThickness*2), boxHeight, -(boxWidth/2)+wallThickness, -wallThickness, wantedTabLength, "Left wall")
#    
#    # width = 8.2 (9 tabs), height = 6.2 (5 tabs)
#    createTopAndBottomFingerJointsWall(newComp, xzPlane, boxWidth-(wallThickness*2), boxDepth-(wallThickness*2), (boxHeight/2)-wallThickness, wallThickness, wantedTabLength, "Top wall")   
#    createTopAndBottomFingerJointsWall(newComp, xzPlane, boxWidth-(wallThickness*2), boxDepth-(wallThickness*2), -(boxHeight/2)+wallThickness, -wallThickness, wantedTabLength, "Bottom wall")    
#    
#    
    
    
    
    
    
    #createWall(newComp, xyPlane, boxWidth, boxHeight, boxDepth/2, wallThickness, "Front wall")
    #createWall(newComp, xyPlane, boxWidth, boxHeight, -(boxDepth/2), -wallThickness, "Back wall")
    
    #createWall(newComp, yzPlane, boxDepth, boxHeight-(wallThickness*2), (boxWidth/2)-wallThickness, wallThickness, "Right wall")
    #createWall(newComp, yzPlane, boxDepth, boxHeight-(wallThickness*2), -(boxWidth/2)+wallThickness, -wallThickness, "Left wall")
    
    #createWall(newComp, xzPlane, boxWidth, boxDepth, (boxHeight/2)-wallThickness, wallThickness, "Top wall")
    #createWall(newComp, xzPlane, boxWidth, boxDepth, -(boxHeight/2)+wallThickness, -wallThickness, "Bottom wall")
    
    
    
    
    try:
        commandDefinitions = ui.commandDefinitions
        #check the command exists or not
        cmdDef = commandDefinitions.itemById('Boxify')
        if not cmdDef:
            cmdDef = commandDefinitions.addButtonDefinition('Boxify', 'Create Box', 'Create a box.', './resources')
        
        onCommandCreated = BoxCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        # keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        inputs = adsk.core.NamedValues.create()
        cmdDef.execute(inputs)
    
        # prevent this module from being terminate when the script returns, because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    
    
    