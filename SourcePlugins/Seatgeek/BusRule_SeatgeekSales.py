from Library.FunctionFiles.Functions import *

def seatgeeksales_busrules(col_list:list, pk:list, phone_col_list:list, bus_rule_obj:object, db_folder:str, runlog:object):
    runlog.log("Generate SeatGeek Payments Business Rules")
    runlog.log("")

    output_folder = f"{db_folder}ForReferenceOnly{os.sep}SEATGEEKSALES_BusRules{os.sep}"
    seatgeeksales_archive(col_list=col_list, pk=pk, phone_col_list=phone_col_list, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=1, runposition=0)
    seatgeeksales_delete_stage(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=2, runposition=0)
    seatgeeksales_delete_import(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=3, runposition=0)

    return

def seatgeeksales_archive(col_list:list, pk:list, phone_col_list:list, bus_rule_obj:object, output_folder:str, runorder:int=1, runposition:int=0):
    # ----------------------------------------------------------------
    # Rule 0_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SEATGEEKSALES_{runposition}_{runorder}"
    busrule["runPosition"] = runposition
    busrule["runOrder"] = runorder

    rulequerydoc = Document()

    rulequerydoc.newline("INSERT INTO STAGE.SEATGEEKSALESARCHIVE")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tFILEDATE,")
    rulequerydoc.newline("\tFILENAME,")
    rulequerydoc.newline("\tFILEROWNUMBER,")
    for col in col_list:
        rulequerydoc.newline(f"\t{col[1].upper()},")
    for phcol in phone_col_list:
        rulequerydoc.newline(f"\t{phcol}formatted,")
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
    rulequerydoc.newline("\tNOW() AS DWINSERTDATE,")
    rulequerydoc.newline("\tNOW() AS DWUPDATEDATE")
    rulequerydoc.newline("FROM STAGE.SEATGEEKSALES")
    rulequerydoc.newline(f"WHERE {pk[0].upper()} IN")
    rulequerydoc.newline("(")
    rulequerydoc.newline(f"\tSELECT {pk[0].upper()} FROM IMPORT.SEATGEEKSALES WHERE _RINGSIDE_OPERATION = 'D'")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SEATGEEKSALES_{runposition}_{runorder} ARCHIVE STAGE.SEATGEEKSALES RINGSIDE D RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return


def seatgeeksales_delete_stage(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder: int = 2, runposition: int = 0):
    # ----------------------------------------------------------------
    # Rule 0_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SEATGEEKSALES_{runposition}_{runorder}"
    busrule["runPosition"] = runposition
    busrule["runOrder"] = runorder

    rulequerydoc = Document()

    rulequerydoc.newline("DELETE FROM STAGE.SEATGEEKSALES")
    rulequerydoc.newline(f"WHERE {pk[0].upper()} IN")
    rulequerydoc.newline("(")
    rulequerydoc.newline(f"\tSELECT {pk[0].upper()} FROM IMPORT.SEATGEEKSALES WHERE _RINGSIDE_OPERATION = 'D'")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SEATGEEKSALES_{runposition}_{runorder} DELETE STAGE.SEATGEEKSALES RINGSIDE D RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def seatgeeksales_delete_import(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder: int = 3, runposition: int = 0):
    # ----------------------------------------------------------------
    # Rule 0_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SEATGEEKSALES_{runposition}_{runorder}"
    busrule["runPosition"] = runposition
    busrule["runOrder"] = runorder

    rulequerydoc = Document()

    rulequerydoc.newline("DELETE FROM IMPORT.SEATGEEKSALES")
    rulequerydoc.newline("WHERE _RINGSIDE_OPERATION = 'D';")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SEATGEEKSALES_{runposition}_{runorder} DELETE IMPORT.SEATGEEKSALES RINGSIDE D RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return