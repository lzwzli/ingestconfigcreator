from Library.FunctionFiles.Functions import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Submissions rule 3_0 for historical inserts
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fn_submissions_bus_rule_3_0(col_list:list, field_name_col:str, form_name_col:str, form_id_col:str, field_id_col:str, field_label_col:str, master_form_id:str):
    select_columns = ""

    # column logic
    # generic column logic
    column_logic = "\n\tMAX("
    column_logic += "\n\t\tIFNULL(("
    column_logic += f"\n\t\t\tCASE WHEN TRIM(LOWER(FSB.value:label::STRING)) IN"
    column_logic += "\n\t\t\t\t(SELECT DISTINCT TRIM(LOWER(<colname>)) FROM &database.STAGE.FORMSTACKFORMQUESTIONS WHERE <colname> IS NOT NULL)"
    column_logic += "\n\t\t\tTHEN IFNULL(FSB.value:value<srcname>::STRING, FSB.value:value::STRING)"
    column_logic += "\n\t\t\tELSE ''"
    column_logic += "\n\t\t\tEND"
    column_logic += "\n\t\t), '')"
    column_logic += "\n\t) AS <colname>,"

    # name logic
    name_logic = "\n\tMAX("
    name_logic += "\n\t\tIFNULL(("
    name_logic += f"\n\t\t\tCASE WHEN TRIM(LOWER(FSB.value:label::STRING)) IN"
    name_logic += "\n\t\t\t\t(SELECT DISTINCT TRIM(LOWER(<colname>)) FROM &database.STAGE.FORMSTACKFORMQUESTIONS WHERE <colname> IS NOT NULL)"
    name_logic += "\n\t\t\tTHEN COALESCE(<srcname>, CASE WHEN FSB.value:value::STRING ILIKE '%{%' THEN NULL ELSE FSB.value:value::STRING END, '')"
    name_logic += "\n\t\t\tELSE ''"
    name_logic += "\n\t\t\tEND"
    name_logic += "\n\t\t), '')"
    name_logic += "\n\t) AS <colname>,"

    # address column logic
    address_logic = "\n\tMAX("
    address_logic += "\n\t\tIFNULL(("
    address_logic += f"\n\t\t\tCASE WHEN TRIM(LOWER(FSB.value:label::STRING)) IN"
    address_logic += "\n\t\t\t\t(SELECT DISTINCT TRIM(LOWER(<colname>)) FROM &database.STAGE.FORMSTACKFORMQUESTIONS WHERE <colname> IS NOT NULL)"
    address_logic += "\n\t\t\tTHEN IFNULL(FSB.value:value<srcname>::STRING, '')"
    address_logic += "\n\t\t\tELSE ''"
    address_logic += "\n\t\t\tEND"
    address_logic += "\n\t\t), '')"
    address_logic += "\n\t) AS <colname>,"

    # gender logic
    gender_logic = f"\n\tMAX("
    gender_logic += f"\n\t\tCASE WHEN"
    gender_logic += f"\n\t\t\tLOWER(FSB.value:label::STRING) IN ('gender')"
    gender_logic += f"\n\t\tTHEN IFNULL(FSB.value:value[0]::STRING, FSB.value:value::STRING)"
    gender_logic += f"\n\t\tELSE ''"
    gender_logic += f"\n\t\tEND"
    gender_logic += f"\n\t) AS <colname>,"

    # country logic
    country_logic = f"\n\tMAX("
    country_logic += f"\n\t\tCASE WHEN"
    country_logic += f"\n\t\t\tLOWER(FSB.value:label::STRING) IN ('country', 'countrycode')"
    country_logic += f"\n\t\tTHEN IFNULL(FSB.value:value[0]::STRING, FSB.value:value::STRING)"
    country_logic += f"\n\t\tELSE ''"
    country_logic += f"\n\t\tEND"
    country_logic += f"\n\t) AS <colname>,"

    # miscdata logic
    miscdata_logic = f"\n\tLISTAGG("
    miscdata_logic += f"\n\t\tCASE WHEN TRIM(LOWER(FSB.value:label::STRING)) IN"
    miscdata_logic += "\n\t\t\t\t(SELECT TRIM(LOWER(MISCDATA)) FROM &database.STAGE.FORMSTACKFORMQUESTIONS WHERE MISCDATA IS NOT NULL)"

    # for col in col_list:
    #     if col[1].lower() != "id" and col[1].lower() != "formname" and col[1].lower() != "formid" and col[1].lower() != "miscdata":
    #         miscdata_logic += f"\n\t\t\tSELECT TRIM(LOWER({col[1]})) AS MISCQUESTIONS FROM &database.STAGE.FORMSTACKFORMQUESTIONS WHERE {col[1]} IS NOT NULL"
    #         miscdata_logic += "\n\t\t\tUNION"
    #
    # miscdata_logic = miscdata_logic[:-9]

    # miscdata_logic += f"\n\t\t)"
    miscdata_logic += f"\n\t\tTHEN FDB.{field_name_col} || ': ' || IFNULL(FSB.value:value[0]::STRING, FSB.value:value::STRING)"
    miscdata_logic += f"\n\t\tELSE NULL"
    miscdata_logic += f"\n\t\tEND"
    miscdata_logic += f"\n\t, ', ') AS MiscData,"

# --------------------------------------------------------------------------------------------

    # MAIN RULE BUILD
    rulequerydoc = Document()
    rulequerydoc.append("INSERT INTO &database.IMPORT.FORMSTACKSUBMISSIONS")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tFILEDATE,")
    rulequerydoc.newline("\tFILENAME,")
    rulequerydoc.newline("\tFILEROWNUMBER,")

    # generate column list
    for col in col_list:
        rulequerydoc.newline(f"\t{col[1]},")

        if col[1].lower() == "id":
            select_columns += f"\n\tFSB.ID as {col[1]},"
        elif col[1].lower() == "formid":
            select_columns += f"\n\tFDB.FORMID AS FORMID,"
        elif col[1].lower() == "formname":
            select_columns += f"\n\tFDB.FORMNAME AS FORMNAME,"
        elif col[1].lower() == "sourceformname":
            select_columns += f"\n\tFDB.FORMNAME as SOURCEFORMNAME,"
        elif col[1].lower() == "sourceformid":
            select_columns += f"\n\tFDB.FORMID as SOURCEFORMID,"
        elif col[1].lower() == "timestamp":
            select_columns += f"\n\tMAX(FSB.timestamp) AS {col[1]},"

        # name and address related fields
        elif col[1].lower() == "firstname" or col[1].lower() == "middlename" or col[1].lower() == "lastname":
            # create list of srcnames
            srcnamelist = col[0].replace(" ","").split(",")
            srcnamereplace = ""
            for srcname in srcnamelist:
                srcnamereplace += f"FSB.value:value:{srcname}::STRING,"
            srcnamereplace = srcnamereplace.strip(",")

            # replace into select_columns
            select_columns += name_logic.replace("<srcname>", srcnamereplace).replace("<colname>", col[1])

        # address
        elif "address" in col[1].lower() or col[1].lower() == "city" or col[1].lower() == "state" or col[1].lower() == "zip":
            select_columns += address_logic.replace("<srcname>", f":{col[0]}").replace("<colname>", col[1])

        # country
        elif col[1].lower() == "country":
            select_columns += country_logic.replace("<colname>", col[1])

        # gender
        elif col[1].lower() == "gender":
            select_columns += gender_logic.replace("<colname>", col[1])

        # misc data
        elif col[1].lower() == "miscdata":
            select_columns += miscdata_logic

        # everything else
        else:
            select_columns += column_logic.replace("<srcname>", "[0]").replace("<colname>", col[1])

    rulequerydoc.trimend(1)

    rulequerydoc.newline(")")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tFSB.FILEDATE AS FILEDATE,")
    rulequerydoc.newline("\tFSB.FILENAME AS FILENAME,")
    rulequerydoc.newline("\tROW_NUMBER() OVER (PARTITION BY FSB.ID ORDER BY FSB.ID) AS FILEROWNUMBER,")

    rulequerydoc.append(select_columns)

    rulequerydoc.trimend(1)

    rulequerydoc.newline("FROM")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tSELECT DISTINCT")
    rulequerydoc.newline("\t\tFILEDATE,")
    rulequerydoc.newline("\t\tFILENAME,")
    rulequerydoc.newline("\t\tJSONDATA:id::STRING AS ID,")
    rulequerydoc.newline("\t\tvalue,")
    rulequerydoc.newline("\t\tJSONDATA:timestamp AS timestamp,")
    rulequerydoc.newline("\t\tkey")
    rulequerydoc.newline(f"\tFROM &database.IMPORT.FORMSTACKSUBMISSIONS_RAW SB, lateral flatten(input => JSONDATA:data)")
    rulequerydoc.newline(f"\tWHERE")
    rulequerydoc.newline(f"\t\tTO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    rulequerydoc.newline(f"\t\t(")
    rulequerydoc.newline(f"\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    rulequerydoc.newline(f"\t\t\tFROM &database.STAGE.FORMSTACKSUBMISSIONS")
    rulequerydoc.newline(f"\t\t)")
    rulequerydoc.newline(") FSB")
    rulequerydoc.newline("INNER JOIN")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline(f"\t\tFSFD.{field_id_col} AS FIELDID,")
    rulequerydoc.newline(f"\t\tFSFD.{field_name_col} AS FIELDNAME,")
    rulequerydoc.newline(f"\t\tFSFD.{field_label_col} AS FIELDLABEL,")
    rulequerydoc.newline(f"\t\tFSFD.{form_id_col} AS FORMID,")
    rulequerydoc.newline(f"\t\tFSF.{form_name_col} AS FORMNAME")
    rulequerydoc.newline("\tFROM")
    rulequerydoc.newline("\t\t&database.STAGE.FORMSTACKFORMDETAILS FSFD")
    rulequerydoc.newline("\tINNER JOIN")
    rulequerydoc.newline("\t\t&database.STAGE.FORMSTACKFORMS FSF")
    rulequerydoc.newline("\tON FSFD.FORMID = FSF.ID")
    rulequerydoc.newline(") FDB")
    rulequerydoc.newline(f"ON FSB.KEY = FDB.{field_id_col}")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline(f"\tFDB.{form_id_col} IN (")
    rulequerydoc.newline("\t\tSELECT ID")
    rulequerydoc.newline("\t\tFROM &database.STAGE.FORMSTACKFORMLIST")
    rulequerydoc.newline(f"\t\tWHERE ID <> {master_form_id}")
    rulequerydoc.newline("\t)")
    rulequerydoc.newline("GROUP BY")
    rulequerydoc.newline("\tFSB.FILEDATE,")
    rulequerydoc.newline("\tFSB.FILENAME,")
    rulequerydoc.newline("\tFSB.ID,")
    rulequerydoc.newline("\tFDB.FORMID,")
    rulequerydoc.newline("\tFDB.FORMNAME")
    rulequerydoc.newline(f";")

    return rulequerydoc