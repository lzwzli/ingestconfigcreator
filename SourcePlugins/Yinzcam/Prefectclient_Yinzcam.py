# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "sftp_ingest_flow"
    config_dict["flowModuleName"] = '"sftp_ingest_flow.py"'
    config_dict["flowPackageName"] = '"prefectshared-sftp"'
    config_dict["flowRunParameters"] = '{"feature": "yinzcam", "sftp_environment_variale_name": "AWS_SECRET_ARN_KAGRSFTP"}'

    return config_dict

# ----------------------------------------------------------------
# block_config custom
# ----------------------------------------------------------------
def fn_block_config_custom(source_name:str, block_dict:dict):
    block_dict["flowName"] = '"sftp-ingest-flow"'

    return block_dict