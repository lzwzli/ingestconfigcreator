from Library.FunctionFiles.Functions import *
from SourcePlugins.Dynamics.BusRule_DynamicsContact import *
from SourcePlugins.Dynamics.BusRule_DynamicsAccount import *

# custom_filedate = "TO_CHAR(REGEXP_SUBSTR(REPLACE(SPLIT_PART(SPLIT_PART(METADATA$FILENAME, '/', -1), '-', -1),'-',''), '[0-9]{14}', 1, 1))"
custom_filedate = "TO_CHAR(SUBSTR(REGEXP_SUBSTR(SPLIT_PART(METADATA$FILENAME, '/', -1), '[0-9]{20}'), 1, 14))"

custom_stage_location = "@IMPORT.INGESTSTAGE/&feature/&teamAbbr/&timestamp/acquire/dynamics"

create_archive_tables = ["dynamicscontact", "dynamicsaccount"]

# Create Feature file
def fn_create_feature_file_custom(source_name:str, table_name_list:list, db_folder:str, runlog:object, repo_root_folder:str, client:str):
    print_section(msg="Working on Feature File", runlog=runlog)

    feature_file = {}
    feature_file_append = []

    # create sources key value dictionary per table
    sources_list = []
    transform_groups0_sources = []
    transform_groups1_sources = []
    for table in table_name_list:
        table_name = table[0].lower()
        has_bus_rule = table[1]
        sources_dict = {}
        sources_dict["name"] = table_name
        sources_dict["configurationFileName"] = f"{table_name}.json"
        sources_dict["hasBusinessRules"] = has_bus_rule

        # dynamics contact is in group 1 because standardization query relies on account data
        if table_name == "dynamicscontact":
            runlog.log(f"Adding {table_name} to transform group 1")
            transform_groups1_sources.append(table_name)
        else:
            runlog.log(f"Adding {table_name} to transform group 0")
            transform_groups0_sources.append(table_name)

        # transform_groups0_sources.append(table_name)

        sources_list.append(sources_dict)

    feature_file["sources"] = sources_list
    feature_file["featureName"] = source_name.lower()

    # transform groups
    transformGroupsList = []

    transformGroupsDict0 = {}
    transformGroupsDict0["runOrder"] = 0
    transformGroupsDict0["sources"] = transform_groups0_sources
    transformGroupsList.append(transformGroupsDict0)

    if len(transform_groups1_sources) > 0:
        transformGroupsDict1 = {}
        transformGroupsDict1["runOrder"] = 1
        transformGroupsDict1["sources"] = transform_groups1_sources
        transformGroupsList.append(transformGroupsDict1)

    feature_file["transformGroups"] = transformGroupsList

    # define output folder and filename
    # filename
    filename = f"{source_name.lower()}.json"

    # output JSON
    writeJSON(filecontent=feature_file, filename=filename, filetype="feature", client=client, source_name=source_name, db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

    return

# ----------------------------------------------------------------
# Append Business Rules
# ----------------------------------------------------------------
def fn_busrules_append(worksheet:object, bus_rule_obj:object, db_folder:str, runlog:object):
    runlog.log("Running Dynamics specific busrules append function")

    # get table name
    table_name = worksheet.table_name()

    # get columns
    col_list = worksheet.columns()

    # phone columns
    phone_cols = worksheet.phone_columns()

    # rawaudience indicator
    rawaudind = worksheet.rawaudience_ind()

    # add phone cols to col list
    if rawaudind == "1":
        for phone in phone_cols:
            col_list.append([phone, f"{phone}formatted", "VARCHAR"])

    # get primary keys
    pk = worksheet.primary_keys()

    # get rawaudience indicator
    rawaud_ind = worksheet.rawaudience_ind()

    # ----------------------------------------------------------------
    # CONTACT
    # ----------------------------------------------------------------
    if "CONTACT" in table_name.upper():
        dynamicscontact_busrules(col_list=col_list, pk=pk, rawaud_ind=rawaud_ind, bus_rule_obj=bus_rule_obj, db_folder=db_folder, runlog=runlog)

    # ----------------------------------------------------------------
    # ACCOUNT
    # ----------------------------------------------------------------
    if "ACCOUNT" in table_name.upper():
        dynamicsaccount_busrules(col_list=col_list, pk=pk, rawaud_ind=rawaud_ind, bus_rule_obj=bus_rule_obj, db_folder=db_folder, runlog=runlog)

    runlog.log("")
    return

# ----------------------------------------------------------------
# Get custom acquire information
# ----------------------------------------------------------------
def fn_get_acquire_custom_info(worksheet:object):
    entity = worksheet.dynamics_entity_name()
    modifiedon = worksheet.sourcedate_ind()

    acquire_custom_info = {}
    acquire_custom_info["entity"] = entity
    acquire_custom_info["modifiedon"] = modifiedon

    return acquire_custom_info

# ----------------------------------------------------------------
# create acquire file
# ----------------------------------------------------------------
def fn_create_acquire_file(file_match_list:list, table_name_list:list, db_folder:str, runlog:object, client:str, repo_root_folder:str, acquire_custom_info_list:list):
    print_section(msg="Working on Acquire File", runlog=runlog)

    acquire_file = {}

    acquire_file["abort_on_failure"] = False
    acquire_file["request_timeout_seconds"] = 300
    acquire_file["default_query"] = "?$filter=modifiedon gt %date%"
    acquire_file["upload_batch_size"] = 4
    acquire_file["max_parallel_subflows"] = 3

    apicallsProperties = []

    idx = 0
    for file in file_match_list:
        if file.upper() != "EXCLUDEFROMFILETRANSFERS":
            entity_dict = {}
            try:
                entity = acquire_custom_info_list[idx]["entity"].lower()
            except:
                entity = "<fill in Dynamics Entity Name>"

            try:
                modifiedon = acquire_custom_info_list[idx]["modifiedon"]
            except:
                modifiedon = "<fill in get last date column>"

            table_name = str(table_name_list[idx][0]).lower()

            entity_dict["entity"] = entity
            if "account" in entity or "contact" in entity:
                entity_dict["query"] = "?$filter=modifiedon ge %date% and merged eq false and _masterid_value eq null"

            # define getLastDateProperties values
            getLastDateParameters = {}
            getLastDateParameters["daysBack"] = -1
            getLastDateParameters["lastDateColumn"] = modifiedon
            getLastDateParameters["tableName"] = table_name
            getLastDateParameters["schema"] = "stage"
            getLastDateParameters["datetimeRequestFormat"] = "%Y-%m-%dT%H:%M:%SZ"

            getLastDateProperties = {}
            if len(modifiedon)>0:
                getLastDateProperties["indicator"] = 1
            else:
                getLastDateProperties["indicator"] = 0
            getLastDateProperties["parameters"] = getLastDateParameters

            entity_dict["getLastDate"] = getLastDateProperties

            apicallsProperties.append(entity_dict)

        idx += 1

    acquire_file["api_calls"] = apicallsProperties

    # filename
    filename = f"acquire.json"

    # output JSON file
    writeJSON(filecontent=acquire_file, filename=filename, filetype="acquire", client=client, source_name="dynamics", db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

    return