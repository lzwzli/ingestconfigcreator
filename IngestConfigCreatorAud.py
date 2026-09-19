import argparse, sys
from Library.Class.Logger import *
from Library.Class.Config import *
from version import *

def ingestconfigcreator_aud(srcType:str="", runProfileDict:dict=None, ui_params:dict=None):
    # ----------------------------------------------------------------
    # create runlog object
    # ----------------------------------------------------------------
    runlog = Logger()
    runProfileDict = runProfileDict or {}
    ui_mode = ui_params is not None

    # ----------------------------------------------------------------
    # report version
    # ----------------------------------------------------------------
    runlog.log(f"Running IngestConfigCreator-RawAudienceOnly version {version}. Released {releasedate}.")
    runlog.log(f"**THIS VERSION IS ONLY TO CREATE RAWAUDIENCE CONFIGURATION**")
    runlog.log("")

    # ----------------------------------------------------------------
    # try import dependencies
    # ----------------------------------------------------------------
    try:
        import pandas
        import openpyxl
        import numpy
    except ModuleNotFoundError:
        print("Please run 'py setup.py install' to install dependency packages.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # parse arguments
    # -----------------------------------------------------------------------
    if ui_mode:
        source_type = ui_params.get("sourcetype", "")
        client = ui_params.get("client", "").strip()
        database = ui_params.get("database", "").strip()
        source_name = ui_params.get("sourcename", "").strip()
        dd_file = ui_params.get("ddfile", "")
        repo_root_folder = ui_params.get("reporootfolder", "") or ""
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('--sourcetype', help="source type. FF=Flat File sources / KIP=KIP acquired sources")
        parser.add_argument('--ddfile', help="input path to data dictionary file")
        parser.add_argument('--database', help="database name, i.e. tepperqa")
        parser.add_argument('--client', help="client abbreviation name, i.e. tepper")
        parser.add_argument('--sourcename', help="source name, i.e. dynamics")
        parser.add_argument('--reporootfolder', help="folder path to user Documents folder")
        args = parser.parse_args()

        source_type = args.sourcetype
        client = args.client
        database = args.database
        source_name = args.sourcename
        dd_file = args.ddfile
        repo_root_folder = args.reporootfolder

    # -----------------------------------------------------------------------
    # ask for arguments
    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------
    # load run profile variables
    # -----------------------------------------------------------------------
    if len(runProfileDict) > 0 and not ui_mode:
        # load variables
        client = loadProfileVars(runProfileDict, varname="client")
        database = loadProfileVars(runProfileDict, varname="database")
        source_name = loadProfileVars(runProfileDict, varname="sourcename")

        runlog.log(f'Loaded profile variables:')
        runlog.log(f"- {client=}")
        runlog.log(f"- {database=}")
        runlog.log(f"- {source_name=}")

    # -----------------------------------------------------------------------
    # dd_file
    # -----------------------------------------------------------------------
    while not ui_mode and (dd_file is None or dd_file == ""):
        print("Select Excel data dictionary file from dialog. Dialog may be hidden behind other windows.")
        dd_file = fileDialog(filetype=("Excel", ".xlsx"), title="Select Excel data dictionary file")
        # exit if no file provided when user hits cancel
        if dd_file == "":
            runlog.log("ERROR: No File Selected. Exiting.")
            sys.exit()

    runlog.log(f"Data Dict. File = {dd_file}")

    # -----------------------------------------------------------------------
    # source type
    # -----------------------------------------------------------------------
    source_type = srcType

    runlog.append(f"Source Type = {source_type}")

    # -----------------------------------------------------------------------
    # client
    # -----------------------------------------------------------------------
    while not ui_mode and (client is None or client == ""):
        client = input("Enter client abbreviation: ")

    client = client.upper()
    runlog.append(f"Client = {client}")

    # -----------------------------------------------------------------------
    # database
    # -----------------------------------------------------------------------
    while not ui_mode and (database is None or database == ""):
        database = input("Enter database name: ")

    database = database.upper()
    runlog.append(f"Database = {database}")

    # -----------------------------------------------------------------------
    # source_name
    # -----------------------------------------------------------------------
    while not ui_mode and (source_name is None or source_name == ""):
        source_name = input("Enter source name: ")

        if source_name.upper() == "ARCHTICS" and source_type == "KIP":
            source_name = "archtics-api"

        source_name = source_name.capitalize()

    runlog.append(f"Source Name = {source_name}")

    # -----------------------------------------------------------------------
    # Repo root folder
    # -----------------------------------------------------------------------
    if not ui_mode:
        select_repo_root_folder = ""
        while select_repo_root_folder.upper() != "Y" and select_repo_root_folder.upper() != "N":
            select_repo_root_folder = input("Create in repo folders for easy commit? [Y/N]: ")

        if select_repo_root_folder.upper() == "N":
            repo_root_folder = ""
        else:
            while repo_root_folder is None:
                print("Select folder containing cloned repositories from dialog. Dialog may be hidden behind other windows.")
                print("Click Cancel to skip creating files in repo folder.")
                repo_root_folder = folderDialog(title="Select folder containing cloned repos. Click Cancel to skip.")

                # if no repo folder selected, note it and move on
                if repo_root_folder == "":
                    runlog.log("No repo folder selected. Not creating files in repo.")

                # else normalize path
                else:
                    repo_root_folder = normalizePath(repo_root_folder) + os.sep

    # -----------------------------------------------------------------------
    # define db output folder for icp creation
    # -----------------------------------------------------------------------
    outputfolder = outputFolder(dd_file) + f"{client.upper()}{os.sep}{database}{os.sep}"

    # -----------------------------------------------------------------------
    # create command with integrated arguments
    # -----------------------------------------------------------------------
    cmd = f"python .\\IngestConfigCreatorAud.py --sourcetype {source_type} --client {client} --database {database} --sourcename {source_name} --ddfile '{dd_file}' --reporootfolder '{repo_root_folder}'"
    runlog.log("")
    runlog.log("Command with arguments:")
    runlog.log("")
    runlog.log(cmd)
    runlog.log("")

    # -----------------------------------------------------------------------
    # create config
    # -----------------------------------------------------------------------
    ConfigCls = Config(client=client, database=database, source_name=source_name, source_type=source_type, dd_file=dd_file, repo_root_folder=repo_root_folder, runlog=runlog)
    ConfigCls.create_config_aud()

    # -----------------------------------------------------------------------
    # create ICP file
    # -----------------------------------------------------------------------
    print_section("Config Creator Profile", runlog=runlog)
    profilename = f"ConfigCreatorProfile_{client}_{database}.icp"
    icplogmsg = CreateICP(profilename=profilename, sourcetype=source_type, client=client, database=database, sourcename=source_name, copyffoptions="", filedateregex="", outputfolder=outputfolder, fileimportmatch="", delimiter="", enclosedby="", pgpkey="")

    runlog.log(icplogmsg)
    return {"outputfolder": outputfolder, "log": runlog.out()}

if __name__ == "__main__":
    ingestconfigcreator_aud()