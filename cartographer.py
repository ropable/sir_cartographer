#!/usr/bin/env python
import os
from xml.etree import ElementTree

sirVersion = '0.11.5583'  # Tested against this game version.


def parse_islandgraph():
    # Get the filename for the graph file and open it.
    abspath = os.path.dirname(os.path.abspath(__file__))
    graphpath = os.path.join(abspath, 'data', 'Static_Content', 'CentreGraph.xml')
    return ElementTree.parse(graphpath)


def point_list(tree):
    # Look through the top level for the point list entry,
    # then look through that for C_Point entries.
    cpoints = list(tree.find('m_PointList').iter('C_Point'))

    # Determine x & y values for each C_Point entry.
    # Return a list of (iteration, x, y) tuples.
    points = []
    for itr, cp in enumerate(cpoints):
        points.append((itr, float(cp.find('X').text), float(cp.find('Y').text)))

    return points


def triangle_list(tree):
    # Look through the top level for the triangle list entry,
    # then look through that for C_Triangle entries
    ctriangles = list(tree.find("m_TriangleList").iter("C_Triangle"))

    # Go through all the C_Triangles getting their point reference values.
    triangles = []
    for itr, ct in enumerate(ctriangles):
        triangles.append((
            itr, int(ct.find('p1').text), int(ct.find('p2').text), int(ct.find('p3').text)))

    return triangles


def voronoi_corner_list(tree):
    # The next one is the Voronoi Corner List
    # Look through for C_Points
    vcorners = list(tree.find("m_VoronoiCornerList").iter("C_Point"))

    # Go through all the C_Points getting their X,Y values
    vor_corners = []
    for itr, cnr in enumerate(vcorners):
        vor_corners.append((itr, float(cnr.find('X').text), float(cnr.find('Y').text)))

    return vor_corners


def voronoi_edge_list(tree):
    # Then the Voronoi Edge List
    # Look through for C_Edges
    vedges = list(tree.find("m_VoronoiEdgeList").iter("C_Edge"))
    # Go through the C_Edges getting their point reference values
    vor_edges = []
    for itr, edge in enumerate(vedges):
        vor_edges.append((itr, int(edge.find('p1').text), int(edge.find('p2').text)))

    return vor_edges
