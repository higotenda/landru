"""
Python module to parse demand in-out files
"""

import logging

logger = logging.getLogger(__name__);
logger.setLevel(logging.DEBUG);

def parse_demands(fp: str):
	"""
	Parse the provided file, and return the correspoding source-sink sets.
	"""

	in_cords = (0,0);
	out_cords = [];

	with open(fp, 'r') as f:
		for line in f:
			line = line.strip();

			if len(line) == 0:
				yield (in_cords, out_cords[::]);
				in_cords = (0,0);
				out_cords.clear();
				continue

			toks = line.split(",");

			try:
				pos = (float(toks[1]), float(toks[2]));
				logger.info(f"Parsed {toks[0]} pos: {pos}");
				if toks[0] == 'in':
					in_cords = pos;
				elif toks[0] == 'out':
					out_cords.append(pos);
			except Exception as e:
				logger.warn(f"Failed to parse line '{line.strip()}', cause: {e}");


def convert_coords(fp: str, out: str, func, center):
	with open(fp, 'r') as f, open(out, 'w') as f2:
		for line in f:
			if len(line) == 0:
				continue;

			toks = line.split(",");
			try:
				pos = float(toks[1]), float(toks[2]);
				cps = func(pos, center);
				print(toks[0], *cps, sep=',', file=f2);
				logger.info(f"Point {pos} from {center} is {cps}");
			except Exception as e:
				logger.warn(f"Failed to parse line {line}");
		print(file=f2);
