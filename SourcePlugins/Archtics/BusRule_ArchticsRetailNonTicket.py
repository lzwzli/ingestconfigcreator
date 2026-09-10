from Library.FunctionFiles.Functions import *

def archticsretailnonticket_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics RetailNonTicket
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsRetailNonTicket_BusRules{os.sep}"
    runlog.log("Generate Archtics RetailNonTicket Business Rules.")
    runlog.log("")

    archticsretailnonticket_1_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsretailnonticket_2_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticsretailnonticket_1_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsRetailNonTicket_1_1"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 1

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSRETAILNONTICKETCUSTOMERNAMEID AS")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tT.HOSTEVENTNAME,")
    rulequerydoc.newline("\tT.HOSTSECTIONNAME,")
    rulequerydoc.newline("\tT.HOSTROWNAME,")
    rulequerydoc.newline("\tT.FIRSTSEAT,")
    rulequerydoc.newline("\tT.ACCOUNTID,")
    rulequerydoc.newline("\tT.ADDDATETIME,")
    rulequerydoc.newline("\tT.REFUNDFLAG,")
    rulequerydoc.newline("\tT.RETAILOPERATERTYPE,")
    rulequerydoc.newline("\tT.RETAILACCOUNTNUMBER,")
    rulequerydoc.newline("\tC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\tC.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSRETAILNONTICKET T")
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
              filename="ArchticsRetailNonTicket_1_1 CREATE TMP.ARCHTICSRETAILNONTICKETCUSTOMERNAMEID RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsretailnonticket_2_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 2_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsRetailNonTicket_2_1"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 1

    rulequerydoc = Document()

    rulequerydoc.append(
        "CREATE OR REPLACE TABLE &database.TMP.ARCHTICSRETAILNONTICKETCUSTOMERNAMEIDJOINED AS")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tT.*,")
    rulequerydoc.newline("\tC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\tC.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSRETAILNONTICKET T")
    rulequerydoc.newline("INNER JOIN &database.TMP.ARCHTICSRETAILNONTICKETCUSTOMERNAMEID C")
    rulequerydoc.newline("\tON T.HOSTEVENTNAME = C.HOSTEVENTNAME")
    rulequerydoc.newline("\tAND T.HOSTSECTIONNAME = C.HOSTSECTIONNAME")
    rulequerydoc.newline("\tAND T.HOSTROWNAME = C.HOSTROWNAME")
    rulequerydoc.newline("\tAND T.FIRSTSEAT = C.FIRSTSEAT")
    rulequerydoc.newline("\tAND T.ACCOUNTID = C.ACCOUNTID")
    rulequerydoc.newline("\tAND T.ADDDATETIME = C.ADDDATETIME")
    rulequerydoc.newline("\tAND T.REFUNDFLAG = C.REFUNDFLAG")
    rulequerydoc.newline("\tAND T.RETAILOPERATERTYPE = C.RETAILOPERATERTYPE")
    rulequerydoc.newline("\tAND T.RETAILACCOUNTNUMBER = C.RETAILACCOUNTNUMBER")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsRetailNonTicket_2_1 CREATE TMP.ARCHTICSRETAILNONTICKETCUSTOMERNAMEIDJOINED RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return