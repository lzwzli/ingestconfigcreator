from SourcePlugins.Fanatics.BusRule_FanaticsOrderDetails import *
from SourcePlugins.Fanatics.BusRule_FanaticsUserDetails import *

need_acquire = 1

# add business rules
def fn_busrules_append(worksheet:object, bus_rule_obj:object, db_folder:str, runlog:object):
    runlog.log("")
    runlog.log("Adding Fanatics specific business rules")

    # get table name
    table_name = worksheet.table_name()

    # get primary keys
    pk = worksheet.primary_keys()

    # get column list
    col_list = worksheet.columns()

    # add rules for FanaticsOrderDetails
    if table_name.upper() == "FANATICSORDERDETAILS":
        fanaticsorderdetails_busrules(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, db_folder=db_folder, runlog=runlog)

        runlog.log("")
        return

    # add rules for FanaticsUserDetails
    elif table_name.upper() == "FANATICSUSERDETAILS":
        fanaticsuserdetails_busrules(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, db_folder=db_folder, runlog=runlog)

        runlog.log("")
        return

# append sources config
def fn_sources_append(worksheet:object, db_folder:str, sources_obj:object, runlog:object, repo_root_folder:str, client:str, source_name:str):
    runlog.log("Running Fanatics specific sources append function")

    # get table name
    table_name = worksheet.table_name().upper()

    # add RowCountCheckOverride if table is order details or user details
    if table_name == "FANATICSORDERDETAILS" or table_name == "FANATICSUSERDETAILS":
        runlog.log(f"Add rowCountCheckOverride = 1 in {table_name} sources file")
        sources_obj.append("rowCountCheckOverride", 1)
        sources_obj.append("importSql", "NOTRUNCATE")

    return

# create acquire file
def fn_create_acquire_file(file_match_list:list, table_name_list:list, db_folder:str, runlog:object, client:str, repo_root_folder:str, acquire_custom_info_list:list):
    print_section(msg="Working on Acquire File", runlog=runlog)

    acquire_file = {}

    # create sourceFile key value dictionary per file pattern
    sourceFile_list = []

    encryption = None

    for file_text in file_match_list:
        if file_text.upper() != "EXCLUDEFROMFILETRANSFERS":
            sourceFile_dict = {}
            file_pattern = file_text.replace(".*", "*")
            subdirectory = None

            sourceFile_dict["fileMatchPattern"] = file_pattern
            sourceFile_dict["subdirectory"] = subdirectory

            sourceFile_list.append(sourceFile_dict)

            if ".gpg" in file_text.lower():
                encryption = "gpg"

    acquire_file["sourceFile"] = sourceFile_list
    acquire_file["zipFoldername"] = None
    acquire_file["baseDirectory"] = "<fill in parent directory path>"

    acquire_file["encryption"] = encryption
    acquire_file["deleteFileFromSource"] = True

    # filename
    filename = f"acquire.json"

    # output JSON file
    writeJSON(filecontent=acquire_file, filename=filename, filetype="acquire", client=client, source_name="fanatics", db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

    return

def fn_create_truncate_query_custom(table_name:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str):
    if table_name.upper() == "FANATICSFEEDIMPORT":
        create_truncate_query(table_name=table_name, db_folder=db_folder, runlog=runlog, repo_root_folder=repo_root_folder, source_name=source_name, client=client)
    else:
        return

    return

def fn_ctrl_ra_src_query_custom(table_name:str, tbl_alias:str, col_list_all:list, col_logic_list:dict):
    src_query = Document()
    src_query.append("SELECT * FROM (")
    src_query.newline("\tSELECT DISTINCT")

    for col in col_list_all:
        if col == "SOURCEINSERTDATE":
            src_query.newline(f"\t\tIFNULL(MIN(od.SOURCEINSERTDATE), MIN({tbl_alias}.DWINSERTDATE)) AS SOURCEINSERTDATE,")
        elif col == "SOURCEUPDATEDATE":
            src_query.newline(f"\t\tIFNULL(MAX(od.SOURCEUPDATEDATE), MAX({tbl_alias}.DWUPDATEDATE)) AS SOURCEUPDATEDATE,")
        else:
            src_query.newline(f"\t\t{col_logic_list[col][1]} AS {col_logic_list[col][0]},")

    src_query.newline(f"\t\t{col_logic_list['STANDARDIZATIONROWID'][1]} AS {col_logic_list['STANDARDIZATIONROWID'][0]},")
    src_query.newline(f"\t\t{col_logic_list['VALIDEMAIL'][1]} AS {col_logic_list['VALIDEMAIL'][0]},")
    src_query.newline(f"\t\t{col_logic_list['VALIDADDRESS'][1]} AS {col_logic_list['VALIDADDRESS'][0]},")
    src_query.newline(f"\t\t{col_logic_list['VALIDPHONE'][1]} AS {col_logic_list['VALIDPHONE'][0]},")
    src_query.newline(f"\t\t{col_logic_list['RN'][1]} AS {col_logic_list['RN'][0]}")
    src_query.newline(f"\tFROM")
    src_query.newline(f"\t\tSTAGE.{table_name} {tbl_alias}")
    src_query.newline(f"\tLEFT JOIN")
    src_query.newline(f"\t(")
    src_query.newline(f"\t\tSELECT")
    src_query.newline(f"\t\t\tCLIENTID,")
    src_query.newline(f"\t\t\tMIN(ORDERDATE) AS SOURCEINSERTDATE,")
    src_query.newline(f"\t\t\tMAX(ORDERDATE) AS SOURCEUPDATEDATE")
    src_query.newline(f"\t\tFROM")
    src_query.newline(f"\t\t\tSTAGE.FANATICSORDERDETAILS")
    src_query.newline(f"\t\tGROUP BY")
    src_query.newline(f"\t\t\tCLIENTID")
    src_query.newline(f"\t) AS od")
    src_query.newline(f"\tON")
    src_query.newline(f"\t\t{tbl_alias}.CLIENTID = od.CLIENTID")
    src_query.newline(f"\tLEFT JOIN")
    src_query.newline(f"\t\tSTAGE.STANDARDIZATION std")
    src_query.newline(f"\tON")
    src_query.newline(f"\t\tstg.STANDARDIZATIONROWID = std.STANDARDIZATIONROWID")
    src_query.newline("\tGROUP BY")

    # group_special = ["FIRSTNAME", "MIDDLENAME", "LASTNAME", "GENDER", "CITY", "PHONE1", "PHONE2", "PHONE3", "FAX", "EMAIL"]
    group_except_list = ["SOURCEINSERTDATE", "SOURCEUPDATEDATE"]
    for col in col_list_all:
        # if col in group_special:
        col_name = col_logic_list[col][0]
        col_logic = col_logic_list[col][1]
        if col_name in group_except_list:
            src_query = src_query
        elif tbl_alias in col_logic or "std" in col_logic:
            src_query.newline(f"\t\t{col_logic},")
        else:
            src_query.newline(f"\t\t{col_name},")

    src_query.newline(f"\t\t{tbl_alias}.STANDARDIZATIONROWID,")
    src_query.newline(f"\t\tVALIDEMAIL,")
    src_query.newline("\t\tVALIDADDRESS,")
    src_query.newline("\t\tVALIDPHONE")
    src_query.newline("\t) SUB")
    src_query.newline("WHERE SUB.RN = 1;")

    return src_query






