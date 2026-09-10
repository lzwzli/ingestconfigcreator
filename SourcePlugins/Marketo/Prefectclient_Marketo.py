# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "marketo_import_ingest_flow"
    config_dict["flowModuleName"] = '"import_ingest_flows.py"'
    config_dict["flowPackageName"] = '"prefectshared-marketo"'

    return config_dict