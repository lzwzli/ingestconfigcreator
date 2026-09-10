# ----------------------------------------------------------------
# Sources Append
# ----------------------------------------------------------------
def fn_sources_append(worksheet:object, db_folder:str, sources_obj:object, runlog:object, repo_root_folder:str, client:str, source_name:str):
    runlog.log("Running WIT specific sources append function")

    # get table name
    table_name = worksheet.table_name().lower()

    if table_name.upper() == "WITENTRIES":
        sources_obj.append("rowCountCheckOverride", 1)

    elif table_name.upper() == "WITLISTS":
        witentries_truncate = {}
        witentries_truncate["sortOrder"] = 3
        witentries_truncate["sqlFileName"] = "witentries-truncate.sql"
        witentries_flatten = {}
        witentries_flatten["sortOrder"] = 4
        witentries_flatten["sqlFileName"] = "witentries-flatten.sql"
        sources_obj.append("importSql", [witentries_truncate])
        sources_obj.append("importSql", [witentries_flatten])

    runlog.log("")

    return