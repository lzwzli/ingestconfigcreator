# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "shopify_main_flow"
    config_dict["flowModuleName"] = '"shopify.py"'
    config_dict["flowPackageName"] = '"prefectshared-shopify"'

    return config_dict