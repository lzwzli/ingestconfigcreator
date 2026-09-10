from Library.FunctionFiles.Functions import *
from SourcePlugins.Dynamics.StandardizationColumns import *
from SourcePlugins.Dynamics.RawAudienceArchiveColumns import *

def dynamicsaccount_busrules(col_list:list, pk:list, rawaud_ind:int, bus_rule_obj:object, db_folder:str, runlog:object):
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}DynamicsAccount_BusRules{os.sep}"
    runlog.log("Generate Dynamics Account Business Rules.")
    runlog.log("")

    dynamicsaccount_merge_archive(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=1, runposition=4)
    dynamicsaccount_delete_stage(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=2, runposition=4)

    return

def dynamicsaccount_merge_archive(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=4, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 4_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"DynamicsAccount_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("MERGE INTO STAGE.DYNAMICSACCOUNTARCHIVE dest")
    rulequerydoc.newline("USING (")
    rulequerydoc.newline("\tSELECT da.*")
    rulequerydoc.newline("\tFROM STAGE.DYNAMICSACCOUNT da")
    rulequerydoc.newline("\tWHERE")
    rulequerydoc.newline("\t\tda.STATECODE = 1")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(da.MASTERID),'')")
    rulequerydoc.newline(") src")
    rulequerydoc.newline("ON dest.ACCOUNTID = src.ACCOUNTID")
    rulequerydoc.newline("WHEN NOT MATCHED THEN INSERT (")

    insert_cols = [["", "FILEDATE", "VARCHAR"], ["", "FILENAME", "VARCHAR"], ["", "FILEROWNUMBER", "NUMBER(38,0)"], ["", "DWINSERTDATE", "TIMESTAMP_LTZ(9)"], ["", "DWUPDATEDATE", "TIMESTAMP_LTZ(9)"]] + col_list

    for col in insert_cols:
        rulequerydoc.newline(f"\t{col[1]},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline(")")
    rulequerydoc.newline("VALUES (")

    for col in insert_cols:
        rulequerydoc.newline(f"\tsrc.{col[1]},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"DYNAMICSACCOUNT_{runorder}_{runposition} MERGE DYNAMICSACCOUNTARCHIVE RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def dynamicsaccount_delete_stage(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder:int=5, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 5_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"DynamicsAccount_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("DELETE FROM STAGE.DYNAMICSACCOUNT")
    rulequerydoc.newline("WHERE ACCOUNTID IN (")
    rulequerydoc.newline("\tSELECT da.ACCOUNTID")
    rulequerydoc.newline("\tFROM STAGE.DYNAMICSACCOUNT da")
    rulequerydoc.newline("\tWHERE")
    rulequerydoc.newline("\t\tda.STATECODE = 1")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(da.MASTERID),'')")
    rulequerydoc.newline("\t\tAND da.ACCOUNTID IN (")
    rulequerydoc.newline("\t\t\tSELECT DISTINCT ACCOUNTID")
    rulequerydoc.newline("\t\t\tFROM STAGE.DYNAMICSACCOUNTARCHIVE")
    rulequerydoc.newline("\t\t)")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"DYNAMICSACCOUNT_{runorder}_{runposition} DELETE FROM DYNAMICSACCOUNT RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return