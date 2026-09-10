from Library.FunctionFiles.BasicFunctions import *
# ----------------------------------------------------------------
# Create Feature file
# ----------------------------------------------------------------
def create_feature_file(source_name:str, table_name_list:list, db_folder:str, runlog:object, repo_root_folder:str, client:str, feature_custom_info:list=[]):
    print_section(msg="Working on Feature File", runlog=runlog)

    feature_file = {}
    feature_file_append = []

    # create sources key value dictionary per table
    sources_list = []
    transform_groups_sources = []
    for table in table_name_list:
        table_name = table[0].lower()
        has_bus_rule = table[1]
        sources_dict = {}
        sources_dict["name"] = table_name
        sources_dict["configurationFileName"] = f"{table_name}.json"
        sources_dict["hasBusinessRules"]=has_bus_rule
        transform_groups_sources.append(table_name)

        sources_list.append(sources_dict)

    feature_file["sources"] = sources_list
    feature_file["featureName"] = source_name.lower()

    # custom feature file info
    if len(feature_custom_info) > 0:
        for feature in feature_custom_info:
            key = feature["key"]
            value = feature["value"]
            feature_file[key] = value

    # transform groups
    transformGroupsList = []
    transformGroupsDict = {}
    transformGroupsDict["runOrder"] = 0
    transformGroupsDict["sources"] = transform_groups_sources
    transformGroupsList.append(transformGroupsDict)

    feature_file["transformGroups"] = transformGroupsList

    # define output folder and filename
    # filename
    filename = f"{source_name.lower()}.json"

    # output JSON
    writeJSON(filecontent=feature_file, filename=filename, filetype="feature", client=client, source_name=source_name, db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

    return