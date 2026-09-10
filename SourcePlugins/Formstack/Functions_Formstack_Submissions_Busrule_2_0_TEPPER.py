from Library.FunctionFiles.Functions import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Submissions rule 2_0 for historical inserts
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fn_submissions_bus_rule_2_0(col_list:list, pk_list:list, field_name_col:str, form_name_col:str, form_id_col:str, variant_col:str, field_id_col:str, master_form_id:str):

    rulequerydoc = Document()
    rulequerydoc.append("INSERT INTO &database.IMPORT.FORMSTACKSUBMISSIONS")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tFILEDATE,")
    rulequerydoc.newline("\tFILENAME,")
    rulequerydoc.newline("\tFILEROWNUMBER,")

    # generate column list for import table
    for col in col_list:
        rulequerydoc.newline(f"\t{col[1]},")

    rulequerydoc.trimend(1)
    rulequerydoc.newline(")")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tCURRENT_DATE() AS FILEDATE,")
    rulequerydoc.newline("\t1 AS FILENAME,")
    rulequerydoc.newline(f"\tROW_NUMBER() OVER (PARTITION BY {pk_list[0]} ORDER BY {pk_list[0]}) AS FILEROWNUMBER,")

    # generate SELECT column logic
    for col in col_list:
        if col[1].upper() == "ID":
            rulequerydoc.newline(f"\tFSB.{col[0]} AS ID,")

        elif col[1].upper() == "FORMNAME":
            rulequerydoc.newline(f"\tMAX(COALESCE(NULLIF(CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('{col[0]}') THEN FSB.value:value::string ELSE '' END, ''), CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('{col[0]}') THEN FDB.{form_name_col} ELSE '' END)) AS FORMNAME,")

        elif col[1].upper() == "FORMID":
            rulequerydoc.newline(f"\tMAX(COALESCE(NULLIF(CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('{col[0]}') THEN FSB.value:value::string ELSE '' END, ''), CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('{col[0]}') THEN FSB.{form_id_col} ELSE '' END)) AS FORMID,")

        elif col[1].upper() == "TIMESTAMP":
            rulequerydoc.newline(f"\tMAX(FSB.{col[0]}) AS TIMESTAMP,")

        elif col[1].upper() == "FIRSTNAME":
            rulequerydoc.newline(f"\tMAX(CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('name') THEN SPLIT(FSB.value:value::string,' ')[0] ELSE '' END) AS {col[1].upper()},")

        elif col[1].upper() == "LASTNAME":
            rulequerydoc.newline(f"\tMAX(CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('name') THEN SPLIT(FSB.value:value::string,' ')[1] ELSE '' END) AS {col[1].upper()},")

        elif col[1].upper() == "ZIPCODE":
            rulequerydoc.newline(f"\tMAX(CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('address') THEN IFNULL(FSB.value:value[0]::STRING, FSB.value:value::STRING) ELSE '' END) AS {col[1].upper()},")

        elif col[1].upper() == "ADDRESS1" or col[1].upper() == "ADDRESS2":
            rulequerydoc.newline(f"\t'' AS {col[1].upper()},")

        else:
            rulequerydoc.newline(f"\tMAX(CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('{col[0]}') THEN IFNULL(FSB.value:value[0]::STRING, FSB.value:value::STRING) ELSE '' END) AS {col[1].upper()},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline("FROM")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\t*")
    rulequerydoc.newline("\tFROM")
    rulequerydoc.newline(f"\t\t&database.IMPORT.FORMSTACKSUBMISSIONSBLOB sb, lateral flatten(input => {variant_col}:data)")
    rulequerydoc.newline(") FSB")
    rulequerydoc.newline("INNER JOIN")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline(f"\t\t{field_id_col} AS FIELDID,")
    rulequerydoc.newline(f"\t\t{field_name_col} AS FIELDNAME,")
    rulequerydoc.newline(f"\t\t{form_id_col} AS FORMID,")
    rulequerydoc.newline(f"\t\t{form_name_col} AS FORMNAME")
    rulequerydoc.newline("\tFROM")
    rulequerydoc.newline("\t\t&database.STAGE.FORMSTACKFORMDETAILSBLOB")
    rulequerydoc.newline(") FDB")
    rulequerydoc.newline(f"ON FSB.KEY = FDB.{field_id_col}")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline(f"\tFDB.FORMID = {master_form_id}")
    rulequerydoc.newline("GROUP BY")
    rulequerydoc.newline("\tFSB.ID,")
    rulequerydoc.newline(f"\tFDB.{form_name_col},")
    rulequerydoc.newline("\tFSB.FORMID")
    rulequerydoc.newline(";")

    return rulequerydoc