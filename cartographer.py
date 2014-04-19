sirVersion = '0.11.5583'
#versionNumber = 'v0.91'

# To do:
# Add toggles for various map display settings
# (e.g. props, names, loot, polygon boundaries, map title) to the UI in a choice screen.
# Integrate a loot finder (wait, why am I making stuff for cheats?)
# Include terrain height indicator!

# This is working well enough for a first build.

# Import libraries.
import xml.etree.ElementTree as ET # For parsing the xml files.
import pygame, sys
from pygame.locals import *
import pygame.gfxdraw
import random
from operator import itemgetter
import easygui as eg

# Prompt user to point at the save game.
msg = 'Choose which save game folder to modify.'
sirPath = eg.diropenbox(msg)

def set_alphas(colour,backCol):
    # Replace given colour with mask.
    if colour == backCol:
        return (0,0,0,0)
    red, green, blue, density = colour
    return (red,green,blue,255)

# Prompt user to choose which island from the save game.
msg = 'Choose which island to map.'
title = msg
choices = ['Centre','North','East','South','West']
islandName = eg.choicebox(msg,title,choices)

# Prompt user to choose output map size.
# This works for me, but people reported problems with the earlier build.
# Could rework this to allow full control over x and y.
NATIVEX = 1024
NATIVEY = 1024

msg = 'Choose the size of the output map. (512 matches in-game map.)'
title = msg
choices = [512,768,1024]
outputSize = int(eg.choicebox(msg,title,choices))

XDISPLAYSIZE = outputSize
YDISPLAYSIZE = outputSize

XSCALE = XDISPLAYSIZE/NATIVEX
YSCALE = YDISPLAYSIZE/NATIVEY
# End of output map size bit.

# Here follows a horrendous slew of crappy undescriptive variable names.

# Get the filename for the graph file and open it.
fileName = sirPath + '\\Static_Content\\' + islandName + 'Graph.xml'
tree = ET.parse(fileName)

# Look through the top level for the point list entry
pLe = tree.find("m_PointList")
# Look through the point list entry for C_Point entries
CPe = list(pLe.iter("C_Point"))

# Go through all the C_Points getting the X,Y values
# Using a counter to number the points.
# Place all results in CPeList
CPeList = []
position = 0
for CPentry in CPe:
    CPeX = list(CPentry.iter("X"))
    CPeY = list(CPentry.iter("Y"))
    CPeList.append([position,float(CPeX[0].text),float(CPeY[0].text)])
    position += 1

# Look through the top level for the triangle list entry
tLe = tree.find("m_TriangleList")
# Look through the point list entry for C_Triangle entries
CTe = list(tLe.iter("C_Triangle"))

# Go through all the C_Triangles getting their point reference values
CTeList = []
position = 0
for CTentry in CTe:
    CTe1 = list(CTentry.iter("p1"))
    CTe2 = list(CTentry.iter("p2"))
    CTe3 = list(CTentry.iter("p3"))
    CTeList.append([position,int(CTe1[0].text),int(CTe2[0].text),int(CTe3[0].text)])
    position += 1

# The next one is the Voronoi Corner List
vCo = tree.find("m_VoronoiCornerList")
# Look through for C_Points
CvCo = list(vCo.iter("C_Point"))
# Go through all the C_Points getting their X,Y values
vCoList = []
position = 0
for CPentry in CvCo:
    CPeX = list(CPentry.iter("X"))
    CPeY = list(CPentry.iter("Y"))
    # Read the ints as well - not that I know exactly what they're doing...
    foundInts = []
    vInt = list(CPentry.iter("int"))
    for vIntLook in vInt:
        foundInts.append(vIntLook.text)
    vCoList.append([position,float(CPeX[0].text),float(CPeY[0].text),foundInts])
    position += 1

# Then the Voronoi Edge List
vEdge = tree.find("m_VoronoiEdgeList")
# Look through for C_Edges
vCEdge = list(vEdge.iter("C_Edge"))
# Go through the C_Edges getting their point reference values
vCEdgeList = []
position = 0
for VCentry in vCEdge:
    vCe1 = list(VCentry.iter("p1"))
    vCe2 = list(VCentry.iter("p2"))
    vCEdgeList.append([position,int(vCe1[0].text),int(vCe2[0].text)])
    position += 1

# Then the Voronoi Cell List
# Okay, this is the biggie.  Each cell refers some Delaunay stuff - is that the main triangle list?
# Then it refers to the Voronoi corners and Voronoi edges from above.
vCell = tree.find("m_C_VoronoiCellList")
# Look through for Voronoi Cells
vCellCells = list(vCell.iter("C_VoronoiCell"))
# Look through for the Corner Indexes.  This xml parsing is doing my head in!
vCellCoList = []
position = 0
for vCellCell in vCellCells:
    # Look for the type
    vCellType = int(vCellCell.find("m_Type").text)
    # Look for the corner indices
    vCellCo = vCellCell.find("m_CornerIndexes")
    foundInts = []
    vCellCoInt = list(vCellCo.iter("int"))
    for vCellCoIntLook in vCellCoInt:
        foundInts.append(int(vCellCoIntLook.text))
    vCellCoList.append([position,foundInts,vCellType])
    position += 1

builtTriangles = []
tcol = 0
# Build a bunch of triangles.
for entry in CTeList:
    pid1 = entry[1]
    pid2 = entry[2]
    pid3 = entry[3]
    # This could be neater and better optimised, but really, who cares?
    for point in CPeList:
        if point[0] == pid1:
            px1 = int(point[1])
            py1 = int(point[2])
        if point[0] == pid2:
            px2 = int(point[1])
            py2 = int(point[2])
        if point[0] == pid3:
            px3 = int(point[1])
            py3 = int(point[2])
    tcol = random.randint(100,255) # adding a random colour to distinguish between triangles
##    if tcol <= 250:
##        tcol += 1
##    else:
##        tcol = 0
    builtTriangles.append([px1,py1,px2,py2,px3,py3,tcol])

builtVoronoiEdges = []
tcol = 0
# Build a bunch of edges.
for entry in vCEdgeList:
    pid1 = entry[1]
    pid2 = entry[2]
    # These refer to points in the Voronoi Corner list.
    for point in vCoList:
        if point[0] == pid1:
            px1 = int(point[1])
            py1 = int(point[2])
        if point[0] == pid2:
            px2 = int(point[1])
            py2 = int(point[2])
    tcol = random.randint(100,255)
    builtVoronoiEdges.append([px1,py1,px2,py2,tcol])

# Build a bunch of polygons using the Voronoi cell data.
position = 0
builtVoronoiPolygons = []
for vCell in vCellCoList:
    foundcoords = []
    for vCellInt in vCell[1]:
        foundcoords.append([vCoList[vCellInt][1],vCoList[vCellInt][2]])
    # Default colour - will highlight any unknown region types in red.
    tcol = (255,0,0)

    # Known types: Sea = 1, Copse = 3, Shore = 5, HedgedField = 6, SoloBuilding = 7
    # Known types: Village = 8, Road = 9, Forest = 11, BaseCamp = 12, FencedField = 13, Church = 14
    # Known types: BoatN = 15, BoatS = 16, BoatE = 17, BoatW = 18
    # Known types: VillageRuined = 19, PineForest = 20, DecidForest = 21, Pool = 22, HillCliff = 23,
    # Known types: Rocks = 24, ForestCamp = 25, Canal = 26, Postfield = 27, SoloSmallBuilding = 31

    # Missing: 2,4,10,28,31

    # v0.9 added with Industrial:
    # 29 = VillageIndustrial, 30 = WalledHayBale, 32 = IndCanal, 33 = IndCanalSide, 34 = JunkPile
    # 35 = SlagHeap, 36 = Pylon

    # Specific colours
    if vCell[2] == 1: # Sea
        tcol = (0,0,255)
    elif vCell[2] == 3: # Copse
        tcol = (0,200,0)
    elif vCell[2] == 5: # Shore
        tcol = (180,180,100)
    elif vCell[2] == 6: # HedgedField
        tcol = (210,210,100)
    elif vCell[2] == 7: # SoloBuilding
        tcol = (160,160,70)
    elif vCell[2] == 8: # Village
        tcol = (128,128,128) # **Grey**
    elif vCell[2] == 9: # Road
        tcol = (96,96,96)
    elif vCell[2] == 11: # Forest
        tcol = (0,150,0)
    elif vCell[2] == 12: # BaseCamp (Circle)
        tcol = (230,230,120)
    elif vCell[2] == 13: # FencedField
        tcol = (210,210,100)
    elif vCell[2] == 14: # Church
        tcol = (80,80,80)
    elif vCell[2] == 15 or vCell[2] == 16 or vCell[2] == 17 or vCell[2] == 18: # Boats
        tcol = (200,200,120)
    elif vCell[2] == 19: # VillageRuined ?different in Fens?
        tcol = (128,128,128) # **Grey**
    elif vCell[2] == 20: # PineForest
        tcol = (0,150,0)
    elif vCell[2] == 21: # DecidForest
        tcol = (80,180,80)
    elif vCell[2] == 22: # Pool
        tcol = (20,40,150)
    elif vCell[2] == 23: # HillCliff
        tcol = (70,70,70)
    elif vCell[2] == 24: # Rocks
        tcol = (140,140,80)
    elif vCell[2] == 25: # ForestCamp
        tcol = (0,130,0)
    elif vCell[2] == 26: # Canal
        tcol = (20,40,160)
    elif vCell[2] == 27: # PostField
        tcol = (40,80,200)
    elif vCell[2] == 29: # VillageIndustrial
        tcol = (64,64,64) # **Dark grey**
    elif vCell[2] == 30: # WalledHayBale
        tcol = (210,210,100)
    elif vCell[2] == 31: # SoloSmallBuilding
        tcol = (180,180,70)
    elif vCell[2] == 32: # IndCanal
        tcol = (10,20,120)
    elif vCell[2] == 33: # IndCanalSide
        tcol = (72,72,72)
    elif vCell[2] == 34: # JunkPile
        tcol = (120,96,96)
    elif vCell[2] == 35: # SlagHeap
        tcol = (100,76,76)
    elif vCell[2] == 36: # Pylon
        tcol = (200,200,80)
    builtVoronoiPolygons.append([position,foundcoords,tcol,vCell[2]])
    position += 1

# Now we need to open and read the container location stuff.
# Target file
fileName = sirPath + '\\Dynamic_Content\\' + islandName + 'Inv.xml'

cacheTree = ET.parse(fileName)
# Look for m_InventoryName entries
INe = list(cacheTree.iter("m_InventoryName"))
foundCaches = []
for entry in INe:
    cacheString = entry.text
    starter = cacheString.find('for ')
    ender = cacheString.find(' At')
    foundLootName = cacheString[starter+4:ender]
    #print(foundLootName)
    cacheString = cacheString[-7:]
    cacheString = cacheString.split(' ')
    x = int(cacheString[0])
    y = int(cacheString[1])
    foundCaches.append([x,y,foundLootName])

# Now open and read the telecache (device piece) locations.
# Target file
fileName = sirPath + '\\Dynamic_Content\\' + islandName + 'TeleCaches.xml'
teleCacheTree = ET.parse(fileName)
# Look for m_Locations entry
tcmL = teleCacheTree.find("m_Locations")
tcV = tcmL.iter("Vector3")
foundTeleCaches = []
for teleCache in tcV:
    x = teleCache.find("x").text
    y = teleCache.find("z").text # don't ask
    x = float(x)
    y = float(y)
    foundTeleCaches.append([x,y])

# Now open and read the village region ids and names.
# Target file
fileName = sirPath + '\\Static_Content\\' + islandName + 'VillageNames.xml'
vTree = ET.parse(fileName)
vL = list(vTree.iter("C_VillageName"))
foundVillages = []
for village in vL:
    villageID = int(village.find("m_RegionID").text)
    villageName = village.find("m_Title").text
    villageSub = village.find("m_SubTitle").text
    foundVillages.append([villageID,villageName,villageSub])

# Now open and read the region stuff.
# (for curiosity, this isn't used, but it returns a list of the region types in case there's an unusual one)
# Target file
fileName = sirPath + '\\Static_Content\\' + islandName + 'Regions.xml'
regionTree = ET.parse(fileName)
regionRegions = list(regionTree.iter("C_RegionData"))
foundRegionTypes = []
bigPropList = []
for region in regionRegions:
    thisRegionType = region.find("m_RegionName").text
    alreadyExists = False
    for thing in foundRegionTypes:
        if thing == thisRegionType:
            alreadyExists = True
    if alreadyExists == False:
        foundRegionTypes.append(thisRegionType)
    # There are also a bunch of other x,z (x,y really) points in there that want looking at, I think these are gravestones and stuff.
    foundPropIDs = []
    foundPropPositions = []
    thisRegionProps = int(region.find("m_NumProps").text)
    regionProps = list(region.iter("m_PropIDs"))
    for regional in regionProps:
        propIDs = regional.iter("int")
        for prop in propIDs:
            foundPropIDs.append(int(prop.text))
    regionPropPositions = list(region.iter("m_PropPositions"))
    for regional in regionPropPositions:
        vectors = regional.iter("Vector3")
        for vector in vectors:
            x = float(vector.find("x").text)
            y = float(vector.find("z").text)
            foundPropPositions.append([x,y])
    for position in range(len(foundPropIDs)):
        bigPropList.append([foundPropIDs[position],foundPropPositions[position],thisRegionType])

# Just a check to see what props are in what regions, because I don't understand it.
propsListByRegion = []
sortedPropList = sorted(bigPropList, key=itemgetter(2,0))
for region in foundRegionTypes:
    propsThisRegion = []
    for prop in sortedPropList:
        if prop[2] == region:
            propsThisRegion.append(prop[0])
    propsThisRegion = list(set(propsThisRegion))
    propsListByRegion.append([region,propsThisRegion])

print(foundRegionTypes)

# Start main display.
# Start Pygame.
pygame.init()

# Timing.
FPS = 30
fpsClock = pygame.time.Clock()

# Colours.
BLACK = (0,0,0)
DARKGREY = (50,50,50)
WHITE = (255,255,255)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BRIGHTBLUE = (200,200,255)
MIDBLUE = (100,100,255)

try:
    fontFilename = pygame.font.match_font('segoeprint')
    fontObj = pygame.font.Font(fontFilename,20)
except:
    fontObj = pygame.font.Font('freesansbold.ttf', 16)

textToDisplay = 'Blankton'
TEXTOFFSETX = 50
TEXTOFFSETY = 50

# Create display surface.
DISPLAYSURF = pygame.display.set_mode((XDISPLAYSIZE,YDISPLAYSIZE))
#pygame.display.set_caption('Sir, You Are Being Mapped '+versionNumber+' - Mapping the '+islandName+' island.')


# Draw the Voronoi cell polygons.
for voronoiPolygon in builtVoronoiPolygons:
    pointList = voronoiPolygon[1]
    correctedList = []
    for point in pointList:
        x = point[0]
        y = point[1]
        x = int(x * XSCALE)
        y = YDISPLAYSIZE - int(y * YSCALE)
        correctedList.append([x,y])
    tcol = voronoiPolygon[2]
    pygame.gfxdraw.filled_polygon(DISPLAYSURF,correctedList,tcol)
    # Draw an anti-aliased boundary around the polygon.
    # If LINEDIM is set above 1, the line will be dimmer.
    r,g,b = tcol
    LINEDIM = 1.1
    r = int(r/LINEDIM)
    g = int(g/LINEDIM)
    b = int(b/LINEDIM)
    dcol = (r,g,b)
    if voronoiPolygon[3] != 1 and voronoiPolygon[3] != 5: # Don't draw polygon boundaries in the sea or shore.
        pygame.gfxdraw.aapolygon(DISPLAYSURF,correctedList,dcol)

# Draw hedges and fences.
for voronoiPolygon in builtVoronoiPolygons:
    pointList = voronoiPolygon[1]
    correctedList = []
    for point in pointList:
        x = point[0]
        y = point[1]
        x = int(x * XSCALE)
        y = YDISPLAYSIZE - int(y * YSCALE)
        correctedList.append([x,y])
    tcol = voronoiPolygon[2]
    # If the polygon is for something with a boundary, draw a suitable outline
    if voronoiPolygon[3] == 6: # hedged
        dcol = (50,150,20)
        pygame.gfxdraw.aapolygon(DISPLAYSURF,correctedList,dcol)
    elif voronoiPolygon[3] == 13: # fenced
        dcol = (100,100,40)
        pygame.gfxdraw.aapolygon(DISPLAYSURF,correctedList,dcol)
    elif voronoiPolygon[3] == 14: # church
        dcol = (20,20,20)
        pygame.gfxdraw.aapolygon(DISPLAYSURF,correctedList,dcol)
    elif voronoiPolygon[3] == 27: # post field
        dcol = (20,60,20)
        pygame.gfxdraw.aapolygon(DISPLAYSURF,correctedList,dcol)
    elif voronoiPolygon[3] == 30: # walled hay bale
        dcol = (80,40,0)
        pygame.gfxdraw.aapolygon(DISPLAYSURF,correctedList,dcol)

# Draw the found caches on the map with a background effect.
for foundCache in foundCaches:
    x = int(foundCache[0] * XSCALE)
    y = YDISPLAYSIZE - int(foundCache[1] * YSCALE)
    pygame.gfxdraw.filled_circle(DISPLAYSURF,x,y,8,DARKGREY)
for foundCache in foundCaches:
    x = int(foundCache[0] * XSCALE)
    y = YDISPLAYSIZE - int(foundCache[1] * YSCALE)
    pygame.gfxdraw.filled_circle(DISPLAYSURF,x,y,3,BLACK)

# Draw all found props.
for prop in bigPropList:
    x = prop[1][0]
    y = prop[1][1]
    x = int(x * XSCALE)
    y = YDISPLAYSIZE - int(y * YSCALE)
    # Really don't get how these work.
    # There are trees in copses with no props for instance.
    dcol = RED
##    if prop[0] == 0: # Boat?  Oh dear, I don't understand this.
##        # Might be dependent on the region type.
##        dcol = (240,0,240)
##    elif prop[0] == 4: # Tree?
##        dcol = (0,220,0)
    #pygame.gfxdraw.filled_circle(DISPLAYSURF,x,y,2,dcol)

# Draw the found caches on the map in black.
for foundCache in foundCaches:
    x = int(foundCache[0] * XSCALE)
    y = YDISPLAYSIZE - int(foundCache[1] * YSCALE)
    pygame.gfxdraw.filled_circle(DISPLAYSURF,x,y,3,BLACK)

# Draw the village names on the map.
for village in foundVillages:
    vindex = village[0]
    # Check whether the village has anything in it by looking at its props.
    villageAliveChecker = regionRegions[vindex].find('m_NumProps')

    pointList = builtVoronoiPolygons[vindex][1]
    x = pointList[0][0] + TEXTOFFSETX
    y = pointList[0][1] + TEXTOFFSETY
    x = int(x * XSCALE)
    y = YDISPLAYSIZE - int(y * YSCALE)
    textToDisplay = village[1]
    backCol = BLACK
    textSurfaceObj = fontObj.render(textToDisplay, False, DARKGREY, backCol).convert_alpha()
    for row in range(textSurfaceObj.get_width()):
        for col in range(textSurfaceObj.get_height()):
            textSurfaceObj.set_at((row,col), set_alphas(textSurfaceObj.get_at((row,col)),backCol))
        textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (x,y)
    # Provided the village really exists, write its name.
    if villageAliveChecker.text != '0':
        DISPLAYSURF.blit(textSurfaceObj,textRectObj)

    textSurfaceObj = fontObj.render(textToDisplay, False, (240,240,240), backCol).convert_alpha()
    for row in range(textSurfaceObj.get_width()):
        for col in range(textSurfaceObj.get_height()):
            textSurfaceObj.set_at((row,col), set_alphas(textSurfaceObj.get_at((row,col)),backCol))
        textRectObj = textSurfaceObj.get_rect()
    x += 1
    y += 1
    textRectObj.center = (x,y)
    # Provided the village really exists, write its name.
    if villageAliveChecker.text != '0':
        DISPLAYSURF.blit(textSurfaceObj,textRectObj)

# Draw the found telecaches on the map.
for foundTeleCache in foundTeleCaches:
    x = int(foundTeleCache[0] * XSCALE)
    y = YDISPLAYSIZE - int(foundTeleCache[1] * YSCALE)
    pygame.gfxdraw.filled_circle(DISPLAYSURF,x,y,5,BRIGHTBLUE)
    pygame.gfxdraw.filled_circle(DISPLAYSURF,x,y,3,MIDBLUE)

# Export the map.
fileName = sirPath + 'outputmap' + '-' + islandName + '.png'
pygame.image.save(DISPLAYSURF,fileName)

# Main loop, just keep displaying the map until the program is exited.
while True:

    # Check for events.
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()

    # Update the display and tick the clock.
    pygame.display.update()
    fpsClock.tick(FPS)
