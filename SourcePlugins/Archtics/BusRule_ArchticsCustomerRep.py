from Library.FunctionFiles.Functions import *

def archticscustomerrep_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics CustomerRep
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsCustomerRep_BusRules{os.sep}"
    runlog.log("Generate Archtics CustomerRep Business Rules.")
    runlog.log("")

    archticscustomerrep_1_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomerrep_2_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticscustomerrep_1_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):


    return

def archticscustomerrep_1_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomerRep_1_1"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 1

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSCUSTOMERREPCUSTOMERNAMEID AS")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tT.ACCOUNTID,")
    rulequerydoc.newline("\tT.REPACCOUNTID,")
    rulequerydoc.newline("\tT.REPCUSTOMERNAMEID,")
    rulequerydoc.newline("\tT.REPACCOUNTTYPE,")
    rulequerydoc.newline("\tC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\tC.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSCUSTOMERREP T")
    rulequerydoc.newline("LEFT JOIN (")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\tACCOUNTID,")
    rulequerydoc.newline("\t\tRAWAUDIENCEID,")
    rulequerydoc.newline("\t\tCUSTOMERNAMEID")
    rulequerydoc.newline("\tFROM (")
    rulequerydoc.newline("\t\tSELECT")
    rulequerydoc.newline("\t\t\tAC.ACCOUNTID,")
    rulequerydoc.newline("\t\t\tAC.RAWAUDIENCEID,")
    rulequerydoc.newline("\t\t\tAC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\t\t\tROW_NUMBER() OVER (")
    rulequerydoc.newline("\t\t\t\tPARTITION BY ACCOUNTID")
    rulequerydoc.newline("\t\t\t\tORDER BY")
    rulequerydoc.newline("\t\t\t\t\tUPDATEDATETIME DESC,")
    rulequerydoc.newline("\t\t\t\t\tCASE")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'primary' THEN 1")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'secondary' THEN 2")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'other' THEN 3")
    rulequerydoc.newline("\t\t\t\t\t\tELSE 4")
    rulequerydoc.newline("\t\t\t\t\tEND ASC")
    rulequerydoc.newline("\t\t\t) ROWNUMBER")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("\t) SUB")
    rulequerydoc.newline("\tWHERE SUB.ROWNUMBER = 1")
    rulequerydoc.newline(") C")
    rulequerydoc.newline("ON T.ACCOUNTID = C.ACCOUNTID")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomerRep_1_1 CREATE TMP.ARCHTICSCUSTOMERREPCUSTOMERNAMEID RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomerrep_2_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 2_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomerRep_2_1"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 1

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSCUSTOMERREPCUSTOMERNAMEIDJOINED AS")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tT.*,")
    rulequerydoc.newline("\tC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\tC.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSCUSTOMERREP T")
    rulequerydoc.newline("INNER JOIN &database.TMP.ARCHTICSCUSTOMERREPCUSTOMERNAMEID C")
    rulequerydoc.newline("\tON T.ACCOUNTID = C.ACCOUNTID")
    rulequerydoc.newline("\tAND T.REPACCOUNTID = C.REPACCOUNTID")
    rulequerydoc.newline("\tAND T.REPCUSTOMERNAMEID = C.REPCUSTOMERNAMEID")
    rulequerydoc.newline("\tAND T.REPACCOUNTTYPE = C.REPACCOUNTTYPE")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomerRep_2_1 CREATE TMP.ARCHTICSCUSTOMERREPCUSTOMERNAMEIDJOINED RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return