from Library.FunctionFiles.Functions import *

class Sources:
    def __init__(self):
        self.src_data = {}
        self.sources_append = []
        self.sources_replace = []
        return

    # Create Sources File
    def create_sources(self, source_name: str, table_name: str, pk_str: str, rawaud_ind: int, src_date_ind: str, std_ind: int, std_query_filename: str, copyinto_filename: str, threshold: int, db_folder: str, runlog: object, repo_root_folder:str, client:str, import_view_name:str="", dlp_cols:list=[]):
        # map import table or view
        import_table_name = table_name
        if len(import_view_name) > 0:
            import_table_name = import_view_name

        # define base key value pairs
        self.src_data["name"] = table_name.lower()
        self.src_data["createHistoryIndicator"] = False
        self.src_data["deletesIndicator"] = False
        self.src_data["deleteFromSourceSql"] = None
        self.src_data["destinationTable"] = f"import.{import_table_name.lower()}"
        self.src_data["destinationTableUnique"] = f"tmp.{table_name.lower()}unique"

        # define getLastDateProperties values
        getLastDateProperties = {}
        getLastDateProperties["daysBack"] = 0
        getLastDateProperties["lastDateColumn"] = src_date_ind
        getLastDateProperties["refresh"] = 0
        getLastDateProperties["schema"] = "stage"
        getLastDateProperties["seasonYearIndicator"] = 0
        getLastDateProperties["whereClause"] = ""
        getLastDateProperties["tableName"] = table_name.lower()

        if len(src_date_ind) > 1:
            self.src_data["getLastDateIndicator"] = True
        else:
            self.src_data["getLastDateIndicator"] = False
        self.src_data["getLastDateProperties"] = getLastDateProperties

        # define importSql values
        importSql = []

        # remove truncate if source customization set it to NoTruncate
        truncatetable = 1
        flattenquery = 1
        for key in self.sources_append:
            if key[0] == "importSql":
                if "NOTRUNCATE" in str(key[1]).upper():
                    truncatetable = 0
                if "NOFLATTEN" in str(key[1]).upper():
                    flattenquery = 0

        if truncatetable == 1:
            importSql.append({"sortOrder": 0, "sqlFileName": f"{table_name.lower()}-truncate.sql", "saveResults": False})

        # if there is no copy into file, don't add copy into reference in import sql
        if copyinto_filename != "":
            importSql.append({"sortOrder": 1, "sqlFileName": copyinto_filename, "saveResults": True})

        self.src_data["historyTableCreateSql"] = None
        self.src_data["importSql"] = importSql

        # set raw_audience_indicator to boolean
        raw_audience_indicator_bool = False
        if rawaud_ind == "1":
            raw_audience_indicator_bool = True
        else:
            raw_audience_indicator_bool = False

        self.src_data["rawaudienceIndicator"] = raw_audience_indicator_bool

        # set standardization_indicator to boolean
        standardization_indicator_bool = False
        if std_ind == "1":
            standardization_indicator_bool = True
        else:
            standardization_indicator_bool = False

        self.src_data["isStandardizationSource"] = standardization_indicator_bool

        if std_ind == "1":
            melissaProperties = {}

            melissaProperties["standardizationtablename"] = f"tmp.{table_name.lower()}_standardization"
            melissaProperties["standardizationquery"] = std_query_filename

            self.src_data["melissaproperties"] = melissaProperties


        self.src_data["mergeDestinationTable"] = f"stage.{table_name.lower()}"
        self.src_data["mergeToStageSql"] = None
        self.src_data["primaryKeyColumns"] = pk_str
        self.src_data["rowCountCheckOverride"] = 1
        self.src_data["sourceQueryFileName"] = table_name
        self.src_data["sourceQueryIncludeDeletedRecords"] = None
        self.src_data["truncateLoadDestinationTable"] = True
        self.src_data["uniqueTableCreateSql"] = None

        # append additional keys from appendkeyslist
        for key in self.sources_append:
            if key[0] == "importSql":
                for val in key[1]:
                    # don't add flatten in importsql if source customization instructed to not include
                    if flattenquery == 0 and "flatten" in str(val):
                        break
                    # only append if value is a dictionary
                    if isinstance(val, dict):
                        self.src_data[key[0]].append(val)
            else:
                self.src_data[key[0]] = key[1]

        # replace keys from replace list
        for key in self.sources_replace:
            self.src_data[key[0]] = key[1]

        # add DLP columns
        dlp_col_str = ""
        for col in dlp_cols:
            dlp_col_str += f"{col},"

        dlp_col_str = dlp_col_str.strip(",")
        self.src_data["dlpColumns"] = dlp_col_str

        # put sources object in an array
        src_data_array = self.src_data

        # add API suffix if source is Archtics to match current naming convention
        if source_name.upper() == "ARCHTICS":
            if "API" in source_name.upper():
                filename = f"{table_name.lower()}_api.json"
            else:
                filename = f"{table_name.lower()}_sftp.json"
        else:
            filename = f"{table_name.lower()}.json"

        # output JSON
        writeJSON(filecontent=src_data_array, filename=filename, filetype="sources", client=client, source_name=source_name, db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)

        return filename

    # append custom keys
    def append(self, key_name:str, value:str):
        self.sources_append.append([key_name,value])
        return

    # replace key value
    def replace(self, key_name:str, value:str):
        self.sources_replace.append([key_name,value])
        return
