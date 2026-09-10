from Library.FunctionFiles.Functions import *

# Create FLATTENJSON CTE for use in Flatten SQL Insert query
def flattenjson(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()

    # array header strings
    lineitems = '"p"."line_items"'
    statehistory = '"p"."state_history"'
    transactionhistory = '"p"."transaction_history"'

    # initialize table from
    from_table = f"\tFROM &database.IMPORT.VENUENEXTSTADIUMORDERSTATEEVENTS_RAW raw"

    # create JSON elements list
    for col in col_list:
        # map source column
        if '"' in col[0]:
            src_col = col[0]
        else:
            src_col = f'"{col[0]}"'

        # map table column name
        tbl_col = col[1].upper()

        # map data type
        datatype = col[2].upper()

        # line items
        if lineitems in src_col:
            src_col = src_col.replace(f"{lineitems}.", "")
            jsonelements.append(f"\t\tline_items.VALUE:{src_col}::STRING AS {tbl_col}")
            if "line_items" not in from_table:
                from_table = f"{from_table}, TABLE(flatten(JSONDATA:{lineitems})) line_items"
        elif statehistory in src_col:
            src_col = src_col.replace(f"{statehistory}.", "")
            jsonelements.append(f"\t\tstate_history.VALUE:{src_col}::STRING AS {tbl_col}")
            if "state_history" not in from_table:
                from_table = f"{from_table}, TABLE(flatten(JSONDATA:{statehistory})) state_history"
        elif transactionhistory in src_col:
            src_col = src_col.replace(f"{transactionhistory}.", "")
            jsonelements.append(f"\t\ttransaction_history.VALUE:{src_col}::STRING AS {tbl_col}")
            if "transaction_history" not in from_table:
                from_table = f"{from_table}, TABLE(flatten(JSONDATA:{transactionhistory})) transaction_history"
        else:
            jsonelements.append(f"\t\traw.JSONDATA:{src_col}::{datatype} AS {tbl_col}")


    # from_table = f"\tFROM &database.IMPORT.{table_name_raw} raw, TABLE(flatten(JSONDATA:\"p\".\"line_items\")) line_items"

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