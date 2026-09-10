# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    module = ""
    module_import = ""
    config_dict["deploy"] = False

    return module, module_import, config_dict

# ----------------------------------------------------------------
# block_config custom
# ----------------------------------------------------------------
def fn_block_config_custom(source_name:str, block_dict:dict):
    block_dict["deploy"] = False

    return block_dict