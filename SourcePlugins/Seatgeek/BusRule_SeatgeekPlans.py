from Library.FunctionFiles.Functions import *

def seatgeekplans_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    runlog.log("Generate SeatGeek Plans Business Rules")
    runlog.log("")

    output_folder = f"{db_folder}ForReferenceOnly{os.sep}SEATGEEKPLANS_BusRules{os.sep}"
    seatgeekplans_delete_plan_product_id(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=1, runposition=4)
    seatgeekplans_delete_old_pk_records(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=2, runposition=4)

    return

def seatgeekplans_delete_plan_product_id(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=1, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 4_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SeatGeekPlans_{runposition}_{runorder}"
    busrule["runPosition"] = runposition
    busrule["runOrder"] = runorder


    rulequerydoc = Document()

    rulequerydoc.append("DELETE FROM STAGE.SEATGEEKPLANS")
    rulequerydoc.newline("WHERE PLAN_PRODUCT_ID IN (")
    rulequerydoc.newline("\tSELECT DISTINCT PLAN_PRODUCT_ID")
    rulequerydoc.newline("\tFROM STAGE.SEATGEEKPLANS")
    rulequerydoc.newline("\tWHERE EVENT <> 'null'")
    rulequerydoc.newline(")")
    rulequerydoc.newline("AND EVENT = 'null';")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SEATGEEKPLANS_{runposition}_{runorder} DELETE STAGE.SEATGEEKPLANS_PLAN_PRODUCT_ID RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return


def seatgeekplans_delete_old_pk_records(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder: int = 2, runposition: int = 4):
    # ----------------------------------------------------------------
    # Rule 4_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SeatGeekPlans_{runposition}_{runorder}"
    busrule["runPosition"] = runposition
    busrule["runOrder"] = runorder

    rulequerydoc = Document()

    rulequerydoc.append("DELETE FROM STAGE.SEATGEEKPLANS")
    rulequerydoc.newline("WHERE (PLAN_PRODUCT_ID, EVENT, DWUPDATEDATE) NOT IN")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\tPLAN_PRODUCT_ID,")
    rulequerydoc.newline("\t\tEVENT,")
    rulequerydoc.newline("\t\tMAX(DWUPDATEDATE)")
    rulequerydoc.newline("\tFROM STAGE.SEATGEEKPLANS")
    rulequerydoc.newline("\tGROUP BY")
    rulequerydoc.newline("\t\tPLAN_PRODUCT_ID,")
    rulequerydoc.newline("\t\tEVENT")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SEATGEEKPLANS_{runposition}_{runorder} DELETE STAGE.SEATGEEKPLANS_OLD_PK_RECORDS RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return