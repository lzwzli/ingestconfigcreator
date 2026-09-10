# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "main_ingest_flow"
    config_dict["flowModuleName"] = '"ingest_flow.py"'
    config_dict["flowPackageName"] = '"prefectshared-podium"'

    return config_dict

def fn_block_config_custom(source_name:str, block_dict:dict):
    block_dict["flowName"] = "main-ingest-flow"

    return block_dict