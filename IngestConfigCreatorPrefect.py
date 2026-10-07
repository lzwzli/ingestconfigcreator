import argparse, sys
from Library.Class.Logger import *
from Library.Class.Config import *
from version import *

def ingestconfigcreator_prefect(srcType:str="", runProfileDict:dict=None, ui_params:dict=None):
    # ----------------------------------------------------------------
    # create runlog object
    # ----------------------------------------------------------------
    runlog = Logger()
    runProfileDict = runProfileDict or {}
    ui_mode = ui_params is not None

    # ----------------------------------------------------------------
    # report version
    # ----------------------------------------------------------------
    runlog.log(f"Running IngestConfigCreator-Prefect version {version}. Released {releasedate}.")
    runlog.log(f"**THIS VERSION IS ONLY FOR PREFECT OCHESTRATED SOURCES**")
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
        source_type = ui_params.get("sourcetype", "").upper()
        client = ui_params.get("client", "").strip().upper()
        database = ui_params.get("database", "").strip().upper()
        source_name = ui_params.get("sourcename", "").strip()
        dd_file = ui_params.get("ddfile", "")
        copy_ff_options = ui_params.get("copyffoptions") or None
        delimiter = ui_params.get("delimiter", "")
        enclosed_by = ui_params.get("enclosedby") or '"'
        file_import_match = ui_params.get("fileimportmatch", "")
        filedate_regex = ui_params.get("filedateregex") or None
        pgp_key = ui_params.get("pgpkey", "")
        repo_root_folder = ui_params.get("reporootfolder", "") or ""
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument('--sourcetype', help="source type. FF=Flat File sources / KIP=KIP acquired sources")
        parser.add_argument('--ddfile', help="input path to data dictionary file")
        parser.add_argument('--database', help="database name, i.e. tepperqa")
        parser.add_argument('--client', help="client abbreviation name, i.e. tepper")
        parser.add_argument('--sourcename', help="source name, i.e. dynamics")
        parser.add_argument('--delimiter', help="field delimiter")
        parser.add_argument('--enclosedby', help="character enclosing value")
        parser.add_argument('--copyffoptions', help="additional copy into file format options")
        parser.add_argument('--fileimportmatch', help="non regex pattern to match all files to be imported")
        parser.add_argument('--filedateregex', help="regex pattern to get file date from file name")
        parser.add_argument('--pgpkey', help="pgp key account to decrypt .gpg or .pgp files")
        parser.add_argument('--reporootfolder', help="folder path to user Documents folder")
        args = parser.parse_args()

        source_type = args.sourcetype
        client = args.client
        database = args.database
        source_name = args.sourcename
        dd_file = args.ddfile
        copy_ff_options = args.copyffoptions
        delimiter = args.delimiter
        enclosed_by = args.enclosedby
        file_import_match = args.fileimportmatch
        filedate_regex = args.filedateregex
        pgp_key = args.pgpkey
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
        file_import_match = loadProfileVars(runProfileDict, varname="fileimportmatch")
        copy_ff_options = loadProfileVars(runProfileDict, varname="copyffoptions")
        delimiter = loadProfileVars(runProfileDict, varname="delimiter")
        enclosed_by = loadProfileVars(runProfileDict, varname="enclosedby")
        filedate_regex = loadProfileVars(runProfileDict, varname="filedateregex")
        pgp_key = loadProfileVars(runProfileDict, varname="pgpkey")

        runlog.log(f'Loaded profile variables:')
        runlog.log(f"- {client=}")
        runlog.log(f"- {database=}")
        runlog.log(f"- {source_name=}")
        runlog.log(f"- {file_import_match=}")
        runlog.log(f"- {copy_ff_options=}")
        runlog.log(f"- {filedate_regex=}")
        if source_type == "FF":
            runlog.log(f"- {delimiter=}")
            runlog.log(f"- {enclosed_by=}")
            runlog.log(f"- {pgp_key=}")

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
    source_type_list = ['FF', 'KIP', 'SDS']
    if not ui_mode and srcType == "" and source_type not in source_type_list:
        while source_type not in source_type_list:
            isFF = input("Is this a Flat File source? (Y/N) : ")
            if isFF.upper() == "Y":
                source_type = "FF"
            elif isFF.upper() == "N":
                isKIP = input("Is this an API (KIP) source? (Y/N) : ")
                if isKIP.upper() == "Y":
                    source_type = "KIP"
                else:
                    source_type = "SDS"
    elif srcType != "":
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
    # Copy Into File Format Options
    # -----------------------------------------------------------------------
    while not ui_mode and copy_ff_options is None:
        copy_ff_options = input("[Optional] Enter any custom Copy Into file format options: ")

    if copy_ff_options == "":
        copy_ff_options = None

    runlog.append(f"Add. Copy Into format options = {copy_ff_options}")

    # -----------------------------------------------------------------------
    # Copy Into File Format Options
    # -----------------------------------------------------------------------
    while not ui_mode and filedate_regex is None:
        if source_type == "KIP":
            filedate_regex = input("[Optional] Enter a custom regex to get file date from file name. Default is '[0-9]{14}': ")
        else:
            filedate_regex = input("[Optional] Enter a custom regex to get file date from file name. Default is '[0-9]{8,12}': ")

    if filedate_regex == "" or filedate_regex == None:
        if source_type == "KIP":
            filedate_regex = '[0-9]{14}'
        else:
            filedate_regex = '[0-9]{8,12}'

    runlog.append(f"Filedate Regex = {filedate_regex}")

    # -----------------------------------------------------------------------
    # ask for Flat File specific arguments
    # -----------------------------------------------------------------------
    if source_type == "FF":
        # delimiter
        while not ui_mode and (delimiter is None or delimiter == ""):
            delimiter = input("Enter column delimiter character: ")
        runlog.append(f"Column Delimiter = {delimiter}")

        # enclosed by
        while not ui_mode and enclosed_by is None:
            enclosed_by = input('[Optional] Override default " character enclosing values: ')

        if enclosed_by == "":
            enclosed_by = '"'
        runlog.append(f"Enclosing character = {enclosed_by}")

        # file_import_match
        while not ui_mode and (file_import_match is None or ("." not in file_import_match)):
            file_import_match = input("Enter the pattern to match all files to be imported. Must end with file extension. Not a regex.: ")
        runlog.append(f"File Import Match = {file_import_match}")

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

                if repo_root_folder == "":
                    runlog.log("No repo folder selected. Not creating files in repo.")
                else:
                    repo_root_folder = normalizePath(repo_root_folder) + os.sep

    # -----------------------------------------------------------------------
    # define db output folder for icp creation
    # -----------------------------------------------------------------------
    outputfolder = outputFolder(dd_file) + f"{client.upper()}{os.sep}{database}{os.sep}"

    # -----------------------------------------------------------------------
    # process Flat File source
    # -----------------------------------------------------------------------
    if source_type == "FF" or source_type == "SDS":
        # -----------------------------------------------------------------------
        # create command with integrated arguments
        # -----------------------------------------------------------------------
        if enclosed_by == None or enclosed_by == 'None':
            cmd = f"python .\\IngestConfigCreatorPrefect.py --sourcetype {source_type} --client {client} --database {database} --sourcename {source_name} --delimiter '{delimiter}' --copyffoptions \"{copy_ff_options}\" --filedateregex '{filedate_regex}' --enclosedby None --fileimportmatch '{file_import_match}' --ddfile '{dd_file}' --reporootfolder '{repo_root_folder}'"
        else:
            if enclosed_by == '"':
                cmd = f"python .\\IngestConfigCreatorPrefect.py --sourcetype {source_type} --client {client} --database {database} --sourcename {source_name} --delimiter '{delimiter}' --copyffoptions \"{copy_ff_options}\" --filedateregex '{filedate_regex}' --enclosedby '{enclosed_by}' --fileimportmatch '{file_import_match}' --ddfile '{dd_file}' --reporootfolder '{repo_root_folder}'"
            else:
                cmd = f"python .\\IngestConfigCreatorPrefect.py --sourcetype {source_type} --client {client} --database {database} --sourcename {source_name} --delimiter '{delimiter}' --copyffoptions \"{copy_ff_options}\" --filedateregex '{filedate_regex}' --enclosedby '{enclosed_by}' --fileimportmatch '{file_import_match}' --ddfile '{dd_file}' --reporootfolder '{repo_root_folder}'"

        runlog.log("")
        runlog.log("Command with arguments:")
        runlog.log("")
        runlog.log(cmd)
        runlog.log("")

        # -----------------------------------------------------------------------
        # create config
        # -----------------------------------------------------------------------
        ConfigCls = Config(client=client, database=database, source_name=source_name, source_type=source_type, dd_file=dd_file, repo_root_folder=repo_root_folder, runlog=runlog)
        ConfigCls.create_config_FF(file_date_regex=filedate_regex, field_delimiter=delimiter, field_enclosed_by=enclosed_by, copyffoptions=copy_ff_options)

    # -----------------------------------------------------------------------
    # process KIP source
    # -----------------------------------------------------------------------
    elif source_type == "KIP":
        # -----------------------------------------------------------------------
        # create command with integrated arguments
        # -----------------------------------------------------------------------
        cmd = f"python .\\IngestConfigCreatorPrefect.py --sourcetype {source_type} --client {client} --database {database} --sourcename {source_name} --copyffoptions {copy_ff_options} --filedateregex '{filedate_regex}' --ddfile '{dd_file}' --reporootfolder '{repo_root_folder}'"

        runlog.log("")
        runlog.log("Command with arguments:")
        runlog.log("")
        runlog.log(cmd)
        runlog.log("")

        # -----------------------------------------------------------------------
        # create config
        # -----------------------------------------------------------------------
        ConfigCls = Config(client=client, database=database, source_name=source_name, source_type=source_type, dd_file=dd_file, repo_root_folder=repo_root_folder, runlog=runlog)
        ConfigCls.create_config_KIP(file_date_regex=filedate_regex, copyffoptions=copy_ff_options)

    # -----------------------------------------------------------------------
    # create ICP file
    # -----------------------------------------------------------------------
    print_section("Config Creator Profile", runlog=runlog)
    profilename = f"ConfigCreatorProfile_{client}_{database}.icp"
    icplogmsg = CreateICP(profilename=profilename, sourcetype=source_type, client=client, database=database, sourcename=source_name, copyffoptions=copy_ff_options, filedateregex=filedate_regex, outputfolder=outputfolder, fileimportmatch=file_import_match, delimiter=delimiter, enclosedby=enclosed_by, pgpkey=pgp_key)

    runlog.log(icplogmsg)
    return {"outputfolder": outputfolder, "log": runlog.out()}

if __name__ == "__main__":
    ingestconfigcreator_prefect()