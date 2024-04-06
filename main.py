from sqlalchemy.sql.ddl import exc
from uxsim import *
import csv
import logging

# logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__);

SIMULATION_DURATION = 3600;

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

W.adddemand_area2area(13.001867215947623, 77.56709046386388, 0, 12.999073447375757, 77.5724257603931, 0.05, 0, 3600, volume=5000)

W.exec_simulation();
W.analyzer.output_data("out/sim");