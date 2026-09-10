import argparse, sys
from Library.Class.Logger import *
from Library.Class.Config import *
from version import *

def ingestconfigcreator_5x(srcType:str="", runProfileDict:dict={}):
    # ----------------------------------------------------------------
    # create runlog object
    # ----------------------------------------------------------------
    runlog = Logger()

    # ----------------------------------------------------------------
    # report version
    # ----------------------------------------------------------------
    runlog.log(f"Running IngestConfigCreator-5x version {version}. Released {releasedate}.")
    runlog.log(f"**THIS VERSION IS ONLY FOR 5x SOURCES**")
    runlog.log("")

    # ----------------------------------------------------------------
    # try import dependencies
    # ----------------------------------------------------------------
    try:
        import argparse
        import json
        import os
        import re
        import sys
        from dataclasses import dataclass
        from pathlib import Path
        from typing import Any, Dict, Iterable, List, Optional, Tuple

        from tqdm import tqdm
        from openpyxl import load_workbook  # type: ignore # pylint: disable=import-error
        from jinja2 import (
            Environment,
            FileSystemLoader,
            StrictUndefined,
            Template,
            TemplateNotFound,
        )
    except ModuleNotFoundError:
        print("Please run 'py setup5x.py install' to install dependency packages.")
        sys.exit(1)

    # -----------------------------------------------------------------------
    # parse arguments
    # -----------------------------------------------------------------------
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
    if len(runProfileDict) > 0:
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
    while dd_file is None or dd_file == "":
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
    while client is None or client == "":
        client = input("Enter client abbreviation: ")

    client = client.upper()
    runlog.append(f"Client = {client}")

    # -----------------------------------------------------------------------
    # database
    # -----------------------------------------------------------------------
    while database is None or database == "":
        database = input("Enter database name: ")

    database = database.upper()
    runlog.append(f"Database = {database}")

    # -----------------------------------------------------------------------
    # source_name
    # -----------------------------------------------------------------------
    while source_name is None or source_name == "":
        source_name = input("Enter source name: ")

        if source_name.upper() == "ARCHTICS" and source_type == "KIP":
            source_name = "archtics-api"

        source_name = source_name.capitalize()

    runlog.append(f"Source Name = {source_name}")

    # -----------------------------------------------------------------------
    # Repo root folder
    # -----------------------------------------------------------------------
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
    ConfigCls.create_config_5x()

    # -----------------------------------------------------------------------
    # create ICP file
    # -----------------------------------------------------------------------
    print_section("Config Creator Profile", runlog=runlog)
    profilename = f"ConfigCreatorProfile_{client}_{database}.icp"
    icplogmsg = CreateICP(profilename=profilename, sourcetype=source_type, client=client, database=database, sourcename=source_name, copyffoptions=copy_ff_options, filedateregex=filedate_regex, outputfolder=outputfolder, fileimportmatch=file_import_match, delimiter=delimiter, enclosedby=enclosed_by, pgpkey=pgp_key)

    runlog.log(icplogmsg)


if __name__ == "__main__":
    ingestconfigcreator_5x()