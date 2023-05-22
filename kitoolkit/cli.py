"""Console script for kitoolkit."""
import argparse
import sys
import os
import subprocess

from kicad2charmhigh import set_args_parser as k2c_set_args_parser
from kicad2charmhigh import main as k2c_main

from . import production

def run_production(args):
    basepath, output_bom_basename = production.check_dir_and_files(args.component_position_file, args.bom, args.output_folder, args.basename, args.dir_exist_ok)


    # Build .dpv (CharmHigh)
    kwargs = vars(args)
    k2c_args = {k:kwargs[k] for k in kwargs if k not in ['bom', 'kicad_pcb', 'dir_exist_ok', 'cmd']}
    k2c_main(**k2c_args)


    # get the bom
    bom = production.extract_bom(args.bom)


    # get the machine config
    machine_conf = production.extract_machine_config(args.feeder_config_file, args.cuttape_config_files)

    bom_annoted, auto_mounted_cmps, nm_cmps = production.tag_bom(bom, machine_conf)
    bom_annoted.save_as(os.path.join(basepath, output_bom_basename + ".xls"))

    with open(os.path.join(basepath, output_bom_basename + ".mounted"), 'w') as fd:
        fd.write(auto_mounted_cmps)
    with open(os.path.join(basepath, output_bom_basename + ".not_mounted"), 'w') as fd:
        fd.write(nm_cmps)

    # Run Interactive Bom TODO: Improve call to the tool...
    if args.kicad_pcb:
        os.environ['INTERACTIVE_HTML_BOM_NO_DISPLAY'] = '1'
        subprocess.run(["generate_interactive_bom.py", args.kicad_pcb, '--highlight-pin1', '--no-browser', '--name-format', output_bom_basename, '--dest-dir', os.path.abspath(basepath), '--blacklist', auto_mounted_cmps + nm_cmps +"FID*"])


def main():
    """Console script for kitoolkit."""

    # top lvl parser
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help', dest='cmd')

    # production parser
    prod_parser = subparsers.add_parser("prod", help="...")

    k2c_set_args_parser(prod_parser)

    prod_parser.add_argument('bom', type=str, help='Kicad BOM File')
    prod_parser.add_argument('--kicad-pcb', type=str, help='Kicad PCB File to generate InteractiveBom')
    prod_parser.add_argument('--dir-exist-ok', action="store_true", help="Do not fail if the directory exists")

    # inventree 
    inventree_subparser = subparsers.add_parser('inventree', help='...')
    inventree_subparsers = inventree_subparser.add_subparsers(help="Inventree related cmds", dest='inventree_cmd')
    # - add parts
    inventree_add = inventree_subparsers.add_parser("add_parts", help='Add Parts from MPN to inventree, data from OctoPart')
    # - add parts from BOMs
    inventree_add_from_bom = inventree_subparsers.add_parser("add_parts_from_bom", help='Add Parts from MPN to inventree, data from OctoPart, using an existing KiCAD BoM')
    inventree_add_from_bom.add_argument("bom", type=str, help='Kicad BOM File')
    # - generate BoM from Kicad 
    # ...
    # - generate basket from PO...
    # ...
    
    args = parser.parse_args()


    # run prod script
    if args.cmd == "prod":
        run_production(args)

    if args.cmd == "inventree":
        if args.inventree_cmd == 'add_parts':
            pass
        elif args.inventree_cmd == 'add_parts_from_bom':
            pass



if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
