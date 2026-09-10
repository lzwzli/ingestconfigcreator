from Library.FunctionFiles.Functions import *
from SourcePlugins.Salesforce.StandardizationColumns import *
from SourcePlugins.Salesforce.RawAudienceArchiveColumns import *

def salesforcelead_busrules(col_list:list, pk:list, rawaud_ind:int, bus_rule_obj:object, db_folder:str, runlog:object):
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}SALESFORCELEAD_BusRules{os.sep}"
    runlog.log("Generate Salesforce Contact Business Rules.")
    runlog.log("")

    salesforcelead_update_import(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=0, runposition=0)
    if rawaud_ind == "1":
        AddStdMerge = False
        for col_def in col_list:
            if col_def[1].upper() == "DW_LEAD_AUDIENCE_ID__C":
                AddStdMerge = True
        if AddStdMerge:
            salesforcelead_merge_standardization(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=1, runposition=0)
        salesforcelead_merge_rawaudience_archive(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=2, runposition=4)
        salesforcelead_delete_rawaudience(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=3, runposition=4)
        salesforcelead_merge_archive(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=4, runposition=4)
        salesforcelead_delete_stage(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=5, runposition=4)

    return

def salesforcelead_update_import(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=0, runposition:int=0):
    # ----------------------------------------------------------------
    # Rule 0_0
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SalesforceLead_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("UPDATE &database.IMPORT.SALESFORCELEAD dest")
    rulequerydoc.newline("SET dest.STREET = src.NEWMAILINGSTREET")
    rulequerydoc.newline("\tFROM (")
    rulequerydoc.newline("\t\tSELECT")
    rulequerydoc.newline("\t\t\tID,")
    rulequerydoc.newline("\t\t\tSTREET,")
    rulequerydoc.newline("\t\t\tREPLACE(REPLACE(REPLACE(REGEXP_REPLACE(STREET,'[0-9]{8,}_[0-9]{1,}\\\\|[0-9]+\\\\|[0-9]+\\\\|',''),'\\n',' '),'\\r',' '),'  ',' ') AS NEWMAILINGSTREET")
    rulequerydoc.newline("\t\tFROM")
    rulequerydoc.newline("\t\t\t&database.IMPORT.SALESFORCELEAD")
    rulequerydoc.newline("\t\tWHERE")
    rulequerydoc.newline("\t\t\tSTREET LIKE '%\\n%'")
    rulequerydoc.newline("\t) src")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline("\tdest.ID = src.ID")
    rulequerydoc.newline(";")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SALESFORCELEAD_{runorder}_{runposition} UPDATE IMPORT SALESFORCELEAD RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def salesforcelead_merge_standardization(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=1, runposition:int=0):
    # ----------------------------------------------------------------
    # Rule 1_0
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SalesforceLead_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    def select_cols():
        std_select_cols_str = bus_rule_obj.get_std_select_columns().replace("A.", "sfl.")
        std_select_cols = std_select_cols_str.split("\n")

        colstring = Document()

        # update std select cols
        for stdcol in std_select_cols:
            if "EmailAddress" in stdcol:
                colstring.newline(stdcol.replace('"EmailAddress"', 'RAWEMAIL'))
            elif "RawPrefix" in stdcol:
                colstring.newline(stdcol.replace('"RawPrefix"', 'RAWPREFIX'))
            elif "RawFirstName" in stdcol:
                colstring.newline(stdcol.replace('"RawFirstName"', 'RAWFIRSTNAME'))
            elif "RawMiddleName" in stdcol:
                colstring.newline(stdcol.replace('"RawMiddleName"', 'RAWMIDDLENAME'))
            elif "RawLastName" in stdcol:
                colstring.newline(stdcol.replace('"RawLastName"', 'RAWLASTNAME'))
            elif "FullName" in stdcol:
                colstring.newline(stdcol.replace('"FullName"', 'RAWFULLNAME'))
            elif "RawSuffix" in stdcol:
                colstring.newline(stdcol.replace('"RawSuffix"', 'RAWSUFFIX'))
            elif "AddressLine1" in stdcol:
                colstring.newline(stdcol.replace('"AddressLine1"', 'RAWADDRESS1'))
            elif "AddressLine2" in stdcol:
                colstring.newline(stdcol.replace('"AddressLine2"', 'RAWADDRESS2'))
            elif "AddressLine3" in stdcol:
                colstring.newline(stdcol.replace('"AddressLine3"', 'RAWADDRESS3'))
            elif "City" in stdcol:
                colstring.newline(stdcol.replace('"City"', 'RAWCITY'))
            elif "State" in stdcol:
                colstring.newline(stdcol.replace('"State"', 'RAWSTATE'))
            elif "PostalCode" in stdcol:
                colstring.newline(stdcol.replace('"PostalCode"', 'RAWZIP'))
            elif "Country" in stdcol:
                colstring.newline(stdcol.replace('"Country"', 'RAWCOUNTRY'))
            elif "PhoneNumber" in stdcol:
                colstring.newline(stdcol.replace('"PhoneNumber"', 'RAWPHONE'))
            elif "CompanyName" in stdcol:
                colstring.newline(stdcol.replace('"CompanyName"', 'RAWCOMPANY'))

        # add other non raw columns
        for col in std_cols:
            if col[1].upper() == "RAWPHONE" or col[1].upper() == "PHONENUMBER":
                colstring.newline(f"\t\tCOALESCE(NULLIF(sfl.PHONE,''), NULLIF(sfl.HOMEPHONE,''), NULLIF(sfl.MOBILEPHONE,''), '') AS {col[1]},")
            elif col[1] == "STANDARDIZATIONDATE" or col[1] == "DWINSERTDATE" or col[1] == "DWUPDATEDATE":
                colstring.newline(f"\t\tCURRENT_TIMESTAMP() AS {col[1]},")
            elif col[1] == "ROUTE":
                colstring.newline("\t\t'-1' AS ROUTE,")
            elif col[1] == "DISTANCETOVENUE":
                colstring.newline("\t\tIFNULL(a.distancetovenue::VARCHAR, '-1') AS DISTANCETOVENUE,")
            elif col[1] == "LATITUDE" or col[1] == "LONGITUDE":
                colstring.newline(f"\t\tIFNULL(a.{col[0]}, '') AS {col[1].upper()},")
            elif col[0] == "":
                colstring.newline(f"\t\t'' AS {col[1]},")
            else:
                colstring.newline(f"\t\tIFNULL(sfl.{col[0]},'') AS {col[1]},")

        colstring.trimend(1)
        return colstring.out()

    rulequerydoc = Document()
    rulequerydoc.append("MERGE INTO &database.STAGE.STANDARDIZATION dest USING (")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline(select_cols())
    rulequerydoc.newline("\tFROM &database.IMPORT.SALESFORCELEAD sfl")
    rulequerydoc.newline("\t\tINNER JOIN &database.STAGE.SALESFORCEUSER su")
    rulequerydoc.newline("\t\t\tON sfl.LASTMODIFIEDBYID = su.ID")
    rulequerydoc.newline("\t\tAND su.USERNAME ILIKE %DATASVC%@KAGR.COM%")
    rulequerydoc.newline("\tLEFT JOIN &database.STAGE.AUDIENCE a")
    rulequerydoc.newline("\t\tON sfl.DW_LEAD_AUDIENCE_ID__C = a.AUDIENCEID::VARCHAR")
    rulequerydoc.newline(") src")
    rulequerydoc.newline("ON")

    for col in std_pk_cols:
        rulequerydoc.newline(f"\tLOWER(dest.{col}) = LOWER(src.{col}) AND")
    rulequerydoc.trimend(4)

    rulequerydoc.newline("WHEN NOT MATCHED THEN INSERT (")

    for col in std_cols_raw:
        rulequerydoc.newline(f"\t{col[1]},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline(") VALUES (")

    for col in std_cols_raw:
        rulequerydoc.newline(f"\tsrc.{col[1]},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SALESFORCELEAD_{runorder}_{runposition} MERGE STAGE STANDARDIZATION RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def salesforcelead_merge_rawaudience_archive(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=2, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 2_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SalesforceLead_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("MERGE INTO &database.STAGE.RAWAUDIENCEARCHIVE dest")
    rulequerydoc.newline("USING (")
    rulequerydoc.newline("\tSELECT raw.*")
    rulequerydoc.newline("\tFROM &database.STAGE.SALESFORCELEAD sl")
    rulequerydoc.newline("\tLEFT JOIN &database.STAGE.RAWAUDIENCE raw")
    rulequerydoc.newline("\t\tON sl.RAWAUDIENCEID = raw.RAWAUDIENCEID")
    rulequerydoc.newline("\t\tAND LOWER(raw.RAWAUDIENCETABLE) = LOWER('stage.salesforcelead')")
    rulequerydoc.newline("\tWHERE")
    rulequerydoc.newline("\t\tLOWER(sl.ISDELETED) = 'true'")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(sl.MASTERRECORDID),'')")
    rulequerydoc.newline(") src")
    rulequerydoc.newline("ON dest.RAWAUDIENCEID = src.RAWAUDIENCEID")
    rulequerydoc.newline("WHEN NOT MATCHED THEN INSERT (")

    for col in rawaud_cols:
        rulequerydoc.newline(f"\t{col},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline(")")
    rulequerydoc.newline("VALUES (")

    for col in rawaud_cols:
        rulequerydoc.newline(f"\tsrc.{col},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SALESFORCELEAD_{runorder}_{runposition} MERGE RAWAUDIENCEARCHIVE RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def salesforcelead_delete_rawaudience(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder:int=3, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 3_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SalesforceLead_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("DELETE FROM &database.STAGE.RAWAUDIENCE")
    rulequerydoc.newline("WHERE RAWAUDIENCEID IN (")
    rulequerydoc.newline("\tSELECT raw.RAWAUDIENCEID")
    rulequerydoc.newline("\tFROM &database.STAGE.SALESFORCELEAD sl")
    rulequerydoc.newline("\tINNER JOIN &database.STAGE.RAWAUDIENCE raw")
    rulequerydoc.newline("\t\tON sl.rawaudienceid = raw.rawaudienceid")
    rulequerydoc.newline("\t\tAND LOWER(raw.RAWAUDIENCETABLE) = LOWER('stage.salesforcelead')")
    rulequerydoc.newline("\tWHERE (")
    rulequerydoc.newline("\t\tLOWER(sl.ISDELETED) = 'true'")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(sl.MASTERRECORDID),'')")
    rulequerydoc.newline("\t);")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SALESFORCELEAD_{runorder}_{runposition} DELETE FROM RAWAUDIENCE RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def salesforcelead_merge_archive(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=4, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 4_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SalesforceLead_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("MERGE INTO &database.STAGE.SALESFORCELEADARCHIVE dest")
    rulequerydoc.newline("USING (")
    rulequerydoc.newline("\tSELECT sc.*")
    rulequerydoc.newline("\tFROM &database.STAGE.SALESFORCELEAD sl")
    rulequerydoc.newline("\tLEFT JOIN &database.STAGE.RAWAUDIENCE raw")
    rulequerydoc.newline("\t\tON sl.RAWAUDIENCEID = raw.RAWAUDIENCEID")
    rulequerydoc.newline("\t\tAND LOWER(raw.RAWAUDIENCETABLE) = LOWER('stage.salesforcelead')")
    rulequerydoc.newline("\tWHERE")
    rulequerydoc.newline("\t\tLOWER(sl.ISDELETED) = 'true'")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(sl.MASTERRECORDID),'')")
    rulequerydoc.newline("\t\tAND raw.RAWAUDIENCEID IS NULL")
    rulequerydoc.newline(") src")
    rulequerydoc.newline("ON dest.RAWAUDIENCEID = src.RAWAUDIENCEID")
    rulequerydoc.newline("WHEN NOT MATCHED THEN INSERT (")

    insert_cols = [["", "FILEDATE", "VARCHAR"], ["", "FILENAME", "VARCHAR"], ["", "FILEROWNUMBER", "NUMBER(38,0)"], ["", "DWINSERTDATE", "TIMESTAMP_LTZ(9)"], ["", "DWUPDATEDATE", "TIMESTAMP_LTZ(9)"], ["", "RAWAUDIENCEID", "NUMBER(38,0)"], ["", "STANDARDIZATIONROWID", "VARCHAR"]] + col_list

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
    filewrite(folder=output_folder, filename=f"SALESFORCELEAD_{runorder}_{runposition} MERGE salesforceleadarchive RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def salesforcelead_delete_stage(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder:int=5, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 5_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"SalesforceLead_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("DELETE FROM &database.STAGE.SALESFORCELEAD")
    rulequerydoc.newline("WHERE ID IN (")
    rulequerydoc.newline("\tSELECT sl.ID")
    rulequerydoc.newline("\tFROM &database.STAGE.SALESFORCELEAD sl")
    rulequerydoc.newline("\tLEFT JOIN &database.STAGE.RAWAUDIENCE raw")
    rulequerydoc.newline("\t\tON sl.RAWAUDIENCEID = raw.RAWAUDIENCEID")
    rulequerydoc.newline("\t\tAND LOWER(raw.RAWAUDIENCETABLE) = LOWER('stage.salesforcelead')")
    rulequerydoc.newline("\tWHERE (")
    rulequerydoc.newline("\t\tLOWER(sl.ISDELETED) = 'true'")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(sl.MASTERRECORDID),'')")
    rulequerydoc.newline("\t\tAND raw.RAWAUDIENCEID IS NULL")
    rulequerydoc.newline("\t\tAND sl.ID IN (")
    rulequerydoc.newline("\t\t\tSELECT ID")
    rulequerydoc.newline("\t\t\tFROM &database.STAGE.SALESFORCELEADARCHIVE")
    rulequerydoc.newline("\t\t\tGROUP BY ID")
    rulequerydoc.newline("\t\t)")
    rulequerydoc.newline("\t);")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"SALESFORCELEAD_{runorder}_{runposition} DELETE FROM SALESFORCELEAD RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return