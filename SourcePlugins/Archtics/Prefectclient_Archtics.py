# ----------------------------------------------------------------
# Prefectclient deploy_config custom module
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    tab = "\t\t"
    if source_name.upper()=="ARCHTICS-API":
        config_dict["deploymentName"] = 'f"{deployment_vars.deployment_name_prefix}archticsapi-import-deployment"'
        config_dict["flowObject"] = "archtics_api_flow"
        config_dict["flowModuleName"] = '"archtics_api.py"'
        config_dict["flowPackageName"] = '"prefectshared-archtics_api"'
    else:
        config_dict["deploymentName"] = 'f"{deployment_vars.deployment_name_prefix}archtics-sftp-import-deployment"'
        config_dict["flowObject"] = "archtics_ingest_flow"
        config_dict["flowModuleName"] = '"archtics_ingest_flow.py"'
        config_dict["flowPackageName"] = '"prefectshared-archtics"'
        config_dict["jobInfrastructureOverride"] = ('{'
                                                    f'\n{tab}\t"ephemeral_storage_size": 50,'
                                                    f'\n{tab}\t"network_configuration": NETWORK_CONFIGURATION,'
                                                    f'\n{tab}}}')

    return config_dict

# ----------------------------------------------------------------
# Prefectclient block_config custom module
# ----------------------------------------------------------------
def fn_block_config_custom(source_name:str, block_dict:dict):
    tab = "\t\t"
    if source_name.upper()=="ARCHTICS-API":
        block_dict["sourceName"] = '"archtics"'
        block_dict["deploymentName"] = '"archticsapi-import-deployment"'
        block_dict["active"] = "True"
        block_dict["hardFailImport"] = "True"
    else:
        block_dict["deploy"] = False

    return block_dict