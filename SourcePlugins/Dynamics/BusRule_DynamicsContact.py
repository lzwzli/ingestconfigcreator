from Library.FunctionFiles.Functions import *
from SourcePlugins.Dynamics.StandardizationColumns import *
from SourcePlugins.Dynamics.RawAudienceArchiveColumns import *

def dynamicscontact_busrules(col_list:list, pk:list, rawaud_ind:int, bus_rule_obj:object, db_folder:str, runlog:object):
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}DynamicsContact_BusRules{os.sep}"
    runlog.log("Generate Dynamics Contact Business Rules.")
    runlog.log("")


    if rawaud_ind == "1":
        AddStdMerge = False
        for col_def in col_list:
            if col_def[1].upper() == "NEW_DW_CONTACT_AUDIENCE_ID":
                AddStdMerge = True
        if AddStdMerge:
            dynamicscontact_merge_standardization(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=1, runposition=0)
        dynamicscontact_merge_rawaudience_archive(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=2, runposition=4)
        dynamicscontact_delete_rawaudience(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=3, runposition=4)
        dynamicscontact_merge_archive(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=4, runposition=4)
        dynamicscontact_delete_stage(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder, runorder=5, runposition=4)

    return

def dynamicscontact_merge_rawaudience_archive(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=2, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 2_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"DynamicsContact_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("MERGE INTO STAGE.RAWAUDIENCEARCHIVE dest")
    rulequerydoc.newline("USING (")
    rulequerydoc.newline("\tSELECT raw.*")
    rulequerydoc.newline("\tFROM STAGE.RAWAUDIENCE raw")
    rulequerydoc.newline("\tLEFT JOIN STAGE.DYNAMICSCONTACT dc")
    rulequerydoc.newline("\t\tON dc.RAWAUDIENCEID = raw.RAWAUDIENCEID")
    rulequerydoc.newline("\t\tAND LOWER(raw.RAWAUDIENCETABLE) = LOWER('stage.dynamicscontact')")
    rulequerydoc.newline("\tWHERE")
    rulequerydoc.newline("\t\tdc.STATECODE = 1")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(dc.MASTERID),'')")
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
    filewrite(folder=output_folder, filename=f"DYNAMICSCONTACT_{runorder}_{runposition} MERGE RAWAUDIENCEARCHIVE RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def dynamicscontact_delete_rawaudience(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder:int=3, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 3_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"DynamicsContact_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("DELETE FROM STAGE.RAWAUDIENCE")
    rulequerydoc.newline("WHERE RAWAUDIENCEID IN (")
    rulequerydoc.newline("\tSELECT raw.RAWAUDIENCEID")
    rulequerydoc.newline("\tFROM STAGE.DYNAMICSCONTACT dc")
    rulequerydoc.newline("\tINNER JOIN STAGE.RAWAUDIENCE raw")
    rulequerydoc.newline("\t\tON dc.rawaudienceid = raw.rawaudienceid")
    rulequerydoc.newline("\t\tAND LOWER(raw.RAWAUDIENCETABLE) = LOWER('stage.dynamicscontact')")
    rulequerydoc.newline("\tWHERE")
    rulequerydoc.newline("\t\tdc.STATECODE = 1")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(dc.MASTERID),'')")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"DYNAMICSCONTACT_{runorder}_{runposition} DELETE FROM RAWAUDIENCE RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def dynamicscontact_merge_archive(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=4, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 4_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"DynamicsContact_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("MERGE INTO STAGE.DYNAMICSCONTACTARCHIVE dest")
    rulequerydoc.newline("USING (")
    rulequerydoc.newline("\tSELECT dc.*")
    rulequerydoc.newline("\tFROM STAGE.DYNAMICSCONTACT dc")
    rulequerydoc.newline("\tLEFT JOIN STAGE.RAWAUDIENCE raw")
    rulequerydoc.newline("\t\tON dc.RAWAUDIENCEID = raw.RAWAUDIENCEID")
    rulequerydoc.newline("\t\tAND LOWER(raw.RAWAUDIENCETABLE) = LOWER('stage.dynamicscontact')")
    rulequerydoc.newline("\tWHERE")
    rulequerydoc.newline("\t\tdc.STATECODE = 1")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(dc.MASTERID),'')")
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
    filewrite(folder=output_folder, filename=f"DYNAMICSCONTACT_{runorder}_{runposition} MERGE DYNAMICSCONTACTARCHIVE RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def dynamicscontact_delete_stage(col_list: list, pk: list, bus_rule_obj: object, output_folder: str, runorder:int=5, runposition:int=4):
    # ----------------------------------------------------------------
    # Rule 5_4
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"DynamicsContact_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    rulequerydoc = Document()
    rulequerydoc.append("DELETE FROM STAGE.DYNAMICSCONTACT")
    rulequerydoc.newline("WHERE CONTACTID IN (")
    rulequerydoc.newline("\tSELECT dc.CONTACTID")
    rulequerydoc.newline("\tFROM STAGE.DYNAMICSCONTACT dc")
    rulequerydoc.newline("\tLEFT JOIN STAGE.RAWAUDIENCE raw")
    rulequerydoc.newline("\t\tON dc.RAWAUDIENCEID = raw.RAWAUDIENCEID")
    rulequerydoc.newline("\t\tAND LOWER(raw.RAWAUDIENCETABLE) = LOWER('stage.dynamicscontact')")
    rulequerydoc.newline("\tWHERE")
    rulequerydoc.newline("\t\tdc.STATECODE = 1")
    rulequerydoc.newline("\t\tAND EQUAL_NULL(TRIM(dc.MASTERID),'')")
    rulequerydoc.newline("\t\tAND raw.RAWAUDIENCEID IS NULL")
    rulequerydoc.newline("\t\tAND dc.CONTACTID IN (")
    rulequerydoc.newline("\t\t\tSELECT CONTACTID")
    rulequerydoc.newline("\t\t\tFROM STAGE.DYNAMICSCONTACTARCHIVE")
    rulequerydoc.newline("\t\t\tGROUP BY CONTACTID")
    rulequerydoc.newline("\t\t)")
    rulequerydoc.newline("\t);")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"DYNAMICSCONTACT_{runorder}_{runposition} DELETE FROM DYNAMICSCONTACT RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def dynamicscontact_merge_standardization(col_list:list, pk:list, bus_rule_obj:object, output_folder:str, runorder:int=1, runposition:int=0):
    # ----------------------------------------------------------------
    # Rule 1_0
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = f"DynamicsContact_{runorder}_{runposition}"
    busrule["runOrder"] = runorder
    busrule["runPosition"] = runposition

    def select_cols():
        std_select_cols_str = bus_rule_obj.get_std_select_columns().replace("A.", "dc.")
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

        for col in std_cols:
            if col[1].upper() == "RAWPHONE" or col[1].upper() == "PHONENUMBER":
                colstring.newline(f"\t\tCOALESCE(NULLIF(dc.PHONE,''), NULLIF(dc.HOMEPHONE,''), NULLIF(dc.MOBILEPHONE,''), '') AS {col[1]},")
            if col[1] == "STANDARDIZATIONDATE" or col[1] == "DWINSERTDATE" or col[1] == "DWUPDATEDATE":
                colstring.newline(f"\t\tCURRENT_TIMESTAMP() AS {col[1]},")
            elif col[1] == "RAWCOMPANY" or col[1] == "COMPANYNAME":
                colstring.newline(f"\t\tIFNULL(da.{col[0]},'') AS {col[1]},")
            elif col[1] == "ROUTE":
                colstring.newline("\t\t'-1' AS ROUTE,")
            elif col[1] == "DISTANCETOVENUE":
                colstring.newline("\t\tIFNULL(a.distancetovenue::VARCHAR, '-1') AS DISTANCETOVENUE,")
            elif col[1] == "LATITUDE" or col[1] == "LONGITUDE":
                colstring.newline(f"\t\tIFNULL(a.{col[0]}, '') AS {col[1].upper()},")
            elif col[0] == "":
                colstring.newline(f"\t\t'' AS {col[1]},")
            else:
                colstring.newline(f"\t\tIFNULL(dc.{col[0]},'') AS {col[1]},")

        colstring.trimend(1)
        return colstring.out()

    rulequerydoc = Document()
    rulequerydoc.append("MERGE INTO STAGE.STANDARDIZATION dest USING (")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline(select_cols())
    rulequerydoc.newline("\tFROM IMPORT.DYNAMICSCONTACT dc")
    rulequerydoc.newline("\t\tINNER JOIN STAGE.DYNAMICSSYSTEMUSER su")
    rulequerydoc.newline("\t\t\tON dc._modifiedby_value = su.systemuserid")
    rulequerydoc.newline("\t\t\tAND su.internalemailaddress ILIKE %KAGRIntegration%")
    rulequerydoc.newline("\t\tLEFT JOIN STAGE.DYNAMICSACCOUNTS da")
    rulequerydoc.newline("\t\t\tON dc._PARENTCUSTOMERID_VALUE = da.ACCOUNTID")
    rulequerydoc.newline("\t\tLEFT JOIN STAGE.AUDIENCE a")
    rulequerydoc.newline("\t\t\tON dc.NEW_DW_CONTACT_AUDIENCE_ID = a.AUDIENCEID::VARCHAR")
    rulequerydoc.newline(") sor")
    rulequerydoc.newline("ON")

    for col in std_pk_cols:
        rulequerydoc.newline(f"\tLOWER(dest.{col}) = LOWER(sor.{col}) AND")
    rulequerydoc.trimend(4)

    rulequerydoc.newline("WHEN NOT MATCHED THEN INSERT (")

    for col in std_cols_raw:
        rulequerydoc.newline(f"\t{col[1]},")

    rulequerydoc.newline(") VALUES (")

    for col in std_cols_raw:
        rulequerydoc.newline(f"\tsor.{col[1]},")

    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename=f"DYNAMICSCONTACT_{runorder}_{runposition} MERGE STAGE STANDARDIZATION RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return