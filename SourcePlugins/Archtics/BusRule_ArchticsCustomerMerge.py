from Library.FunctionFiles.Functions import *

def archticscustomermerge_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics CustomerMerge
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsCustomerMerge_BusRules{os.sep}"
    runlog.log("Generate Archtics CustomerMerge Business Rules.")
    runlog.log("")

    archticscustomermerge_1_4_buyer(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomermerge_1_4_seller(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomermerge_1_4_account(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticscustomermerge_1_4_buyer(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomerMerge_1_4_BUYER"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    rulequerydoc.append("MERGE INTO &database.STAGE.ARCHTICSTICKETEXCHANGE TEX USING (")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\tOLDACCOUNTID,")
    rulequerydoc.newline("\t\tNEWACCOUNTID,")
    rulequerydoc.newline("\t\tCUSTOMERNAMEID AS NEWCUSTOMERNAMEID,")
    rulequerydoc.newline("\t\tRAWAUDIENCEID AS NEWRAWAUDIENCEID")
    rulequerydoc.newline("\tFROM (")
    rulequerydoc.newline("\t\tSELECT")
    rulequerydoc.newline("\t\t\tCM.OLDACCOUNTID,")
    rulequerydoc.newline("\t\t\tCM.NEWACCOUNTID,")
    rulequerydoc.newline("\t\t\tAC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\t\t\tAC.RAWAUDIENCEID,")
    rulequerydoc.newline("\t\t\tROW_NUMBER() OVER (")
    rulequerydoc.newline("\t\t\t\tPARTITION BY CM.NEWACCOUNTID")
    rulequerydoc.newline("\t\t\t\tORDER BY")
    rulequerydoc.newline("\t\t\t\t\tAC.UPDATEDATETIME DESC,")
    rulequerydoc.newline("\t\t\t\t\tCASE")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'primary' THEN 1")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'secondary' THEN 2")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'other' THEN 3")
    rulequerydoc.newline("\t\t\t\t\t\tELSE 4")
    rulequerydoc.newline("\t\t\t\t\tEND ASC")
    rulequerydoc.newline("\t\t\t) ROWNUMBER")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSTICKETEXCHANGE TEX")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERMERGE CM")
    rulequerydoc.newline("\t\t\tON TEX.BUYERACCOUNTID = CM.OLDACCOUNTID")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("\t\t\tON CM.NEWACCOUNTID = AC.ACCOUNTID")
    rulequerydoc.newline("\t\tWHERE CM.OLDACCOUNTID IS NOT NULL")
    rulequerydoc.newline("\t) SUB")
    rulequerydoc.newline("\tINNER JOIN (")
    rulequerydoc.newline("\t\tSELECT DISTINCT")
    rulequerydoc.newline("\t\t\tT.BUYERACCOUNTID")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSTICKETEXCHANGE T")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("\t\t\tON T.BUYERACCOUNTID = AC.ACCOUNTID")
    rulequerydoc.newline("\t\tWHERE AC.ACCOUNTID IS NULL")
    rulequerydoc.newline("\t) VALIDUPDATE")
    rulequerydoc.newline("\tON SUB.OLDACCOUNTID = VALIDUPDATE.BUYERACCOUNTID")
    rulequerydoc.newline("\tWHERE SUB.ROWNUMBER = 1")
    rulequerydoc.newline(") CM")
    rulequerydoc.newline("ON TEX.BUYERACCOUNTID = CM.OLDACCOUNTID")
    rulequerydoc.newline("WHEN MATCHED THEN UPDATE SET")
    rulequerydoc.newline("\tTEX.BUYERACCOUNTID = CM.NEWACCOUNTID,")
    rulequerydoc.newline("\tTEX.BUYERCUSTOMERNAMEID = CM.NEWCUSTOMERNAMEID,")
    rulequerydoc.newline("\tTEX.BUYERRAWAUDIENCEID = CM.NEWRAWAUDIENCEID,")
    rulequerydoc.newline("\tTEX.DWUPDATEDATE = CURRENT_TIMESTAMP()")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomerMerge_1_4_BUYER MERGE INTO STAGE.ARCHTICSTICKETEXCHANGE RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomermerge_1_4_seller(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomerMerge_1_4_SELLER"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    rulequerydoc.append("MERGE INTO &database.STAGE.ARCHTICSTICKETEXCHANGE TEX USING (")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\tOLDACCOUNTID,")
    rulequerydoc.newline("\t\tNEWACCOUNTID,")
    rulequerydoc.newline("\t\tCUSTOMERNAMEID AS NEWCUSTOMERNAMEID,")
    rulequerydoc.newline("\t\tRAWAUDIENCEID AS NEWRAWAUDIENCEID")
    rulequerydoc.newline("\tFROM (")
    rulequerydoc.newline("\t\tSELECT")
    rulequerydoc.newline("\t\t\tCM.OLDACCOUNTID,")
    rulequerydoc.newline("\t\t\tCM.NEWACCOUNTID,")
    rulequerydoc.newline("\t\t\tAC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\t\t\tAC.RAWAUDIENCEID,")
    rulequerydoc.newline("\t\t\tROW_NUMBER() OVER (")
    rulequerydoc.newline("\t\t\t\tPARTITION BY CM.NEWACCOUNTID")
    rulequerydoc.newline("\t\t\t\tORDER BY")
    rulequerydoc.newline("\t\t\t\t\tAC.UPDATEDATETIME DESC,")
    rulequerydoc.newline("\t\t\t\t\tCASE")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'primary' THEN 1")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'secondary' THEN 2")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'other' THEN 3")
    rulequerydoc.newline("\t\t\t\t\t\tELSE 4")
    rulequerydoc.newline("\t\t\t\t\tEND ASC")
    rulequerydoc.newline("\t\t\t) ROWNUMBER")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSTICKETEXCHANGE TEX")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERMERGE CM")
    rulequerydoc.newline("\t\t\tON TEX.SELLERACCOUNTID = CM.OLDACCOUNTID")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("\t\t\tON CM.NEWACCOUNTID = AC.ACCOUNTID")
    rulequerydoc.newline("\t\tWHERE CM.OLDACCOUNTID IS NOT NULL")
    rulequerydoc.newline("\t) SUB")
    rulequerydoc.newline("\tINNER JOIN (")
    rulequerydoc.newline("\t\tSELECT DISTINCT")
    rulequerydoc.newline("\t\t\tT.SELLERACCOUNTID")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSTICKETEXCHANGE T")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("\t\t\tON T.SELLERACCOUNTID = AC.ACCOUNTID")
    rulequerydoc.newline("\t\tWHERE AC.ACCOUNTID IS NULL")
    rulequerydoc.newline("\t) VALIDUPDATE")
    rulequerydoc.newline("\tON SUB.OLDACCOUNTID = VALIDUPDATE.SELLERACCOUNTID")
    rulequerydoc.newline("\tWHERE SUB.ROWNUMBER = 1")
    rulequerydoc.newline(") CM")
    rulequerydoc.newline("ON TEX.SELLERACCOUNTID = CM.OLDACCOUNTID")
    rulequerydoc.newline("WHEN MATCHED THEN UPDATE SET")
    rulequerydoc.newline("\tTEX.SELLERACCOUNTID = CM.NEWACCOUNTID,")
    rulequerydoc.newline("\tTEX.SELLERCUSTOMERNAMEID = CM.NEWCUSTOMERNAMEID,")
    rulequerydoc.newline("\tTEX.SELLERRAWAUDIENCEID = CM.NEWRAWAUDIENCEID,")
    rulequerydoc.newline("\tTEX.DWUPDATEDATE = CURRENT_TIMESTAMP()")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomerMerge_1_4_SELLER MERGE INTO STAGE.ARCHTICSTICKETEXCHANGE RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomermerge_1_4_account(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomerMerge_1_4_TICKETEXPANDED"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    rulequerydoc.append("MERGE INTO &database.STAGE.ARCHTICSTICKETEXPANDED TEX USING (")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\tOLDACCOUNTID,")
    rulequerydoc.newline("\t\tNEWACCOUNTID,")
    rulequerydoc.newline("\t\tCUSTOMERNAMEID AS NEWCUSTOMERNAMEID,")
    rulequerydoc.newline("\t\tRAWAUDIENCEID AS NEWRAWAUDIENCEID")
    rulequerydoc.newline("\tFROM (")
    rulequerydoc.newline("\t\tSELECT")
    rulequerydoc.newline("\t\t\tCM.OLDACCOUNTID,")
    rulequerydoc.newline("\t\t\tCM.NEWACCOUNTID,")
    rulequerydoc.newline("\t\t\tAC.CUSTOMERNAMEID,")
    rulequerydoc.newline("\t\t\tAC.RAWAUDIENCEID,")
    rulequerydoc.newline("\t\t\tROW_NUMBER() OVER (")
    rulequerydoc.newline("\t\t\t\tPARTITION BY CM.NEWACCOUNTID")
    rulequerydoc.newline("\t\t\t\tORDER BY")
    rulequerydoc.newline("\t\t\t\t\tAC.UPDATEDATETIME DESC,")
    rulequerydoc.newline("\t\t\t\t\tCASE")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'primary' THEN 1")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'secondary' THEN 2")
    rulequerydoc.newline("\t\t\t\t\t\tWHEN LOWER(ACCOUNTCODE) = 'other' THEN 3")
    rulequerydoc.newline("\t\t\t\t\t\tELSE 4")
    rulequerydoc.newline("\t\t\t\t\tEND ASC")
    rulequerydoc.newline("\t\t\t) ROWNUMBER")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSTICKETEXPANDED TE")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERMERGE CM")
    rulequerydoc.newline("\t\t\tON TE.ACCOUNTID = CM.OLDACCOUNTID")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("\t\t\tON CM.NEWACCOUNTID = AC.ACCOUNTID")
    rulequerydoc.newline("\t\tWHERE CM.OLDACCOUNTID IS NOT NULL")
    rulequerydoc.newline("\t) SUB")
    rulequerydoc.newline("\tINNER JOIN (")
    rulequerydoc.newline("\t\tSELECT DISTINCT")
    rulequerydoc.newline("\t\t\tT.ACCOUNTID")
    rulequerydoc.newline("\t\tFROM &database.STAGE.ARCHTICSTICKETEXPANDED T")
    rulequerydoc.newline("\t\tLEFT JOIN &database.STAGE.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("\t\t\tON T.ACCOUNTID = AC.ACCOUNTID")
    rulequerydoc.newline("\t\tWHERE AC.ACCOUNTID IS NULL")
    rulequerydoc.newline("\t) VALIDUPDATE")
    rulequerydoc.newline("\tON SUB.OLDACCOUNTID = VALIDUPDATE.ACCOUNTID")
    rulequerydoc.newline("\tWHERE SUB.ROWNUMBER = 1")
    rulequerydoc.newline(") CM")
    rulequerydoc.newline("ON TEX.ACCOUNTID = CM.OLDACCOUNTID")
    rulequerydoc.newline("WHEN MATCHED THEN UPDATE SET")
    rulequerydoc.newline("\tTEX.ACCOUNTID = CM.NEWACCOUNTID,")
    rulequerydoc.newline("\tTEX.CUSTOMERNAMEID = CM.NEWCUSTOMERNAMEID,")
    rulequerydoc.newline("\tTEX.RAWAUDIENCEID = CM.NEWRAWAUDIENCEID,")
    rulequerydoc.newline("\tTEX.DWUPDATEDATE = CURRENT_TIMESTAMP()")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsCustomerMerge_1_4_TICKETEXPANDED MERGE INTO STAGE.ARCHTICSTICKETEXPANDED RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return