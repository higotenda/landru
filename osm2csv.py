import osmnx as ox
import pandas as pd
import logging
import math

logger = logging.getLogger(__name__);

RAD_DIST = 1.5; # Get Radius of region around required place.

FREE_FLOW_SPEED_MAP = {
    "highway":      28,
    "residential":  7,
    "primary":      12,
    "secondary":    9,
    "tertiary":     4
};

DEFAULT_FREE_FLOW_SPEED = 5;
GLOBAL_BASE_JAM_DENSITY = 0.16;

"""
IMPL Ideas:
    1. Ditch Global jam denstiy - and use a better model per street.
    2. Add variance to free flow speed.
    3. Make demand non-uniform.
"""

def local_coords(p1, p0, R=6_366_707):
    """
    Get local co-ords of p1 around p0
    """

    # lat1, lon1 = p1;
    # lat2, lon2 = p0;
    # # Convert latitude and longitude from degrees to radians
    # lat1, lon1, lat2, lon2 = map(lambda x: x/180*math.pi, [lat1, lon1, lat2, lon2])
    
    # # Haversine formula
    # dlat = lat2 - lat1
    # dlon = lon2 - lon1
    # a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    # c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    # distance = 6371 * c  # Earth radius in kilometers
    
    theta, phi0 = p0;
    theta1, phi1= p1;

    theta, phi0, theta1, phi1 = (x*math.pi/180 for x in (theta, phi0, theta1, phi1));

    Tdiff = theta1 - theta;
    Pdiff = phi1 - phi0;
    dx = R*math.cos(theta)*Pdiff;
    dy = R*Tdiff;
    print(f"p1: {p1}, p0: {p0} are {(dx, dy)}");
    return (Tdiff, Pdiff);


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
        logger.error(f"Failed to geocode {location_name}");
        return (None, None);

def node_proc(nodes_iter, center):
    for node in nodes_iter:
        print("Node", node);
        p1 = node[1]['x'], node[1]['y'];
        yield (node[0], *local_coords(p1, center));

def edge_proc(edges_iter):
    """
    Obtain edges from OSM and export it.
    Future Improvement - Add method to infer jam density.
    """

    for i, edge in enumerate(edges_iter):
        name = f"E{i}";
        road_len = edge[2]['length'];
        rtype = str(edge[2]['highway']);
        free_flow = FREE_FLOW_SPEED_MAP.get(rtype, DEFAULT_FREE_FLOW_SPEED);
        print(name, ":", edge);
        yield (name, edge[0], edge[1], float(road_len), float(free_flow), GLOBAL_BASE_JAM_DENSITY, 1);

def export_to_csv(graph, center, filename):
    """
    Export graphs into two csv files
    """
    
    a = node_proc(graph.nodes(data=True), center);
    b = edge_proc(graph.edges(data=True));

    nodes_df = pd.DataFrame(a, columns=['node_id', 'x', 'y']);
    edges_df = pd.DataFrame(b, columns=['name', 'source', 'target', 'length', 'free_flow_speed', 'jam_density', 'merge_priority']);

    logger.info("Generated DataFrames.");
    
    # Export DataFrames to CSV
    nodes_df.to_csv(f'{filename}_nodes.csv', index=False)
    edges_df.to_csv(f'{filename}_edges.csv', index=False)

    return (nodes_df, edges_df);


def find_graph(addr: str):
    logger.info("Querying graph from OSM.");
    s = ox.graph_from_address(
        addr, 
        dist=int(RAD_DIST*1000),
        dist_type="network",
        network_type="drive",
        simplify=True,
        retain_all=False,
        truncate_by_edge=False,
    );
    logger.info("Obtained result.");
    loc = get_lat_lon(addr)[::-1];
    return s, loc;

if __name__ == "__main__":
    g, loc = find_graph("Malleshwaram, Bengaluru, India");
    logger.info("Collecting and Exporting to CSV..");
    ndf, edf = export_to_csv(g, loc, "osm/map");
