# ----------------------------------------------------------------
# deploy_config custom
# ----------------------------------------------------------------
def fn_deploy_config_custom(source_name:str, config_dict:dict):
    # override dict values
    tab = "\t\t"
    config_dict["flowObject"] = "oneoffimport_ingest_main"
    config_dict["flowModuleName"] = '"flows.py"'
    config_dict["flowPackageName"] = '"prefectshared-oneoffimport"'
    config_dict["flowRunParameters"] = ('{'
                                        f'\n{tab}\t"feature": "oneoffimport",'
                                        f'\n{tab}}}')

    return config_dict