#!/usr/bin/env python
import os
from PIL import Image, ImageDraw
from xml.etree import ElementTree

sirVersion = '0.11.5583'  # Tested against this game version.


def parse_islandgraph():
    # Get the filename for the graph file and open it.
    abspath = os.path.dirname(os.path.abspath(__file__))
    # TODO: accept user input to the Save path.
    graphpath = os.path.join(abspath, 'data', 'Static_Content', 'CentreGraph.xml')
    return ElementTree.parse(graphpath)


def point_list(tree):
    # Look through the tree for the point list entry,
    # then look through that for C_Point entries.
    cpoints = list(tree.find('m_PointList').iter('C_Point'))

    # Determine x & y values for each C_Point entry.
    # Return a list of (iteration, x, y) tuples.
    points = []
    for itr, cp in enumerate(cpoints):
        points.append((itr, float(cp.find('X').text), float(cp.find('Y').text)))

    return points


def triangle_list(tree):
    # Look through the tree for the triangle list entry,
    # then look through that for C_Triangle entries.
    ctriangles = list(tree.find("m_TriangleList").iter("C_Triangle"))

    # Go through all the C_Triangles getting their point reference values.
    triangles = []
    for itr, ct in enumerate(ctriangles):
        triangles.append((
            itr, int(ct.find('p1').text), int(ct.find('p2').text), int(ct.find('p3').text)))

    return triangles


def voronoi_edge_list(tree):
    # Look through the tree for the Voronoi edge list entry,
    # then look through that for C_Edge data.
    vedges = list(tree.find("m_VoronoiEdgeList").iter("C_Edge"))
    # Gather the p1 & p2 values for each C_Edges entry.
    vor_edges = []
    for itr, edge in enumerate(vedges):
        vor_edges.append((itr, int(edge.find('p1').text), int(edge.find('p2').text)))

    return vor_edges


def voronoi_corner_list(tree):
    # Look through the tree for the Voronoi corner list entry,
    # then look through that for C_Points data.
    vcorners = list(tree.find("m_VoronoiCornerList").iter("C_Point"))

    # Gather the X, Y value for each C_Points entry.
    vor_corners = []
    for itr, cnr in enumerate(vcorners):
        vor_corners.append((itr, float(cnr.find('X').text), float(cnr.find('Y').text)))

    return vor_corners


def voronoi_cell_list(tree):
    # Look through the tree for the Voronoi cell list entry,
    # then look through that for C_VoronoiCell data.
    vcells = list(tree.find("m_C_VoronoiCellList").iter("C_VoronoiCell"))
    # Look through for the Corner Indexes.
    vcell_corners = []
    for itr, cell in enumerate(vcells):
        # Look for the corner indices and cell type.
        cell_corner_idx = list(cell.find("m_CornerIndexes").iter("int"))
        ints = [int(i.text) for i in cell_corner_idx]
        celltype = int(cell.find("m_Type").text)
        vcell_corners.append((itr, ints, celltype))

    return vcell_corners


# Define a dict of cell types, plus a tuple of RGB colours to use for each
# cell type.
CELLTYPE = {
    1: (0, 0, 255),  # Sea
    # 2
    3: (0, 200, 0),  # Copse
    # 4
    5: (180, 180, 100),  # Shore
    6: (210, 210, 100),  # HedgedField
    7: (160, 160, 70),  # SoloBuilding
    8: (128, 128, 128),  # Village
    9: (96, 96, 96),  # Road
    # 10
    11: (0, 150, 0),  # Forest
    12: (230, 230, 120),  # BaseCamp
    13: (210, 210, 100),  # FencedField
    14: (80, 80, 80),  # Church
    15: (200, 200, 120),  # Boat
    16: (200, 200, 120),  # Boat
    17: (200, 200, 120),  # Boat
    18: (200, 200, 120),  # Boat
    19: (128, 128, 128),  # VillageRuined
    20: (0, 150, 0),  # PineForest
    21: (80, 180, 80),  # DecidForest
    22: (20, 40, 150),  # Pool
    23: (70, 70, 70),  # HillCliff
    24: (140, 140, 80),  # Rocks
    25: (0, 130, 0),  # ForestCamp
    26: (20, 40, 160),  # Canal
    27: (40, 80, 200),  # PostField
    # 28
    29: (64, 64, 64),  # VillageIndustrial
    30: (210, 210, 210),  # WalledHayBale
    31: (180, 180, 70),  # SoloSmallBuilding
    32: (10, 20, 120),  # IndCanal
    33: (72, 72, 72),  # IndCanalSide
    34: (120, 96, 96),  # JunkPile
    35: (100, 76, 76),  # SlagHeap
    36: (200, 200, 80),  # Pylon
}


def get_polygons(tree):
    # Returns a list of polygons in the format:
    # (primary_key, [[X, Y], ...], (R, B, G), type_integer)
    # Determine Voronoi corners and cells for the island graph.
    vcorners = voronoi_corner_list(tree)
    vcells = voronoi_cell_list(tree)
    # Build map polygons using Voronoi cell data.
    polygons = []
    for itr, cell in enumerate(vcells):
        coords = []
        for cell_int in cell[1]:
            coords.append([vcorners[cell_int][1], vcorners[cell_int][2]])
        cell_type = cell[2]
        if cell[2] in CELLTYPE:
            polygons.append([itr, coords, CELLTYPE[cell_type], cell_type])
        else:
            # Highlight any unknown region types in red.
            polygons.append([itr, coords, (255, 0, 0), cell_type])

    return polygons


def render_island(tree):
    bg = Image.new('RGBA', (1024, 1024), (255, 0, 0, 0))
    polygons = get_polygons(tree)
    # TODO: allow different sizes of rendering. For now just render an island
    # 1024x1024.
    xscale = 1.0
    yscale = 1.0
    ydisplaysize = 1024
    # Draw the Voronoi cell polygons.
    for p in polygons:
        # Take the list of coords and modify them in-place.
        coords = p[1]
        for idx, coord in enumerate(coords):
            coord[0] = int(coord[0] * xscale)
            coord[1] = ydisplaysize - int(coord[1] * yscale)
            coords[idx] = tuple(coord)  # Cast the list as a 2-tuple.

        poly = Image.new('RGBA', (1024, 1024))
        poly_draw = ImageDraw.Draw(poly)
        poly_draw.polygon(coords, fill=p[2])#, outline=(255, 255, 255, 255))
        bg.paste(poly, mask=poly)

    bg.save('test.png')
    return True
