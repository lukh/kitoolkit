"""Main module."""
import os
import pyexcel



def extract_bom(bom_file):
    return pyexcel.get_sheet(file_name=bom_file, start_row=0, delimiter=";")


def extract_feeders_data(feeders_file):
    """
    returns data of the form
    [
        {"alias":["ALIAS", ...], feeder_index:X},
    ]
    """
    feeeders_data = []
    for row in pyexcel.get_array(file_name=feeders_file, start_row=1): # skip header
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
    for row in pyexcel.get_array(file_name=feeders_file, start_row=1): # skip header
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
    for cuttape_file in cuttape_config_files:
        cuttape = os.path.splitext(os.path.basename(cuttape_file))[0]
        machine_config['cuttapes'][cuttape] = extract_tape_data(cuttape_file)

    return machine_config


def tag_bom(bom_sheet, machine_conf):
    ID=0
    DES=1
    PACKAGE=2
    QUANTITY=3
    DESIGNATION=4


    append_col = bom_sheet.number_of_columns()
    print(append_col)

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



    for row in bom_sheet:
        cmp = row[DESIGNATION] + "-" + row[PACKAGE]

        row[assembly_mode_index] = 'Manual'

        fid = find_comp(cmp, machine_conf['feeders'])
        if fid is not None:
            row[assembly_mode_index] = 'Feeder'
            row[feeder_index_index] = fid

        else:
            l = [(ct, find_comp(cmp, machine_conf['cuttapes'][ct])) for ct in machine_conf['cuttapes']]
            if len(l) > 1:
                raise Exception(f"More than one CutTape found for {cmp}")

            ct, fid = l[0]

            if fid != None:
                row[assembly_mode_index] = 'Cut Tape'
                row[cuttape_job_name] = ct
                row[feeder_index_index] = fid

    print(bom_sheet)
