"""Console script for kitoolkit."""
import argparse
import sys

from kicad2charmhigh import get_args_parser
from kicad2charmhigh import main as k2c_main

def main():
    """Console script for kitoolkit."""
    parser = get_args_parser()

    parser.add_argument('bom', type=str, help='Kicad BOM File')
    parser.add_argument('--kicad-pcb', type=str, help='Kicad PCB File to generate InteractiveBom')
    
    args = parser.parse_args()
    print("\n".join([f"{k} = {getattr(args, k)}" for k in vars(args)]))

    kwargs = vars(args)

    k2c_args = {k:kwargs[k] for k in kwargs if k not in ['bom', 'kicad_pcb']}
    k2c_main(**k2c_args)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
