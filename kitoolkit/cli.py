"""Console script for kitoolkit."""
import argparse
import sys
import os
import subprocess

from kicad2charmhigh import get_args_parser
from kicad2charmhigh import main as k2c_main

from . import kitoolkit

def main():
    """Console script for kitoolkit."""
    parser = get_args_parser()

    parser.add_argument('bom', type=str, help='Kicad BOM File')
    parser.add_argument('--kicad-pcb', type=str, help='Kicad PCB File to generate InteractiveBom')
    parser.add_argument('--dir-exist-ok', action="store_true", help="Do not fail if the directory exists")
    
    args = parser.parse_args()

    kwargs = vars(args)

    basepath, output_bom_basename = kitoolkit.check_dir_and_files(kwargs['component_position_file'], kwargs['bom'], kwargs['output_folder'], kwargs['basename'], kwargs['dir_exist_ok'])


    # Build .dpv (CharmHigh)
    k2c_args = {k:kwargs[k] for k in kwargs if k not in ['bom', 'kicad_pcb', 'dir_exist_ok']}
    k2c_main(**k2c_args)


    # get the bom
    bom = kitoolkit.extract_bom(args.bom)


    # get the machine config
    machine_conf = kitoolkit.extract_machine_config(args.feeder_config_file, args.cuttape_config_files)

    bom_annoted, auto_mounted_cmps, nm_cmps = kitoolkit.tag_bom(bom, machine_conf)
    bom_annoted.save_as(os.path.join(basepath, output_bom_basename + ".xls"))

    # Run Interactive Bom TODO: Improve call to the tool...
    subprocess.run(["interactive_html_bom", args.kicad_pcb, '--highlight-pin1', '--no-browser', '--name-format', output_bom_basename, '--dest-dir', os.path.abspath(basepath), '--blacklist', auto_mounted_cmps + nm_cmps +"FID*"])

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
