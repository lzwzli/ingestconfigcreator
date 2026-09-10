from Library.FunctionFiles.Functions import *
from SourcePlugins.Archtics.ArchticsTicketExpandedColumns import *

def archticsticketexpanded_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics TicketExpanded
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsTicketExpanded_BusRules{os.sep}"
    runlog.log("Generate Archtics TicketExpanded Business Rules.")
    runlog.log("")

    archticsticketexpanded_1_0(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsticketexpanded_1_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsticketexpanded_1_2(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsticketexpanded_2_2(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsticketexpanded_3_2(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsticketexpanded_4_2(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsticketexpanded_5_2(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticsticketexpanded_1_0(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_0
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsTicketExpanded_1_0"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 0

    rulequerydoc = Document()

    rulequerydoc.append("DELETE FROM &database.import.archticsticketexpanded")
    rulequerydoc.newline("WHERE filedate <> (")
    rulequerydoc.newline("\tSELECT max(filedate)")
    rulequerydoc.newline("\tFROM &database.import.archticsticketexpanded")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsTicketExpanded_1_0 DELETE IMPORT.ARCHTICSTICKETEXPANDED RULE QUERY.sql",content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsticketexpanded_1_1(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 1_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsTicketExpanded_1_1"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 1

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSTICKETEXPANDED AS")
    rulequerydoc.newline("SELECT SHA2(")
    rulequerydoc.newline("\tIFNULL(TO_CHAR(TE.FILEDATE), '') || '_' ||")

    for col in col_list:
        rulequerydoc.newline(f"\tIFNULL(TO_CHAR(TE.{col[1]}),'') ||'_'||")

    rulequerydoc.trimend(8)
    rulequerydoc.newline(", 512) AS KEYHASH,")
    rulequerydoc.newline("TE.*")
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSTICKETEXPANDED TE;")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsTicketExpanded_1_1 CREATE TMP.ARCHTICSTICKETEXPANDED RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)
    return

def archticsticketexpanded_1_2(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 1_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsTicketExpanded_1_2"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 2
    busrule["ruleQuery"] = "CREATE OR REPLACE TABLE &database.TMP.ARCHTICSTICKETEXPANDEDWORKTABLE AS SELECT * FROM &database.TMP.ARCHTICSTICKETEXPANDEDUNIQUE;"

    bus_rule_obj.add_rule(busrule)

    return

def archticsticketexpanded_2_2(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 2_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsTicketExpanded_2_2"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 2

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSTICKETEXPANDEDCUSTOMERNAMEID AS")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tT.KEYHASH,")
    rulequerydoc.newline("\tC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\tC.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.TMP.ARCHTICSTICKETEXPANDEDWORKTABLE T")
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
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("\t) SUB")
    rulequerydoc.newline("WHERE SUB.ROWNUMBER = 1) C")
    rulequerydoc.newline("ON T.ACCOUNTID = C.ACCOUNTID;")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsTicketExpanded_2_2 CREATE TMP.ARCHTICSTICKETEXPANDEDCUSTOMERNAMEID RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsticketexpanded_3_2(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 3_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsTicketExpanded_3_2"
    busrule["runOrder"] = 3
    busrule["runPosition"] = 2

    rulequery = "CREATE OR REPLACE TABLE &database.TMP.ARCHTICSTICKETEXPANDEDUNIQUE AS "
    rulequery += "SELECT T.*, C.CUSTOMERNAMEID, C.RAWAUDIENCEID "
    rulequery += "FROM &database.TMP.ARCHTICSTICKETEXPANDEDWORKTABLE T "
    rulequery += "INNER JOIN &database.TMP.ARCHTICSTICKETEXPANDEDCUSTOMERNAMEID C "
    rulequery += "ON T.KEYHASH = C.KEYHASH;"

    busrule["ruleQuery"] = rulequery

    bus_rule_obj.add_rule(busrule)
    return

def archticsticketexpanded_4_2(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 4_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsTicketExpanded_4_2"
    busrule["runOrder"] = 4
    busrule["runPosition"] = 2

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSTICKETEXPANDED_NEWDATA_DEDUPED AS")
    rulequerydoc.newline("WITH")

    # ATESEATS CTE
    ate_seats_cte_doc = Document()
    ate_seats_cte_doc.append("\tSELECT ATE.*, SEATS.MYCOUNT AS SEAT")
    ate_seats_cte_doc.newline("\tFROM &database.TMP.ARCHTICSTICKETEXPANDEDUNIQUE ATE")
    ate_seats_cte_doc.newline("\tINNER JOIN (")
    ate_seats_cte_doc.newline("\t\tSELECT ROW_NUMBER() OVER (PARTITION BY 1 ORDER BY 1) AS MYCOUNT")
    ate_seats_cte_doc.newline("\t\tFROM TABLE(GENERATOR(ROWCOUNT =>(SELECT 100000) ))")
    ate_seats_cte_doc.newline("\t) SEATS")
    ate_seats_cte_doc.newline("\tON SEATS.MYCOUNT <= ATE.LASTSEAT")
    ate_seats_cte_doc.newline("\tAND SEATS.MYCOUNT >= ATE.FIRSTSEAT")

    rulequerydoc.newline("ATESEATS AS (")
    rulequerydoc.newline(ate_seats_cte_doc.out())
    rulequerydoc.newline("),")

    # DUPREMOVAL CTE
    dupremoval_cte_doc = Document()
    dupremoval_cte_blockhash_nonzero_list = ["ORDERNUMBER", "ORDERLINEITEM", "ORDERLINEITEMSEQUENCE", "EVENTID",
                                             "TICKETSEQUENCEID"]
    dupremoval_cte_blockhash_eqzero_list = ["EVENTID", "SECTIONNAME", "ROWNAME", "FIRSTSEAT", "LASTSEAT",
                                            "TICKETSEQUENCEID"]
    dupremoval_cte_seathash_list = ["ORDERNUMBER", "ORDERLINEITEM", "ORDERLINEITEMSEQUENCE", "EVENTID", "SECTIONNAME",
                                    "ROWNAME", "SEAT", "TICKETSTATUS", "TICKETSEQUENCEID", "RETURNREASONDESCRIPTION",
                                    "RETURNDATETIME", "ADDDATETIME", "RAWAUDIENCEID"]
    dupremoval_cte_between_host_record_ind_col_list = ["FILEDATE", "EVENTNAME", "SECTIONNAME", "ROWNAME",
                                                       "NUMBEROFSEATS", "TICKETSTATUS", "ACCOUNTID", "CUSTOMERNAMEID",
                                                       "RAWAUDIENCEID", "UPDATEDATETIME", "SEQUENCENUMBER",
                                                       "BLOCKPURCHASEPRICE", "ORDERNUMBER", "ORDERLINEITEM",
                                                       "ORDERLINEITEMSEQUENCE", "PRICECODE", "PRICINGMETHOD",
                                                       "COMPCODE", "COMPNAME", "UPDATEUSER", "CLASSNAME",
                                                       "SELLLOCATION", "FULLPRICE", "TICKETTYPE",
                                                       "PRICECODEDESCRIPTION", "EVENTID", "PLANEVENTID",
                                                       "PLANEVENTNAME", "FIRSTSEAT", "LASTSEAT", "REPACCOUNTID",
                                                       "REPACCOUNTFULLNAME", "TRANSACTIONTYPE", "SECTIONID", "ROWID",
                                                       "PROMOCODE", "ADDDATETIME", "RENEWALINDICATOR", "RETURNREASON",
                                                       "RETURNREASONDESCRIPTION", "EXPANDEDFLAG", "DELIVERYMETHODCODE",
                                                       "DELIVERYMETHODNAME", "LEDGERID", "PRICECOMPONENTTAX",
                                                       "ORIGINALREPACCOUNTID", "TICKETSEQUENCEID", "RETURNDATETIME",
                                                       "TICKETTYPECATEGORY", "SEAT"]
    dupremoval_cte_record_ind_col_list_A = ["ORDERNUMBER", "ORDERLINEITEM", "EVENTID", "SECTIONNAME", "ROWNAME", "SEAT",
                                            "TICKETSEQUENCEID"]
    dupremoval_cte_record_ind_col_list_XR = ["ORDERNUMBER", "ORDERLINEITEM", "EVENTID", "SECTIONNAME", "ROWNAME",
                                             "SEAT", "RETURNREASONDESCRIPTION", "RETURNDATETIME", "RAWAUDIENCEID"]
    dupremoval_cte_orderupdatetime_col_list = ["ORDERNUMBER", "ORDERLINEITEM", "EVENTID", "SECTIONNAME", "ROWNAME",
                                               "SEAT"]
    dupremoval_cte_after_salessourcename_col_list = ["PAIDAMOUNT", "PRICECOMPONENTTICKET", "PRICECOMPONENTLICENSEFEE",
                                                     "PRICECOMPONENTOTHER1", "PRICECOMPONENTOTHER2",
                                                     "PRICECOMPONENTOTHER3", "PRICECOMPONENTOTHER4",
                                                     "PRICECOMPONENTOTHER5", "PRICECOMPONENTOTHER6",
                                                     "PRICECOMPONENTOTHER7", "PRICECOMPONENTOTHER8"]

    dupremoval_cte_doc.append("\tSELECT * FROM (")
    dupremoval_cte_doc.newline("\t\tSELECT CASE")
    dupremoval_cte_doc.newline("\t\t\tWHEN ATESEATS.ORDERNUMBER <> 0")
    dupremoval_cte_doc.newline("\t\t\t\tAND ATESEATS.ORDERLINEITEM <> 0")
    dupremoval_cte_doc.newline("\t\t\t\tAND ATESEATS.ORDERLINEITEMSEQUENCE <> 0")
    dupremoval_cte_doc.newline("\t\t\tTHEN")

    # DUPREMOVAL - non zero hash
    dupremoval_cte_doc.newline("\t\t\t\tSHA2(")
    dupremoval_cte_doc.newline("\t\t\t\t\t'&teamAbbr'")
    dupremoval_cte_doc.newline("\t\t\t\t\t|| '-' || 'N'")

    for col in dupremoval_cte_blockhash_nonzero_list:
        dupremoval_cte_doc.newline(f"\t\t\t\t\t|| '-' || IFNULL(TO_CHAR(ATESEATS.{col}),'')")

    dupremoval_cte_doc.newline("\t\t\t\t,512)")

    # DUPREMOVAL - zero hash
    dupremoval_cte_doc.newline("\t\t\tWHEN ATESEATS.ORDERNUMBER = 0")
    dupremoval_cte_doc.newline("\t\t\t\tAND ATESEATS.ORDERLINEITEM = 0")
    dupremoval_cte_doc.newline("\t\t\t\tAND ATESEATS.ORDERLINEITEMSEQUENCE = 0")
    dupremoval_cte_doc.newline("\t\t\tTHEN")
    dupremoval_cte_doc.newline("\t\t\t\tSHA2(")
    dupremoval_cte_doc.newline("\t\t\t\t\t'&teamAbbr'")
    dupremoval_cte_doc.newline("\t\t\t\t\t|| '-' || 'Y'")

    for col in dupremoval_cte_blockhash_eqzero_list:
        dupremoval_cte_doc.newline(f"\t\t\t\t\t|| '-' || IFNULL(TO_CHAR(ATESEATS.{col}),'')")

    dupremoval_cte_doc.newline("\t\t\t\t,512)")
    dupremoval_cte_doc.newline("\t\t\tEND AS BLOCKHASH,")

    # DUPREMOVAL - seat hash
    dupremoval_cte_doc.newline("\t\t\tSHA2(")
    dupremoval_cte_doc.newline("\t\t\t\t'&teamAbbr'")

    for col in dupremoval_cte_seathash_list:
        dupremoval_cte_doc.newline(f"\t\t\t\t|| '-' || IFNULL(TO_CHAR(ATESEATS.{col}),'')")

    dupremoval_cte_doc.newline("\t\t\t,512)")
    dupremoval_cte_doc.newline("\t\t\tAS SEATHASH,")

    # DUPREMOVAL - host indicator
    dupremoval_cte_doc.newline("\t\t\tCASE")
    dupremoval_cte_doc.newline("\t\t\t\tWHEN ATESEATS.PRICECODE NOT ILIKE '%*%' THEN 'N'")
    dupremoval_cte_doc.newline("\t\t\t\tWHEN ATESEATS.PRICECODE ILIKE '%*%' THEN 'Y'")
    dupremoval_cte_doc.newline("\t\t\tEND AS HOSTINDICATOR,")

    # DUPREMOVAL - columns between hostindicator and recordindicator
    for col in dupremoval_cte_between_host_record_ind_col_list:
        dupremoval_cte_doc.newline(f"\t\t\tATESEATS.{col},")

    # DUPREMOVAL - record indicator
    dupremoval_cte_doc.newline("\t\t\tCASE")
    dupremoval_cte_doc.newline("\t\t\t\tWHEN TICKETSTATUS = 'A' THEN ROW_NUMBER() OVER (PARTITION BY")

    for col in dupremoval_cte_record_ind_col_list_A:
        dupremoval_cte_doc.newline(f"\t\t\t\t\t{col},")

    dupremoval_cte_doc.trimend(1)
    dupremoval_cte_doc.newline("\t\t\t\tORDER BY FILEDATE DESC, ADDDATETIME DESC)")

    dupremoval_cte_doc.newline("\t\t\t\tWHEN TICKETSTATUS IN ('X', 'R') THEN DENSE_RANK() OVER (PARTITION BY")

    for col in dupremoval_cte_record_ind_col_list_XR:
        dupremoval_cte_doc.newline(f"\t\t\t\t\t{col},")

    dupremoval_cte_doc.trimend(1)
    dupremoval_cte_doc.newline("\t\t\t\tORDER BY FILEDATE DESC, RETURNDATETIME DESC, SEQUENCENUMBER DESC)")
    dupremoval_cte_doc.newline("\t\t\t\tELSE 1")
    dupremoval_cte_doc.newline("\t\t\tEND AS RECORDINDICATOR,")

    # DUPREMOVAL - orderupdatetime
    dupremoval_cte_doc.newline("\t\t\tMIN(UPDATEDATETIME) OVER (PARTITION BY")

    for col in dupremoval_cte_orderupdatetime_col_list:
        dupremoval_cte_doc.newline(f"\t\t\t\t{col},")

    dupremoval_cte_doc.newline("\t\t\t\tCASE WHEN TICKETSTATUS IN ('X','R') THEN RETURNDATETIME END,")
    dupremoval_cte_doc.newline("\t\t\t\tCASE WHEN TICKETSTATUS IN ('X','R') THEN RETURNREASONDESCRIPTION END,")
    dupremoval_cte_doc.newline("\t\t\t\tCASE WHEN TICKETSTATUS IN ('X','R') THEN RAWAUDIENCEID END")

    dupremoval_cte_doc.newline("\t\t\tORDER BY FILEDATE, UPDATEDATETIME, SEQUENCENUMBER) AS ORDERUPDATETIME,")

    dupremoval_cte_doc.newline("\t\t\tIFNULL(ATESEATS.SALESSOURCENAME,'') AS SALESSOURCENAME,")

    for col in dupremoval_cte_after_salessourcename_col_list:
        dupremoval_cte_doc.newline(f"\t\t\tATESEATS.{col},")

    dupremoval_cte_doc.trimend(1)

    dupremoval_cte_doc.newline("\t\tFROM ATESEATS")
    dupremoval_cte_doc.newline("\t)")

    # add dupremoval cte to main query
    rulequerydoc.newline("DUPREMOVAL AS (")
    rulequerydoc.newline(dupremoval_cte_doc.out())
    rulequerydoc.newline(") ")
    rulequerydoc.newline("SELECT * FROM DUPREMOVAL WHERE RECORDINDICATOR = 1;")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsTicketExpanded_4_2 TMP.ARCHTICSTICKETEXPANDED_NEWDATA_DEDUPED RULE_QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsticketexpanded_5_2(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 5_2
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsTicketExpanded_5_2"
    busrule["runOrder"] = 5
    busrule["runPosition"] = 2

    rulequerydoc = Document()

    rulequerydoc.append("MERGE INTO &database.STAGE.ARCHTICSTICKETEXPANDEDDEDUP DEST")
    rulequerydoc.newline("USING &database.TMP.ARCHTICSTICKETEXPANDED_NEWDATA_DEDUPED SOR")
    rulequerydoc.newline("ON DEST.SEATHASH = SOR.SEATHASH")
    rulequerydoc.newline("WHEN MATCHED AND")

    notnull_cols = []
    update_cols = []
    insert_cols = []
    for col in ArchticsTicketExpandedColumns:
        if "NOTNULL" in col[2]:
            notnull_cols.append(col[0])
        if "UPDATE" in col[2]:
            update_cols.append(col[0])
        if "INSERT" in col[2]:
            insert_cols.append(col[0])

    # notnull_cols = ["BLOCKHASH", "SEATHASH", "HOSTINDICATOR", "FILEDATE", "EVENTNAME", "SECTIONNAME", "ROWNAME",
    #                 "NUMBEROFSEATS", "TICKETSTATUS", "ACCOUNTID", "CUSTOMERNAMEID", "RAWAUDIENCEID", "UPDATEDATETIME",
    #                 "SEQUENCENUMBER", "BLOCKPURCHASEPRICE", "ORDERNUMBER", "ORDERLINEITEM", "ORDERLINEITEMSEQUENCE",
    #                 "PRICECODE", "PRICINGMETHOD", "COMPCODE", "COMPNAME", "UPDATEUSER", "CLASSNAME", "SELLLOCATION",
    #                 "FULLPRICE", "TICKETTYPE", "PRICECODEDESCRIPTION", "EVENTID", "PLANEVENTID", "PLANEVENTNAME",
    #                 "FIRSTSEAT", "LASTSEAT", "REPACCOUNTID", "REPACCOUNTFULLNAME", "TRANSACTIONTYPE", "SECTIONID",
    #                 "ROWID", "PROMOCODE", "ADDDATETIME", "RENEWALINDICATOR", "RETURNREASON", "RETURNREASONDESCRIPTION",
    #                 "EXPANDEDFLAG", "DELIVERYMETHODCODE", "DELIVERYMETHODNAME", "LEDGERID", "PRICECOMPONENTTAX",
    #                 "ORIGINALREPACCOUNTID", "TICKETSEQUENCEID", "RETURNDATETIME", "TICKETTYPECATEGORY", "SEAT",
    #                 "RECORDINDICATOR", "ORDERUPDATETIME", "SALESSOURCENAME", "PAIDAMOUNT", "PRICECOMPONENTTICKET",
    #                 "PRICECOMPONENTLICENSEFEE", "PRICECOMPONENTOTHER1", "PRICECOMPONENTOTHER2", "PRICECOMPONENTOTHER3",
    #                 "PRICECOMPONENTOTHER4", "PRICECOMPONENTOTHER5", "PRICECOMPONENTOTHER6", "PRICECOMPONENTOTHER7",
    #                 "PRICECOMPONENTOTHER8"]
    # update_cols = ["BLOCKHASH", "HOSTINDICATOR", "FILEDATE", "EVENTNAME", "SECTIONNAME", "ROWNAME", "NUMBEROFSEATS",
    #                "TICKETSTATUS", "ACCOUNTID", "CUSTOMERNAMEID", "RAWAUDIENCEID", "UPDATEDATETIME", "SEQUENCENUMBER",
    #                "BLOCKPURCHASEPRICE", "ORDERNUMBER", "ORDERLINEITEM", "ORDERLINEITEMSEQUENCE", "PRICECODE",
    #                "PRICINGMETHOD", "COMPCODE", "COMPNAME", "UPDATEUSER", "CLASSNAME", "SELLLOCATION", "FULLPRICE",
    #                "TICKETTYPE", "PRICECODEDESCRIPTION", "EVENTID", "PLANEVENTID", "PLANEVENTNAME", "FIRSTSEAT",
    #                "LASTSEAT", "REPACCOUNTID", "REPACCOUNTFULLNAME", "TRANSACTIONTYPE", "SECTIONID", "ROWID",
    #                "PROMOCODE", "ADDDATETIME", "RENEWALINDICATOR", "RETURNREASON", "RETURNREASONDESCRIPTION",
    #                "EXPANDEDFLAG", "DELIVERYMETHODCODE", "DELIVERYMETHODNAME", "LEDGERID", "PRICECOMPONENTTAX",
    #                "ORIGINALREPACCOUNTID", "TICKETSEQUENCEID", "RETURNDATETIME", "TICKETTYPECATEGORY", "DWUPDATEDATE",
    #                "SEAT", "RECORDINDICATOR", "ORDERUPDATETIME", "SALESSOURCENAME", "PAIDAMOUNT",
    #                "PRICECOMPONENTTICKET", "PRICECOMPONENTLICENSEFEE", "PRICECOMPONENTOTHER1", "PRICECOMPONENTOTHER2",
    #                "PRICECOMPONENTOTHER3", "PRICECOMPONENTOTHER4", "PRICECOMPONENTOTHER5", "PRICECOMPONENTOTHER6",
    #                "PRICECOMPONENTOTHER7", "PRICECOMPONENTOTHER8"]
    # insert_cols = ["BLOCKHASH", "SEATHASH", "HOSTINDICATOR", "FILEDATE", "EVENTNAME", "SECTIONNAME", "ROWNAME",
    #                "NUMBEROFSEATS", "TICKETSTATUS", "ACCOUNTID", "CUSTOMERNAMEID", "RAWAUDIENCEID", "UPDATEDATETIME",
    #                "SEQUENCENUMBER", "BLOCKPURCHASEPRICE", "ORDERNUMBER", "ORDERLINEITEM", "ORDERLINEITEMSEQUENCE",
    #                "PRICECODE", "PRICINGMETHOD", "COMPCODE", "COMPNAME", "UPDATEUSER", "CLASSNAME", "SELLLOCATION",
    #                "FULLPRICE", "TICKETTYPE", "PRICECODEDESCRIPTION", "EVENTID", "PLANEVENTID", "PLANEVENTNAME",
    #                "FIRSTSEAT", "LASTSEAT", "REPACCOUNTID", "REPACCOUNTFULLNAME", "TRANSACTIONTYPE", "SECTIONID",
    #                "ROWID", "PROMOCODE", "ADDDATETIME", "RENEWALINDICATOR", "RETURNREASON", "RETURNREASONDESCRIPTION",
    #                "EXPANDEDFLAG", "DELIVERYMETHODCODE", "DELIVERYMETHODNAME", "LEDGERID", "PRICECOMPONENTTAX",
    #                "ORIGINALREPACCOUNTID", "TICKETSEQUENCEID", "RETURNDATETIME", "TICKETTYPECATEGORY", "DWINSERTDATE",
    #                "DWUPDATEDATE", "SEAT", "RECORDINDICATOR", "ORDERUPDATETIME", "SALESSOURCENAME", "PAIDAMOUNT",
    #                "PRICECOMPONENTTICKET", "PRICECOMPONENTLICENSEFEE", "PRICECOMPONENTOTHER1", "PRICECOMPONENTOTHER2",
    #                "PRICECOMPONENTOTHER3", "PRICECOMPONENTOTHER4", "PRICECOMPONENTOTHER5", "PRICECOMPONENTOTHER6",
    #                "PRICECOMPONENTOTHER7", "PRICECOMPONENTOTHER8"]

    for col in notnull_cols:
        rulequerydoc.newline(f"\tNOT EQUAL_NULL(DEST.{col}, SOR.{col}) OR")
    rulequerydoc.trimend(3)

    # update
    rulequerydoc.newline("THEN UPDATE SET")

    for col in update_cols:
        if col == "DWUPDATEDATE":
            rulequerydoc.newline(f"\tDEST.{col} = CURRENT_TIMESTAMP(),")
        else:
            rulequerydoc.newline(f"\tDEST.{col} = SOR.{col},")
    rulequerydoc.trimend(1)

    # insert
    rulequerydoc.newline("WHEN NOT MATCHED THEN INSERT (")

    for col in insert_cols:
        rulequerydoc.newline(f"\tDEST.{col},")
    rulequerydoc.trimend(1)

    rulequerydoc.newline(") VALUES (")

    for col in insert_cols:
        if col == "DWINSERTDATE" or col == "DWUPDATEDATE":
            rulequerydoc.newline(f"\tCURRENT_TIMESTAMP(),")
        else:
            rulequerydoc.newline(f"\tSOR.{col},")
    rulequerydoc.trimend(1)

    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsTicketExpanded_5_2 MERGE INTO STAGE.ARCHTICSTICKETEXPANDEDDEDUP RULE_QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return