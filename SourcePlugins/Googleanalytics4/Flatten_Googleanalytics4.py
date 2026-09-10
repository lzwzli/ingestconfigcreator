from Library.FunctionFiles.Functions import *

# Create FLATTENJSON CTE for use in Flatten SQL Insert query
def flattenjson(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    dimelements = []
    flattendoc = Document()

    # define dimensions
    if 'PAGES' in table_name.upper():
        dimensions = ['date', 'pageTitle']
    else:
        dimensions = ['date']

    dim_index = 0
    for dim in dimensions:
        dimelements.append(f"\t\tGET_PATH(dimval[{dim_index}], 'value')::STRING AS {dim}")
        dim_index += 1

    # create JSON elements list
    metricList = ""
    for col in col_list:
        src_col = str(col[0])
        tbl_col = str(col[1]).upper()
        datatype = str(col[2]).upper()

        if src_col not in dimensions:
            metricList += f"'{src_col}',"
            if datatype == "ARRAY":
                jsonelements.append(f"\t\tCOALESCE(raw.JSONDATA:{src_col}::ARRAY, ARRAY_CONSTRUCT(NULL::STRING)) AS {tbl_col}")
            elif "VARCHAR" in datatype or "TIMESTAMP" in datatype or "NUMBER" in datatype or "DATETIME" in datatype:
                jsonelements.append(f"\t\t\"'{src_col}'\"::STRING AS {tbl_col}")
            else:
                jsonelements.append(f"\t\t\"'{src_col}'\"::{datatype} AS {tbl_col}")

    metricList = metricList[:-1]

    # create flatten query
    flattendoc.append("\tSELECT")
    flattendoc.newline("\t\tRPAD(FILEDATE,14,'0') AS FILEDATE,")
    flattendoc.newline("\t\tFILENAME,")
    flattendoc.newline("\t\trowid AS FILEROWNUMBER,")
    flattendoc.newlinelist(dimelements)
    flattendoc.append(",")
    flattendoc.newlinelist(jsonelements)
    flattendoc.newline("\tFROM (")
    flattendoc.newline("\t\tSELECT")
    flattendoc.newline("\t\t\tmv.FILEDATE,")
    flattendoc.newline("\t\t\tmv.FILENAME,")
    flattendoc.newline("\t\t\tmv.rowId,")
    flattendoc.newline("\t\t\tmv.dimVal,")
    flattendoc.newline("\t\t\tmv.metricVal,")
    flattendoc.newline("\t\t\tmetricName")
    flattendoc.newline("\t\tFROM")
    flattendoc.newline("\t\t(")
    flattendoc.newline("\t\t\tSELECT")
    flattendoc.newline("\t\t\t\tFILEDATE,")
    flattendoc.newline("\t\t\t\tFILENAME,")
    flattendoc.newline("\t\t\t\trowval.index AS rowId,")
    flattendoc.newline("\t\t\t\trowval.value:dimensionValues AS dimVal,")
    flattendoc.newline("\t\t\t\tmetricval.index AS metricId,")
    flattendoc.newline("\t\t\t\tmetricval.value:value::STRING AS metricVal")
    flattendoc.newline(f"\t\t\tFROM")
    flattendoc.newline(f"\t\t\t\t&database.IMPORT.{table_name_raw},")
    flattendoc.newline(f"\t\t\t\tTABLE(FLATTEN(JSONDATA:rows)) rowVal,")
    flattendoc.newline(f"\t\t\t\tTABLE(FLATTEN(rowVal.value:metricValues)) metricVal")
    flattendoc.newline(f"\t\t\tWHERE")
    flattendoc.newline("\t\t\t\tTO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t\t\t(")
    flattendoc.newline(f"\t\t\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t\t\t)")
    flattendoc.newline("\t\t) mv")
    flattendoc.newline("\t\tINNER JOIN")
    flattendoc.newline("\t\t(")
    flattendoc.newline("\t\t\tSELECT")
    flattendoc.newline("\t\t\t\tmetricH.index AS metricId,")
    flattendoc.newline("\t\t\t\tmetricH.value:name::STRING AS metricName")
    flattendoc.newline(f"\t\t\tFROM")
    flattendoc.newline(f"\t\t\t\t&database.IMPORT.{table_name_raw},")
    flattendoc.newline(f"\t\t\t\tTABLE(FLATTEN(JSONDATA:metricHeaders)) metricH")
    flattendoc.newline(f"\t\t\tWHERE")
    flattendoc.newline("\t\t\t\tTO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t\t\t(")
    flattendoc.newline(f"\t\t\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t\t\t)")
    flattendoc.newline("\t\t) mn")
    flattendoc.newline("\tON mv.metricId = mn.metricId")
    flattendoc.newline("\t) raw")
    flattendoc.newline(f"\tPIVOT(MAX(metricVal) FOR metricName IN ({metricList}))")
    flattendoc.newline("\tORDER BY rowId")

    return flattendoc.out()