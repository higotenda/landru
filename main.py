from uxsim import *
import csv
import logging
from demparser import parse_demands

logging.basicConfig(level=logging.INFO);
logger = logging.getLogger(__name__);

SIMULATION_DURATION = 2*3600;

def gen_links_from_csv(W, fname):
    """
    Generate links in the network from a CSV file.

    Parameters
    ----------
    fname : str
        The file name of the CSV file containing link data.
    """
    with open(fname) as f:
        succ = 0;
        total = 0;
        for r in csv.reader(f):
            if r[3] != "length":
                try:
                    W.addLink(r[0], r[1], r[2], length=float(r[3]), free_flow_speed=float(r[4]), jam_density=float(r[5]), merge_priority=float(r[6]));
                    succ += 1;
                except Exception as e:
                    logger.warn(f"Failed to add link {r},\n\tcause: {e}");
            total += 1;
        logger.info(f"Imported {succ} links, success rate {succ / total} [{total - succ} fails]");


# Define the main simulation
# Units are standardized to seconds (s) and meters (m)
W = World(
    name="",    # Scenario name
    deltan=5,   # Simulation aggregation unit delta n
    tmax=SIMULATION_DURATION,  # Total simulation time (s)
    print_mode=1, save_mode=1, show_mode=0,    # Various options
    random_seed=0xb00b  # Set the random seed
)

W.generate_Nodes_from_csv("osm/map_nodes.csv");
gen_links_from_csv(W, "osm/map_edges.csv");

W.show_network(network_font_size=1)

for (incord, outcords) in parse_demands("osm/area_demands.csv"):
    logger.info(f"incord: {incord}, outcords: {outcords}");
    for c in outcords:
        logger.info(f"Added demand between {c} and {incord}");
        W.adddemand_area2area(c[0], c[1], 0, incord[0], incord[1], 0.05, 0, SIMULATION_DURATION, volume=5000);

W.exec_simulation();
W.analyzer.output_data("out/sim");