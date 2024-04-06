from collections import namedtuple
import random
import osmnx as ox
import pandas as pd
import logging
import math
from demparser import convert_coords

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#########SETTINGS########################

RAD_DIST = 1.5
# Get Radius of region around required place.

FREE_FLOW_SPEED_MAP = {
    "motorway": 13,
    "highway": 28,
    "residential": 7,
    "primary": 12,
    "secondary": 9,
    "tertiary": 4,
}

PRUNE_SET = {"tertiary", "highway"}

# Generate the appropriate filters, based on the aforementioned dict and set.
FILTER = (
    r'["highway" ~ "' + "|".join(set(FREE_FLOW_SPEED_MAP.keys()) - PRUNE_SET) + '"]'
)

logger.info(f"Using filters: {FILTER}")

FUDGE_IDEAL_VALUES = True

DEFAULT_FREE_FLOW_SPEED = 5
GLOBAL_MEAN_JAM_DENSITY = 0.16

JAM_DENSITY_VARIANCE = 0.02
FREEFLOW_SPEED_VARIANCE = 0.05
FREEFLOW_MEAN_SHIFTCOEF = 0.0025

HEAVY_PRUNE = False

"""
IMPL Ideas:
    1. Ditch Global jam denstiy - and use a better model per street.
    2. Add variance to free flow speed.
    3. Make demand non-uniform.
"""

##########################################


def local_coords(p1, p0, R=6_366_707):
    """
    Get local co-ords of p1 around p0 tuples of (lat, lon)
    """

    theta, phi0 = p0
    theta1, phi1 = p1

    theta, phi0, theta1, phi1 = (x * math.pi / 180 for x in (theta, phi0, theta1, phi1))

    Tdiff = theta1 - theta
    Pdiff = phi1 - phi0
    dx = R * math.cos(theta) * Pdiff
    dy = R * Tdiff
    logger.debug(f"p1: {p1}, p0: {p0} [{Tdiff}, {Pdiff}] are {(dx, dy)} away.")
    return (dy, dx)


def get_lat_lon(location_name):
    """
    Get latitude and longitude details of a location using OpenStreetMap via OSMnx.

    Parameters:
    location_name: Name or address of the location.

    Returns:
    Tuple containing latitude and longitude details (latitude, longitude).
    """
    try:
        # Retrieve the point of interest from OpenStreetMap
        return ox.geocode(location_name)
    except Exception as e:
        logger.error(f"Failed to geocode {location_name}")
        return (None, None)


def node_proc(nodes_iter, center):
    for node in nodes_iter:
        logger.info(f"Node {node}")
        p1 = node[1]["y"], node[1]["x"]
        yield (node[0], *local_coords(p1, center))


def edge_proc(edges_iter):
    """
    Obtain edges from OSM and export it.
    Future Improvement - Add method to infer jam density.
    """

    for i, edge in enumerate(edges_iter):
        name = f"E{i}"
        road_len = float(edge[2]["length"])
        rtype = str(edge[2]["highway"])

        # Probably not necessary, but keeping it here for paranioa's sake.
        if rtype in PRUNE_SET:
            continue

        if HEAVY_PRUNE and "name" not in edge[2]:
            continue

        logger.info(f"{name} : {edge}")

        defined_free_flow = float(
            FREE_FLOW_SPEED_MAP.get(rtype, DEFAULT_FREE_FLOW_SPEED)
        )
        if FUDGE_IDEAL_VALUES:
            free_flow = random.gauss(
                defined_free_flow + (FREEFLOW_MEAN_SHIFTCOEF) * road_len,
                FREEFLOW_SPEED_VARIANCE,
            )
            jd = random.gauss(GLOBAL_MEAN_JAM_DENSITY, JAM_DENSITY_VARIANCE)
        else:
            free_flow = defined_free_flow
            jd = GLOBAL_MEAN_JAM_DENSITY

        yield (
            name,
            edge[0],
            edge[1],
            road_len,
            free_flow,
            jd,
            1,
            edge[2].get("name", "unnamed"),
        )


def export_to_csv(graph, center, filename):
    """
    Export graphs into two csv files
    """

    a = node_proc(graph.nodes(data=True), center)
    b = edge_proc(graph.edges(data=True))

    nodes_df = pd.DataFrame(a, columns=["node_id", "x", "y"])
    edges_df = pd.DataFrame(
        b,
        columns=[
            "name",
            "source",
            "target",
            "length",
            "free_flow_speed",
            "jam_density",
            "merge_priority",
            "st_name",
        ],
    )

    # Export DataFrames to CSV
    nodes_df.to_csv(f"{filename}_nodes.csv", index=False)
    edges_df.to_csv(f"{filename}_edges.csv", index=False)

    return (nodes_df, edges_df)


def find_graph(addr: str):
    logger.info("Querying graph from OSM.")
    s = ox.graph_from_address(
        addr,
        dist=int(RAD_DIST * 1000),
        dist_type="network",
        network_type="drive_service",
        simplify=True,
        retain_all=False,
        truncate_by_edge=False,
        custom_filter=FILTER,
    )
    logger.info("Obtained result.")
    loc = get_lat_lon(addr)
    return s, loc


def find_graph_from_loc(point):
    logger.info("Querying graph from OSM.")
    s = ox.graph_from_point(
        point,
        dist=int(RAD_DIST * 1000),
        dist_type="network",
        network_type="drive_service",
        simplify=True,
        retain_all=False,
        truncate_by_edge=False,
        custom_filter=FILTER,
    )
    logger.info("Obtained result.")
    return s


def process_address(addr):
    g, loc = find_graph(addr)
    logger.info("Collecting and Exporting to CSV..")
    ndf, edf = export_to_csv(g, loc, "osm/map")
    logger.info("Converting raw_demands.csv global co-ords to local.")
    convert_coords("raw_demands.csv", "osm/area_demands.csv", local_coords, loc)


def process_coords(point):
    g = find_graph(point)
    logger.info("Collecting and Exporting to CSV..")
    ndf, edf = export_to_csv(g, point, "osm/map")
    logger.info("Converting raw_demands.csv global co-ords to local.")
    convert_coords("raw_demands.csv", "osm/area_demands.csv", local_coords, point)


if __name__ == "__main__":
    process_address("Malleshwaram, Bengaluru, India")
