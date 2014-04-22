#!/usr/bin/env python
import os
from xml.etree import ElementTree


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
    # Return a list of (iteration, x, y, height) tuples.
    points = []
    for itr, cp in enumerate(cpoints):
        points.append((
            itr, float(cp.find('X').text), float(cp.find('Y').text),
            int(cp.find('Height').text)
        ))

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
    # Gather the p1, p2, hasgate and type values for each C_Edges entry.
    vor_edges = []
    for itr, edge in enumerate(vedges):
        vor_edges.append((
            itr, int(edge.find('p1').text), int(edge.find('p2').text),
            float(edge.find('hasgate').text),
            int(edge.find('type').text)
        ))

    return vor_edges


def voronoi_corner_list(tree):
    # Look through the tree for the Voronoi corner list entry,
    # then look through that for C_Points data.
    vcorners = list(tree.find("m_VoronoiCornerList").iter("C_Point"))

    # Gather the X, Y, Type and Height values for each C_Points entry.
    vor_corners = []
    for itr, cnr in enumerate(vcorners):
        vor_corners.append((
            itr, float(cnr.find('X').text), float(cnr.find('Y').text),
            int(cnr.find('type').text),
            float(cnr.find('Height').text)
        ))

    return vor_corners
