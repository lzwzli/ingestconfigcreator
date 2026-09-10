# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "salesforce_ingest_main"
    config_dict["flowModuleName"] = '"imports.py"'
    config_dict["flowPackageName"] = '"prefectshared-salesforce"'
    config_dict["flowRunParameters"] = ('{'
                                        f'{tab}\t"feature_sources_filter": SALESFORCE_IMPORT_SOURCES_FILTER'
                                        f'{tab}}},')

    return config_dict

# ----------------------------------------------------------------
# Prefectclient block_config custom module
# ----------------------------------------------------------------
def fn_block_config_custom(source_name:str, block_dict:dict):
    block_dict["hardFailImport"] = "True"

    return block_dict