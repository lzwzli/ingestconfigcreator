# ----------------------------------------------------------------
# block_config custom
# ----------------------------------------------------------------
def fn_block_config_custom(source_name:str, block_dict:dict):
    block_dict["flowName"] = '"ingest-mlsfangenome-data"'
    block_dict["sourceName"] = '"mlsfangenome"'
    block_dict["deploymentName"] = '"mlsfangenome-instance_mlsfangenome-ingest-main"'

    return block_dict