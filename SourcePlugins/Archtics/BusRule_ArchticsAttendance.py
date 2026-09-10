from Library.FunctionFiles.Functions import *

def archticsattendance_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics Attendance
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsAttendance_BusRules{os.sep}"
    runlog.log("Generate Archtics Attendance Business Rules.")
    runlog.log("")

    archticsattendance_1_0(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsattendance_1_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsattendance_1_2(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsattendance_2_2(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsattendance_3_2(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticsattendance_1_0(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_0
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAttendance_1_0"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 0

    rulequerydoc = Document()

    rulequerydoc.append("DELETE FROM &database.import.archticsattendance")
    rulequerydoc.newline("WHERE filedate <> (")
    rulequerydoc.newline("\tSELECT max(filedate)")
    rulequerydoc.newline("\tFROM &database.import.archticsattendance")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsAttendance_1_0 DELETE IMPORT.ARCHTICSATTENDANCE RULE QUERY.sql",content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsattendance_1_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAttendance_1_1"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 1

    rulequerydoc = Document()
    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSATTENDANCE AS")
    rulequerydoc.newline("SELECT\n\tFILEDATE,\n\tFILENAME,\n\tFILEROWNUMBER,")

    # add columns
    for col in col_list:
        # add custom logic for SCANTIME
        if col[1].upper() == "SCANTIME":
            rulequerydoc.newline("\tCASE")
            rulequerydoc.newline("\t\tWHEN TRIM(SCANTIME,':') REGEXP '[0-9]:[0-9][0-9]'")
            rulequerydoc.newline("\t\tTHEN")
            rulequerydoc.newline("\t\t\tCASE")
            rulequerydoc.newline("\t\t\t\tWHEN LEFT('0' || TRIM(SCANTIME,':'),1) = 0 AND SUBSTR('0' || TRIM(SCANTIME,':'), 2, 1) BETWEEN 0 AND 4")
            rulequerydoc.newline("\t\t\t\tTHEN CAST(CAST(DATEADD(DAY, 1, EVENTDATE) AS DATE) || ' ' || '0' || TRIM(SCANTIME,':') || ':00' AS TIMESTAMP_LTZ)")
            rulequerydoc.newline("\t\t\t\tELSE CAST(EVENTDATE || ' ' || '0' || TRIM(SCANTIME,':') || ':00' AS TIMESTAMP_LTZ)")
            rulequerydoc.newline("\t\t\tEND")
            rulequerydoc.newline("\t\tWHEN LEFT(TRIM(SCANTIME,':'),1) = 0 AND SUBSTR(TRIM(SCANTIME,':'), 2, 1) BETWEEN 0 AND 4")
            rulequerydoc.newline("\t\tTHEN CAST(CAST(DATEADD(DAY, 1, EVENTDATE) AS DATE) || ' ' || TRIM(SCANTIME,':') || ':00' AS TIMESTAMP_LTZ)")
            rulequerydoc.newline("\t\tELSE CAST(EVENTDATE || ' ' || TRIM(SCANTIME,':') || ':00' AS TIMESTAMP_LTZ)")
            rulequerydoc.newline("\tEND AS SCANTIME,")
        else:
            rulequerydoc.newline(f"\t{col[1]},")

    rulequerydoc.trimend(1)
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSATTENDANCE;")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsAttendance_1_1 CREATE TMP.ARCHTICSATTENDANCE RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsattendance_1_2(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAttendance_1_2"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 2
    busrule["ruleQuery"] = "CREATE OR REPLACE TABLE &database.TMP.ARCHTICSATTENDANCEWORKTABLE AS SELECT * FROM &database.TMP.ARCHTICSATTENDANCEUNIQUE;"

    bus_rule_obj.add_rule(busrule)

    return

def archticsattendance_2_2(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 2_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAttendance_2_2"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 2

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSATTENDANCECUSTOMERNAMEID AS")
    rulequerydoc.newline("SELECT")

    for key in pk:
        rulequerydoc.newline(f"\tT.{key},")

    rulequerydoc.newline("\tC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\tC.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.TMP.ARCHTICSATTENDANCEWORKTABLE T")
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
    rulequerydoc.newline("\t\t\t\tCASE")
    rulequerydoc.newline("\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'primary' THEN 1")
    rulequerydoc.newline("\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'secondary' THEN 2")
    rulequerydoc.newline("\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'other' THEN 3")
    rulequerydoc.newline("\t\t\t\t\tELSE 4")
    rulequerydoc.newline("\t\t\t\tEND ASC")
    rulequerydoc.newline("\t\t\t) ROWNUMBER")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSCUSTOMERS AC) SUB")
    rulequerydoc.newline("\tWHERE SUB.ROWNUMBER = 1) C")
    rulequerydoc.newline("ON T.ACCOUNTID = C.ACCOUNTID;")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsAttendance_2_2 CREATE TMP.ARCHTICSATTENDANCECUSTOMERNAMEID RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsattendance_3_2(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 3_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsAttendance_3_2"
    busrule["runOrder"] = 3
    busrule["runPosition"] = 2

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSATTENDANCEUNIQUE AS")
    rulequerydoc.newline("SELECT T.*, C.CUSTOMERNAMEID, C.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.TMP.ARCHTICSATTENDANCEWORKTABLE T")
    rulequerydoc.newline("INNER JOIN &database.TMP.ARCHTICSATTENDANCECUSTOMERNAMEID C")
    rulequerydoc.newline("ON")
    for key in pk:
        rulequerydoc.newline(f"T.{key} = C.{key} AND")

    rulequerydoc.trimend(4)
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsAttendance_3_2 CREATE TMP.ARCHTICSATTENDANCEUNIQUE RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return