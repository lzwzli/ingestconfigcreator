from Library.FunctionFiles.Functions import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Submissions rule 2_0 for historical inserts
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def fn_submissions_bus_rule_2_0(col_list:list, pk_list:list, field_id_col:str, field_name_col:str, field_label_col:str, form_name_col:str, form_id_col:str, master_form_id:str):

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
    rulequerydoc.newline("\tFSB.FILEDATE AS FILEDATE,")
    rulequerydoc.newline("\tFSB.FILENAME AS FILENAME,")
    rulequerydoc.newline(f"\tROW_NUMBER() OVER (PARTITION BY FSB.JSONDATA:id::STRING ORDER BY FSB.JSONDATA:id::STRING) AS FILEROWNUMBER,")

    # generate SELECT column logic
    for col in col_list:
        # build compound comparison string if multiple src columns are provided
        src_col_comp = ""
        if "," in col[0]:
            src_col_list = col[0].split(",")
            for src_col in src_col_list:
                src_col_comp += f"LOWER(FDB.{field_name_col}) = LOWER('{src_col.strip()}') OR "
            src_col_comp = src_col_comp[:-4]
        # else just do a simple comparison
        else:
            src_col_comp = f"LOWER(FDB.{field_name_col}) = LOWER('{col[0].strip()}')"

        if col[1].upper() == "ID":
            rulequerydoc.newline(f"\tFSB.JSONDATA:id::STRING AS ID,")

        elif col[1].upper() == "FORMNAME":
            rulequerydoc.newline(f"\tMAX(COALESCE(NULLIF(CASE WHEN LOWER(FDB.{field_label_col}) = LOWER('{col[0]}') THEN FSB.value:value::string ELSE '' END, ''), CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('{col[0]}') THEN FDB.FORMNAME ELSE '' END)) AS FORMNAME,")

        elif col[1].upper() == "FORMID":
            rulequerydoc.newline("\tFDB.FORMID AS FORMID,")

        elif col[1].upper() == "SOURCEFORMID":
            rulequerydoc.newline(f"\tMAX(COALESCE(NULLIF(CASE WHEN LOWER(FDB.{field_label_col}) = LOWER('{col[0]}') THEN FSB.value:value::string ELSE '' END, ''), CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('{col[0]}') THEN FDB.FORMID ELSE '' END)) AS SOURCEFORMID,")

        elif col[1].upper() == "TIMESTAMP":
            rulequerydoc.newline(f"\tMAX(FSB.JSONDATA:{col[0]}::STRING) AS TIMESTAMP,")

        else:
            # rulequerydoc.newline(f"\tMAX(CASE WHEN LOWER(FDB.{field_name_col}) = LOWER('{col[0]}') THEN IFNULL(FSB.value:value[0]::STRING, FSB.value:value::STRING) ELSE '' END) AS {col[1].upper()},")
            rulequerydoc.newline(f"\tMAX(CASE WHEN {src_col_comp} THEN IFNULL(FSB.value:value[0]::STRING, FSB.value:value::STRING) ELSE '' END) AS {col[1].upper()},")
    rulequerydoc.trimend(1)

    rulequerydoc.newline("FROM")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline("\t\t*")
    rulequerydoc.newline("\tFROM")
    rulequerydoc.newline(f"\t\t&database.IMPORT.FORMSTACKSUBMISSIONS_RAW raw, lateral flatten(input => JSONDATA:data)")
    rulequerydoc.newline(f"\tWHERE")
    rulequerydoc.newline(f"\t\tTO_TIMESTAMP(RPAD(raw.FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    rulequerydoc.newline(f"\t\t(")
    rulequerydoc.newline(f"\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    rulequerydoc.newline(f"\t\t\tFROM &database.STAGE.FORMSTACKSUBMISSIONS")
    rulequerydoc.newline(f"\t\t)")
    rulequerydoc.newline(") FSB")
    rulequerydoc.newline("INNER JOIN")
    rulequerydoc.newline("(")
    rulequerydoc.newline("\tSELECT")
    rulequerydoc.newline(f"\t\tFSFD.{field_id_col} AS FIELDID,")
    rulequerydoc.newline(f"\t\tFSFD.{field_label_col} AS FIELDLABEL,")
    rulequerydoc.newline(f"\t\tFSFD.{field_name_col} AS FIELDNAME,")
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
    rulequerydoc.newline(f"\tFDB.FORMID = {master_form_id}")
    rulequerydoc.newline("GROUP BY")
    rulequerydoc.newline("\tFSB.FILEDATE,")
    rulequerydoc.newline("\tFSB.FILENAME,")
    rulequerydoc.newline("\tFSB.FILEROWNUMBER,")
    rulequerydoc.newline("\tFSB.JSONDATA:id::STRING,")
    rulequerydoc.newline(f"\tFDB.FORMNAME,")
    rulequerydoc.newline("\tFDB.FORMID")
    rulequerydoc.newline(";")

    return rulequerydoc