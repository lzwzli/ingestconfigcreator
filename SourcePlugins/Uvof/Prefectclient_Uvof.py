# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "uvof_ingest_main_flow"
    config_dict["flowModuleName"] = '"uvof.py"'
    config_dict["flowPackageName"] = '"prefectshared-uvof"'

    return config_dict