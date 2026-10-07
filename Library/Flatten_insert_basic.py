from Library.FunctionFiles.Functions import *

# Create FLATTENJSON CTE for use in Flatten SQL Insert query
def flatteninsert(table_name:str, table_name_raw:str, col_list:list):
    colelements = []
    flattendoc = Document()

    # if table_name_raw is empty, maybe due to the table being excluded from file transfers, use table_name and append _RAW
    if len(table_name_raw)<1:
        table_name_raw = f"{table_name.upper()}_RAW"

    # create JSON elements list
    for col in col_list:
        # wrap source field in double quotes
        if '"' in col[0]:
            src_col = f'{str(col[0]).strip()}'
        else:
            src_col = f'"{str(col[0]).strip()}"'
        tbl_col = str(col[1]).strip().upper()
        datatype = str(col[2]).strip().upper()

        # build element list
        if datatype == "ARRAY":
            colelements.append(f"\t\tCOALESCE(raw.{src_col}::ARRAY, ARRAY_CONSTRUCT(NULL::STRING)) AS {tbl_col}")
        elif "VARCHAR" in datatype or "TIMESTAMP" in datatype or "NUMBER" in datatype or "DATETIME" in datatype:
            colelements.append(f"\t\traw.{src_col}::STRING AS {tbl_col}")
        elif "VARIANT" in datatype:
            colelements.append(f"\t\tparse_json(raw.JSONDATA:{src_col}) AS {tbl_col}")
        else:
            colelements.append(f"\t\traw.{src_col}::{datatype} AS {tbl_col}")

    flattendoc.append("\tSELECT")
    flattendoc.newline("\t\tRPAD(raw.FILEDATE,14,'0') AS FILEDATE,")
    flattendoc.newline("\t\traw.FILENAME,")
    flattendoc.newline("\t\traw.FILEROWNUMBER,")
    flattendoc.newlinelist(colelements)
    flattendoc.newline(f"\tFROM &database.IMPORT.{table_name_raw.upper()} raw")
    flattendoc.newline(f"\tWHERE")
    flattendoc.newline("\t\tTO_TIMESTAMP(RPAD(raw.FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t(")
    flattendoc.newline(f"\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t)")

    return flattendoc.out()