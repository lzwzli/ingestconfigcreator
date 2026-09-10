# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "googleanalytics_flow"
    config_dict["flowModuleName"] = '"googleanalytics4.py"'
    config_dict["flowPackageName"] = '"prefectshared-googleanalytics"'

    return config_dict