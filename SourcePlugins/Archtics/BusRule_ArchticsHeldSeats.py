from Library.FunctionFiles.Functions import *

def archticsheldseats_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics Heldseats
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsHeldSeats_BusRules{os.sep}"
    runlog.log("Generate Archtics Held Seats Business Rules.")
    runlog.log("")

    archticsheldseats_1_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsheldseats_2_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsheldseats_5_3(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsheldseats_6_3(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsheldseats_1_4(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsheldseats_2_4(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticsheldseats_1_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsHeldSeats_1_1"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 1

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSHELDSEATSCUSTOMERNAMEID AS")
    rulequerydoc.newline("SELECT")

    for key in pk:
        rulequerydoc.newline(f"\tT.{key},")

    rulequerydoc.newline("\tC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\tC.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSHELDSEATS T")
    rulequerydoc.newline("LEFT JOIN(")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\tACCOUNTID,")
    rulequerydoc.newline("\t\tCUSTOMERNAMEID,")
    rulequerydoc.newline("\t\tRAWAUDIENCEID")
    rulequerydoc.newline("\tFROM (")
    rulequerydoc.newline("\t\tSELECT")
    rulequerydoc.newline("\t\t\tAC.ACCOUNTID,")
    rulequerydoc.newline("\t\t\tAC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\t\t\tAC.RAWAUDIENCEID,")
    rulequerydoc.newline("\t\t\tROW_NUMBER() OVER (")
    rulequerydoc.newline("\t\t\t\tPARTITION BY ACCOUNTID ORDER BY UPDATEDATETIME DESC,")
    rulequerydoc.newline("\t\t\t\t\tCASE")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'primary' THEN 1")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'secondary' THEN 2")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'other' THEN 3")
    rulequerydoc.newline("\t\t\t\t\t\tELSE 4")
    rulequerydoc.newline("\t\t\t\t\tEND ASC")
    rulequerydoc.newline("\t\t\t) ROWNUMBER")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSCUSTOMERS AC) SUB")
    rulequerydoc.newline("\t\tWHERE SUB.ROWNUMBER = 1")
    rulequerydoc.newline("\t) C")
    rulequerydoc.newline("ON T.ACCOUNTID = C.ACCOUNTID;")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsHeldSeats_1_1 CREATE TMP.ARCHTICSHELDSEATSCUSTOMERNAMEID RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsheldseats_2_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 2_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsHeldSeats_2_1"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 1

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSHELDSEATSCUSTOMERNAMEIDJOINED AS")
    rulequerydoc.newline("SELECT T.*, C.CUSTOMERNAMEID, C.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSHELDSEATS T")
    rulequerydoc.newline("INNER JOIN &database.TMP.ARCHTICSHELDSEATSCUSTOMERNAMEID C")
    rulequerydoc.newline("ON")

    for key in pk:
        rulequerydoc.newline(f"T.{key} = C.{key} AND")

    rulequerydoc.trimend(4)
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsHeldSeats_2_1 CREATE TMP.ARCHTICSHELDSEATSCUSTOMERNAMEIDJOINED RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsheldseats_5_3(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 5_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsHeldSeats_5_3"
    busrule["runOrder"] = 5
    busrule["runPosition"] = 3

    rulequerydoc = Document()

    pk_string = create_pk_string(pk)

    rulequerydoc.append("INSERT INTO &database.TMP.HELDSEATS_DELETES")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tS.*,")
    rulequerydoc.newline("\tCURRENT_TIMESTAMP() as DELETEDATETIME")
    rulequerydoc.newline("FROM &database.STAGE.ARCHTICSHELDSEATS S")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline(pk_string)
    rulequerydoc.newline("NOT IN (")
    rulequerydoc.newline("\tSELECT DISTINCT")
    rulequerydoc.newline(f"\t\t{pk_string}")
    rulequerydoc.newline("\tFROM &database.IMPORT.ARCHTICSHELDSEATS I")
    rulequerydoc.newline(")")
    rulequerydoc.newline("AND S.EVENTID IN (")
    rulequerydoc.newline("\tSELECT DISTINCT EVENTID FROM &database.IMPORT.ARCHTICSHELDSEATS I")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsHeldSeats_5_3 INSERT INTO TMP.HELDSEATS_DELETES RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsheldseats_6_3(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 6_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsHeldSeats_6_3"
    busrule["runOrder"] = 6
    busrule["runPosition"] = 3

    rulequerydoc = Document()

    pk_string = create_pk_string(pk)

    rulequerydoc.append("DELETE FROM &database.STAGE.ARCHTICSHELDSEATS S")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline(f"\t{pk_string}")
    rulequerydoc.newline("NOT IN (")
    rulequerydoc.newline("\tSELECT DISTINCT")
    rulequerydoc.newline(f"\t{pk_string}")
    rulequerydoc.newline("\tFROM &database.IMPORT.ARCHTICSHELDSEATS I")
    rulequerydoc.newline(")")
    rulequerydoc.newline("AND S.EVENTID IN (")
    rulequerydoc.newline("\tSELECT DISTINCT EVENTID FROM &database.IMPORT.ARCHTICSHELDSEATS I")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsHeldSeats_6_3 DELETE FROM STAGE.ARCHTICSHELDSEATS RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsheldseats_1_4(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsHeldSeats_1_4"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSHELDSEATSSNAPSHOT AS")
    rulequerydoc.newline("SELECT SHA2(")

    for col in col_list:
        rulequerydoc.newline(f"\tIFNULL(TO_CHAR({col[1]}),'') ||'_'||")

    rulequerydoc.trimend(8)
    rulequerydoc.newline(", 512) AS HELDSEATSHASH, *")
    rulequerydoc.newline("FROM &database.STAGE.ARCHTICSHELDSEATS;")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsHeldSeats_1_4 CREATE TMP.ARCHTICSHELDSEATSSNAPSHOT RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsheldseats_2_4(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 2_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsHeldSeats_2_4"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    rulequerydoc.append("MERGE INTO &database.STAGE.ARCHTICSHELDSEATSSNAPSHOT DEST")
    rulequerydoc.newline("USING (")
    rulequerydoc.newline("\tSELECT HS.*")
    rulequerydoc.newline("\tFROM &database.TMP.ARCHTICSHELDSEATSSNAPSHOT HS")
    rulequerydoc.newline("\tLEFT JOIN &database.STAGE.ARCHTICSEVENTS B")
    rulequerydoc.newline("\tON HS.EVENTID = B.EVENTID")
    rulequerydoc.newline("\tWHERE B.EVENTDATE >= DATEADD('day', -7, current_date())")
    rulequerydoc.newline(") SOR")
    rulequerydoc.newline("ON DEST.HELDSEATSHASH = SOR.HELDSEATSHASH")
    rulequerydoc.newline("WHEN MATCHED THEN UPDATE SET")
    rulequerydoc.newline("\tDEST.HELDSEATSRUNDATETIMETO = current_timestamp(),")
    rulequerydoc.newline("\tDEST.FILEDATE = SOR.FILEDATE,")
    rulequerydoc.newline("\tDEST.FILENAME = SOR.FILENAME,")
    rulequerydoc.newline("\tDEST.FILEROWNUMBER = SOR.FILEROWNUMBER,")
    rulequerydoc.newline("\tDEST.DWINSERTDATE = SOR.DWINSERTDATE,")
    rulequerydoc.newline("\tDEST.DWUPDATEDATE = SOR.DWUPDATEDATE")
    rulequerydoc.newline("WHEN NOT MATCHED THEN INSERT (")
    rulequerydoc.newline("\tDEST.HELDSEATSHASH,")
    rulequerydoc.newline("\tDEST.HELDSEATSRUNDATETIMEFROM,")
    rulequerydoc.newline("\tDEST.HELDSEATSRUNDATETIMETO,")
    rulequerydoc.newline("\tDEST.FILEDATE,")
    rulequerydoc.newline("\tDEST.FILENAME,")
    rulequerydoc.newline("\tDEST.FILEROWNUMBER,")

    for col in col_list:
        rulequerydoc.newline(f"\tDEST.{col[1]},")

    rulequerydoc.newline("\tDEST.DWINSERTDATE,")
    rulequerydoc.newline("\tDEST.DWUPDATEDATE")
    rulequerydoc.newline(") VALUES (")
    rulequerydoc.newline("\tSOR.HELDSEATSHASH,")
    rulequerydoc.newline("\tCURRENT_TIMESTAMP(),")
    rulequerydoc.newline("\tCURRENT_TIMESTAMP(),")
    rulequerydoc.newline("\tSOR.FILEDATE,")
    rulequerydoc.newline("\tSOR.FILENAME,")
    rulequerydoc.newline("\tSOR.FILEROWNUMBER,")

    for col in col_list:
        rulequerydoc.newline(f"\tSOR.{col[1]},")

    rulequerydoc.newline("\tSOR.DWINSERTDATE,")
    rulequerydoc.newline("\tSOR.DWUPDATEDATE")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsHeldSeats_2_4 MERGE INTO STAGE.ARCHTICSHELDSEATSSNAPSHOT RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return