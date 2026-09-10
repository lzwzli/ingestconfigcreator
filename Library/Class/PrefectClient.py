import os
from fileinput import filename
from importlib import import_module

from Library.FunctionFiles.Functions import *
class prefectclient:
    def __init__(self, client:str, source_name:str, db_folder:str, repo_root_folder:str, runlog:object):
        self.client = client
        self.source_name = source_name
        self.db_folder = db_folder
        self.repo_root_folder = repo_root_folder

        if repo_root_folder != "":
            self.repo_root_folder = normalizePath(repo_root_folder) + os.sep
            self.filefolder = self.repo_root_folder + f"prefectclient{os.sep}{self.client.upper()}{os.sep}"

        self.runlog = runlog

        # initialize custom variables
        self.has_fn_deploy_config_custom = False
        self.has_fn_block_config_custom = False

        # try to load custom functions
        self.load_source_functions()
        return

    # =======================================================================
    # load source custom functions
    # =======================================================================
    def load_source_functions(self):
        try:
            # ----------------------------------------------------------------
            # load source specific functions file
            # ----------------------------------------------------------------
            functions_plugin_name = f"SourcePlugins.{self.source_name.capitalize()}.Prefectclient_{self.source_name.capitalize()}"

            self.runlog.log(f"Try to load {functions_plugin_name}")
            functions_plugin = import_module(functions_plugin_name)
            self.has_source_functions = True
            self.runlog.log("")
            self.runlog.log(f"Imported {functions_plugin_name} into PrefectClient class.")

            # ----------------------------------------------------------------
            # try to load fn_deploy_config_custom function
            # ----------------------------------------------------------------
            try:
                self.fn_deploy_config_custom = getattr(functions_plugin, "fn_deploy_config_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_deploy_config_custom function loaded.")
                self.has_fn_deploy_config_custom = True
            except:
                self.runlog.log(f"{indent}No fn_deploy_config_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load fn_block_config_custom function
            # ----------------------------------------------------------------
            try:
                self.fn_block_config_custom = getattr(functions_plugin, "fn_block_config_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_block_config_custom function loaded.")
                self.has_fn_block_config_custom = True
            except:
                self.runlog.log(f"{indent}No fn_block_config_custom function found in {functions_plugin_name}.")

        except Exception as e:
            self.runlog.log(f"WARNING: {e}")
            self.has_source_functions = False
            self.runlog.log("")
            self.runlog.log(f"No {functions_plugin_name} found.")

        return

    # ----------------------------------------------------------------
    # create deploy_config config
    # ----------------------------------------------------------------
    def deploy_config(self):
        print_section(msg="Working on PrefectClient deploy_config file", runlog=self.runlog)

        # define default variables
        self.source_deployment_name = f"{self.source_name.lower()}-import-deployment"

        # build dictionary
        self.config_dict = {}
        self.config_dict["deploymentName"] = 'f"{deployment_vars.deployment_name_prefix}' + self.source_deployment_name + '"'
        self.config_dict["workPoolName"] = "deployment_vars.work_pool_name"
        self.config_dict["workQueueName"] = "deployment_vars.work_queue_name"
        self.config_dict["sharedPackagePath"] = "deployment_vars.shared_packages_prefix"
        self.config_dict["flowObject"] = f"{self.source_name.lower()}_ingest_flow"
        self.config_dict["flowModuleName"] = f'"ingest_flow.py"'
        self.config_dict["flowPackageName"] = f'"prefectshared-{self.source_name.lower()}"'

        # load custom module definitions
        if self.has_fn_deploy_config_custom:
            try:
                self.config_dict = self.fn_deploy_config_custom(source_name=self.source_name, config_dict=self.config_dict)
            except Exception as e:
                raise Exception(f"Unable to load deploy_config_custom. {e}")

        # build module import
        flowpackagename = self.config_dict["flowPackageName"].replace("-", ".").replace('"','')
        flowmodulename = self.config_dict["flowModuleName"].replace(".py", "").replace('"','')
        flowobject = self.config_dict["flowObject"]
        self.pkg_import = f"from {flowpackagename}.{flowmodulename} import {flowobject}"

        # check if deploy is False
        self.add_to_deploy = True
        try:
            self.add_to_deploy = self.config_dict["deploy"]
        except:
            pass

        if self.add_to_deploy is False:
            print_section_detail(msg=f"PREFECTCLIENT - deploy_config\n{self.source_name} not to be added to deploy config", runlog=self.runlog)
            return

        # generate item string
        source_item_doc = Document()
        source_item_doc.newline("\t{")

        keylist = list(self.config_dict.keys())
        for key in keylist:
            source_item_doc.newline(f'\t\t"{key}": {self.config_dict[key]},')

        source_item_doc.newline("\t},")

        self.deploy_config_str = source_item_doc.out()

        # generate output
        output = Document()
        output.newline(self.pkg_import)
        output.newline("")
        output.newline(f"prefectshared_deployments = [")
        output.newline(self.deploy_config_str)
        output.newline("]")

        filename = "deploy_config.py.txt"
        output_folder = f"{self.db_folder}prefectclient_repo{os.sep}"
        filewrite(folder=output_folder, filename=filename, content=output.out())
        print_section_detail(msg=f"PREFECTCLIENT - {filename}\nCreated in: {output_folder}", runlog=self.runlog)

        # add to deploy_config
        self.add_to_deploy_config()

        return self.pkg_import, self.config_dict

    # ----------------------------------------------------------------
    # add deploy_config to repo file
    # ----------------------------------------------------------------
    def add_to_deploy_config(self):

        # exit if deploy is False
        if self.add_to_deploy is False:
            return

        # check repo_root_folder path
        if self.repo_root_folder == "":
            self.runlog.log("INFO: repo_root_folder empty. Not adding to deploy_config.py")
            return

        # read deploy_block_config
        filename = "deploy_config.py"
        filepath = self.filefolder + filename
        print_section_detail(msg=f'PREFECTCLIENT - deploy_config.py\nReading "{filepath}"', runlog=self.runlog)
        try:
            config_str = str(open(filepath, "r").read())
        except Exception as e:
            raise Exception(e)

        # check if source already exist
        import_idx = config_str.find(self.config_dict["deploymentName"])
        if import_idx != -1:
            self.runlog.log(f"{indent}{self.source_name} deployment already in deploy_config at position {import_idx}")
            return

        # add package if it doesn't exist
        pkg_idx = config_str.find(self.pkg_import)
        if pkg_idx == -1:
            pkg = self.pkg_import.split(" ")[-1]
            self.runlog.log(f"{indent}Adding {pkg} import")
            # find last prefectshared import
            last_from_index = config_str.rfind("from prefectshared")
            add_index = config_str.index("\n", last_from_index)

            # add import
            top = config_str[:add_index]
            bottom = config_str[add_index:]
            newconfig = top + "\n" + self.pkg_import + bottom

            self.runlog.log(f"{indent}{pkg} import added at position {add_index}")
        else:
            self.runlog.log(f"{indent}{self.pkg_import} already imported in deploy_config at position {pkg_idx}")
            newconfig = config_str

        # find prefectshared_deployments
        self.runlog.log(f"{indent}Adding {self.source_name} to deployments")
        psd_index = newconfig.index("prefectshared_deployments")
        psd_equal = newconfig.index("=", psd_index)
        psd_start_bracket = newconfig.index("[", psd_equal)

        # add deployment string
        top = newconfig[:psd_start_bracket + 1]
        bottom = newconfig[psd_start_bracket + 1:]
        newconfig = top + "\n" + self.deploy_config_str + bottom

        # write file
        filewrite(folder=self.filefolder, filename=filename, content=newconfig)
        self.runlog.log(f"{indent}{self.source_name} deployment added at position {psd_start_bracket}")

        return

    # ----------------------------------------------------------------
    # create deploy_block_config config
    # ----------------------------------------------------------------
    def deploy_block_config(self):
        print_section(msg="Working on PrefectClient deploy_block_config file", runlog=self.runlog)

        self.block_dict = {}
        self.block_dict["sourceName"] = f'"{self.source_name.lower()}"'
        self.block_dict["active"] = "True"
        self.block_dict["flowName"] = f'"{self.config_dict["flowObject"].replace("_", "-")}"'
        self.block_dict["deploymentName"] = f'"{self.source_deployment_name}"'
        self.block_dict["hardFailImport"] = "False"
        self.block_dict["executeImportRegression"] = "True"
        self.block_dict["executeImportThreshold"] = "False"

        # load custom module definitions
        if self.has_fn_block_config_custom:
            try:
                self.block_dict = self.fn_block_config_custom(source_name=self.source_name, block_dict=self.block_dict)
            except Exception as e:
                raise Exception(f"Unable to load block_config_custom. {e}")

        # check if deploy is False
        self.add_to_block = True
        try:
            self.add_to_block = self.block_dict["deploy"]
        except:
            pass

        if self.add_to_block is False:
            print_section_detail(msg=f"PREFECTCLIENT - deploy_block_config\n{self.source_name} not to be added to deploy block config", runlog=self.runlog)
            return

        # generate item string
        block_config_doc = Document()
        block_config_doc.newline("\t\t{")

        keylist = list(self.block_dict.keys())
        for key in keylist:
            block_config_doc.newline(f'\t\t\t"{key}": {self.block_dict[key]},')

        block_config_doc.newline("\t\t},")

        self.deploy_block_str = block_config_doc.out()

        # generate output
        output = Document()
        output.newline('\t"importSettings": [')
        output.newline(self.deploy_block_str)
        output.newline("\t]")

        filename = "deploy_block_config.py.txt"
        output_folder = f"{self.db_folder}prefectclient_repo{os.sep}"
        filewrite(folder=output_folder, filename=filename, content=output.out())
        print_section_detail(msg=f"PREFECTCLIENT - {filename}\nCreated in: {output_folder}", runlog=self.runlog)

        # add to repo file
        self.add_to_deploy_block_config()
        # add to test_master_schedule
        self.add_to_test_master_schedule()

        return self.block_dict

    # ----------------------------------------------------------------
    # add deploy_block_config to repo file
    # ----------------------------------------------------------------
    def add_to_deploy_block_config(self):
        # exit if deploy is False
        if self.add_to_block is False:
            return

        # check repo_root_folder path
        if self.repo_root_folder == "":
            self.runlog.log("INFO: repo_root_folder empty. Not adding to deploy_block_config.py")
            return

        # read deploy_block_config
        filename = "deploy_block_config.py"
        filepath = self.filefolder+filename
        print_section_detail(msg=f'PREFECTCLIENT - deploy_block_config.py\nReading "{filepath}"', runlog=self.runlog)
        try:
            block_str = str(open(filepath, "r").read())
        except Exception as e:
            raise Exception(e)

        # check if source already exist
        source_idx = block_str.find(self.block_dict["sourceName"])
        if source_idx != -1:
            self.runlog.log(f"{indent}{self.source_name} already in deploy_block_config at position {source_idx}")
            return

        # find importSettings and closing bracket
        iS_index = block_str.index('"importSettings":')
        iS_start_bracket = block_str.index("]", iS_index)

        # add string
        top = block_str[:iS_start_bracket-1].rstrip(" ")
        bottom = block_str[iS_start_bracket-1:].lstrip(" ")
        newconfig = top + self.deploy_block_str + "\n\t" + bottom

        # write file
        filewrite(folder=self.filefolder, filename=filename, content=newconfig)
        self.runlog.log(f"{indent}{self.source_name} added to deploy_block_config.py")

        return

    # ----------------------------------------------------------------
    # add to test_master_schedule.py
    # ----------------------------------------------------------------
    def add_to_test_master_schedule(self):
        # check repo_root_folder path
        if self.repo_root_folder == "":
            self.runlog.log("INFO: repo_root_folder empty. Not adding to test_master_schedule.py")
            return

        # read deploy_block_config
        filename = "test_master_schedule.py"
        testfolder = self.filefolder + f"tests{os.sep}"
        filepath =  testfolder + filename
        print_section_detail(msg=f'PREFECTCLIENT - test_master_schedule.py\nReading "{filepath}"', runlog=self.runlog)
        try:
            test_ms_str = str(open(filepath, "r").read())
        except Exception as e:
            raise Exception(e)

        # check if source already exist
        source_idx = test_ms_str.find(self.block_dict["sourceName"])
        if source_idx != -1:
            self.runlog.log(f"{indent}{self.source_name} already in test_master_schedule at position {source_idx}")
            return

        # find importSettings and closing bracket
        iS_index = test_ms_str.index('"importSettings":')
        iS_start_bracket = test_ms_str.index("]", iS_index)

        # add string
        top = test_ms_str[:iS_start_bracket - 1].rstrip(" ")
        bottom = test_ms_str[iS_start_bracket - 1:].lstrip(" ")
        new_test_ms = top + "\t" + self.deploy_block_str.replace("\n","\n\t") + "\n\t\t" + bottom

        # write file
        filewrite(folder=testfolder, filename=filename, content=new_test_ms)
        self.runlog.log(f"{indent}{self.source_name} added to test_master_schedule.py")

        return

    # ----------------------------------------------------------------
    # requirements.txt
    # ----------------------------------------------------------------
    def requirements(self):
        print_section(msg="Working on PrefectClient requirements.txt file", runlog=self.runlog)
        self.pkg = self.config_dict["flowPackageName"].replace('"','')
        self.pkg_req = f"{self.pkg}==<get latest version from release page>"

        output = Document()
        output.newline(self.pkg_req)

        filename = "requirements.txt"
        output_folder = f"{self.db_folder}prefectclient_repo{os.sep}"
        filewrite(folder=output_folder, filename=filename, content=output.out())
        print_section_detail(msg=f"PREFECTCLIENT - {filename}\nCreated in: {output_folder}", runlog=self.runlog)

        # add to requirements.txt
        self.add_to_requirements()

        return

    # ----------------------------------------------------------------
    # add to requirements.txt repo file
    # ----------------------------------------------------------------
    def add_to_requirements(self):
        # check repo_root_folder path
        if self.repo_root_folder == "":
            self.runlog.log("INFO: repo_root_folder empty. Not adding to requirements.txt")
            return

        # read existing requirements.txt
        filename = "requirements.txt"
        filepath = self.filefolder+filename
        print_section_detail(msg=f'PREFECTCLIENT - requirements.txt\nReading "{filepath}"', runlog=self.runlog)
        try:
            req_str = str(open(filepath, "r").read())
        except Exception as e:
            raise Exception(e)

        # check if source already exist
        req_idx = req_str.find(self.pkg)
        if req_idx != -1:
            self.runlog.log(f'{indent}"{self.pkg}" package already in requirements at position {req_idx}')
            return

        # add module to end of file
        new_req = req_str + "\n" + self.pkg_req

        # write file
        filewrite(folder=self.filefolder, filename=filename, content=new_req)
        self.runlog.log(f"{indent}{self.source_name} added to requirements.txt")
        self.runlog.log(f"{indent}PLEASE UPDATE VERSION!")

        return


