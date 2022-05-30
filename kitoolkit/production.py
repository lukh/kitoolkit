"""Main module."""
import sys
import os
import pyexcel
import logging
import datetime


def check_dir_and_files(component_position_file, bom_file, output_folder, basename, dir_exist_ok):
    # basic file verification
    if not os.path.isfile(component_position_file):
        logging.error("{} is not an existing file".format(component_position_file))
        sys.exit(-1)

    if not os.path.isfile(bom_file):
        logging.error("{} is not an existing file".format(component_position_file))
        sys.exit(-1)


    if output_folder is None:
        basepath = os.path.dirname(os.path.abspath(component_position_file))
    else:
        basepath = output_folder

    if os.path.isdir(basepath) and not dir_exist_ok:
        logging.warning("{} is an existing dir, cancelling,".format(basepath))
        sys.exit(0)

    os.makedirs(os.path.join(basepath), exist_ok=dir_exist_ok)

    if basename is None:
        basename = "{date}-{basename}".format(date=datetime.datetime.now().strftime("%Y%m%d-%H%M%S"), basename=os.path.splitext(os.path.basename(bom_file))[0])

    return basepath, basename

def extract_bom(bom_file):
    bom_content = pyexcel.get_sheet(file_name=bom_file, start_row=0, delimiter=",")
    return bom_content


def extract_feeders_data(feeders_file):
    """
    returns data of the form
    [
        {"alias":["ALIAS", ...], feeder_index:X},
    ]
    """
    feeeders_data = []
    first_row = True
    for row in pyexcel.get_array(file_name=feeders_file):
        if first_row: 
            first_row = False
            continue
        cmp = row[2]
        alias = row[15]
        index = row[1]

        alias = [cmp] + alias.split(":")

        if(row[0] != "Stop"):
            feeeders_data.append({"alias":alias, "feeder_index":index})

        else:
            break

    return feeeders_data

def extract_tape_data(feeders_file):
    """
    returns data of the form
    [
        {"alias":["ALIAS", ...], feeder_index:X},
    ]
    """
    feeeders_data = []
    
    first_row = True
    for row in pyexcel.get_array(file_name=feeders_file): # skip header
        if first_row: 
            first_row = False
            continue

        cmp = row[2]
        alias = row[16]
        index = row[1]

        alias = [cmp] + alias.split(":")

        if(row[0] != "Stop"):
            feeeders_data.append({"alias":alias, "feeder_index":index})

        else:
            break

    return feeeders_data


def extract_machine_config(feeders_file, cuttape_config_files):
    machine_config = {}

    machine_config['feeders'] = extract_feeders_data(feeders_file)

    machine_config['cuttapes'] = {}
    if cuttape_config_files is not None:
        for cuttape_file in cuttape_config_files:
            cuttape = os.path.splitext(os.path.basename(cuttape_file))[0]
            machine_config['cuttapes'][cuttape] = extract_tape_data(cuttape_file)

    return machine_config


def tag_bom(bom_sheet, machine_conf):
    ID=0
    DES=3
    PACKAGE=5
    QUANTITY=6
    DESIGNATION=4

    auto_mounted_cmps = ""
    nm_cmp = ""


    append_col = bom_sheet.number_of_columns()

    assembly_mode_index = append_col
    bom_sheet.column += ["Assembly Mode"]
    cuttape_job_name = append_col + 1
    bom_sheet.column += ["Cuttape Job"]
    feeder_index_index = append_col + 2
    bom_sheet.column += ["Feeder Index"]


    def find_comp(c, confs):
        # return ID or None

        d = map(lambda feeder: feeder['feeder_index'] if cmp in feeder['alias'] else None, confs)
        fis = list(filter(lambda x: x is not None, d))

        if len(fis) > 1:
            raise Exception(f"More than one feeder found for {c}")

        elif len(fis) == 1:
            return fis[0]

        return None


    first_row = True
    for row in bom_sheet:
        if first_row:
            first_row = False
            continue
    
        if not isinstance(row[ID], int):
            break

        cmp = row[DESIGNATION] + "-" + row[PACKAGE]

        row[assembly_mode_index] = 'Manual'

        fid = find_comp(cmp, machine_conf['feeders'])
        if fid is not None:
            row[assembly_mode_index] = 'Feeder'
            row[feeder_index_index] = fid

        else:
            l = [(ct, find_comp(cmp, machine_conf['cuttapes'][ct])) for ct in machine_conf['cuttapes']]
            l = filter(lambda  t: t[1] is not None, l)
            l = list(l)
            if len(l) > 1:
                raise Exception(f"More than one CutTape found for {cmp}")

            elif len(l) == 1:
                ct, fid = l[0]

                row[assembly_mode_index] = 'Cut Tape'
                row[cuttape_job_name] = ct
                row[feeder_index_index] = fid

        if row[assembly_mode_index] != 'Manual':
            auto_mounted_cmps += row[DES] + ','

        if row[DESIGNATION].find("/NM") != -1:
            row[assembly_mode_index] = 'NotMounted'
            nm_cmp += row[DES] + ','


    return bom_sheet, auto_mounted_cmps, nm_cmp
