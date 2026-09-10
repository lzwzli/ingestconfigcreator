from Library.Class.Document import *
import Library.Flatten_basic as Flatten_basic

def flattenjson_podiumcontacts(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()

    def array_item(src_col:str, tbl_col:str, index:int):
        colstring = f"\t\tparse_json(raw.JSONDATA:{src_col})[{index}]::STRING AS {tbl_col}"
        return colstring

    # create JSON elements list
    for col in col_list:
        # wrap source field in double quotes
        if '"' in col[0]:
            src_col = f'{str(col[0])}'
        else:
            src_col = f'"{str(col[0])}"'
        tbl_col = str(col[1]).upper()
        if tbl_col == "FIRST_NAME":
            tbl_col = "NAME"
        datatype = str(col[2]).upper()

        # build element list
        if "_NAME" in col[1].upper() and col[1].upper() != "FULL_NAME":
            continue
        elif col[1].upper() == "EMAIL":
            jsonelements.append(array_item(src_col, tbl_col, 0))
        elif "PHONE" in col[1].upper() and col[1][-1].isnumeric():
            # get index from phone column name
            ph_ind = int(col[1][-1])-1
            jsonelements.append(array_item(src_col, tbl_col, ph_ind))
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


def flattenjson_podiummessages(table_name: str, table_name_raw: str, col_list: list):
    jsonelements = []
    flattendoc = Document()

    def array_item(src_col: str, tbl_col: str, col_type:str):
        # split parent and child field
        if "." in src_col:
            src_col_split = src_col.split(".")
            src_col0 = src_col_split[0].strip('"')
            src_col1 = src_col_split[1].strip('"')
        else:
            src_col0 = src_col
            src_col1 = ""

        # determine element index as attachment info will be at index 0 if it exists
        if col_type == "message":
            index1 = 1
            index2 = 0
        else:
            index1 = 0
            index2 = 1

        colstring = f"\t\tCASE\n"
        colstring += f"\t\t\tWHEN parse_json(raw.JSONDATA:\"items\")[0]::VARIANT:\"type\"::STRING = 'attachment'\n"
        colstring += f"\t\t\tTHEN parse_json(raw.JSONDATA:\"{src_col0}\")[{index1}]::VARIANT:\"{src_col1}\"::STRING\n"
        colstring += f"\t\t\tELSE parse_json(raw.JSONDATA:\"{src_col0}\")[{index2}]::VARIANT:\"{src_col1}\"::STRING\n"
        colstring += f"\t\tEND AS {tbl_col}"

        return colstring

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
        if "ITEM" in col[0].upper() and "MESSAGE" in col[1].upper():
            jsonelements.append(array_item(src_col, tbl_col, "message"))
        elif "ITEM" in col[0].upper() and "ATTACHMENT" in col[1].upper():
            jsonelements.append(array_item(src_col, tbl_col, "attachment"))
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


def flattenjson(table_name:str, table_name_raw:str, col_list:list):
    if table_name.upper() == "PODIUMCONTACTS":
        flattendoc = flattenjson_podiumcontacts(table_name, table_name_raw, col_list)
    elif table_name.upper() == "PODIUMMESSAGES":
        flattendoc = flattenjson_podiummessages(table_name, table_name_raw, col_list)
    else:
        flattendoc = Flatten_basic.flattenjson(table_name, table_name_raw, col_list)

    return flattendoc