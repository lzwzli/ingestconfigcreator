from Library.FunctionFiles.Functions import *

# Create FLATTENJSON CTE for use in Flatten SQL Insert query
def flattenjson(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()
    # create JSON elements list
    for col in col_list:
        src_col_raw = str(col[0])

        src_col = f'"{src_col_raw.replace(".",'"."')}"'

        tbl_col = str(col[1]).upper()
        datatype = str(col[2]).upper()

        if (table_name.upper() == "SHOPIFYCUSTOMERS" and tbl_col == "CUSTOMERID") or (table_name.upper() == "SHOPIFYINVENTORY" and tbl_col == "INVENTORYITEMID") or (table_name.upper() == "SHOPIFYORDERLINEITEMS" and (tbl_col == "ORDERID" or tbl_col == "PRODUCTID")) or (table_name.upper() == "SHOPIFYORDERS" and (tbl_col == "CUSTOMERID" or tbl_col == "ORDERID")) or (table_name.upper() == "SHOPIFYPRODUCTS" and tbl_col == "PRODUCTID"):
          if "VARCHAR" in datatype or "TIMESTAMP" in datatype or "NUMBER" in datatype or "DATETIME" in datatype:
              jsonelements.append(f"\t\tSPLIT_PART(raw.JSONDATA:{src_col}::STRING, '/', -1) AS {tbl_col}")
          else:
            jsonelements.append(f"\t\tSPLIT_PART(raw.JSONDATA:{src_col}::{datatype}, '/', -1) AS {tbl_col}")
        elif table_name.upper() == "SHOPIFYINVENTORY" and tbl_col == "INVENTORYLEVELID":
          jsonelements.append(f"\t\tSPLIT_PART(SPLIT_PART(raw.JSONDATA:{src_col}::STRING, '/', 5), '?', 1) || '-' || SPLIT_PART(SPLIT_PART(raw.JSONDATA:{src_col}::STRING, '=', 2), '?', 1) AS {tbl_col}")
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
    flattendoc.newline(f"\tFROM &database.IMPORT.{table_name_raw} raw")
    flattendoc.newline(f"\tWHERE")
    flattendoc.newline("\t\tTO_TIMESTAMP(RPAD(raw.FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t(")
    flattendoc.newline(f"\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t)")
    if table_name.upper() == "SHOPIFYINVENTORY" or table_name.upper() == "SHOPIFYORDERLINEITEMS":
        flattendoc.newline("\t\tAND JSONDATA:__parentId::STRING IS NOT NULL")

    return flattendoc.out()
