from Library.Class.Document import *
import Library.Flatten_basic as Flatten_basic

def flattenjson_seatgeekevents(table_name:str, table_name_raw:str, col_list:list):
    flattendoc = Document()

    def split_show_name(source_column:str, column_name:str):
        colstring = f"\tsplit({source_column},',')[Show_Name.index]::string AS {column_name},"
        return colstring

    def replace_string(source_column:str, column_name:str):
        colstring = f"\t\tREPLACE(REPLACE(REPLACE({source_column}.value::string, '[',''), '\"', ''), ']','') AS {column_name},"
        return colstring

    def flatten_table(output_name:str, table_to_parse:str="PRODUCT_DETAILS"):
        if output_name != "Show_Name":
            output_name = output_name.upper()

        tablestring = f"\t\tLATERAL FLATTEN(input => PARSE_JSON({table_to_parse}), OUTER => true) {output_name},"
        return tablestring

    outer_select_columns = Document()
    inner_select_columns = Document()
    flatten_tables = Document()
    where_clause = Document()
    for col in col_list:
        src_col = col[0].strip()
        tbl_col = col[1].strip()
        if tbl_col.upper() == "EVENT_PRODUCT_ID":
            outer_select_columns.newline(f"\t{src_col.upper()} AS {tbl_col.upper()},")
            inner_select_columns.newline(f"\t\t{src_col},")
        elif tbl_col.upper() == "EVENT_DATE":
            outer_select_columns.newline(f"\t{src_col},")
            inner_select_columns.newline(f"\t\t{src_col},")
        elif tbl_col.upper() == "EVENT":
            outer_select_columns.newline(f"\t{src_col}.value::string AS {tbl_col},")
            inner_select_columns.newline(replace_string(src_col, src_col))
            flatten_tables.newline(flatten_table(src_col))
            where_clause.newline(f"\t\t{src_col}.path = '{src_col}' AND")
        elif tbl_col.upper() == "EVENT_TIER":
            outer_select_columns.newline(split_show_name(src_col.upper(),tbl_col))
            inner_select_columns.newline(replace_string(src_col.upper(),src_col.upper()))
            flatten_tables.newline(flatten_table(src_col))
            where_clause.newline(f"\t\t{src_col.upper()}.path = '{src_col}' AND")
        elif tbl_col.upper() == "SEASONNAME":
            outer_select_columns.newline(f"\tREPLACE(split({src_col.upper()},',')[Show_Name.index]::string, 'HISTORIC', year(to_datetime(EVENT_DATE))) AS {tbl_col.upper()},")
            inner_select_columns.newline(replace_string(src_col.upper(), src_col.upper()))
            flatten_tables.newline(flatten_table(src_col))
            where_clause.newline(f"\t\t{src_col.upper()}.path = '{src_col}' AND")
        else:
            outer_select_columns.newline(split_show_name(tbl_col.upper(), tbl_col.upper()))
            inner_select_columns.newline(replace_string(src_col.upper(), tbl_col.upper()))
            flatten_tables.newline(flatten_table(src_col))
            where_clause.newline(f"\t\t{src_col.upper()}.path = '{src_col}' AND")

    outer_select_columns.trimend(1)
    inner_select_columns.trimend(1)
    flatten_tables.trimend(1)
    where_clause.newline("\t\tproduct_type = 'Event'")

    inner_select = Document()

    inner_select.newline("\tSELECT")
    inner_select.newline("\t\tFILEDATE,")
    inner_select.newline("\t\tFILENAME,")
    inner_select.newline("\t\tFILEROWNUMBER,")
    inner_select.newline(inner_select_columns.out())
    inner_select.newline("\tFROM")
    inner_select.newline("\t\t&database.IMPORT.SEATGEEKPRODUCTS,")
    inner_select.newline(flatten_tables.out())
    inner_select.newline("\tWHERE")
    inner_select.newline(where_clause.out())

    flattendoc.newline("SELECT")
    flattendoc.newline("\tFILEDATE,")
    flattendoc.newline("\tFILENAME,")
    flattendoc.newline("\tFILEROWNUMBER,")
    flattendoc.newline(outer_select_columns.out())
    flattendoc.newline("FROM (")
    flattendoc.newline(inner_select.out())
    flattendoc.newline("),")
    flattendoc.newline("LATERAL FLATTEN(input => split(Show_Name, ','), OUTER => TRUE) Show_Name")

    return flattendoc.out()

def flattenjson_seatgeekplans(table_name:str, table_name_raw:str, col_list:list):
    flattendoc = Document()

    def split_string(source_column:str, column_name:str, data_type:str):
        inner_split = f"IFNULL(split({source_column.upper()}, ',')[event.index]::string, split({source_column.upper()}, ',')[0]::string)"

        if "NUMBER" in data_type:
            colstring = f"\tTRY_CAST({inner_split} AS INT) AS {column_name.upper()},"
        else:
            colstring = f"\t{inner_split} AS {column_name},"
        return colstring

    def replace_string(source_column: str, column_name: str):
        colstring = f"\t\tREPLACE(REPLACE(REPLACE({source_column}.value::string, '[',''), '\"', ''), ']','') AS {column_name.upper()},"
        return colstring

    def flatten_table(output_name: str, table_to_parse: str = "PRODUCT_DETAILS"):
        tablestring = f"\t\tLATERAL FLATTEN(input => PARSE_JSON({table_to_parse}), OUTER => true) {output_name.lower()},"
        return tablestring

    outer_select_columns = Document()
    inner_select_columns = Document()
    flatten_tables = Document()
    where_clause = Document()
    for col in col_list:
        src_col = col[0].strip()
        tbl_col = col[1].strip()
        if tbl_col.upper() == "PLAN_PRODUCT_ID":
            outer_select_columns.newline(f"\t{src_col} AS {tbl_col.upper()},")
            inner_select_columns.newline(f"\t\t{src_col},")
        elif tbl_col.upper() == "EVENT":
            outer_select_columns.newline(f"\t{src_col.lower()}.value::string AS {tbl_col.upper()},")
            inner_select_columns.newline(replace_string(src_col.lower(), src_col.lower()))
            flatten_tables.newline(flatten_table(src_col))
            where_clause.newline(f"\t\t{src_col}.path = '{tbl_col}' AND")
        elif tbl_col.upper() == "EVENT_DATE":
            outer_select_columns.newline(f"\tTRY_CAST(split({src_col.lower()}, ',')[event.index]::string AS TIMESTAMP) AS {tbl_col.upper()},")
            inner_select_columns.newline(replace_string(src_col.lower(), src_col.lower()))
            flatten_tables.newline(flatten_table(src_col))
            where_clause.newline(f"\t\t{src_col}.path = '{tbl_col}' AND")
        elif tbl_col.upper() == "PLANNAME":
            outer_select_columns.newline(f"\t{src_col.upper()} AS {tbl_col.upper()},")
            inner_select_columns.newline(f"\t\t{src_col.upper()},")
        else:
            outer_select_columns.newline(split_string(tbl_col.upper(), tbl_col.upper(), col[2]))
            inner_select_columns.newline(replace_string(src_col, tbl_col.upper()))
            flatten_tables.newline(flatten_table(src_col))
            where_clause.newline(f"\t\t{src_col}.path = '{tbl_col}' AND")

    outer_select_columns.trimend(1)
    inner_select_columns.trimend(1)
    flatten_tables.trimend(1)
    where_clause.newline("\t\tproduct_type = 'Series'")

    inner_select = Document()

    inner_select.newline("\tSELECT")
    inner_select.newline("\t\tFILEDATE,")
    inner_select.newline("\t\tFILENAME,")
    inner_select.newline("\t\tFILEROWNUMBER,")
    inner_select.newline(inner_select_columns.out())
    inner_select.newline("\tFROM")
    inner_select.newline("\t\t&database.IMPORT.SEATGEEKPRODUCTS,")
    inner_select.newline(flatten_tables.out())
    inner_select.newline("\tWHERE")
    inner_select.newline(where_clause.out())

    flattendoc.newline("SELECT")
    flattendoc.newline("\tFILEDATE,")
    flattendoc.newline("\tFILENAME,")
    flattendoc.newline("\tFILEROWNUMBER,")
    flattendoc.newline(outer_select_columns.out())
    flattendoc.newline("FROM (")
    flattendoc.newline(inner_select.out())
    flattendoc.newline("),")
    flattendoc.newline("LATERAL FLATTEN(input => split(event, ','), OUTER => TRUE) event")

    return flattendoc.out()

def flattenjson(table_name:str, table_name_raw:str, col_list:list):
    # get table name
    table_name = table_name.upper().replace("_","")

    if table_name == "SEATGEEKEVENTS":
        flattendoc = flattenjson_seatgeekevents(table_name, table_name_raw, col_list)
    elif table_name == "SEATGEEKPLANS":
        flattendoc = flattenjson_seatgeekplans(table_name, table_name_raw, col_list)
    else:
        flattendoc = Flatten_basic.flattenjson(table_name, table_name_raw, col_list)

    return flattendoc