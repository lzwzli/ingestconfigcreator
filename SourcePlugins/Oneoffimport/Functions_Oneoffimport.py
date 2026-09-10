from Library.FunctionFiles.Functions import *
from Library.Class.Document import *

custom_filedate = "TO_CHAR(REGEXP_SUBSTR(METADATA$FILENAME, '[0-9]{8,12}', 1, 1))"

def fn_create_import_DDL_custom(table_name:str, col_list:list, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str, data_resources:list):
    # create normal import table
    create_import_DDL(table_name=table_name, col_list=col_list, version=version, db_folder=db_folder, runlog=runlog, repo_root_folder=repo_root_folder, client=client, source_name=source_name)
    # append data resources
    data_resources.append(["import", table_name.lower()])
    data_resources.append(["control", "sp_oneoffCheckDuplicateFile"])
    data_resources.append(["control", "sp_oneoffGetNotificationIndex"])
    data_resources.append(["control", "sp_oneoffInsertIntoImportValidationMonitoring"])
    data_resources.append(["control", "sp_oneoffUpdateValidationIndex"])
    data_resources.append(["control", "sp_oneoffUpdateValidationMonitoring"])
    data_resources.append(["control", "importvalidationmonitoring"])

    return

# stage DDL and framework config file
def fn_create_stage_DDL_custom(table_name:str, col_list:list, pk_str:str, phone_col_list:list, std_ind:int, rawaud_ind:int, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str, data_resources:list, email_col_list:list=[]):

    StageDDL_str, StageArchive_DDL = create_stage_DDL(table_name=table_name.lower(), col_list=col_list, pk_str=pk_str, phone_col_list=phone_col_list, std_ind=std_ind, rawaud_ind=rawaud_ind, version=version, db_folder=db_folder, runlog=runlog, repo_root_folder=repo_root_folder, client=client, source_name=source_name, email_col_list=email_col_list)

    StageDDL = Document()
    StageDDL.newline(StageDDL_str)

    # append data resources
    data_resources.append(["stage", table_name.lower()])

    #--------------------------
    # framework config files
    # --------------------------
    # create import.json file
    expectedcols = []
    datecols = []
    numbercols = []
    emailcols = []

    for col in col_list:
        colname = col[1].upper()
        datatype = col[2].upper()

        expectedcols.append(colname)
        if "TIMESTAMP" in datatype:
            datecols.append(colname)
        elif "NUMBER" in datatype:
            numbercols.append(colname)

    importdict = {}
    importdict["expectedColumns"] = expectedcols
    importdict["dateColumns"] = datecols
    importdict["numberColumns"] = numbercols
    importdict["phoneColumns"] = phone_col_list
    importdict["emailColumns"] = email_col_list

    # output JSON
    writeJSON(filecontent=importdict, filename="import.json", filetype="framework", client=client, source_name=source_name, db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

    # create email.json file
    emaildict={}
    emaildict["senderEmail"] = "DoNotReply@kagr.com"
    emaildict["recipientEmail"] = []
    emaildict["ccRecipientEmail"] = []
    emaildict["bccRecipientEmail"] = []

    # output JSON
    writeJSON(filecontent=emaildict, filename="email.json", filetype="framework", client=client, source_name=source_name, db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

    # return StageDDL
    return StageDDL.out(), data_resources


# create acquire file
def fn_create_acquire_file(file_match_list:list, table_name_list:list, db_folder:str, runlog:object, client:str, repo_root_folder:str, acquire_custom_info_list:list):
    print_section(msg="Working on Acquire File", runlog=runlog)

    acquire_file = {}

    # create sourceFile key value dictionary per file pattern
    sourceFile_list = []

    sourceFile_dict_passing = {}
    sourceFile_dict_passing["fileMatchPattern"] = "OneOff_*.txt"
    sourceFile_dict_passing["subdirectory"] = "Passing"

    sourceFile_list.append(sourceFile_dict_passing)

    sourceFile_dict_override = {}
    sourceFile_dict_override["fileMatchPattern"] = "OneOff_*.txt"
    sourceFile_dict_override["subdirectory"] = "Override/Passing"
    sourceFile_list.append(sourceFile_dict_override)

    acquire_file["sourceFile"] = sourceFile_list
    acquire_file["zipFoldername"] = None
    acquire_file["baseDirectory"] = "<fill in parent directory path>"
    acquire_file["encryption"] = None
    acquire_file["deleteFileFromSource"] = True

    # filename
    filename = f"acquire.json"

    # output JSON file
    writeJSON(filecontent=acquire_file, filename=filename, filetype="acquire", client=client, source_name="oneoffimport", db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

    # create framework files

    return
