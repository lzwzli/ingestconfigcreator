# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "sftp_ingest_flow"
    config_dict["flowModuleName"] = '"sftp_ingest_flow.py"'
    config_dict["flowPackageName"] = '"prefectshared-sftp"'
    config_dict["flowRunParameters"] = ('{'
                           f'\n{tab}\t"feature": "liveanalytics",'
                           f'\n{tab}\t"sftp_environment_variable_name": "AWS_SECRET_ARN_KAGRSFTP",'
                           f'\n{tab}}}')

    return config_dict