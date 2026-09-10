from Library.FunctionFiles.Functions import *

class BusRules:
    def __init__(self):
        self.br_array = []
        self.hasrules = False
        self.select_columns = ""
        self.join_columns = ""
        self.rownum_columns = ""

        return

    def set_std_cols(self, select_columns:str, join_columns:str, rownum_columns:str):
        self.select_columns = select_columns
        self.join_columns = join_columns
        self.rownum_columns = rownum_columns

        return

    def get_std_select_columns(self):
        return self.select_columns

    def get_std_join_columns(self):
        return self.join_columns

    def get_std_rownum_columns(self):
        return self.rownum_columns

    def add_rule(self, rule_dict:dict):
        self.br_array.append(rule_dict)
        self.hasrules = True
        return

    def out(self, table_name:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str):
        if self.hasrules:

            # define output folder and filename
            filename = f"{table_name.lower()}.json"

            # write json to file
            writeJSON(filecontent=self.br_array, filename=filename, filetype="businessrules", client=client, source_name=source_name, db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

        return self.hasrules

    def br_array_out(self):
        return self.br_array
