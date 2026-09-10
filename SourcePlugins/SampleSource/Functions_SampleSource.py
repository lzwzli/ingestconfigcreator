from Library.FunctionFiles.Functions import *

# Sources specific sources append
def fn_sources_append(worksheet:object, db_folder:str, sources_obj:object, runlog:object):
    runlog.log("Running Source specific sources append function")

    runlog.log("")
    return

# Sources specific business rules append
def fn_busrules_append(worksheet:object, bus_rule_obj:object, db_folder:str, runlog:object):
    runlog.log("Running Source specific busrules append function")

    runlog.log("")
    return

# Sources specific environment append
def fn_env_append(env_obj:object, env_name:str, runlog:object):
    runlog.log("Running Source specific environment append function")

    runlog.log("")
    return

# Sources specific copy into
def fn_create_copyinto_custom(client:str, source_name:str, table_name:str, col_list:list, file_match_text:str, file_date_regex:str, field_delimiter:str, version:str, db_folder:str, runlog:object, field_enclosed_by:str, custom_fileformat_options:str, repo_root_folder:str, worksheet:object):
    runlog.log("Running Source specific copyinto function")

    filename = ""

    # initialize CopyInto Document
    CopyInto = Document()

    runlog.log("")
    return filename

# Sources specific flatten
def fn_create_flatten_custom(source_name:str, table_name:str, table_name_raw:str, col_list:list, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, worksheet: object):
    runlog.log("Running Source specific flatten function")

    # define output folder and filename
    filename = f"{table_name.lower()}-flatten.sql"
    output_folder = f"{db_folder}config_repo{os.sep}sources{os.sep}"

    # initialize Flatten document
    Flatten = Document()

    # write flatten insert to file
    filewrite(folder=output_folder, filename=filename, content=Flatten.out())

    # trace log
    print_section_detail(msg=f"FLATTEN - {filename}\nCreated in: {output_folder}", runlog=runlog)

    return filename

# Sources specific import raw ddl
def fn_create_importraw_DDL_custom(table_name:str, version:str, db_folder:str, runlog:object):
    runlog.log("Running Source specific import raw ddl function")

    runlog.log("")
    return

# Sources specific import ddl
def fn_create_import_DDL_custom(table_name:str, col_list:list, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str, data_resources:list):
    runlog.log("Running Source specific import ddl function")

    # append data resources
    data_resources.append(["import", table_name.lower()])

    runlog.log("")
    return

# Sources specific file transfers
def fn_file_transfers_append(file_transfers_obj:object, client_project:str, runlog:object):
    runlog.log("Running Source specific file_transfers append function")

    runlog.log("")
    return