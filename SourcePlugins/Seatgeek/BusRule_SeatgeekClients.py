from Library.FunctionFiles.Functions import *

def seatgeekclients_busrules(col_list:list, pk:list, phone_col_list:list, bus_rule_obj:object, db_folder:str, runlog:object):
    runlog.log("Generate SeatGeek Clients Business Rules")
    runlog.log("")

    output_folder = f"{db_folder}ForReferenceOnly{os.sep}SEATGEEKCLIENTS_BusRules{os.sep}"
    seatgeekclients_archive(col_list=col_list, pk=pk, phone_col_list=phone_col_list, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=1, runposition=0)
    seatgeekclients_delete_stage(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=2, runposition=0)
    seatgeekclients_delete_import(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=3, runposition=0)

    return

def seatgeekclients_archive(col_list:list, pk:list, phone_col_list:list, bus_rule_obj:object, output_folder:str, runorder:int=1, runposition:int=0):
    # ----------------------------------------------------------------
    # Rule 0_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SEATGEEKCLIENTS_{runposition}_{runorder}"
    busrule["runPosition"] = runposition
    busrule["runOrder"] = runorder

    rulequerydoc = Document()

    rulequerydoc.newline("INSERT INTO STAGE.SEATGEEKCLIENTSARCHIVE")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tFILEDATE,")
    rulequerydoc.newline("\tFILENAME,")
    rulequerydoc.newline("\tFILEROWNUMBER,")
    for col in col_list:
        rulequerydoc.newline(f"\t{col[1].upper()},")
    for phcol in phone_col_list:
        rulequerydoc.newline(f"\t{phcol}formatted,")
    rulequerydoc.newline("\tSTANDARDIZATIONROWID,")
    rulequerydoc.newline("\tRAWAUDIENCEID,")
    rulequerydoc.newline("\tDWINSERTDATE,")
    rulequerydoc.newline("\tDWUPDATEDATE")
    rulequerydoc.newline(")")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tFILEDATE,")
    rulequerydoc.newline("\tFILENAME,")
    rulequerydoc.newline("\tFILEROWNUMBER,")
    for col in col_list:
        rulequerydoc.newline(f"\t{col[1].upper()},")
    for phcol in phone_col_list:
        rulequerydoc.newline(f"\t{phcol}formatted,")
    rulequerydoc.newline("\tSTANDARDIZATIONROWID,")
    rulequerydoc.newline("\tRAWAUDIENCEID,")
    rulequerydoc.newline("\tNOW() AS DWINSERTDATE,")
    rulequerydoc.newline("\tNOW() AS DWUPDATEDATE")
    rulequerydoc.newline("FROM STAGE.SEATGEEKCLIENTS")
    rulequerydoc.newline(f"WHERE {pk[0].upper()} IN")
    rulequerydoc.newline("(")
    rulequerydoc.newline(f"\tSELECT {pk[0].upper()} FROM IMPORT.SEATGEEKCLIENTS WHERE _RINGSIDE_OPERATION = 'D'")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SEATGEEKCLIENTS_{runposition}_{runorder} ARCHIVE STAGE.SEATGEEKCLIENTS RINGSIDE D RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return


def seatgeekclients_delete_stage(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder: int = 2, runposition: int = 0):
    # ----------------------------------------------------------------
    # Rule 0_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SEATGEEKCLIENTS_{runposition}_{runorder}"
    busrule["runPosition"] = runposition
    busrule["runOrder"] = runorder

    rulequerydoc = Document()

    rulequerydoc.newline("DELETE FROM STAGE.SEATGEEKCLIENTS")
    rulequerydoc.newline(f"WHERE {pk[0].upper()} IN")
    rulequerydoc.newline("(")
    rulequerydoc.newline(f"\tSELECT {pk[0].upper()} FROM IMPORT.SEATGEEKCLIENTS WHERE _RINGSIDE_OPERATION = 'D'")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SEATGEEKCLIENTS_{runposition}_{runorder} DELETE STAGE.SEATGEEKCLIENTS RINGSIDE D RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def seatgeekclients_delete_import(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder: int = 3, runposition: int = 0):
    # ----------------------------------------------------------------
    # Rule 0_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SEATGEEKCLIENTS_{runposition}_{runorder}"
    busrule["runPosition"] = runposition
    busrule["runOrder"] = runorder

    rulequerydoc = Document()

    rulequerydoc.newline("DELETE FROM IMPORT.SEATGEEKCLIENTS")
    rulequerydoc.newline("WHERE _RINGSIDE_OPERATION = 'D';")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SEATGEEKCLIENTS_{runposition}_{runorder} DELETE IMPORT.SEATGEEKCLIENTS RINGSIDE D RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return