# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "judo_flow"
    config_dict["flowModuleName"] = '"judo.py"'

    return config_dict