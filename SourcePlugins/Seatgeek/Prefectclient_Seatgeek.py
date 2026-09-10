# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "main_ingest_flow"
    config_dict["flowModuleName"] = '"ingest_flow.py"'
    config_dict["flowPackageName"] = '"prefectshared-seatgeek"'
    config_dict["jobInfrastructureOverride"] = ('{'
                                        f'{tab}\t"cpu": 4096'
                                        f'{tab}\t"memory": 20480'
                                        f'{tab}}},')

    return config_dict


# ----------------------------------------------------------------
# Prefectclient block_config custom module
# ----------------------------------------------------------------
def fn_block_config_custom(source_name: str, block_dict: dict):
    block_dict["hardFailImport"] = "True"

    return block_dict