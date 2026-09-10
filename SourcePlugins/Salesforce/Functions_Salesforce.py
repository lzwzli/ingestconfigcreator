from SourcePlugins.Salesforce.BusRule_SalesforceAccount import *
from SourcePlugins.Salesforce.BusRule_SalesforceContact import *
from SourcePlugins.Salesforce.BusRule_SalesforceLead import *

# ----------------------------------------------------------------
# Set creation options
# ----------------------------------------------------------------
need_flatten = False
need_import_raw = False

# ----------------------------------------------------------------
# Create SOQL Query
# ----------------------------------------------------------------
def create_SOQL_query(salesforce_object_name:str, column_list:list, rawaudience_indicator:str):
    soql = Document()

    soql.append("SELECT")

    for row in column_list:
        soql.newline(f"\t{row[0]},")

    soql.trimend(1)

    soql.newline(f"FROM")
    soql.newline(f"\t{salesforce_object_name}")
    soql.newline("WHERE")
    if rawaudience_indicator == "1":
        soql.newline(f"\tMasterRecordId = null AND ")

    soql.newline(f"\tDAY_ONLY(LastModifiedDate) >= %DATE%")

    return soql

# ----------------------------------------------------------------
# Salesforce specific sources append
# ----------------------------------------------------------------
def fn_sources_append(worksheet:object, db_folder:str, sources_obj:object, runlog:object, repo_root_folder:str, client:str, source_name:str):
    runlog.log("Running Salesforce specific sources append function")

    # create output folder
    ref_folder = f"{db_folder}{os.sep}ForReferenceOnly{os.sep}"
    os.makedirs(ref_folder, exist_ok=True)

    # get table name
    table_name = worksheet.table_name().lower()
    sources_folder = f"{db_folder}config_repo{os.sep}sources{os.sep}"

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        configrepo_folder = f"{repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{client.upper()}{os.sep}{source_name.lower()}{os.sep}sources{os.sep}"

    # get salesforce object name
    sf_obj = worksheet.salesforce_object_name()

    # get rawaudienceindicator
    rawaudience_ind = worksheet.rawaudience_ind()

    # get column list
    col_list = worksheet.columns()

    # create SOQL query
    runlog.log(f"{indent}Create SOQL Query")
    soql = create_SOQL_query(sf_obj, col_list, rawaudience_ind)

    filewrite(folder=sources_folder, filename=f"salesforce{str(sf_obj).lower().replace('salesforce','')}-select.soql", content=soql.out())
    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        filewrite(folder=configrepo_folder, filename=f"salesforce{str(sf_obj).lower().replace('salesforce', '')}-select.soql", content=soql.out())

    # add SOQL to sources file
    runlog.log(f"{indent}Add to sources list")
    sources_obj.append("sourceQueryFileName", f"salesforce{str(sf_obj).lower().replace('salesforce','')}-select.soql")

    # add IMPORTSOURCEINDICATOR to sources file
    sources_obj.append("sourceType", "SOQL")

    # add SALESFORCEOBJECTNAME to sources file
    sources_obj.append("salesforceObjectName", None)

    # getLastDate
    sources_obj.replace("getLastDateIndicator", True)
    sources_obj.append("rowCountCheckOverride", 1)

    # define getLastDateProperties values
    getLastDateProperties = {}
    getLastDateProperties["daysBack"] = 0
    getLastDateProperties["lastDateColumn"] = "LastModifiedDate"
    getLastDateProperties["refresh"] = 0
    getLastDateProperties["schema"] = "stage"
    getLastDateProperties["seasonYearIndicator"] = 0
    getLastDateProperties["whereClause"] = ""
    getLastDateProperties["tableName"] = table_name
    sources_obj.append("getLastDateProperties", getLastDateProperties)

    runlog.log("")
    return

# ----------------------------------------------------------------
# Append Environment
# ----------------------------------------------------------------
def fn_env_append(env_obj:object, envname:str, runlog:object):
    runlog.log("Running Salesforce specific environment append function")

    env_obj.append("QueryAccount", f"REPLACE_WITH_{envname}_SALESFORCE_ACCOUNT")

    runlog.log("")
    return

# ----------------------------------------------------------------
# Append File Transfers
# ----------------------------------------------------------------
def fn_file_transfers_append(file_transfers_obj:object, client_project:str, runlog:object):
    runlog.log("Running Salesforce specific file_transfers append function")

    # add acquire pipeline
    file_transfers_obj.append("AQUIRE_PIPELINE", f"../{client_project}/Salesforce_Acquire_Pipeline")

    # add MASTERSCHEDULE
    file_transfers_obj.append("MASTERSCHEDULE", f"../{client_project}/SalesforceMasterImport")

    runlog.log("")
    return

# ----------------------------------------------------------------
# Append Business Rules
# ----------------------------------------------------------------
def fn_busrules_append(worksheet:object, bus_rule_obj:object, db_folder:str, runlog:object):
    runlog.log("Running Salesforce specific busrules append function")

    # salesforce object name
    sf_obj = worksheet.salesforce_object_name()

    # get table name
    table_name = worksheet.table_name()

    # get columns
    col_list = worksheet.columns()

    # get primary keys
    pk = worksheet.primary_keys()

    # get rawaudience indicator
    rawaud_ind = worksheet.rawaudience_ind()

    # ----------------------------------------------------------------
    # ACCOUNT
    # ----------------------------------------------------------------
    if sf_obj.upper() == "ACCOUNT":
        salesforceaccount_busrules(col_list=col_list, pk=pk, rawaud_ind=rawaud_ind, bus_rule_obj=bus_rule_obj, db_folder=db_folder, runlog=runlog)

    # ----------------------------------------------------------------
    # CONTACT
    # ----------------------------------------------------------------
    if sf_obj.upper() == "CONTACT":
        salesforcecontact_busrules(col_list=col_list, pk=pk, rawaud_ind=rawaud_ind, bus_rule_obj=bus_rule_obj, db_folder=db_folder, runlog=runlog)

    # ----------------------------------------------------------------
    # LEAD
    # ----------------------------------------------------------------
    if sf_obj.upper() == "LEAD":
        salesforcelead_busrules(col_list=col_list, pk=pk, rawaud_ind=rawaud_ind, bus_rule_obj=bus_rule_obj, db_folder=db_folder, runlog=runlog)


    runlog.log("")
    return

# ----------------------------------------------------------------
# Create Stage DDL
# ----------------------------------------------------------------
def fn_create_stage_DDL_custom(table_name:str, col_list:list, pk_str:str, phone_col_list:list, std_ind:int, rawaud_ind:int, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str, data_resources:list, email_col_list:list=[]):
    StageDDL_str = create_stage_DDL(table_name=table_name.lower(), col_list=col_list, pk_str=pk_str, phone_col_list=phone_col_list, std_ind=std_ind, rawaud_ind=rawaud_ind, version=version, db_folder=db_folder, runlog=runlog, repo_root_folder=repo_root_folder, client=client, source_name="salesforce", email_col_list=email_col_list)
    # append data resources
    data_resources.append(["stage", table_name.lower()])

    if table_name.upper() == "SALESFORCEACCOUNT" or table_name.upper() == "SALESFORCECONTACT" or table_name.upper() == "SALESFORCELEAD":
        archive_table_name = f"{table_name.upper()}ARCHIVE"
        create_stage_DDL(table_name=archive_table_name.lower(), col_list=col_list, pk_str=pk_str, phone_col_list=phone_col_list, std_ind=std_ind, rawaud_ind=rawaud_ind, version=version, db_folder=db_folder, runlog=runlog, repo_root_folder=repo_root_folder, client=client, source_name="salesforce", email_col_list=email_col_list)
        data_resources.append(["stage", archive_table_name.lower()])

    return StageDDL_str, data_resources

# ----------------------------------------------------------------
# Create Copy Into
# ----------------------------------------------------------------
def fn_create_copyinto_custom(client:str, source_name:str, table_name:str, col_list:list, file_match_text:str, file_date_regex:str, field_delimiter:str, version:str, db_folder:str, runlog:object, field_enclosed_by:str, custom_fileformat_options:str, repo_root_folder:str, worksheet:object):
    runlog.log("Running Salesforce specific copyinto function")

    # build column list
    elementidx = 1
    copyintocolumns = []
    copyelements = []
    for col in col_list:
        copyintocolumns.append(f"\t{col[1].upper()}")
        copyelements.append(f"\t\tT.\"$1\":\"{col[0]}\"")
        elementidx += 1

    # define stage location path
    stage_location = f"@IMPORT.INGESTSTAGE/&feature/&teamAbbr/&timestamp"

    # format custom_fileformat_options
    custom_fileformat_options = custom_fileformat_options.strip()

    if custom_fileformat_options == "None":
        custom_fileformat_options = ""
    elif custom_fileformat_options != '':
        custom_fileformat_options = f" {custom_fileformat_options}"
    else:
        custom_fileformat_options = ""

    # append .* to file_match_text if it doesn't start with it
    if file_match_text[:2] != ".*":
        file_match_text = f".*{file_match_text}"

    # initialize CopyInto Document
    CopyInto = Document()

    # Write CopyInto statement
    CopyInto.append(f"/*{table_name} Copy Into version={version} generated by config generator */")
    CopyInto.newline(f"COPY INTO import.{table_name.lower()}")
    CopyInto.newline("(")
    CopyInto.newline("\tFILEDATE,")
    CopyInto.newline("\tFILENAME,")
    CopyInto.newline("\tFILEROWNUMBER,")
    CopyInto.newlinelist(copyintocolumns)
    CopyInto.newline(")")
    CopyInto.newline("FROM")
    CopyInto.newline("(")
    CopyInto.newline("\tSELECT")
    CopyInto.newline(
        f"\t\tTO_CHAR(REGEXP_SUBSTR(REPLACE(REPLACE(SPLIT_PART(METADATA$FILENAME, '/', -1),'_',''),'-',''), '{file_date_regex}', 1, 1)),")
    CopyInto.newline("\t\tMETADATA$FILENAME,")
    CopyInto.newline("\t\tMETADATA$FILE_ROW_NUMBER,")
    CopyInto.newlinelist(copyelements)
    CopyInto.newline("\tFROM ")
    CopyInto.append(f"{stage_location} T")
    CopyInto.newline(")")
    CopyInto.newline(f"PATTERN = '{file_match_text}'")
    CopyInto.newline("ON_ERROR = CONTINUE")
    CopyInto.newline("FORCE = TRUE")
    CopyInto.newline(
        f"FILE_FORMAT = (TYPE = JSON STRIP_OUTER_ARRAY = TRUE{custom_fileformat_options})")
    CopyInto.newline(";")

    # define output folder and filename
    filename = f"{table_name.lower()}-copy.sql"
    output_folder = f"{db_folder}config_repo{os.sep}sources{os.sep}"

    # write copyinto to file
    filewrite(folder=output_folder, filename=filename, content=CopyInto.out())

    # trace log
    print_section_detail(msg=f"COPYINTO - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        configrepo_folder = f"{repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{client.upper()}{os.sep}{source_name.lower()}{os.sep}sources{os.sep}"
        filewrite(folder=configrepo_folder, filename=filename, content=CopyInto.out())

        # trace log
        print_section_detail(msg=f"COPYINTO - {filename}\nCreated in: {configrepo_folder}", runlog=runlog)

    return filename