from Library.FunctionFiles.Functions import *

def archticscustomers_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics Customers
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsCustomers_BusRules{os.sep}"
    runlog.log("Generate Archtics Customers Business Rules.")
    runlog.log("")

    archticscustomers_0_0(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomers_1_0(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomers_1_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomers_1_3(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomers_2_3(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomers_1_4(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticscustomers_2_4(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticscustomers_0_0(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 0_0
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomers_0_0"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 0

    rulequerydoc = Document()

    rulequerydoc.append("DELETE FROM &database.import.archticscustomers")
    rulequerydoc.newline("WHERE filedate <> (")
    rulequerydoc.newline("\tSELECT max(filedate)")
    rulequerydoc.newline("\tFROM &database.import.archticscustomers")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsCustomers_0_0 DELETE IMPORT.ARCHTICSCUSTOMERS RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomers_1_0(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_0
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomers_1_0"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 0

    rulequerydoc = Document()

    rulequerydoc.append("UPDATE &database.IMPORT.ARCHTICSCUSTOMERS")
    rulequerydoc.newline("SET BIRTHDATE = '1900-01-01'")
    rulequerydoc.newline("WHERE CAST(SUBSTRING(BIRTHDATE,1,2) AS INT) <13")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomers_1_0 UPDATE IMPORT.ARCHTICSCUSTOMERS RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomers_1_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    def col_string(col_name:str, col_list:list):
        col_name = col_name.upper()
        colstring = ""
        for col in col_list:
            if "ST.RAW" not in col:
                colstring += f"NULLIF({col},''),"
        colstring = colstring[:-1]
        finalstring = f"\tCOALESCE({colstring},'') {col_name},"

        return finalstring

    def join_string(col_list:list):
        joinstring = ""
        finaljoinstring = "LOWER(AC_COLS) = LOWER(ST_COL)"
        for col in col_list:
            if "ST." not in col:
                joinstring += f"NULLIF({col},''),"
            else:
                if "ST.RAW" in col:
                    finaljoinstring = finaljoinstring.replace("ST_COL",col)

        finaljoinstring = finaljoinstring.replace("AC_COLS", f"COALESCE({joinstring}'')")

        return finaljoinstring

    def fullname_joinstring():
        cols = ["AC.RAWFIRSTNAME", "AC.RAWMIDDLENAME", "AC.RAWLASTNAME"]

        fullnamestring = ""
        for col in cols:
            casewhen = (f"\n\t\tCASE\n"
                        f"\t\t\tWHEN IFNULL({col}, '') <> ''\n"
                        f"\t\t\tTHEN IFNULL({col},'') || ' '\n"
                        f"\t\t\tELSE ''\n"
                        f"\t\tEND ||")

            fullnamestring += casewhen

        fullnamestring = fullnamestring[:-3]
        finalfullnamestring = f"IFNULL(LOWER({fullnamestring}\n\t), '') = LOWER(ST.RAWFULLNAME)"

        return finalfullnamestring


    # ----------------------------------------------------------------
    # Rule 1_1
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomers_1_1"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 1

    email_cols = ["ST.RAWEMAIL", "ST.EMAIL", "AC.RAWEMAIL", "AC.MAEMAIL"]
    prefix_cols = ["ST.NAMEPREFIX"]
    firstname_cols = ["ST.RAWFIRSTNAME","ST.NAMEFIRST", "AC.RAWFIRSTNAME"]
    middlename_cols = ["ST.RAWMIDDLENAME","ST.NAMEMIDDLE", "AC.RAWMIDDLENAME"]
    lastname_cols = ["ST.RAWLASTNAME","ST.NAMELAST", "AC.RAWLASTNAME"]
    suffix_cols = ["ST.NAMESUFFIX"]
    fullname_cols = ["ST.NAMEFULL"]
    address1_cols = ["ST.RAWADDRESS1", "ST.ADDRESS1", "AC.RAWADDRESS1"]
    address2_cols = ["ST.RAWADDRESS2","ST.ADDRESS2", "AC.RAWADDRESS2"]
    address3_cols = ["ST.ADDRESS3"]
    city_cols = ["ST.RAWCITY","ST.CITY", "AC.RAWCITY"]
    state_cols = ["ST.RAWSTATE", "ST.STATE", "AC.RAWSTATE"]
    zip_cols = ["ST.RAWZIP", "ST.ZIP", "AC.RAWZIP"]
    country_cols = ["ST.RAWCOUNTRY", "ST.COUNTRYNAME", "AC.RAWCOUNTRY"]
    phoneday_cols = ["ST.RAWPHONE", "ST.PHONENUMBER", "AC.RAWPHONEDAY", "AC.MAPHONE", "AC.PHONEEVENING"]
    companyname_cols = ["ST.RAWCOMPANY", "ST.COMPANYNAME", "AC.RAWCOMPANYNAME"]

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE TMP.ARCHTICSCUSTOMERSmelissa AS")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tAC.*,")
    rulequerydoc.newline("\tIFNULL(ST.STANDARDIZATIONROWID,0) STANDARDIZATIONROWID,")
    rulequerydoc.newline(col_string("EMAIL", email_cols))
    rulequerydoc.newline(col_string("PREFIX", prefix_cols))
    rulequerydoc.newline(col_string("FIRSTNAME", firstname_cols))
    rulequerydoc.newline(col_string("MIDDLENAME", middlename_cols))
    rulequerydoc.newline(col_string("LASTNAME", lastname_cols))
    rulequerydoc.newline(col_string("SUFFIX", suffix_cols))
    rulequerydoc.newline(col_string("FULLNAME", fullname_cols))
    rulequerydoc.newline(col_string("ADDRESS1", address1_cols))
    rulequerydoc.newline(col_string("ADDRESS2", address2_cols))
    rulequerydoc.newline(col_string("ADDRESS3", address3_cols))
    rulequerydoc.newline(col_string("CITY", city_cols))
    rulequerydoc.newline(col_string("STATE", state_cols))
    rulequerydoc.newline(col_string("ZIP", zip_cols))
    rulequerydoc.newline(col_string("COUNTRY", country_cols))
    rulequerydoc.newline(col_string("PHONEDAY", phoneday_cols))
    rulequerydoc.newline(col_string("COMPANYNAME", companyname_cols))
    rulequerydoc.trimend(1)
    rulequerydoc.newline("FROM &database.IMPORT.ARCHTICSCUSTOMERS AC")
    rulequerydoc.newline("LEFT JOIN &database.STAGE.STANDARDIZATION ST")
    rulequerydoc.newline(f"\tON {join_string(email_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(firstname_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(middlename_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(lastname_cols)}")
    rulequerydoc.newline(f"\tAND {fullname_joinstring()}")
    rulequerydoc.newline(f"\tAND {join_string(address1_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(address2_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(city_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(state_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(zip_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(country_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(phoneday_cols)}")
    rulequerydoc.newline(f"\tAND {join_string(companyname_cols)}")
    rulequerydoc.newline("\tAND LOWER(IFNULL(ST.RAWPREFIX,'')) = ''")
    rulequerydoc.newline("\tAND LOWER(IFNULL(ST.RAWSUFFIX,'')) = ''")
    rulequerydoc.newline("\tAND LOWER(IFNULL(ST.RAWADDRESS3,'')) = ''")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomers_1_1 CREATE TMP.ARCHTICSCUSTOMERSmelissa RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomers_1_3(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomers_1_3"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 3

    rulequerydoc = Document()

    columns = ["RAWAUDIENCETABLE","RAWAUDIENCESOURCE","RAWAUDIENCESUBSOURCE","SOURCEACCOUNTID","SOURCEACCOUNTSECONDARYID"]
    colstring = ""
    for col in columns:
        colstring += (f"\t{col},\n")
    colstring = colstring[:-2]

    rulequerydoc.append("INSERT INTO &database.STAGE.RAWAUDIENCE")
    rulequerydoc.newline("(")
    rulequerydoc.newline(colstring)
    rulequerydoc.newline(")")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline(colstring)
    rulequerydoc.newline("FROM (")
    rulequerydoc.newline("\tSELECT DISTINCT")
    rulequerydoc.newline("\t\t'STAGE.ARCHTICSCUSTOMERS' RAWAUDIENCETABLE,")
    rulequerydoc.newline("\t\t'Archtics' RAWAUDIENCESOURCE,")
    rulequerydoc.newline("\t\tT.SOURCENAME RAWAUDIENCESUBSOURCE,")
    rulequerydoc.newline("\t\tCAST(ACCOUNTID AS VARCHAR) SOURCEACCOUNTID,")
    rulequerydoc.newline("\t\tCAST(CUSTOMERNAMEID AS VARCHAR) SOURCEACCOUNTSECONDARYID,")
    rulequerydoc.newline("\t\tROW_NUMBER() OVER (")
    rulequerydoc.newline("\t\tPARTITION BY")
    rulequerydoc.newline("\t\t\tLOWER(T.ACCOUNTID),")
    rulequerydoc.newline("\t\t\tLOWER(T.CUSTOMERNAMEID)")
    rulequerydoc.newline("\t\tORDER BY")
    rulequerydoc.newline("\t\t\tT.CUSTOMERNAMEID")
    rulequerydoc.newline("\t\t) ROWNUMBER")
    rulequerydoc.newline("\tFROM &database.TMP.ARCHTICSCUSTOMERSUNIQUE T")
    rulequerydoc.newline("\tLEFT JOIN &database.STAGE.RAWAUDIENCE RA   ")
    rulequerydoc.newline("\t\tON LOWER(CAST(T.ACCOUNTID AS STRING)) = LOWER(RA.SOURCEACCOUNTID)")
    rulequerydoc.newline("\t\tAND LOWER(CAST(T.CUSTOMERNAMEID AS STRING)) = LOWER(RA.SOURCEACCOUNTSECONDARYID)")
    rulequerydoc.newline("\t\tAND LOWER(RA.RAWAUDIENCETABLE) = LOWER('STAGE.ARCHTICSCUSTOMERS')")
    rulequerydoc.newline("\tWHERE RA.RAWAUDIENCEID IS NULL")
    rulequerydoc.newline(") SUB")
    rulequerydoc.newline("WHERE SUB.ROWNUMBER  = 1")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomers_1_3 INSERT INTO STAGE.RAWAUDIENCE RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomers_2_3(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 2_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomers_2_3"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 3

    rulequerydoc = Document()

    rulequerydoc.append("CREATE OR REPLACE TABLE &database.TMP.ARCHTICSCUSTOMERSRAWAUDIENCE AS")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tT.*,")
    rulequerydoc.newline("\tRA.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.TMP.ARCHTICSCUSTOMERSUNIQUE T")
    rulequerydoc.newline("INNER JOIN &database.STAGE.RAWAUDIENCE RA")
    rulequerydoc.newline("\tON LOWER(CAST(T.ACCOUNTID AS STRING)) = LOWER(RA.SOURCEACCOUNTID)")
    rulequerydoc.newline("\tAND LOWER(CAST(T.CUSTOMERNAMEID AS STRING)) = LOWER(RA.SOURCEACCOUNTSECONDARYID)")
    rulequerydoc.newline("\tAND LOWER(RA.RAWAUDIENCETABLE) = LOWER('STAGE.ARCHTICSCUSTOMERS')")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomers_2_3 CREATE TMP.ARCHTICSCUSTOMERSRAWAUDIENCE RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomers_1_4(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 1_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomers_1_4"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    columns = ["RAWAUDIENCETABLE","RAWAUDIENCESOURCE","RAWAUDIENCESUBSOURCE","SOURCEACCOUNTID","SOURCEACCOUNTSECONDARYID"]
    colstring = ""
    for col in columns:
        colstring += (f"\t{col},\n")
    colstring = colstring[:-2]

    rulequerydoc.append("INSERT INTO &database.STAGE.RAWAUDIENCE")
    rulequerydoc.newline("(")
    rulequerydoc.newline(colstring)
    rulequerydoc.newline(")")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline(colstring)
    rulequerydoc.newline("FROM (")
    rulequerydoc.newline("\tSELECT DISTINCT")
    rulequerydoc.newline("\t\t'STAGE.ARCHTICSCUSTOMERS' RAWAUDIENCETABLE,")
    rulequerydoc.newline("\t\t'Archtics' RAWAUDIENCESOURCE,")
    rulequerydoc.newline("\t\tT.SOURCENAME RAWAUDIENCESUBSOURCE,")
    rulequerydoc.newline("\t\tCAST(ACCOUNTID AS VARCHAR) SOURCEACCOUNTID,")
    rulequerydoc.newline("\t\tCAST(CUSTOMERNAMEID AS VARCHAR) SOURCEACCOUNTSECONDARYID,")
    rulequerydoc.newline("\t\tROW_NUMBER() OVER (")
    rulequerydoc.newline("\t\tPARTITION BY")
    rulequerydoc.newline("\t\t\tLOWER(T.ACCOUNTID),")
    rulequerydoc.newline("\t\t\tLOWER(T.CUSTOMERNAMEID)")
    rulequerydoc.newline("\t\tORDER BY")
    rulequerydoc.newline("\t\t\tT.CUSTOMERNAMEID")
    rulequerydoc.newline("\t\t) ROWNUMBER")
    rulequerydoc.newline("\tFROM &database.STAGE.ARCHTICSCUSTOMERS T")
    rulequerydoc.newline("\tLEFT JOIN &database.STAGE.RAWAUDIENCE RA   ")
    rulequerydoc.newline("\t\tON LOWER(CAST(T.ACCOUNTID AS STRING)) = LOWER(RA.SOURCEACCOUNTID)")
    rulequerydoc.newline("\t\tAND LOWER(CAST(T.CUSTOMERNAMEID AS STRING)) = LOWER(RA.SOURCEACCOUNTSECONDARYID)")
    rulequerydoc.newline("\t\tAND LOWER(RA.RAWAUDIENCETABLE) = LOWER('STAGE.ARCHTICSCUSTOMERS')")
    rulequerydoc.newline("\tWHERE RA.RAWAUDIENCEID IS NULL")
    rulequerydoc.newline(") SUB")
    rulequerydoc.newline("WHERE SUB.ROWNUMBER  = 1")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomers_1_4 INSERT INTO STAGE.RAWAUDIENCE RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticscustomers_2_4(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # ----------------------------------------------------------------
    # Rule 2_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsCustomers_2_4"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 4

    rulequerydoc = Document()

    rulequerydoc.append("UPDATE &database.STAGE.ARCHTICSCUSTOMERS T")
    rulequerydoc.newline("SET T.RAWAUDIENCEID = RA.RAWAUDIENCEID")
    rulequerydoc.newline("FROM &database.STAGE.RAWAUDIENCE RA")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline("\tLOWER(CAST(T.ACCOUNTID AS STRING)) = LOWER(RA.SOURCEACCOUNTID)")
    rulequerydoc.newline("\tAND LOWER(CAST(T.CUSTOMERNAMEID AS STRING)) = LOWER(RA.SOURCEACCOUNTSECONDARYID)")
    rulequerydoc.newline("\tAND LOWER(RA.RAWAUDIENCETABLE) = LOWER('STAGE.ARCHTICSCUSTOMERS')")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder,
              filename="ArchticsCustomers_2_4 UPDATE IMPORT.ARCHTICSCUSTOMERS RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return