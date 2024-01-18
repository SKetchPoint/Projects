import maya.cmds as cmds
import random
import math

class LightningGenerator:
    def __init__(self, startPoint, midPoint, endPoint):
        '''single itteration based on that generation
        startPoint:beginning of the lightning bolt
        midPoint:max value control of randomization
        endPoint:end of lightning bolt
         '''
        self.startPoint = startPoint
        self.midPoint = midPoint
        self.endPoint = endPoint

    def get_distance(self, point1, point2):
        '''finds distance based on  square root((x2-x1)^2+(y2-y1)^2+(z2-z1)^2)
        point1:first point comparison
        point2:2nd point comparison
        return : distance between the two points
        '''
        return math.sqrt((point2[0]-point1[0])**2 + (point2[1]-point1[1])**2 + (point2[2]-point1[2])**2)

    def get_midpoint(self, point1, point2):
        '''finds midpoint of two points
        point1:first point comparison
        point2:2nd point comparison
        return : middle cordnates between the two points
        '''
        x = (point1[0]+point2[0])/2.0
        y = (point1[1]+point2[1])/2.0
        z = (point1[2]+point2[2])/2.0
        return (x, y, z)

    def get_axis(self, point1, point2):
        '''finds  the axis based on the normals of the diffrence between the two points
        point1:first point comparison
        point2:2nd point comparison
        return : normalized diffrence or the axis used in a formula later on
        '''
        x_diff = point2[0] - point1[0]
        y_diff = point2[1] - point1[1]
        z_diff = point2[2] - point1[2]
        magnitude = math.sqrt(x_diff**2 + y_diff**2 + z_diff**2)
        if magnitude == 0:
            return (0, 0, 0)
        x_norm = x_diff / magnitude
        y_norm = y_diff / magnitude
        z_norm = z_diff / magnitude
        return (x_norm, y_norm, z_norm)

    def rotate_point(self, point, axis, angle):
        '''Rodrigues formula/ matrix applied
        point: the point desired to rotate
        axis:what it rotates by
        angle:the applied angle to perform rotation
        return : the new point that will replace point
        '''
        x, y, z = point
        u, v, w = axis
        cos = math.cos(angle)
        sin = math.sin(angle)
        matrix = [
            [cos + (u**2)*(1 - cos), u*v*(1 - cos)-w*sin, u*w*(1 - cos)+v*sin],
            [u*v*(1 - cos)+w*sin, cos+(v**2)*(1 - cos), v*w*(1 - cos)-u*sin],
            [u*w*(1 - cos)-v*sin, v*w*(1 - cos)+u*sin, cos+(w**2)*(1-cos)]
        ]
        x_new = x*matrix[0][0] + y*matrix[1][0] + z*matrix[2][0]
        y_new = x*matrix[0][1] + y*matrix[1][1] + z*matrix[2][1]
        z_new = x*matrix[0][2] + y*matrix[1][2] + z*matrix[2][2]
        return (x_new, y_new, z_new)

    def subdivide_curve(self, startPoint, midPoint, endPoint, subdivisions, curveDeg):
        '''subdivides an initial curve based on current's midpoints, preps curve
        startPoint:start of curve
        midpoint:middle of curve
        endPoint:end of curve
        subdivisions: int value to split the points
        return : new points
        '''
        points = [startPoint, midPoint, endPoint]
        print("Initial list of points: ", points)
        for i in range(subdivisions):
            newPoints = []
            for j in range(len(points) - 1):
                midpoint = self.get_midpoint(points[j], points[j+1])
                newPoints.append(points[j])
                newPoints.append(midpoint)
            newPoints.append(points[-1])
            points = newPoints
            print("List of points after subdivision", i+1, ": ", points)
        curveName = cmds.curve(d=curveDeg, p=points,n="subdividedCurve")
        return points

    def curve_lightning_main(self, curvePoints, startPoint, endPoint, breakingDistance, maxAngle, minAngle):
        '''applies rodrigue's formula and subdivision of curve to create a controlled randomized curve
        curvePoints:subdivided curve
        startPoint:start of curve
        endPoint:end of curve
        breakingDistance:ability to manipulate subdivision spread
        maxAngle:one extreme limit for angle rotate
        minAngle:other extreme limit for angle rotate
        return : altered points
        '''
        curveLightningPoints = []
        for i in range(len(curvePoints)):
            curvePoint = curvePoints[i]
            if self.get_distance(curvePoint, startPoint) < self.get_distance(curvePoint, endPoint):
                # start point closer
                rotationRadius = self.get_distance(curvePoint, startPoint) / breakingDistance
            else:
                # end point closer
                rotationRadius = self.get_distance(curvePoint, endPoint) / breakingDistance
            angle = random.uniform(minAngle, maxAngle)
            axis = self.get_axis(startPoint, endPoint)
            rotatedPoint = self.rotate_point(curvePoint, axis, angle)
            curveLightningPoints.append(rotatedPoint)
        return curveLightningPoints

def create_tubular_mesh(curves, radius, expand, meshName):
    '''turns curve into mesh 
    curve:any curve desired
    radius:radius of the tube to be generated around the curve
    expand:scaling
    return : generates meshgroup and returns that grouping
    '''
    meshGroup = []

    for current in curves:
        circleEx = cmds.circle(n="circle", r=radius, ch=False)

        offset = cmds.pointPosition(current + ".cv[0]")
        cmds.move(offset[0], offset[1], offset[2], circleEx, absolute=True)

        mesh = cmds.extrude(
            circleEx, current, ch=False, rn=False, polygon=3, extrudeType=2, fixedPath=1, useProfileNormal=1, scale=expand
        )

        if meshName:  # rename if one is picked
            tubular_mesh = cmds.rename(mesh[0], meshName + str(curves.index(current) + 1))
        else:
            tubular_mesh = cmds.rename(mesh[0], "mesh" + str(curves.index(current) + 1))
        # Create spheres at the start and end points
        start_sphere = cmds.polySphere(r=radius, sx=8, sy=8)[0]
        end_sphere = cmds.polySphere(r=radius, sx=8, sy=8)[0]

        start_position = cmds.pointPosition(current + ".cv[0]")
        end_position = cmds.pointPosition(current + ".cv[-1]")

        cmds.move(start_position[0], start_position[1], start_position[2], start_sphere, absolute=True)
        cmds.move(end_position[0], end_position[1], end_position[2], end_sphere, absolute=True)

        # Group the mesh, spheres, and curve
        group = cmds.group([tubular_mesh, start_sphere, end_sphere, current], name=meshName + "_group")
        meshGroup.append(group)
        cmds.delete(circleEx)

    # Return the group containing all the mesh elements
    return meshGroup

def apply_glow(meshes,out1, out2, out3,glow1, glow2, glow3):
    '''surface shader created 
    meshes:meshes selected to apply to 
    out1:hue base
    out2:saturation base
    out3:value of base
    glow1:hue of glow
    glow2:saturation of glow
    glow 3:value/strength of glow
    return : with maya software renders out glowing mesh
    '''
    surfaceShader = cmds.shadingNode('surfaceShader', asShader=True)
    surfaceShaderSG = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=surfaceShader+'SG')
    cmds.connectAttr(surfaceShader+'.outColor', surfaceShaderSG+'.surfaceShader', force=True)

    cmds.setAttr(surfaceShader+'.outColor', out1, out2, out3, type='double3')
    cmds.setAttr(surfaceShader+'.outGlowColor', glow1, glow2, glow3, type='double3')

    for mesh in meshes:
        cmds.select(mesh)
        cmds.hyperShade(assign=surfaceShaderSG)
        
        
#-------------GUI Implementation---------------------------------GUI Implementation-------------------------------------GUI Inplementation


def button1Clicked(x1Field, y1Field, z1Field, x2Field, y2Field, z2Field, x3Field, y3Field, z3Field):
    '''previewing the cordnates 
    x1Field,y1Field,z1Field:startPoint
    x2Field,y2Field,z2Field:midPoint
    x3Field,y3Field,z3Field:endPoint
    return : 3 point curve
    '''
    # Get the values from the text fields
    x1 = cmds.floatFieldGrp(x1Field, query=True, value1=True)
    y1 = cmds.floatFieldGrp(y1Field, query=True, value1=True)
    z1 = cmds.floatFieldGrp(z1Field, query=True, value1=True)
    
    x2 = cmds.floatFieldGrp(x2Field, query=True, value1=True)
    y2 = cmds.floatFieldGrp(y2Field, query=True, value1=True)
    z2 = cmds.floatFieldGrp(z2Field, query=True, value1=True)
    
    x3 = cmds.floatFieldGrp(x3Field, query=True, value1=True)
    y3 = cmds.floatFieldGrp(y3Field, query=True, value1=True)
    z3 = cmds.floatFieldGrp(z3Field, query=True, value1=True)
    
    # Use the values as points
    startPoint = (x1,y1,z1)
    midPoint = (x2,y2,z2)
    endPoint = (x3,y3,z3)
    cmds.curve(d=1, p=[startPoint, midPoint,endPoint],n="visualizePoints")
    
def button2Clicked(x1Field, y1Field, z1Field, x2Field, y2Field, z2Field, x3Field, y3Field, z3Field,subdivi,breakingDis,cDeg,maxA,minA):
    '''previewing the cordnates 
    x1Field,y1Field,z1Field:startPoint
    x2Field,y2Field,z2Field:midPoint
    x3Field,y3Field,z3Field:endPoint
    subdivi:increases ammount of points of result
    breakingDis:scrunching or straching of division spread
    cDeg: the d value in a curve
    maxA:maxAngle
    minA:minAngle
    return :controlled randomized curve
    '''
    # Get the values from the text fields
    x1 = cmds.floatFieldGrp(x1Field, query=True, value1=True)
    y1 = cmds.floatFieldGrp(y1Field, query=True, value1=True)
    z1 = cmds.floatFieldGrp(z1Field, query=True, value1=True)
    
    x2 = cmds.floatFieldGrp(x2Field, query=True, value1=True)
    y2 = cmds.floatFieldGrp(y2Field, query=True, value1=True)+0.1
    z2 = cmds.floatFieldGrp(z2Field, query=True, value1=True)+0.1
    
    x3 = cmds.floatFieldGrp(x3Field, query=True, value1=True)
    y3 = cmds.floatFieldGrp(y3Field, query=True, value1=True)
    z3 = cmds.floatFieldGrp(z3Field, query=True, value1=True)
    
    # Use the values as points
    startPoint = (x1,y1,z1)
    midPoint = (x2,y2,z2)
    endPoint = (x3,y3,z3)
    subdivisions = cmds.intFieldGrp(subdivi, query=True, value1=True)
    if (subdivisions<0):
        subdivisions=0
    breakingDistance = cmds.intFieldGrp(breakingDis, query=True, value1=True)
    if (breakingDistance==0):
        breakingDistance=1#prevents division issues
    curveDeg = cmds.intFieldGrp(cDeg, query=True, value1=True)
    if (curveDeg<=0):
        curveDeg=1#low as it can go
    maxAngle = cmds.intSliderGrp(maxA, query=True, value=True)
    minAngle = cmds.intSliderGrp(minA, query=True, value=True)
    generator = LightningGenerator(startPoint, midPoint, endPoint)
    curvePoints = generator.subdivide_curve(startPoint, midPoint, endPoint,subdivisions, curveDeg)
    curveBolt = generator.curve_lightning_main(curvePoints, startPoint, endPoint, breakingDistance, maxAngle, minAngle)
    cmds.curve(d=curveDeg, p=curveBolt,n="randomizedCurve")
    
def button3Clicked(radius, expand,stringField):
    '''meshing the selected curves
    (implicit)curve(s):what to follow in the extrusion
    radius:radius of the circle
    expand:increasing the size, similar to radius but dosent change end spheres
    stringField:optional meshing name
    return:mesh(s) of the curves that were selected
    '''
    curves = cmds.ls(selection=True)
    print("Selected curves:", curves)
    if not curves:
        cmds.error("No curves have been selected. Please select curves before pushing this button.")
        return
    radCircle = cmds.floatFieldGrp(radius, query=True, value1=True)
    scaling = cmds.floatFieldGrp(expand, query=True, value1=True)
    meshName = cmds.textField(stringField, query=True, text=True)
    meshes = create_tubular_mesh(curves, radCircle, scaling, meshName)
def button4Clicked(o1, o2, o3,g1, g2, g3):
    '''altering and assigning the surfaceShader to have mesh glow
    (implicit) mesh(s):lighting branches
    o1:base hue
    o2:base saturation
    o3:base value
    g1:glow hue
    g2:glow saturation
    g3:glow value/brightness
    return : 3 point curve
    '''
    meshes = cmds.ls(selection=True)
    if not meshes:
        cmds.error("No mesh have been selected. Please select mesh(s) before pushing this button.")
        return
    out1 = cmds.floatFieldGrp(o1, query=True, value1=True)
    out2 = cmds.floatFieldGrp(o2, query=True, value1=True)
    out3 = cmds.floatFieldGrp(o3, query=True, value1=True)
    
    glow1 = cmds.floatFieldGrp(g1, query=True, value1=True)
    glow2 = cmds.floatFieldGrp(g2, query=True, value1=True)+0.1
    glow3 = cmds.floatFieldGrp(g3, query=True, value1=True)+0.1
    
    apply_glow(meshes,out1, out2, out3,glow1, glow2, glow3)

def createUI():
    '''creates a new window with 4 tabs to preview the points, create a lighting bolt (or several branches),
    mesh curves based on extrusion,
    and assigning to the meshes the surface shader resulting in a glowing effect
    return : shows the UI to the tool
    '''
    winID = cmds.window(title="Generate Lightning", widthHeight=(360, 310))
    tabs = cmds.tabLayout()

    # Add first tab for points
    firstTab = cmds.columnLayout()
    cmds.tabLayout(tabs, edit=True, tabLabel=[firstTab, 'Initial Points'])
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    #first point
    cmds.text(label="Start X:")
    x1Field = cmds.floatFieldGrp(value1= 0.0)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Start Y:")
    y1Field = cmds.floatFieldGrp(value1=0.0)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Start Z:")
    z1Field = cmds.floatFieldGrp(value1=0.0)
    cmds.setParent("..")
    cmds.separator(height=10, style="none")
    #second point
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Mid X:")
    x2Field = cmds.floatFieldGrp(value1=1.0)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Mid Y:")
    y2Field = cmds.floatFieldGrp(value1=1.2)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Mid Z:")
    z2Field = cmds.floatFieldGrp(value1=1.0)
    cmds.setParent("..")
    cmds.separator(height=10, style="none")
    #third point
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="End X:")
    x3Field = cmds.floatFieldGrp(value1=2.0)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="End Y:")
    y3Field = cmds.floatFieldGrp(value1=2.0)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="End Z:")
    z3Field = cmds.floatFieldGrp(value1=2.0)
    cmds.setParent("..")
    cmds.text(label="Important Note:if all points linear,randomization will be weak")
    cmds.text(label="Mid values set max randomization")
    #initial curve button
    cmds.button(label="Preview", command=lambda *args: button1Clicked(x1Field, y1Field, z1Field, 
    x2Field, y2Field, z2Field, 
    x3Field, y3Field, z3Field))
    cmds.setParent("..")
    
    #second tab is to subdivide curve
    secondTab = cmds.columnLayout()
    cmds.tabLayout(tabs, edit=True, tabLabel=[secondTab, 'Curve Create'])
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    #subdivisions
    cmds.text(label="Subdivide Curve:")
    subdivisions = cmds.intFieldGrp(value1=2)
    cmds.setParent("..")
    cmds.separator(height=20, style="none")
    #breakingDistance
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Scrunching:")
    breakingDistance = cmds.intFieldGrp(value1=1)
    cmds.setParent("..")
    cmds.separator(height=20, style="none")
    #curveDeg
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Curve Deg(smooth):")
    curveDeg = cmds.intFieldGrp(value1=1)
    cmds.setParent("..")
    cmds.separator(height=20, style="none")
    #maxAngle
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Max Angle:")
    maxAngle = cmds.intSliderGrp(field=True, minValue=-180.0, maxValue=180.0, value=180)
    cmds.setParent("..")
    cmds.separator(height=20, style="none")
    #minAngle
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Min Angle:")
    minAngle = cmds.intSliderGrp(field=True, minValue=-180.0, maxValue=180.0, value=-180)
    cmds.setParent("..")
    cmds.separator(height=20, style="none")
    cmds.text(label="the two angle values help limit randomization rotation")
    cmds.separator(height=10, style="none")
    #create subdivisions and randomization
    cmds.button(label="Create randomized curve", command=lambda *args: button2Clicked(x1Field, y1Field, z1Field,
    x2Field, y2Field, z2Field,
    x3Field, y3Field, z3Field,
    subdivisions,breakingDistance, curveDeg,
    maxAngle, minAngle))
    cmds.setParent("..")
    
    # Add third tab mesh and material
    thirdTab = cmds.columnLayout()
    cmds.tabLayout(tabs, edit=True, tabLabel=[thirdTab, 'Mesh'])
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    #radius
    cmds.text(label="Radius of mesh:")
    radius = cmds.floatFieldGrp(value1= 0.1)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    #expand
    cmds.text(label="Scale:")
    expand= cmds.floatFieldGrp(value1=1.0)
    cmds.setParent("..")
    #optional name
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Name mesh:")
    stringField = cmds.textField()
    cmds.setParent("..")
    cmds.text(label="select curve(s) to mesh BEFORE pressing the button")
    cmds.text(label="if no curves are selected, will not preform the mesh")
    cmds.button(label="Mesh", command=lambda *args: button3Clicked(radius, expand,stringField))
    cmds.setParent("..")
    
    fourthTab = cmds.columnLayout()
    cmds.tabLayout(tabs, edit=True, tabLabel=[fourthTab, 'Material'])
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    #Values for material
    #first Base
    cmds.text(label="Hue Base:")
    out1 = cmds.floatFieldGrp(value1= 0.1)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Transparency Base:")
    out2 = cmds.floatFieldGrp(value1=0.4)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Value Base:")
    out3 = cmds.floatFieldGrp(value1=0.6)
    cmds.setParent("..")
    #second Glow
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Hue Glow:")
    glow1 = cmds.floatFieldGrp(value1=0.1)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Transparency Base:")
    glow2 = cmds.floatFieldGrp(value1=0.4)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Value Base:")
    glow3 = cmds.floatFieldGrp(value1=0.2)
    cmds.setParent("..")
    cmds.rowLayout(nc=2, columnWidth2=(100, 100))
    cmds.text(label="Important Note:inputs based on Node graph values")
    cmds.button(label="Apply Material", command=lambda *args: button4Clicked(out1, out2, out3,glow1, glow2, glow3))
    cmds.showWindow(winID)

if __name__ == "__main__":
    createUI()