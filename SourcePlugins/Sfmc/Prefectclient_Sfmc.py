# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "sfmc_flow"
    config_dict["flowModuleName"] = '"sfmc.py"'
    config_dict["flowPackageName"] = '"prefectshared-sfmc"'

    return config_dict