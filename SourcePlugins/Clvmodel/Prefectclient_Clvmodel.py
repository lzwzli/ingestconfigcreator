# ----------------------------------------------------------------
# Prefectclient deploy_config custom module
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    config_dict["flowObject"] = "load_model"
    config_dict["flowModuleName"] = '"load_model.py"'
    config_dict["flowPackageName"] = '"prefectshared-datascience"'
    config_dict["deploymentName"] = 'f"{deployment_vars.deployment_name_prefix}datascience-model-load-deployment"'

    return config_dict

# ----------------------------------------------------------------
# Prefectclient block_config custom module
# ----------------------------------------------------------------
def fn_block_config_custom(source_name:str, block_dict:dict):
    block_dict["deploy"] = False

    return block_dict