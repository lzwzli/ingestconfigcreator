from Library.FunctionFiles.Functions import *

def archticsavailableinventory_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsAvailableInventory_BusRules{os.sep}"
    runlog.log("Generate Archtics Available Inventory Business Rules.")
    runlog.log("")

    archticsavailableinventory_1_3(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsavailableinventory_2_3(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsavailableinventory_1_4(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsavailableinventory_2_4(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticsavailableinventory_1_3(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAvailableInventory_1_3"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 3

    rulequerydoc = Document()

    pk_string = create_pk_string(pk)

    rulequerydoc.append("INSERT INTO &database.TMP.AVAILINVENTORY_DELETES")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tS.*,")
    rulequerydoc.newline("\tcurrent_timestamp() as DELETEDATETIME")
    rulequerydoc.newline("FROM &database.STAGE.ARCHTICSAVAILABLEINVENTORY S")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline(pk_string)
    rulequerydoc.newline("\tNOT IN (")
    rulequerydoc.newline("\t\tSELECT DISTINCT")
    rulequerydoc.newline(f"\t\t{pk_string}")
    rulequerydoc.newline("\t\tFROM &database.IMPORT.ARCHTICSAVAILABLEINVENTORY I")
    rulequerydoc.newline("\t)")
    rulequerydoc.newline("\tAND S.EVENTID IN (")
    rulequerydoc.newline("\t\tSELECT DISTINCT EVENTID FROM &database.IMPORT.ARCHTICSAVAILABLEINVENTORY I")
    rulequerydoc.newline("\t);")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsAvailableInventory_1_3 INSERT INTO TMP.AVAILINVENTORY_DELETES RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsavailableinventory_2_3(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 2_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAvailableInventory_2_3"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 3

    rulequerydoc = Document()

    pk_string = create_pk_string(pk)

    rulequerydoc.append("DELETE FROM &database.STAGE.ARCHTICSAVAILABLEINVENTORY S")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline(f"\t{pk_string}")
    rulequerydoc.newline("NOT IN (")
    rulequerydoc.newline("\tSELECT DISTINCT")
    rulequerydoc.newline(f"\t\t{pk_string}")
    rulequerydoc.newline("\tFROM &database.IMPORT.ARCHTICSAVAILABLEINVENTORY I")
    rulequerydoc.newline(")")
    rulequerydoc.newline("AND S.EVENTID IN (")
    rulequerydoc.newline("\tSELECT DISTINCT EVENTID FROM &database.IMPORT.ARCHTICSAVAILABLEINVENTORY I")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsAvailableInventory_2_3 DELETE FROM STAGE.ARCHTICSAVAILABLEINVENTORY RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsavailableinventory_1_4(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 1_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAvailableInventory_1_4"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSAVAILABLEINVENTORYSNAPSHOT AS")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tSHA2(")

    for col in col_list:
        rulequerydoc.newline(f"\t\tIFNULL(TO_CHAR({col[1]}),'') ||'_'||")

    rulequerydoc.trimend(8)
    rulequerydoc.newline("\t, 512) AS INVENTORYHASH,")
    rulequerydoc.newline("\t*")
    rulequerydoc.newline("FROM &database.STAGE.ARCHTICSAVAILABLEINVENTORY;")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsAvailableInventory_1_4 CREATE TMP.ARCHTICSAVAILABLEINVENTORYSNAPSHOT RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsavailableinventory_2_4(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 2_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAvailableInventory_2_4"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    rulequerydoc.append("MERGE INTO &database.STAGE.ARCHTICSAVAILABLEINVENTORYSNAPSHOT DEST")
    rulequerydoc.newline("USING (")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\tAI.*")
    rulequerydoc.newline("\tFROM")
    rulequerydoc.newline("\t\t&database.TMP.ARCHTICSAVAILABLEINVENTORYSNAPSHOT AI")
    rulequerydoc.newline("\tLEFT JOIN")
    rulequerydoc.newline("\t\t&database.STAGE.ARCHTICSEVENTS B")
    rulequerydoc.newline("\tON AI.EVENTID = B.EVENTID")
    rulequerydoc.newline("\tWHERE B.EVENTDATE >= DATEADD('day', -7, current_date())")
    rulequerydoc.newline(") SOR")
    rulequerydoc.newline("ON DEST.INVENTORYHASH = SOR.INVENTORYHASH")
    rulequerydoc.newline("WHEN MATCHED THEN UPDATE SET")
    rulequerydoc.newline("\tDEST.INVENTORYRUNDATETIMETO = current_timestamp(),")
    rulequerydoc.newline("\tDEST.FILEDATE = SOR.FILEDATE,")
    rulequerydoc.newline("\tDEST.FILENAME = SOR.FILENAME,")
    rulequerydoc.newline("\tDEST.FILEROWNUMBER = SOR.FILEROWNUMBER,")
    rulequerydoc.newline("\tDEST.DWINSERTDATE = SOR.DWINSERTDATE,")
    rulequerydoc.newline("\tDEST.DWUPDATEDATE = SOR.DWUPDATEDATE")
    rulequerydoc.newline("WHEN NOT MATCHED THEN INSERT (")
    rulequerydoc.newline("\tDEST.INVENTORYHASH,")
    rulequerydoc.newline("\tDEST.INVENTORYRUNDATETIMEFROM,")
    rulequerydoc.newline("\tDEST.INVENTORYRUNDATETIMETO,")
    rulequerydoc.newline("\tDEST.FILEDATE,")
    rulequerydoc.newline("\tDEST.FILENAME,")
    rulequerydoc.newline("\tDEST.FILEROWNUMBER,")

    for col in col_list:
        rulequerydoc.newline(f"\tDEST.{col[1]},")

    rulequerydoc.newline("\tDEST.DWINSERTDATE,")
    rulequerydoc.newline("\tDEST.DWUPDATEDATE")
    rulequerydoc.newline(") VALUES (")
    rulequerydoc.newline("\tSOR.INVENTORYHASH,")
    rulequerydoc.newline("\tcurrent_timestamp(),")
    rulequerydoc.newline("\tcurrent_timestamp(),")
    rulequerydoc.newline("\tSOR.FILEDATE,")
    rulequerydoc.newline("\tSOR.FILENAME,")
    rulequerydoc.newline("\tSOR.FILEROWNUMBER,")

    for col in col_list:
        rulequerydoc.newline(f"\tSOR.{col[1]},")

    rulequerydoc.newline("\tSOR.DWINSERTDATE,")
    rulequerydoc.newline("\tSOR.DWUPDATEDATE")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsAvailableInventory_2_4 MERGE INTO STAGE.ARCHTICSAVAILABLEINVENTORYSNAPSHOT RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return