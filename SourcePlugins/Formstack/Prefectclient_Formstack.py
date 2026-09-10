# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "formstack_ingest_flow"
    config_dict["flowModuleName"] = '"ingest_flow.py"'
    config_dict["flowPackageName"] = '"prefectshared-formstack"'

    return config_dict