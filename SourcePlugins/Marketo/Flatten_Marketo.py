from Library.FunctionFiles.Functions import *

# Create FLATTENJSON CTE for use in Flatten SQL Insert query
def flattenjson(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()

    # if table_name_raw is empty, maybe due to the table being excluded from file transfers, use table_name and append _RAW
    if len(table_name_raw)<1:
        table_name_raw = f"{table_name.upper()}_RAW"

    # create JSON elements list
    for col in col_list:
        # wrap source field in double quotes
        if '"' in col[0]:
            src_col = f'{str(col[0])}'    
        else:
            src_col = f'"{str(col[0])}"'
        tbl_col = str(col[1]).upper()
        datatype = str(col[2]).upper()

        # build element list
        if tbl_col == "RESPONSEDATE" or tbl_col == "STARTTIME":
          jsonelements.append(f"\t\t'' AS {tbl_col}")
        elif tbl_col == "REQUESTDATE":
          jsonelements.append("\t\tTO_TIMESTAMP_LTZ(RPAD(raw.FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') AS REQUESTDATE")
        elif datatype == "ARRAY":
            jsonelements.append(f"\t\tCOALESCE(raw.JSONDATA:{src_col}::ARRAY, ARRAY_CONSTRUCT(NULL::STRING)) AS {tbl_col}")
        elif "VARCHAR" in datatype or "TIMESTAMP" in datatype or "NUMBER" in datatype or "DATETIME" in datatype:
            jsonelements.append(f"\t\traw.JSONDATA:{src_col}::STRING AS {tbl_col}")
        elif "VARIANT" in datatype:
            jsonelements.append(f"\t\tparse_json(raw.JSONDATA:{src_col}) AS {tbl_col}")
        else:
            jsonelements.append(f"\t\traw.JSONDATA:{src_col}::{datatype} AS {tbl_col}")

    flattendoc.append("\tSELECT")
    flattendoc.newline("\t\tRPAD(raw.FILEDATE,14,'0') AS FILEDATE,")
    flattendoc.newline("\t\traw.FILENAME,")
    flattendoc.newline("\t\traw.FILEROWNUMBER,")
    flattendoc.newlinelist(jsonelements)
    flattendoc.newline(f"\tFROM &database.IMPORT.{table_name_raw.upper()} raw")
    flattendoc.newline(f"\tWHERE")
    flattendoc.newline("\t\tTO_TIMESTAMP(RPAD(raw.FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t(")
    flattendoc.newline(f"\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t)")

    return flattendoc.out()