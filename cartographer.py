#!/usr/bin/env python
from PIL import Image, ImageDraw
from utils import voronoi_corner_list#, voronoi_cell_list

GAMEVERSION = '0.11.5583'  # Tested against this version of the game.


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
    1: [0, 0, 255],  # Sea
    # 2
    3: [0, 200, 0],  # Copse
    # 4
    5: [180, 180, 100],  # Shore
    6: [210, 210, 100],  # HedgedField
    7: [160, 160, 70],  # SoloBuilding
    8: [128, 128, 128],  # Village
    9: [96, 96, 96],  # Road
    # 10
    11: [0, 150, 0],  # Forest
    12: [230, 230, 120],  # BaseCamp
    13: [210, 210, 100],  # FencedField
    14: [80, 80, 80],  # Church
    15: [200, 200, 120],  # Boat
    16: [200, 200, 120],  # Boat
    17: [200, 200, 120],  # Boat
    18: [200, 200, 120],  # Boat
    19: [128, 128, 128],  # VillageRuined
    20: [0, 150, 0],  # PineForest
    21: [80, 180, 80],  # DecidForest
    22: [20, 40, 150],  # Pool
    23: [70, 70, 70],  # HillCliff
    24: [140, 140, 80],  # Rocks
    25: [0, 130, 0],  # ForestCamp
    26: [20, 40, 160],  # Canal
    27: [40, 80, 200],  # PostField
    # 28
    29: [64, 64, 64],  # VillageIndustrial
    30: [210, 210, 210],  # WalledHayBale
    31: [180, 180, 70],  # SoloSmallBuilding
    32: [10, 20, 120],  # IndCanal
    33: [72, 72, 72],  # IndCanalSide
    34: [120, 96, 96],  # JunkPile
    35: [100, 76, 76],  # SlagHeap
    36: [200, 200, 80],  # Pylon
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


def island_size(xscale=1.0, yscale=1.0):
    # Return a tuple of (x, y) pixel size for each island.
    # TODO: allow different sizes of rendering. For now just render an island
    # 1024x1024.
    return (int(1024*xscale), int(1024*yscale))


def render_island(tree):
    # Obtain polygons, except for sea or shore type.
    # Don't draw polygon boundaries in the sea or shore.
    polygons = [p for p in get_polygons(tree) if p[3] not in [1, 5]]
    size = island_size()
    bg = Image.new('RGBA', size, (255, 0, 0, 0))
    # Draw the map background.
    tile = Image.open('assets/old_map.png')
    tilesize = tile.size
    tilex = int(size[0] / tilesize[0])
    tiley = int(size[1] / tilesize[1])
    for i in range(tilex):
        for j in range(tiley):
            bg.paste(tile, (i*tilesize[0], j*tilesize[1]))

    # Draw the Voronoi cell polygons.
    for p in polygons:
        # Take the list of coords and modify them in-place.
        coords = p[1]
        for idx, coord in enumerate(coords):
            coord[0] = int(coord[0])
            coord[1] = size[1] - int(coord[1])
            coords[idx] = tuple(coord)  # Cast the list as a 2-tuple.

        poly = Image.new('RGBA', size)
        poly_draw = ImageDraw.Draw(poly)
        #poly_draw.polygon(coords, fill=None, outline=(0, 0, 0, 255))  # Black outline, no fill.
        poly_draw.polygon(coords, fill=tuple(p[2] + [255]))
        bg.paste(poly, mask=poly)

    bg.save('test.png')
    return True
