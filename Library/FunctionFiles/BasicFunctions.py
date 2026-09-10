import os, json, sys, subprocess
from datetime import date
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from Library.Class.Document import *
from importlib import import_module

indent = " "*3

# ----------------------------------------------------------------
# file write
# ----------------------------------------------------------------
def filewrite(folder:str, filename:str, content:str):
    # prefix folder with \\?\ to use extended length path as DOS paths has a limit of 260
    folder = f"\\\\?\\{folder}"
    os.makedirs(folder, exist_ok=True)
    filetowrite = open(folder + filename, "w")
    filetowrite.write(content)
    filetowrite.close()

# ----------------------------------------------------------------
# validate values
# ----------------------------------------------------------------
def validate(input_val:str, values:list):
    default_val = values[0]
    result = None

    if str(default_val).lower() == "int":
        try:
            result = int(input_val)
        except:
            result = 0
    else:
        for val in values:
            if str(input_val) == str(val):
                result = input_val
            else:
                result = default_val

    return result

# ----------------------------------------------------------------
# file dialog
# ----------------------------------------------------------------
def fileDialog(filetype:tuple, title:str):
    tk = Tk()
    tk.withdraw()
    filename = askopenfilename(filetypes=[filetype], title=title)

    return filename

# ----------------------------------------------------------------
# folder dialog
# ----------------------------------------------------------------
def folderDialog(title:str):
    tk = Tk()
    tk.withdraw()
    folder = askdirectory(title=title)

    return folder

# ----------------------------------------------------------------
# create all parts of folder path
# ----------------------------------------------------------------
def create_folders(folder:str, runlog:object):
    os.makedirs(folder, exist_ok=True)
    runlog.log(f"Create folder: {folder}")

# ----------------------------------------------------------------
# console section output
# ----------------------------------------------------------------
def print_section(msg:str, runlog:object):
    seperatorline = "-" * 100
    tablefiller = "-" * 5
    runlog.log("")
    runlog.log(seperatorline)
    runlog.log(f"{tablefiller} {msg} {tablefiller}")
    runlog.log(seperatorline)

# ----------------------------------------------------------------
# console section details output
# ----------------------------------------------------------------
def print_section_detail(msg:str, runlog:object):
    top, bottom = msg.split("\n")
    runlog.log(top)
    runlog.log(indent + f"{bottom}")
    runlog.log("")

# ----------------------------------------------------------------
# normalize the seperators in folder path (resulting path does not end with os.sep
# ----------------------------------------------------------------
def normalizePath(folder_path:str):

    if os.sep == "\\":
        folder_path = folder_path.replace("/", os.sep)
    else:
        folder_path = folder_path.replace("\\", os.sep)

    if folder_path[-1] == os.sep:
        folder_path = folder_path[:-1]

    return folder_path

# ----------------------------------------------------------------
# lookup using query
# ----------------------------------------------------------------
def qlookup(df:object, lookup_col:str, return_col:str, runlog:object):

    returncols = []

    # as provided
    # runlog.log(f"qlookup: {lookup_col}")
    try:
        returncols += df.query(f'{lookup_col}=="Y"')[return_col].dropna(how='all').tolist()
        returncols += df.query(f'{lookup_col}=="y"')[return_col].dropna(how='all').tolist()
    except:
        pass

    # try upper case
    # runlog.log(f"qlookup: {lookup_col.upper()}")
    try:
        returncols += df.query(f'{lookup_col.upper()}=="Y"')[return_col].dropna(how='all').tolist()
        returncols += df.query(f'{lookup_col.upper()}=="y"')[return_col].dropna(how='all').tolist()
    except:
        pass

    # try lower case
    # runlog.log(f"qlookup: {lookup_col.lower()}")
    try:
        returncols += df.query(f'{lookup_col.lower()}=="Y"')[return_col].dropna(how='all').tolist()
        returncols += df.query(f'{lookup_col.lower()}=="y"')[return_col].dropna(how='all').tolist()
    except:
        pass

    if len(returncols) == 0:
        raise Exception(f"No columns found for {lookup_col}")

    return returncols

# ----------------------------------------------------------------
# lookup using index
# ----------------------------------------------------------------
def ilookup(worksheet:object, lookup_col:str):
    returnidx = worksheet.index[worksheet[lookup_col] == "Y"].tolist()
    returnidx += worksheet.index[worksheet[lookup_col] == "y"].tolist()
    return returnidx

# ----------------------------------------------------------------
# lookup value of one column and return another
# ----------------------------------------------------------------
def clookup(worksheet:object, lookup_col:str, lookup_val:str, return_col:str):
    returncols = worksheet.query(f'{lookup_col}=="{lookup_val}"')[return_col].dropna(how='all').tolist()
    return returncols

# ----------------------------------------------------------------
# Get client Snaplogic project name
# ----------------------------------------------------------------
def get_client_project(client_name:str):
    CICD_Clients = ["NJD", "FLYERS", "RAMS", "TEPPER"]

    client_name = client_name.upper()

    if client_name in CICD_Clients:
        return f"{client_name}_CICD"
    else:
        return client_name

# ----------------------------------------------------------------
# create pk string
# ----------------------------------------------------------------
def create_pk_string(pk:list):
    pk_string = "\t"
    for key in pk:
        pk_string += f"{key}||'-'||"

    pk_string = pk_string[:-7]

    return pk_string

# ----------------------------------------------------------------
# get output folder
# ----------------------------------------------------------------
def outputFolder(path:str):
    # define output folders
    return os.path.dirname(os.path.abspath(path)) + os.sep

# ----------------------------------------------------------------
# build Tests Folder
# ----------------------------------------------------------------
def outputTestFolder(path:str):
    return outputFolder(path) + f"TestResults{os.sep}"

# ----------------------------------------------------------------
# get file name from path
# ----------------------------------------------------------------
def getFilename(file_path:str):
    file_path = normalizePath(file_path)
    path_list = file_path.split(os.sep)
    path_list.reverse()
    filename = path_list[0]

    return filename

# ----------------------------------------------------------------
# open file
# ----------------------------------------------------------------
def openFile(file_path:str):
    if sys.platform == "win32":
        os.startfile(file_path)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, file_path])

    return

# ----------------------------------------------------------------
# parse profile variables
# ----------------------------------------------------------------
def getProfileDict(profilelist:list):
    profileDict = {}
    for param in profilelist:
        name = param.split("=")[0]
        val = param.split("=")[1]

        profileDict[name] = val

    return profileDict

# ----------------------------------------------------------------
# load profile variables
# ----------------------------------------------------------------
def loadProfileVars(profiledict:dict, varname:str):
    try:
        var = profiledict[varname]
    except:
        var = ""

    return var

# ----------------------------------------------------------------
# output JSON
# ----------------------------------------------------------------
def writeJSON(filecontent, filename:str, filetype:str, client:str, source_name:str, db_folder:str, repo_root_folder:str, runlog:object, header:str="", footer:str=""):
    # convert to json
    json_file_data = json.dumps(filecontent, indent=2, separators=(", ", ": "))

    # determine file type folder
    if filetype.upper() == "PREFECTCLIENT":
        output_folder = f"{db_folder}prefectclient_repo{os.sep}"
    else:
        if filetype.upper() == "SOURCES":
            filetypefolder = "sources"
        elif filetype.upper() == "BUSINESSRULE" or filetype.upper() == "BUSINESSRULES":
            filetypefolder = "businessrules"
        elif filetype.upper() == "ACQUIRE" or filetype.upper() == "FEATURE":
            filetypefolder = "feature"
        elif filetype.upper() == "FRAMEWORK":
            filetypefolder = "framework"
        else:
            sys.exit()

        if source_name == "rawaudience":
            output_folder = f"{db_folder}config_repo{os.sep}{filetypefolder}{os.sep}rawaudience{os.sep}"
        else:
            output_folder = f"{db_folder}config_repo{os.sep}{filetypefolder}{os.sep}"

    # add header
    if header != "":
        json_file_data = header + json_file_data

    if footer != "":
        json_file_data = json_file_data + footer

    # output to output folder
    filewrite(folder=output_folder, filename=filename, content=json_file_data)
    print_section_detail(msg=f"{filetype.upper()} FILE - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # output to repo folder
    if repo_root_folder != "":
        configrepo_folder = f"{repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{client.upper()}{os.sep}{source_name.lower()}{os.sep}{filetypefolder}{os.sep}"
        filewrite(folder=configrepo_folder, filename=filename, content=json_file_data)
        print_section_detail(msg=f"{filetype.upper()} FILE - {filename}\nCreated in: {configrepo_folder}", runlog=runlog)

    return