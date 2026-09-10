# ----------------------------------------------------------------
# Prefectclient deploy_config custom module
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    config_dict["flowObject"] = "load_and_transform_wrapper"
    config_dict["flowModuleName"] = '"non_acquire.py"'
    config_dict["flowPackageName"] = '"prefectshared-client"'
    config_dict["flowRunParameters"] = '{"feature": "axs"}'

    return config_dict