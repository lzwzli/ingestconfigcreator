from Library.FunctionFiles.Functions import *

def fn_create_acquire_file(file_match_list:list, table_name_list:list, db_folder:str, runlog:object, client:str, repo_root_folder:str, acquire_custom_info_list:list):
    print_section(msg="Working on Acquire File", runlog=runlog)

    acquire_file = {}

    # create sourceFile key value dictionary per file pattern
    sourceFile_list = []

    for file_text in file_match_list:
        sourceFile_dict = {}
        file_pattern = file_text.replace(".*", "*")
        subdirectory = (file_text
                        .replace(".json","")
                        .replace(".*","")
                        )

        sourceFile_dict["fileMatchPattern"] = file_pattern
        sourceFile_dict["subdirectory"] = subdirectory

        sourceFile_list.append(sourceFile_dict)

    acquire_file["sourceFile"] = sourceFile_list
    acquire_file["zipFoldername"] = None
    acquire_file["baseDirectory"] = "<fill in parent directory path>"
    acquire_file["encryption"] = None
    acquire_file["deleteFileFromSource"] = True

    # filename
    filename = f"acquire.json"

    # output JSON
    writeJSON(filecontent=acquire_file, filename=filename, filetype="acquire", client=client, source_name="fanaticspos", db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

    return