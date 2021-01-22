"""Console script for kitoolkit."""
import argparse
import sys
import os

from kicad2charmhigh import get_args_parser
from kicad2charmhigh import main as k2c_main

from . import kitoolkit

def main():
    """Console script for kitoolkit."""
    parser = get_args_parser()

    parser.add_argument('bom', type=str, help='Kicad BOM File')
    parser.add_argument('--kicad-pcb', type=str, help='Kicad PCB File to generate InteractiveBom')
    
    args = parser.parse_args()

    kwargs = vars(args)

    basepath, output_bom_basename = kitoolkit.check_dir_and_files(kwargs['component_position_file'], kwargs['bom'], kwargs['output_folder'], kwargs['basename'])


    # Build .dpv (CharmHigh)
    k2c_args = {k:kwargs[k] for k in kwargs if k not in ['bom', 'kicad_pcb']}
    k2c_main(**k2c_args)


    # get the bom
    bom = kitoolkit.extract_bom(args.bom)


    # get the machine config
    machine_conf = kitoolkit.extract_machine_config(args.feeder_config_file, args.cuttape_config_files)

    bom_annoted = kitoolkit.tag_bom(bom, machine_conf)
    bom_annoted.save_as(os.path.join(basepath, output_bom_basename + ".xls"))

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
