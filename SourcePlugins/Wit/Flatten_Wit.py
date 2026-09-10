from Library.FunctionFiles.Functions import *

# Create FLATTENJSON CTE for use in Flatten SQL Insert query
def flattenjson(table_name:str, table_name_raw:str, col_list:str):
    jsonelements = []
    flattendoc = Document()

    #WITLISTS
    if table_name.upper() == "WITLISTS":
        # create JSON elements list
        for col in col_list:
            src_col = str(col[0])
            if "VARCHAR" in col[2].upper() or "TIMESTAMP" in col[2] or "NUMBER" in col[2]:
                jsonelements.append(f"\t\traw.JSONDATA:{src_col}::STRING AS {col[1].upper()}")
            else:
                jsonelements.append(f"\t\traw.JSONDATA:{src_col}::{col[2].upper()} AS {col[1].upper()}")
        from_table = f"\tFROM &database.IMPORT.{table_name_raw} raw"

    #WITENTRIES
    elif table_name.upper() == "WITENTRIES":
        # create JSON elements list
        for col in col_list:
            src_col = str(col[0])
            tbl_col = str(col[1]).upper()
            datatype = str(col[2]).upper()

            if "ACTIVATION.ID" in col[0].upper():
                jsonelements.append(f"\t\traw.JSONDATA:{src_col}::STRING AS {tbl_col}")
            elif "VARCHAR" in datatype or "TIMESTAMP" in datatype or "NUMBER" in datatype or "DATETIME" in datatype:
                jsonelements.append(f"\t\te.VALUE:{src_col}::STRING AS {tbl_col}")
            elif "VARIANT" in datatype:
                jsonelements.append(f"\t\tparse_json(raw.JSONDATA:{src_col}) AS {tbl_col}")
            else:
                jsonelements.append(f"\t\te.VALUE:{src_col}::{datatype} AS {tbl_col}")

        from_table = f"\tFROM &database.IMPORT.WITLISTS_RAW raw, TABLE(flatten(JSONDATA:entries)) e"

    # create flatten query
    flattendoc.append("\tSELECT")
    flattendoc.newline("\t\tRPAD(raw.FILEDATE,14,'0') AS FILEDATE,")
    flattendoc.newline("\t\traw.FILENAME,")
    flattendoc.newline("\t\traw.FILEROWNUMBER,")
    flattendoc.newlinelist(jsonelements)
    flattendoc.newline(from_table)
    flattendoc.newline(f"\tWHERE")
    flattendoc.newline("\t\tTO_TIMESTAMP(RPAD(raw.FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t(")
    flattendoc.newline(
        f"\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t)")

    return flattendoc.out()