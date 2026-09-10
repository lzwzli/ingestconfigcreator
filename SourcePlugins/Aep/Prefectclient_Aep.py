# ----------------------------------------------------------------
# Prefectclient deploy_config custom module
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):

    # override dict values
    config_dict["flowObject"] = "aep_import_main"
    config_dict["flowModuleName"] = '"imports.py"'
    config_dict["flowPackageName"] = '"prefectshared-adobeexperienceplatform"'

    return config_dict