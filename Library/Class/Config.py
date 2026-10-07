from Library.Class.Sources import *
from Library.Class.SourceTable import *
from Library.Class.BusRules import *
from Library.Class.StdSheet import *
from Library.Class.RawAudSheet import *
from Library.Class.PrefectClient import *
from Library.Tests.TestsGenerator import *
from Library.Class.MenuPrompt import *
from importlib import import_module
from datetime import datetime

indent = " "*3

class Config:
    def __init__(self, client:str, database:str, source_name:str, source_type:str, dd_file:str, repo_root_folder:str, runlog:object):
        # map input param to class param
        self.runlog = runlog
        self.client = client
        self.database = database
        self.source_name = source_name
        self.source_type = source_type
        self.dd_file = dd_file
        self.repo_root_folder = repo_root_folder
        self.isStandardizedSource = 0
        self.isRawAudienceSource = 0

        # initialize custom function variables
        self.has_source_functions = False
        self.has_fn_sources_append = False
        self.has_fn_busrules_append = False
        self.has_fn_create_copyinto_custom = False
        self.has_fn_dataresources_append = False
        self.has_fn_create_importraw_DDL_custom = False
        self.has_fn_create_import_DDL_custom = False
        self.has_fn_create_stage_DDL_custom = False
        self.has_fn_create_flatten_custom = False
        self.has_fn_create_truncate_query_custom = False
        self.has_fn_create_feature_file_custom = False
        self.has_fn_create_acquire_file = False
        self.has_fn_get_acquire_custom_info = False
        self.has_fn_feature_custom_info = False
        self.has_fn_create_unique_sp_custom = False
        self.has_fn_create_merge_sp_custom = False

        # initialize resource list
        self.data_resources = []
        self.config_resources = []
        self.schema_drift_result = [0, 0]
        self.schema_drift_script_name_list = []
        self.table_name_list = []
        self.filematchtext_list = []
        self.filesuffixmap_list = []
        self.ra_filename_list = []
        self.acquire_custom_info_list = []

        # set timestamp
        now = datetime.now()
        self.dts = now.strftime("%Y%m%d%H%M")

        # runlog variables
        self.runlog_filename = f"{client}_{database}_{source_name}_{self.dts}.txt"

        # test file
        self.test_file = Document()

        # define output folders
        self.client_folder = os.path.dirname(os.path.abspath(dd_file)) + os.sep + client.upper()
        self.database_folder = self.client_folder + os.sep + database + os.sep
        self.ref_folder = f"{self.database_folder}{os.sep}ForReferenceOnly{os.sep}"
        os.makedirs(self.ref_folder, exist_ok=True)

        return

    # =======================================================================
    # load source custom functions
    # =======================================================================
    def load_source_functions(self):
        try:
            # ----------------------------------------------------------------
            # load source specific functions file
            # ----------------------------------------------------------------
            functions_plugin_name = f"SourcePlugins.{self.source_name.capitalize()}.Functions_{self.source_name.capitalize()}"

            self.runlog.log(f"Try to load {functions_plugin_name}")
            functions_plugin = import_module(functions_plugin_name)

            self.has_source_functions = True

            self.runlog.log("")
            self.runlog.log(f"Imported {functions_plugin_name} into Config class.")

            # ----------------------------------------------------------------
            # try to load sources_append function
            # ----------------------------------------------------------------
            try:
                self.fn_sources_append = getattr(functions_plugin, "fn_sources_append")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_sources_append function loaded.")
                self.has_fn_sources_append = True
            except:
                self.runlog.log(f"{indent}No fn_sources_append function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load busrules_append function
            # ----------------------------------------------------------------
            try:
                self.fn_busrules_append = getattr(functions_plugin, "fn_busrules_append")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_busrules_append function loaded.")
                self.has_fn_busrules_append = True
            except:
                self.runlog.log(f"{indent}No fn_busrules_append function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom copy into
            # ----------------------------------------------------------------
            try:
                self.fn_create_copyinto_custom = getattr(functions_plugin, "fn_create_copyinto_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_copyinto_custom loaded.")
                self.has_fn_create_copyinto_custom = True
            except:
                self.runlog.log(f"{indent}No fn_create_copyinto_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom feature file
            # ----------------------------------------------------------------
            try:
                self.fn_create_feature_file_custom = getattr(functions_plugin, "fn_create_feature_file_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_feature_file_custom loaded.")
                self.has_fn_create_feature_file_custom = True

            except:
                self.runlog.log(f"{indent}No fn_create_feature_file_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom importraw DDL
            # ----------------------------------------------------------------
            try:
                self.fn_create_importraw_DDL_custom = getattr(functions_plugin, "fn_create_importraw_DDL_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_importraw_DDL_custom loaded.")
                self.has_fn_create_importraw_DDL_custom = True
            except:
                self.runlog.log(f"{indent}No fn_create_importraw_DDL_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom import DDL
            # ----------------------------------------------------------------
            try:
                self.fn_create_import_DDL_custom = getattr(functions_plugin, "fn_create_import_DDL_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_import_DDL_custom loaded.")
                self.has_fn_create_import_DDL_custom = True
            except:
                self.runlog.log(f"{indent}No fn_create_import_DDL_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom stage DDL
            # ----------------------------------------------------------------
            try:
                self.fn_create_stage_DDL_custom = getattr(functions_plugin, "fn_create_stage_DDL_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_stage_DDL_custom loaded.")
                self.has_fn_create_stage_DDL_custom = True
            except:
                self.runlog.log(
                    f"{indent}No fn_create_stage_DDL_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom merge SP
            # ----------------------------------------------------------------
            try:
                self.fn_create_merge_sp_custom = getattr(functions_plugin, "fn_create_merge_sp_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_merge_sp_custom loaded.")
                self.has_fn_create_merge_sp_custom = True
            except:
                self.runlog.log(
                    f"{indent}No fn_create_merge_sp_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom unique SP
            # ----------------------------------------------------------------
            try:
                self.fn_create_unique_sp_custom = getattr(functions_plugin, "fn_create_unique_sp_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_unique_sp_custom loaded.")
                self.has_fn_create_unique_sp_custom = True
            except:
                self.runlog.log(
                    f"{indent}No fn_create_unique_sp_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom flatten
            # ----------------------------------------------------------------
            try:
                self.fn_create_flatten_custom = getattr(functions_plugin, "fn_create_flatten_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_flatten_custom loaded.")
                self.has_fn_create_flatten_custom = True
            except:
                self.runlog.log(f"{indent}No fn_create_flatten_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load custom truncate
            # ----------------------------------------------------------------
            try:
                self.fn_create_truncate_query_custom = getattr(functions_plugin, "fn_create_truncate_query_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_truncate_query_custom loaded.")
                self.has_fn_create_truncate_query_custom = True
            except:
                self.runlog.log(f"{indent}No fn_create_truncate_query_custom function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load data resources append
            # ----------------------------------------------------------------
            try:
                self.fn_dataresources_append = getattr(functions_plugin, "fn_dataresources_append")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_dataresources_append loaded.")
                self.has_fn_dataresources_append = True

            except:
                self.runlog.log(f"{indent}No fn_dataresources_append function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load create acquire file
            # ----------------------------------------------------------------
            try:
                self.fn_create_acquire_file = getattr(functions_plugin, "fn_create_acquire_file")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_create_acquire_file loaded.")
                self.has_fn_create_acquire_file = True

            except:
                self.runlog.log(f"{indent}No fn_create_acquire_file function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load get acquire custom info
            # ----------------------------------------------------------------
            try:
                self.fn_get_acquire_custom_info = getattr(functions_plugin, "fn_get_acquire_custom_info")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_get_acquire_custom_info loaded.")
                self.has_fn_get_acquire_custom_info = True

            except:
                self.runlog.log(f"{indent}No fn_get_acquire_custom_info function found in {functions_plugin_name}.")

            # ----------------------------------------------------------------
            # try to load feature custom info
            # ----------------------------------------------------------------
            try:
                self.fn_feature_custom_info = getattr(functions_plugin, "fn_feature_custom_info")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_feature_custom_info loaded.")
                self.has_fn_feature_custom_info = True

            except:
                self.runlog.log(f"{indent}No fn_feature_custom_info function found in {functions_plugin_name}.")

        except Exception as e:
            self.runlog.log(f"WARNING: {e}")
            self.has_source_functions = False
            self.runlog.log("")
            self.runlog.log(f"No {functions_plugin_name} found.")

        # ----------------------------------------------------------------
        # check if source specific function file has need_flatten
        # ----------------------------------------------------------------
        self.need_flatten = True
        if self.has_source_functions:
            try:
                self.need_flatten = functions_plugin.need_flatten
            except:
                self.need_flatten = True

        # ----------------------------------------------------------------
        # check if source specific function file has need_import_raw
        # ----------------------------------------------------------------
        try:
            self.need_import_raw = functions_plugin.need_import_raw
        except:
            self.need_import_raw = True

        # ----------------------------------------------------------------
        # check if source specific function file has create_std_busrule
        # ----------------------------------------------------------------
        self.need_create_std_busrule = True
        if self.has_source_functions:
            try:
                self.need_create_std_busrule = functions_plugin.need_create_std_busrule
            except:
                self.need_create_std_busrule = True

        # ----------------------------------------------------------------
        # check if source specific function file has need_create_stg_rawaud_busrule
        # ----------------------------------------------------------------
        self.need_create_stg_rawaud_busrule = True
        if self.has_source_functions:
            try:
                self.need_create_stg_rawaud_busrule = functions_plugin.need_create_stg_rawaud_busrule
            except:
                self.need_create_stg_rawaud_busrule = 1

        # check if source specific function file has need_create_tmp_rawaud_busrule
        self.need_create_tmp_rawaud_busrule = True
        if self.has_source_functions:
            try:
                self.need_create_tmp_rawaud_busrule = functions_plugin.need_create_tmp_rawaud_busrule
            except:
                self.need_create_tmp_rawaud_busrule = 1

        # ----------------------------------------------------------------
        # check if source specific function file has deleteraw_order
        # ----------------------------------------------------------------
        self.deleteraw_order = 3
        if self.has_source_functions:
            try:
                self.deleteraw_order = functions_plugin.deleteraw_order
            except:
                self.deleteraw_order = 3

        # ----------------------------------------------------------------
        # check if source specific function file has custom_filedate
        # ----------------------------------------------------------------
        self.custom_filedate = ''
        if self.has_source_functions:
            try:
                self.custom_filedate = functions_plugin.custom_filedate
            except:
                self.custom_filedate = ''

        # ----------------------------------------------------------------
        # check if source specific function file has custom_stage_location
        # ----------------------------------------------------------------
        self.custom_stage_location = ''
        if self.has_source_functions:
            try:
                self.custom_stage_location = functions_plugin.custom_stage_location
            except:
                self.custom_stage_location = ''

        # ---------------------------------------------------------------
        # check if source specific function files has additions to installDoc
        # ---------------------------------------------------------------
        try:
            self.installDocAdditions = functions_plugin.installDocAdditions
        except:
            self.installDocAdditions = []

        # ----------------------------------------------------------------
        # check if source specific function file has create_archive
        # ----------------------------------------------------------------
        self.create_archive_tables = []
        if self.has_source_functions:
            try:
                self.create_archive_tables = functions_plugin.create_archive_tables
            except:
                self.create_archive_tables = []

        return

    # =======================================================================
    # Read data dictionary file
    # =======================================================================
    def read_dd_file(self):
        self.wslist = []

        # ----------------------------------------------------------------
        # read WorksheetList worksheet from ddfile
        # ----------------------------------------------------------------
        try:
            wslist_sheet = pd.read_excel(io=self.dd_file, sheet_name="WorksheetList")
        except:
            try:
                wslist_sheet = pd.read_excel(io=self.dd_file, sheet_name="Worksheet List")
            except Exception as e:
                raise Exception(f'ERROR: "WorksheetList" or "Worksheet List" not found. {e}')

        # ----------------------------------------------------------------
        # get row index list where Ready column = Y or y
        # ----------------------------------------------------------------
        try:
            # check if Ready column is available
            wslist_sheet["Ready"]
            ws_ready_idx = ilookup(worksheet=wslist_sheet, lookup_col="Ready")

            # ----------------------------------------------------------------
            # get list of worksheet names based on row index where Ready column = Y or y
            # ----------------------------------------------------------------
            for ws_ready_idx_key in ws_ready_idx:
                self.wslist += [wslist_sheet.values[ws_ready_idx_key][0]]

        except:
            # if Ready column is not available, then get all sheets
            self.wslist = wslist_sheet["Worksheet List"].tolist()

        return

    # =======================================================================
    # Flat File Copy into
    # =======================================================================
    def create_copyinto_FF(self, table_name: str, col_list: list, file_match_text: str, file_date_regex: str, field_delimiter: str, field_enclosed_by: str = '', custom_fileformat_options: str = ''):
        # ----------------------------------------------------------------
        # build column list
        # ----------------------------------------------------------------
        elementidx = 1
        copyintocolumns = []
        copyelements = []
        for col in col_list:
            copyintocolumns.append(f"\t{col[1].upper()}")
            copyelements.append(f"\t\tT.\"${str(elementidx)}\"")
            elementidx += 1

        # ----------------------------------------------------------------
        # define filedate_query
        # ----------------------------------------------------------------
        if self.custom_filedate == '':
            filedate_query = f"TO_CHAR(REGEXP_SUBSTR(REPLACE(REPLACE(SPLIT_PART(METADATA$FILENAME, '/', -1),'_',''),'-',''), '{file_date_regex}', 1, 1))"
        else:
            filedate_query = self.custom_filedate

        # ----------------------------------------------------------------
        # define stage location path
        # ----------------------------------------------------------------
        stage_location = f"@IMPORT.INGESTSTAGE/&feature/&teamAbbr/&timestamp"

        # ----------------------------------------------------------------
        # determine FieldEnclosedBy
        # ----------------------------------------------------------------
        if field_enclosed_by == None:
            field_enclosed_by = '"'

        copy_field_enclosed_by = f" FIELD_OPTIONALLY_ENCLOSED_BY = '{field_enclosed_by}'"

        # ----------------------------------------------------------------
        # format custom_fileformat_options
        # ----------------------------------------------------------------
        custom_fileformat_options = custom_fileformat_options.strip()

        if custom_fileformat_options == "None":
            custom_fileformat_options = ""
        elif custom_fileformat_options != '':
            custom_fileformat_options = f" {custom_fileformat_options}"
        else:
            custom_fileformat_options = ""

        # ----------------------------------------------------------------
        # get file extension
        # ----------------------------------------------------------------
        file_extension = file_match_text.split(".")[-1]

        # ----------------------------------------------------------------
        # append .* to file_match_text if it doesn't start with it
        # ----------------------------------------------------------------
        if file_match_text[:2] != ".*":
            file_match_text = f".*{file_match_text}"

        # ----------------------------------------------------------------
        # add compression to file format options
        # ----------------------------------------------------------------
        if file_extension.lower() == "gz":
            custom_fileformat_options += " COMPRESSION = GZIP"

        # ----------------------------------------------------------------
        # initialize CopyInto Document
        # ----------------------------------------------------------------
        CopyInto = Document()

        # ----------------------------------------------------------------
        # Write CopyInto statement
        # ----------------------------------------------------------------
        CopyInto.append(f"/*{table_name} Copy Into version={self.dts} generated by config generator */")
        CopyInto.newline(f"COPY INTO import.{table_name.lower()}")
        CopyInto.newline("(")
        CopyInto.newline("\tFILEDATE,")
        CopyInto.newline("\tFILENAME,")
        CopyInto.newline("\tFILEROWNUMBER,")
        CopyInto.newlinelist(copyintocolumns)
        CopyInto.newline(")")
        CopyInto.newline("FROM")
        CopyInto.newline("(")
        CopyInto.newline("\tSELECT")
        CopyInto.newline(f"\t\t{filedate_query},")
        CopyInto.newline("\t\tMETADATA$FILENAME,")
        CopyInto.newline("\t\tMETADATA$FILE_ROW_NUMBER,")
        CopyInto.newlinelist(copyelements)
        CopyInto.newline("\tFROM ")
        CopyInto.append(f"{stage_location} T")
        CopyInto.newline(")")
        CopyInto.newline(f"PATTERN = '{file_match_text}'")
        CopyInto.newline("ON_ERROR = CONTINUE")
        CopyInto.newline("FORCE = TRUE")
        CopyInto.newline(f"FILE_FORMAT = (TYPE = CSV FIELD_DELIMITER = '{field_delimiter}' TRIM_SPACE = TRUE SKIP_HEADER = 1 ENCODING = 'utf-8'{copy_field_enclosed_by}{custom_fileformat_options})")
        CopyInto.newline(";")

        # ----------------------------------------------------------------
        # define output folder and filename
        # ----------------------------------------------------------------
        filename = f"{table_name.lower()}-copy.sql"
        output_folder = f"{self.database_folder}config_repo{os.sep}sources{os.sep}"

        # ----------------------------------------------------------------
        # write copyinto to file
        # ----------------------------------------------------------------
        filewrite(folder=output_folder, filename=filename, content=CopyInto.out())

        # ----------------------------------------------------------------
        # trace log
        # ----------------------------------------------------------------
        print_section_detail(msg=f"COPYINTO - {filename}\nCreated in: {output_folder}", runlog=self.runlog)

        # ----------------------------------------------------------------
        # write output repo files if repo_root_folder is not empty
        # ----------------------------------------------------------------
        if self.repo_root_folder != "":
            configrepo_folder = f"{self.repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{self.client.upper()}{os.sep}{self.source_name.lower()}{os.sep}sources{os.sep}"
            filewrite(folder=configrepo_folder, filename=filename, content=CopyInto.out())

            print_section_detail(msg=f"COPYINTO - {filename}\nCreated in: {configrepo_folder}", runlog=self.runlog)

        return filename

    # =======================================================================
    # JSON Copy Into
    # =======================================================================
    def create_copyinto_JSON(self, table_name: str, file_match_text: str, file_date_regex: str, custom_fileformat_options: str = ''):
        # ----------------------------------------------------------------
        # initialize CopyInto Document
        # ----------------------------------------------------------------
        CopyInto = Document()

        # ----------------------------------------------------------------
        # define filedate_query
        # ----------------------------------------------------------------
        if self.custom_filedate == '':
            filedate_query = f"TO_CHAR(REGEXP_SUBSTR(REPLACE(SPLIT_PART(SPLIT_PART(METADATA$FILENAME, '/', -1), '_', -1),'-',''), '{file_date_regex}', 1, 1))"
        else:
            filedate_query = self.custom_filedate

        # ----------------------------------------------------------------
        # format custom_fileformat_options
        # ----------------------------------------------------------------
        custom_fileformat_options = custom_fileformat_options.strip()

        if custom_fileformat_options == "None":
            custom_fileformat_options = ""
        elif custom_fileformat_options != '':
            custom_fileformat_options = f" {custom_fileformat_options}"
        else:
            custom_fileformat_options = ""

        # ----------------------------------------------------------------
        # define stage location path
        # ----------------------------------------------------------------
        if self.custom_stage_location == '':
            stage_location = f"@IMPORT.INGESTSTAGE/&feature/&teamAbbr/&timestamp"
        else:
            stage_location = self.custom_stage_location

        # ----------------------------------------------------------------
        # append .* to file_match_text if it doesn't start with it
        # ----------------------------------------------------------------
        if file_match_text[:2] != ".*":
            file_match_text = f".*{file_match_text}"

        # ----------------------------------------------------------------
        # initialize elements of the CopyInto statement
        # ----------------------------------------------------------------
        CopyInto.append(f"/*{table_name} Copy Into version={self.dts} generated by config generator */")
        CopyInto.newline(f"COPY INTO import.{table_name.lower()}_raw")
        CopyInto.newline("(")
        CopyInto.newline("\tFILEDATE,")
        CopyInto.newline("\tFILENAME,")
        CopyInto.newline("\tFILEROWNUMBER,")
        CopyInto.newline("\tJSONDATA")
        CopyInto.newline(")")
        CopyInto.newline("FROM")
        CopyInto.newline("(")
        CopyInto.newline("\tSELECT")
        CopyInto.newline(f"\t\t{filedate_query}FILEDATE,")
        CopyInto.newline("\t\tMETADATA$FILENAME,")
        CopyInto.newline("\t\tMETADATA$FILE_ROW_NUMBER,")
        CopyInto.newline("\t\tPARSE_JSON(T.\"$1\") AS JSONDATA")
        CopyInto.newline("\tFROM ")
        CopyInto.append(f"{stage_location} T")
        CopyInto.newline(")")
        CopyInto.newline(f"PATTERN = '{file_match_text}'")
        CopyInto.newline("ON_ERROR = CONTINUE")
        CopyInto.newline("FORCE = TRUE")
        CopyInto.newline(f"FILE_FORMAT = (TYPE = JSON STRIP_OUTER_ARRAY = TRUE{custom_fileformat_options})")
        CopyInto.newline(";")

        # ----------------------------------------------------------------
        # define output folder and filename
        # ----------------------------------------------------------------
        filename = f"{table_name.lower()}-copy.sql"
        output_folder = f"{self.database_folder}config_repo{os.sep}sources{os.sep}"

        # ----------------------------------------------------------------
        # write copyinto to file
        # ----------------------------------------------------------------
        filewrite(folder=output_folder, filename=filename, content=CopyInto.out())

        # ----------------------------------------------------------------
        # trace log
        # ----------------------------------------------------------------
        print_section_detail(msg=f"COPYINTO - {filename}\nCreated in: {output_folder}", runlog=self.runlog)

        # ----------------------------------------------------------------
        # write output repo files if repo_root_folder is not empty
        # ----------------------------------------------------------------
        if self.repo_root_folder != "":
            configrepo_folder = f"{self.repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{self.client.upper()}{os.sep}{self.source_name.lower()}{os.sep}sources{os.sep}"
            filewrite(folder=configrepo_folder, filename=filename, content=CopyInto.out())

            print_section_detail(msg=f"COPYINTO - {filename}\nCreated in: {configrepo_folder}", runlog=self.runlog)

        return filename

    # =======================================================================
    # Read Worksheet info
    # =======================================================================
    def read_worksheet_info(self, worksheet: str, audonly: bool=False):
        # ----------------------------------------------------------------
        # try to read worksheet. If not found, skip to next sheet.
        # ----------------------------------------------------------------
        self.runlog.log("Get worksheet")
        try:
            wstable = SourceTable(workbook=self.dd_file, worksheet=worksheet, runlog=self.runlog)
        except Exception as errmsg:
            self.runlog.log(f"Worksheet error: {errmsg}")
            raise Exception("Worksheet not found")

        # initialize variables
        col_list = []
        std_sheet_name = ""
        FileReceiptCheck = ""
        Threshold = ""
        SourceDateIndicator = ""
        FileSuffixMap = ""
        SourceTableName = ""
        ImportViewName = ""
        CreateFlattenView = 0
        FileMatchText = ""
        FileMatchTextFileType = ""
        CreateKeyhash = 0
        Keyhash = ""
        primary_keys = ""
        primary_key_DDL = ""
        primary_keys_list = []
        phone_cols = []
        dlp_cols = []
        email_cols = []
        MaterializeView = 0
        MaterializeViewVal = ""
        acquire_custom_info = ""
        pk_case_sensitive = ""

        # ----------------------------------------------------------------
        # store table info in variables
        # TableName. Exit loop if TableName not found or if it is empty.
        # ----------------------------------------------------------------
        self.runlog.log("Get tablename")
        try:
            TableName = str(wstable.table_name())
        except:
            raise Exception("TableName not found or empty")

        # ----------------------------------------------------------------
        # StandardizationIndicator
        # ----------------------------------------------------------------
        self.runlog.log("Get Read standardization indicator")
        StandardizationIndicator = wstable.standardization_ind()
        if StandardizationIndicator == "1":
            self.isStandardizedSource = 1

        # ----------------------------------------------------------------
        # RawAudienceIndicator
        # ----------------------------------------------------------------
        self.runlog.log("Get rawaudience indicator")
        RawAudienceIndicator = wstable.rawaudience_ind()
        if RawAudienceIndicator == "1":
            self.isRawAudienceSource = 1

        # ----------------------------------------------------------------
        # Get list of columns
        # ----------------------------------------------------------------
        self.runlog.log("Get columns")
        col_list = wstable.columns()

        # ----------------------------------------------------------------
        # Get Primary Key columns where PrimaryKey == Y or y
        # ----------------------------------------------------------------
        self.runlog.log("Get pk list")
        if CreateKeyhash == "1":
            primary_keys = "KEYHASH"
            primary_key_DDL = "PRIMARY KEY (KEYHASH)"
        else:
            primary_keys, primary_key_DDL = wstable.primary_keys_string()

        primary_keys_list = wstable.primary_keys()

        # Read all other info if its not a rawaudience only processing
        if audonly == False:

            # ----------------------------------------------------------------
            # get standardization sheet
            # ----------------------------------------------------------------
            self.runlog.log("Get standardization sheet")
            std_sheet_name = ""
            if StandardizationIndicator == "1":
                std_sheet_name = str(wstable.standardization_sheet())
                self.runlog.log(f"Standardization sheet name = {std_sheet_name}")

            # ----------------------------------------------------------------
            # FileReceiptCheck
            # ----------------------------------------------------------------
            self.runlog.log("Get filereceiptcheck")
            FileReceiptCheck = wstable.filereceiptcheck()

            # ----------------------------------------------------------------
            # Threshold
            # ----------------------------------------------------------------
            self.runlog.log("Get Read threshold")
            Threshold = wstable.threshold()

            # ----------------------------------------------------------------
            # SourceDateIndicator
            # ----------------------------------------------------------------
            self.runlog.log("Get sourcedate indicator")
            SourceDateIndicator = str(wstable.sourcedate_ind())

            # ----------------------------------------------------------------
            # FileSuffixMap. Exit loop if not found or empty.
            # ----------------------------------------------------------------
            self.runlog.log("Get filesuffixmap")
            try:
                FileSuffixMap = str(wstable.filesuffixmap())
                self.filesuffixmap_list.append(FileSuffixMap)
            except:
                raise Exception("FileSuffixMap not found or empty")

            # ----------------------------------------------------------------
            # SourceTableName
            # ----------------------------------------------------------------
            self.runlog.log("Get sourcetablename")
            try:
                SourceTableName = str(wstable.tableinfo()["SourceTableName"]).strip()
            except Exception as e:
                self.runlog.log(f"Optional field SourceTableName not found. {e}")
                SourceTableName = ""

            # ----------------------------------------------------------------
            # ImportViewName
            # ----------------------------------------------------------------
            self.runlog.log("Get importviewname")
            try:
                ImportViewName = str(wstable.tableinfo()["ImportViewName"]).strip()
            except Exception as e:
                self.runlog.log(f"Optional field ImportViewName not found. {e}")
                ImportViewName = ""

            try:
                ImportViewName = ImportViewName.split(".")[1]
            except:
                ImportViewName = ImportViewName

            # ----------------------------------------------------------------
            # CreateFlattenView
            # ----------------------------------------------------------------
            self.runlog.log("Get createflattenview")
            CreateFlattenView = 0
            try:
                CreateFlattenViewVal = str(wstable.tableinfo()["CreateFlattenView"]).strip()
                if CreateFlattenViewVal == "1":
                    CreateFlattenView = 1

            except Exception as e:
                self.runlog.log(f"Optional field CreateFlattenView not found. {e}")

            # ----------------------------------------------------------------
            # FileMatchText. Exit loop if not found or empty.
            # ----------------------------------------------------------------
            self.runlog.log("Get filematchtext")
            try:
                FileMatchText = str(wstable.filematchtext())
                self.filematchtext_list.append(FileMatchText)

                # ----------------------------------------------------------------
                # get file type
                # ----------------------------------------------------------------
                FileMatchTextFileType = FileMatchText.split(".")
                FileMatchTextFileType.reverse()
                if len(FileMatchTextFileType) > 1:
                    FileMatchTextFileType = FileMatchTextFileType[1].upper() + '.' + FileMatchTextFileType[
                        0].upper()
                else:
                    FileMatchTextFileType = FileMatchTextFileType[0].upper()
            except Exception as e:
                self.runlog.log(f"ERROR: {e}")
                raise Exception("FileMatchText not found or empty")

            # ----------------------------------------------------------------
            # CreateKeyHash
            # ----------------------------------------------------------------
            self.runlog.log("Get createkeyhash")
            try:
                CreateKeyhash, Keyhash = wstable.create_keyhash()
            except:
                CreateKeyhash = 0
                Keyhash = ""

            # ----------------------------------------------------------------
            # Get columns where IsPhone == Y or y
            # ----------------------------------------------------------------
            self.runlog.log("Get phone columns")
            phone_cols = wstable.phone_columns()

            # ----------------------------------------------------------------
            # Get columns where IsDLP == Y or y
            # ----------------------------------------------------------------
            self.runlog.log("Get dlp columns")
            dlp_cols = wstable.dlp_columns()

            # ----------------------------------------------------------------
            # Get columns where IsEmail == Y or y (commenting out temporarily pending PII tagging discussion)
            # ----------------------------------------------------------------
            self.runlog.log("Get email columns")
            email_cols = wstable.email_columns()

            # ----------------------------------------------------------------
            # MaterializeView
            # ----------------------------------------------------------------
            self.runlog.log("Get materializeview")
            MaterializeView = 0
            try:
                MaterializeViewVal = str(wstable.tableinfo()["MaterializeView"]).strip()
                if MaterializeViewVal == "1":
                    MaterializeView = 1

            except Exception as e:
                self.runlog.log(f"Optional field MaterializeView not found. {e}")

            # ----------------------------------------------------------------
            # Source object name
            # ----------------------------------------------------------------
            self.runlog.log("Get acquire custom info")
            acquire_custom_info = ""
            if self.has_fn_get_acquire_custom_info:
                try:
                    acquire_custom_info = self.fn_get_acquire_custom_info(worksheet=wstable)
                except Exception as e:
                    self.runlog.log(f"Failed to get acquire custom info using custom function")

            # ----------------------------------------------------------------
            # PK Case Sensitive
            # ----------------------------------------------------------------
            self.runlog.log("Get pk case sensitive")
            pk_case_sensitive = wstable.pk_case_sensitive()

        # ----------------------------------------------------------------
        # build return dictionary
        # ----------------------------------------------------------------
        wsheetinfo = {}
        wsheetinfo["wstable"] = wstable
        wsheetinfo["TableName"] = TableName
        wsheetinfo["col_list"] = col_list
        wsheetinfo["FileReceiptCheck"] = FileReceiptCheck
        wsheetinfo["Threshold"] = Threshold
        wsheetinfo["StandardizationIndicator"] = StandardizationIndicator
        wsheetinfo["RawAudienceIndicator"] = RawAudienceIndicator
        wsheetinfo["SourceDateIndicator"] = SourceDateIndicator
        wsheetinfo["FileSuffixMap"] = FileSuffixMap
        wsheetinfo["SourceTableName"] = SourceTableName
        wsheetinfo["FileMatchText"] = FileMatchText
        wsheetinfo["FileMatchTextFileType"] = FileMatchTextFileType
        wsheetinfo["CreateKeyhash"] = CreateKeyhash
        wsheetinfo["Keyhash"] = Keyhash
        wsheetinfo["primary_keys"] = primary_keys
        wsheetinfo["primary_key_DDL"] = primary_key_DDL
        wsheetinfo["primary_keys_list"] = primary_keys_list
        wsheetinfo["phone_cols"] = phone_cols
        wsheetinfo["dlp_cols"] = dlp_cols
        wsheetinfo["email_cols"] = email_cols
        wsheetinfo["std_sheet_name"] = std_sheet_name
        wsheetinfo["ImportViewName"] = ImportViewName
        wsheetinfo["CreateFlattenView"] = CreateFlattenView
        wsheetinfo["pk_case_sensitive"] = pk_case_sensitive
        wsheetinfo["MaterializeView"] = MaterializeView
        wsheetinfo["acquire_custom_info"] = acquire_custom_info

        return wsheetinfo

    # =======================================================================
    # Create Config per Worksheet
    # =======================================================================
    def create_base_config(self, dd_file:str, bus_rules:object, sources_obj:object, wsheetinfo:dict, copyinto_filename:str):

        # ----------------------------------------------------------------
        # map variables
        # ----------------------------------------------------------------
        wstable = wsheetinfo["wstable"]
        TableName = wsheetinfo["TableName"]
        ImportTableName = TableName
        SourceTableName = wsheetinfo["SourceTableName"]
        col_list = wsheetinfo["col_list"]
        Threshold = wsheetinfo["Threshold"]
        StandardizationIndicator = wsheetinfo["StandardizationIndicator"]
        RawAudienceIndicator = wsheetinfo["RawAudienceIndicator"]
        SourceDateIndicator = wsheetinfo["SourceDateIndicator"]
        FileMatchText = wsheetinfo["FileMatchText"]
        FileMatchTextFileType = wsheetinfo["FileMatchTextFileType"]
        CreateKeyhash = wsheetinfo["CreateKeyhash"]
        Keyhash = wsheetinfo["Keyhash"]
        primary_keys = wsheetinfo["primary_keys"]
        primary_key_DDL = wsheetinfo["primary_key_DDL"]
        primary_keys_list = wsheetinfo["primary_keys_list"]
        phone_cols = wsheetinfo["phone_cols"]
        dlp_cols = wsheetinfo["dlp_cols"]
        email_cols = wsheetinfo["email_cols"]
        std_sheet_name = wsheetinfo["std_sheet_name"]
        import_view_name = wsheetinfo["ImportViewName"]
        pk_case_sensitive = wsheetinfo["pk_case_sensitive"]
        acquire_custom_info = wsheetinfo["acquire_custom_info"]
        useImportView = False
        if len(import_view_name) > 0:
            useImportView = True
            ImportTableName = import_view_name

        # ----------------------------------------------------------------
        # check extension if source type is not SDS
        # ----------------------------------------------------------------
        if self.source_type != "SDS":
            if self.source_type == "FF":
                # EXIT PROCESSING if filematchtextfiletype is JSON
                if "JSON" in FileMatchTextFileType:
                    self.runlog.log(f"FileMatchText file extension is JSON. Try KIP or SLAPI processing.")
                    raise Exception("FileMatchText file extension is JSON. Try KIP or SLAPI processing.")
            else:
                # EXIT PROCESSING if filematchtextfiletype is not JSON and the FileMatchText is not EXCLUDEFROMFILETRANSFERS.
                # Tables with EXCLUDEFROMFILETRANSFERS is populated via flatten or bus rules
                if "JSON" not in FileMatchTextFileType and FileMatchText.upper() != "EXCLUDEFROMFILETRANSFERS":
                    self.runlog.log(f"FileMatchText file extension is not JSON. Try flat file processing.")
                    raise Exception("FileMatchText file extension is not JSON. Try flat file processing.")

        # ----------------------------------------------------------------
        # Add unique work table business rule if CreateKeyhash = 1
        # ----------------------------------------------------------------
        if len(Keyhash) > 1:
            WT_busrule = create_keyhash_worktable_busrule(table_name=ImportTableName.lower(), keyhash=Keyhash, runlog=self.runlog, platform="Prefect")
            bus_rules.add_rule(WT_busrule)

        # ----------------------------------------------------------------
        # Create Import DDL File if source type is not SDS
        # ----------------------------------------------------------------
        if useImportView is False and self.source_type != "SDS":
            if self.has_fn_create_import_DDL_custom:
                self.runlog.log(f"Creating {self.source_name} custom Import table DDL.")
                self.fn_create_import_DDL_custom(table_name=TableName.lower(), col_list=col_list, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, data_resources=self.data_resources)
            else:
                create_import_DDL(table_name=TableName.lower(), col_list=col_list, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name)
                self.data_resources.append(["import", TableName.lower()])

        # ----------------------------------------------------------------
        # Create Stage DDL File
        # ----------------------------------------------------------------
        if self.has_fn_create_stage_DDL_custom:
            self.runlog.log(f"Creating {self.source_name} custom Stage table DDL.")
            Stage_DDL, self.data_resources = self.fn_create_stage_DDL_custom(table_name=TableName.lower(), col_list=col_list, pk_str=primary_key_DDL, phone_col_list=phone_cols, std_ind=StandardizationIndicator, rawaud_ind=RawAudienceIndicator, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, data_resources=self.data_resources, email_col_list=email_cols)
        else:
            Stage_DDL, StageArchive_DDL = create_stage_DDL(table_name=TableName.lower(), col_list=col_list, pk_str=primary_key_DDL, phone_col_list=phone_cols, std_ind=StandardizationIndicator, rawaud_ind=RawAudienceIndicator, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, email_col_list=email_cols, create_archive_tables=self.create_archive_tables)
            self.data_resources.append(["stage", TableName.lower()])

            # add archive table to deployment list
            if StageArchive_DDL != "":
                self.data_resources.append(["stage", f"{TableName.lower()}archive"])

        # ----------------------------------------------------------------
        # Create Import View DDL File
        # ----------------------------------------------------------------
        if self.source_type == "SDS":
            create_import_view_DDL(table_name=TableName.lower(), col_list=col_list, source_table_name=SourceTableName, source_date_indicator=SourceDateIndicator, pk_list=primary_keys_list, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name)
            self.data_resources.append(["import", "vw_"+TableName.lower()])

        # ----------------------------------------------------------------
        # Create truncate file if source type is not SDS
        # ----------------------------------------------------------------
        # skip creating truncate file if its an import view or if its a no acquire ingest.
        # Expectation for no acquire ingest is that the import table is populated by either data share or some other process.
        if self.source_type == "SDS" or (useImportView or FileMatchText.upper() == "EXCLUDEFROMFILETRANSFERS"):
            sources_obj.append("importSql", "NOTRUNCATE")
        else:
            if self.has_fn_create_truncate_query_custom:
                self.runlog.log(f"Creating {self.source_name} custom truncate query.")
                self.fn_create_truncate_query_custom(table_name=TableName.lower(), db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, source_name=self.source_name, client=self.client)
            else:
                self.runlog.log("Creating truncate query.")
                create_truncate_query(table_name=TableName.lower(), db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, source_name=self.source_name, client=self.client)

        # ----------------------------------------------------------------
        # add mergetoStageSql
        # ----------------------------------------------------------------
        if self.has_fn_create_merge_sp_custom:
            mergeToStageSql = self.fn_create_merge_sp_custom(table_name=TableName, pk_list=primary_keys_list, col_list=col_list, db_folder=self.database_folder, runlog=self.runlog, std_ind=StandardizationIndicator, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, create_keyhash=CreateKeyhash)
        else:
            mergeToStageSql = create_merge_sp(table_name=TableName, pk_list=primary_keys_list, col_list=col_list, db_folder=self.database_folder, runlog=self.runlog, std_ind=StandardizationIndicator, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, create_keyhash=CreateKeyhash, pk_case_sensitive=pk_case_sensitive)
        sources_obj.append("mergeToStageSql", f"CALL {mergeToStageSql}")
        self.data_resources.append([mergeToStageSql.split(".")[0], mergeToStageSql.split(".")[1].replace("()", "")])

        # ----------------------------------------------------------------
        # add uniqueTableCreateSql
        # ----------------------------------------------------------------
        if self.has_fn_create_unique_sp_custom:
            self.runlog.log(f"\nCreating {self.source_name} custom unique SP.")
            uniqueTableCreateSql = self.fn_create_unique_sp_custom(table_name=TableName, pk_list=primary_keys_list, col_list=col_list, db_folder=self.database_folder, runlog=self.runlog, std_ind=StandardizationIndicator, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, import_view_name=import_view_name, create_keyhash=CreateKeyhash)
        else:
            # if source type is SDS, provide sourcetablename
            if self.source_type == "SDS":
                uniqueTableCreateSql = create_unique_sp(table_name=TableName, pk_list=primary_keys_list, col_list=col_list, db_folder=self.database_folder, runlog=self.runlog, std_ind=StandardizationIndicator, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, import_view_name=import_view_name, create_keyhash=CreateKeyhash, pk_case_sensitive=pk_case_sensitive, source_table_name=SourceTableName)
            else:
                uniqueTableCreateSql = create_unique_sp(table_name=TableName, pk_list=primary_keys_list, col_list=col_list, db_folder=self.database_folder, runlog=self.runlog, std_ind=StandardizationIndicator, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, import_view_name=import_view_name, create_keyhash=CreateKeyhash, pk_case_sensitive=pk_case_sensitive)

        sources_obj.append("uniqueTableCreateSql", f"CALL {uniqueTableCreateSql}")
        self.data_resources.append([uniqueTableCreateSql.split(".")[0], uniqueTableCreateSql.split(".")[1].replace("()","")])

        # ----------------------------------------------------------------
        # generate standardization query
        # ----------------------------------------------------------------
        StandardizationQuery = ""
        std_query_filename = ""
        if StandardizationIndicator == "1":
            # output folder
            std_query_filename = f"standardization_{TableName.lower()}.sql"
            output_folder = f"{self.database_folder}config_repo{os.sep}sources{os.sep}"
            try:
                self.runlog.log(f"STANDARDIZATION QUERY - {std_query_filename}")

                # ----------------------------------------------------------------
                # initialize standardization object
                # ----------------------------------------------------------------
                StdObj = StdSheet(workbook=dd_file, worksheet=std_sheet_name, bus_rule_obj=bus_rules, runlog=self.runlog, db_folder=self.database_folder, platform="Prefect")

                # ----------------------------------------------------------------
                # generate standardization query for sources file
                # ----------------------------------------------------------------
                StdQueryDoc = StdObj.std_query()
                StandardizationQuery = f"CREATE OR REPLACE TABLE TMP.{TableName}_standardization AS \n" + StdQueryDoc.out()

                # ----------------------------------------------------------------
                # output standardization query to file
                # ----------------------------------------------------------------
                filewrite(folder=output_folder, filename=std_query_filename, content=StandardizationQuery)

                # ----------------------------------------------------------------
                # write output repo files if repo_root_folder is not empty
                # ----------------------------------------------------------------
                if self.repo_root_folder != "":
                    configrepo_folder = f"{self.repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{self.client.upper()}{os.sep}{self.source_name.lower()}{os.sep}sources{os.sep}"

                    # ----------------------------------------------------------------
                    # output standardization query to file
                    # ----------------------------------------------------------------
                    filewrite(folder=configrepo_folder, filename=std_query_filename, content=StandardizationQuery)

                self.runlog.log(f"{indent}Output {TableName} Standardization Query")
                self.runlog.log("")

                # ----------------------------------------------------------------
                # generate standard standardization business rules if need_create_std_busrule is True.
                # mainly used to skip this for Archtics Customers
                # ----------------------------------------------------------------
                if self.need_create_std_busrule:
                    # generate standardization business rule and add to business rule document
                    StdObj.create_std_busrule()

            except Exception as stdobjerr:
                self.runlog.log(stdobjerr)

            # ----------------------------------------------------------------
            # add table name to list for feature file, True for has business rule
            # ----------------------------------------------------------------
            self.table_name_list.append([TableName, True, FileMatchText])

        else:
            # ----------------------------------------------------------------
            # add table name to list for feature file, False for has business rule
            # ----------------------------------------------------------------
            self.table_name_list.append([TableName, False, FileMatchText])

        # ----------------------------------------------------------------
        # run source specific functions
        # ----------------------------------------------------------------
        if self.has_fn_sources_append:
            self.fn_sources_append(worksheet=wstable, db_folder=self.database_folder, sources_obj=sources_obj, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name)

        # ----------------------------------------------------------------
        # create sources file
        # ----------------------------------------------------------------
        sources_filename = sources_obj.create_sources(source_name=self.source_name, table_name=TableName.lower(), pk_str=primary_keys, rawaud_ind=RawAudienceIndicator, src_date_ind=SourceDateIndicator, std_ind=StandardizationIndicator, std_query_filename=std_query_filename, copyinto_filename=copyinto_filename, threshold=Threshold, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, import_view_name=import_view_name, dlp_cols=dlp_cols)

        self.config_resources.append(["sources", sources_filename])

        # ----------------------------------------------------------------
        # Create RawAudience Business Rule and control-rawaudience
        # ----------------------------------------------------------------
        if RawAudienceIndicator == "1":
            self.runlog.log(f"RawAudienceIndicator = {RawAudienceIndicator}")

            # ----------------------------------------------------------------
            # get rawaudience sheet name
            # ----------------------------------------------------------------
            ra_sheet_name = str(wstable.rawaudience_sheet())
            self.runlog.log(f"{indent}RawAudienceSheet = {ra_sheet_name}")

            try:
                # ----------------------------------------------------------------
                # initialize rawaudience object
                # ----------------------------------------------------------------
                rawaud = RawAudSheet(client=self.client, workbook=dd_file, worksheet=ra_sheet_name, source_name=self.source_name, table_name=TableName, bus_rule_obj=bus_rules, runlog=self.runlog, db_folder=self.database_folder, platform="Prefect", pk_case_sensitive=pk_case_sensitive)

                # ----------------------------------------------------------------
                # Create stage raw audience business rule if need_create_stg_rawaud_busrule is true
                # Mainly used to skip for Archtics Customers
                # ----------------------------------------------------------------
                if self.need_create_stg_rawaud_busrule:
                    self.runlog.log(f"{indent}Creating Stage RawAudience Business Rule")
                    rawaud.create_stg_rawaud_busrule()

                # ----------------------------------------------------------------
                # Create tmp raw audience business rule if need_create_tmp_rawaud_busrule is true
                # Mainly used to skip for Archtics Customers
                # ----------------------------------------------------------------
                if self.need_create_tmp_rawaud_busrule:
                    self.runlog.log(f"{indent}Creating Tmp RawAudience Business Rule")
                    rawaud.create_tmp_rawaud_busrule()

                # ----------------------------------------------------------------
                # control-rawaudience
                # ----------------------------------------------------------------
                self.runlog.log(f"{indent}Creating control-rawaudience.sql file")
                ra_filename = rawaud.ctrl_ra_file(self.database_folder, repo_root_folder=self.repo_root_folder, client=self.client)
                self.ra_filename_list.append(ra_filename)

                # ----------------------------------------------------------------
                # merge into rawaudience
                # ----------------------------------------------------------------
                self.runlog.log(f"{indent}Creating sp_merge{TableName.lower()}intorawsudience.sql file")
                self.runlog.log("")
                mergeToRawAudSql = rawaud.create_merge_to_rawaudience_sp(table_name=TableName, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)
                self.data_resources.append([mergeToRawAudSql.split(".")[0], mergeToRawAudSql.split(".")[1].replace("()", "")])

                # ----------------------------------------------------------------
                # delete orphan rawaudience
                # ----------------------------------------------------------------
                self.runlog.log(f"{indent}Creating sp_delete{TableName.lower()}orphansfromrawaudience.sql file")
                self.runlog.log("")
                delOrphanFromRawAudSql = rawaud.delete_orphan_from_rawaudience_sp(table_name=TableName, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)
                self.data_resources.append([delOrphanFromRawAudSql.split(".")[0], delOrphanFromRawAudSql.split(".")[1].replace("()", "")])

                # ----------------------------------------------------------------
                # RawAudience Sources
                # ----------------------------------------------------------------
                self.runlog.log(f"{indent}Creating {TableName.lower()}rawaudience.json file")
                self.runlog.log("")
                rawaud.rawaudience_sources(table_name=TableName, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)

                # ----------------------------------------------------------------
                # Add Phone formatter business rule if RawAudience is 1 and there are phone columns
                # ----------------------------------------------------------------
                if len(phone_cols) != 0:
                    self.runlog.log("")
                    self.runlog.log(f"Phone columns count = {len(phone_cols)}")
                    self.runlog.log(f"{indent}Creating phone formatter business rule")
                    self.runlog.log("")
                    pf_busrule = create_phone_formatter_busrule(table_name=TableName, pk_list=primary_keys_list, phone_cols=phone_cols, platform="Prefect", import_view_name=import_view_name)
                    bus_rules.add_rule(pf_busrule)

            except Exception as rawauderr:
                self.runlog.log(f"{indent}RawAudience Error: {rawauderr}")

        else:
            if len(phone_cols) != 0:
                self.runlog.log("")
                self.runlog.log(f"Phone columns found but not creating phone formatter business rule since RawAudienceIndicator is 0")
                self.runlog.log("")

        # ----------------------------------------------------------------
        # Run source specific fn_busrules_append
        # ----------------------------------------------------------------
        if self.has_fn_busrules_append:
            self.fn_busrules_append(worksheet=wstable, bus_rule_obj=bus_rules, db_folder=self.database_folder, runlog=self.runlog)

        # ----------------------------------------------------------------
        # Create Business Rules File
        # ----------------------------------------------------------------
        # if there are business rules to output, append to config deployment script
        has_rules = bus_rules.out(table_name=TableName, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name) == 1
        if has_rules:
            self.config_resources.append(["businessrules", f"{TableName.lower()}.json"])
            i=0
            for table in self.table_name_list:
                if table[0].upper() == TableName.upper():
                    self.table_name_list[i] = [TableName, True, FileMatchText]
                i += 1

        # ----------------------------------------------------------------
        # Check schema drift
        # ----------------------------------------------------------------
        self.runlog.log("Checking if there is schema drift")

        try:
            schema_drift_result = wstable.check_schema_drift()
            self.runlog.log("-Schema drift check successful")
            if schema_drift_result[0] == 1:
                self.runlog.log("-Schema drifted. Create schema drift script.")
                schema_drift_script_name = create_schema_drift_script(table_name=TableName, stage_DDL=Stage_DDL, old_cols=schema_drift_result[1], db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, std_ind=StandardizationIndicator)
                self.schema_drift_script_name_list.append(schema_drift_script_name)

                if TableName in self.create_archive_tables:
                    archive_schema_drift_script_name = create_schema_drift_script(table_name=TableName, stage_DDL=StageArchive_DDL, old_cols=schema_drift_result[1], db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, std_ind=StandardizationIndicator)
                    self.archive_schema_drift_script_name_list.append(archive_schema_drift_script_name)
            else:
                self.runlog.log("-No schema drift.")
        except Exception as e:
            self.runlog.log(f"-WARNING: {e}. Ignore if table doesn't have new columns.")

        # Get Source object name
        self.runlog.log("")
        if self.has_fn_get_acquire_custom_info:
            self.acquire_custom_info_list.append(acquire_custom_info)

        # ----------------------------------------------------------------
        # Create Tests
        # ----------------------------------------------------------------
        self.runlog.log("")
        testQueries = createTest(client=self.client, table_name=TableName, pk_list=primary_keys_list, col_list=col_list, db_folder=self.database_folder, runlog=self.runlog)

        self.test_file.newline(testQueries)

        return

    # =======================================================================
    # Create Raw Audience only
    # =======================================================================
    def create_base_config_aud(self, dd_file: str, wsheetinfo: dict):

        # ----------------------------------------------------------------
        # map variables
        # ----------------------------------------------------------------
        wstable = wsheetinfo["wstable"]
        TableName = wsheetinfo["TableName"]
        RawAudienceIndicator = wsheetinfo["RawAudienceIndicator"]
        pk_case_sensitive = wsheetinfo["pk_case_sensitive"]
        primary_keys_list = wsheetinfo["primary_keys_list"]
        col_list = wsheetinfo["col_list"]

        # ----------------------------------------------------------------
        # Create RawAudience Business Rule and control-rawaudience
        # ----------------------------------------------------------------
        if RawAudienceIndicator == "1":
            self.runlog.log(f"RawAudienceIndicator = {RawAudienceIndicator}")

            # ----------------------------------------------------------------
            # get rawaudience sheet name
            # ----------------------------------------------------------------
            ra_sheet_name = str(wstable.rawaudience_sheet())
            self.runlog.log(f"{indent}RawAudienceSheet = {ra_sheet_name}")

            try:
                # ----------------------------------------------------------------
                # initialize rawaudience object
                # ----------------------------------------------------------------
                rawaud = RawAudSheet(client=self.client, workbook=dd_file, worksheet=ra_sheet_name, source_name=self.source_name, table_name=TableName, bus_rule_obj=None, runlog=self.runlog, db_folder=self.database_folder, platform="Prefect", pk_case_sensitive=pk_case_sensitive)

                # ----------------------------------------------------------------
                # control-rawaudience
                # ----------------------------------------------------------------
                self.runlog.log(f"{indent}Creating control-rawaudience.sql file")
                ra_filename = rawaud.ctrl_ra_file(self.database_folder, repo_root_folder=self.repo_root_folder, client=self.client)
                self.ra_filename_list.append(ra_filename)

                # ----------------------------------------------------------------
                # merge into rawaudience
                # ----------------------------------------------------------------
                self.runlog.log(f"{indent}Creating sp_merge{TableName.lower()}intorawsudience.sql file")
                self.runlog.log("")
                mergeToRawAudSql = rawaud.create_merge_to_rawaudience_sp(table_name=TableName, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)
                self.data_resources.append([mergeToRawAudSql.split(".")[0], mergeToRawAudSql.split(".")[1].replace("()", "")])

                # ----------------------------------------------------------------
                # delete orphan rawaudience
                # ----------------------------------------------------------------
                self.runlog.log(f"{indent}Creating sp_delete{TableName.lower()}orphansfromrawaudience.sql file")
                self.runlog.log("")
                delOrphanFromRawAudSql = rawaud.delete_orphan_from_rawaudience_sp(table_name=TableName, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)
                self.data_resources.append([delOrphanFromRawAudSql.split(".")[0], delOrphanFromRawAudSql.split(".")[1].replace("()", "")])

                # ----------------------------------------------------------------
                # RawAudience Sources
                # ----------------------------------------------------------------
                self.runlog.log(f"{indent}Creating {TableName.lower()}rawaudience.json file")
                self.runlog.log("")
                rawaud.rawaudience_sources(table_name=TableName, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)

            except Exception as rawauderr:
                self.runlog.log(f"{indent}RawAudience Error: {rawauderr}")

        # ----------------------------------------------------------------
        # Create Tests
        # ----------------------------------------------------------------
        self.runlog.log("")
        testQueries = createTest(client=self.client, table_name=TableName, pk_list=primary_keys_list, col_list=col_list, db_folder=self.database_folder, runlog=self.runlog)

        self.test_file.newline(testQueries)

        return

    # =======================================================================
    # Create Config End
    # =======================================================================
    def create_config_end(self, audonly:bool=False):

        # ----------------------------------------------------------------
        # console output variables
        # ----------------------------------------------------------------
        startendfiller = "=" * 5

        if audonly == False:
            # ----------------------------------------------------------------
            # Get Feature custom info
            # ----------------------------------------------------------------
            feature_custom_info = {}
            if self.has_fn_feature_custom_info:
                self.runlog.log(f"Getting custom feature info.")
                feature_custom_info = self.fn_feature_custom_info()

            # ----------------------------------------------------------------
            # Create Feature File
            # ----------------------------------------------------------------
            if self.has_fn_create_feature_file_custom:
                self.runlog.log("")
                self.runlog.log(f"Creating {self.source_name} custom Feature file.")
                self.fn_create_feature_file_custom(source_name=self.source_name, table_name_list=self.table_name_list, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)
            else:
                create_feature_file(source_name=self.source_name, table_name_list=self.table_name_list, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, feature_custom_info=feature_custom_info)

            # ----------------------------------------------------------------
            # Create Acquire File
            # ----------------------------------------------------------------
            if self.has_fn_create_acquire_file:
                self.fn_create_acquire_file(file_match_list=self.filesuffixmap_list, table_name_list = self.table_name_list, db_folder=self.database_folder, runlog=self.runlog, client=self.client, repo_root_folder=self.repo_root_folder, acquire_custom_info_list=self.acquire_custom_info_list)
            else:
                self.runlog.log(f"No Acquire file needed for {self.source_name}")

            # ----------------------------------------------------------------
            # Create Prefectclient Files
            # ----------------------------------------------------------------
            pclient = prefectclient(client=self.client, source_name=self.source_name, source_type=self.source_type, db_folder=self.database_folder, repo_root_folder=self.repo_root_folder, runlog=self.runlog)
            pclient.deploy_config()
            pclient.deploy_block_config()
            pclient.requirements()

            # ----------------------------------------------------------------
            # Custom append to data resources
            # ----------------------------------------------------------------
            if self.has_fn_dataresources_append:
                self.data_resources = self.fn_dataresources_append(data_resources=self.data_resources, runlog=self.runlog)

        # ----------------------------------------------------------------
        # Create Consolidated Test File
        # ----------------------------------------------------------------
        print_section(msg="Working on Test Files", runlog=self.runlog)
        self.runlog.log(f"Creating consolidated test file")
        testoutputfolder = f"{self.database_folder}Tests{os.sep}"
        alltestfilename = f"{self.source_name.upper()}_All_Test Queries.sql"
        filewrite(folder=testoutputfolder, filename=alltestfilename, content=self.test_file.out())

        # ----------------------------------------------------------------
        # Create Data Tester Profile
        # ----------------------------------------------------------------
        self.runlog.log(f"Creating Data Tester Profile")
        role = f"{self.client.upper()}_ALL_DATA_ENGINEER"
        testfilepath = testoutputfolder + alltestfilename
        profilename = f"DataTesterProfile_{self.client}_{self.database}_RunTests.dtp"
        dtplogmsg = CreateDTP(profilename=profilename, client=self.client, database=self.database, role=role, testfilepath=testfilepath, outputfolder=self.database_folder, testfilter="0")
        self.runlog.log(dtplogmsg)

        # ----------------------------------------------------------------
        # Create Deployment Script
        # ----------------------------------------------------------------
        # Set environment
        if self.client == self.database:
            env = "PROD"
        elif "qa" in self.database.lower():
            env = "QA"
        elif "dev" in self.database.lower():
            env = "DEV"
        else:
            env = "NA"

        # ----------------------------------------------------------------
        # create data repo deploy scripts
        # ----------------------------------------------------------------
        data_deploy_scripts, dataInstallDoc = create_deployment_scripts(client_name=self.client, database=self.database, env=env, source_name=self.source_name, repo_name="data", resources=self.data_resources)

        if audonly == False:
            # ----------------------------------------------------------------
            # add phone formatter deployment
            # ----------------------------------------------------------------
            if self.isStandardizedSource == 1:
                data_deploy_scripts += f".\\installComponent.ps1 -cn {self.client} -toDB {self.database} -env {env} -fr base -s 1public -c fn_phoneformatter -silent\n"
                dataInstallDoc.newline(f"-fr base -s 1public -c fn_phoneformatter")

        # ----------------------------------------------------------------
        # add control rawaudience deployment
        # ----------------------------------------------------------------
        if len(self.ra_filename_list) > 0:
            for ra_filename in self.ra_filename_list:

                # archtics override
                if self.source_name.upper() == "ARCHTICS-API":
                    self.source_name = "archtics"
                    
                data_deploy_scripts += f".\\installComponent.ps1 -cn {self.client} -toDB {self.database} -env {env} -fr {self.source_name.lower()} -s seed_data -c {ra_filename} -silent\n"
                dataInstallDoc.newline(f"-fr {self.source_name.lower()} -s seed_data -c {ra_filename}")

        # ----------------------------------------------------------------
        # add installDoc additions
        # ----------------------------------------------------------------
        if len(self.installDocAdditions) > 0:
            for item in self.installDocAdditions:
                dataInstallDoc.newline(item)

        # ----------------------------------------------------------------
        # Output installComponent install.txt File
        # ----------------------------------------------------------------
        dataInstallDocOut = dataInstallDoc.out()
        filewrite(folder=self.database_folder, filename="install.txt", content=dataInstallDocOut)

        print_section(msg="Deployment Scripts", runlog=self.runlog)
        self.runlog.log("--data repo")
        if len(self.schema_drift_script_name_list) > 0:
            data_deploy_scripts = data_deploy_scripts[:-1]
            self.runlog.log(data_deploy_scripts)
            for script_name in self.schema_drift_script_name_list:
                self.runlog.log(f".\\installSQLFile.ps1 -cn {self.client} -toDB {self.database} -env {env} -dirName \"<localfolderpath>\" -fileName {script_name}")
            self.runlog.log("")
        else:
            self.runlog.log(data_deploy_scripts)

        self.runlog.log("--pyInstallComponent command")
        self.runlog.log(f'python .\\installComponent.py -cn {self.client} -toDB {self.database} -env {env} --file "{self.database_folder}install.txt" -silent')
        self.runlog.log("")
        self.runlog.log("--kagr-configuration repo")
        self.runlog.log("USE CIRCLECI TO DEPLOY")

        # ----------------------------------------------------------------
        # END
        # ----------------------------------------------------------------
        self.runlog.log("")
        self.runlog.log(f"{startendfiller} END {startendfiller}")
        self.runlog.log("")

        # ----------------------------------------------------------------
        # Output Trace Log to File
        # ----------------------------------------------------------------
        runlogmsg = self.runlog.out()
        filewrite(folder=self.database_folder, filename=self.runlog_filename, content=runlogmsg)

        print(f"Trace log \"{self.runlog_filename}\" created in: {self.database_folder}\n")

        return

    # =======================================================================
    # Create Overall Config For Flat File
    # =======================================================================
    def create_config_FF(self, file_date_regex:str, field_delimiter:str, field_enclosed_by:str, copyffoptions:str):

        # ----------------------------------------------------------------
        # initialize
        # ----------------------------------------------------------------
        self.load_source_functions()
        self.read_dd_file()

        for worksheet in self.wslist:
            print_section(msg=f"Working on {worksheet}", runlog=self.runlog)

            # ----------------------------------------------------------------
            # read worksheet info
            # ----------------------------------------------------------------
            try:
                wsheetinfo = self.read_worksheet_info(worksheet=worksheet)
            except Exception as err:
                self.runlog.log(f"Failed to read worksheet, exiting {worksheet} config creation process.")
                self.runlog.log(f"ERROR: {err}")
                continue

            wstable = wsheetinfo["wstable"]
            TableName = wsheetinfo["TableName"]
            col_list = wsheetinfo["col_list"]
            FileMatchText = wsheetinfo["FileMatchText"]
            SourceTableName = wsheetinfo["SourceTableName"]
            ImportViewName = wsheetinfo["ImportViewName"]
            useImportView = False
            if len(ImportViewName) > 0:
                useImportView = True

            # ----------------------------------------------------------------
            # Initialize Business Rule File
            # ----------------------------------------------------------------
            bus_rules = BusRules()

            # ----------------------------------------------------------------
            # Create Sources File
            # ----------------------------------------------------------------
            sources_obj = Sources()

            # ----------------------------------------------------------------
            # Create CopyInto File
            # ----------------------------------------------------------------
            copyinto_filename = ""

            # ----------------------------------------------------------------
            # set CustomFileFormatOptions to empty string if no custom options provided
            # ----------------------------------------------------------------
            CustomFileFormatOptions = ""
            if copyffoptions is None:
                CustomFileFormatOptions = ""
            else:
                CustomFileFormatOptions = f" {copyffoptions}"

            # # if DD specifies an import view, then no need to do any copy into
            # if useImportView:
            #     copyinto_filename = None
            # else:
            # don't create copy into file if instructed to exclude from file transfers or SourceTableName is not empty
            if self.source_type == "FF" and (FileMatchText.upper() != "EXCLUDEFROMFILETRANSFERS" and len(SourceTableName) < 1 and useImportView is False):
                if self.has_fn_create_copyinto_custom:
                    self.runlog.log(f"Creating {self.source_name} custom copy into.")
                    try:
                        copyinto_filename = self.fn_create_copyinto_custom(client=self.client, source_name=self.source_name, table_name=TableName.lower(), col_list=col_list, file_match_text=FileMatchText, file_date_regex=file_date_regex, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, custom_fileformat_options=CustomFileFormatOptions, worksheet=wstable)
                    except:
                        copyinto_filename = self.fn_create_copyinto_custom(client=self.client, source_name=self.source_name, table_name=TableName.lower(), col_list=col_list, file_match_text=FileMatchText, file_date_regex=file_date_regex, field_delimiter=field_delimiter, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, field_enclosed_by=field_enclosed_by, custom_fileformat_options=CustomFileFormatOptions, worksheet=wstable)
                else:
                    copyinto_filename = self.create_copyinto_FF(table_name=TableName.lower(), col_list=col_list, file_match_text=FileMatchText, file_date_regex=file_date_regex, field_delimiter=field_delimiter, field_enclosed_by=field_enclosed_by, custom_fileformat_options=CustomFileFormatOptions)

            if copyinto_filename != None:
                self.config_resources.append(["sources", copyinto_filename])

            # ----------------------------------------------------------------
            # Create Base Config
            # ----------------------------------------------------------------
            self.create_base_config(dd_file=self.dd_file, bus_rules=bus_rules, sources_obj=sources_obj, wsheetinfo=wsheetinfo, copyinto_filename=copyinto_filename)

            # Parking this for now in case I need it for the future
            # # ----------------------------------------------------------------
            # # Create Flatten Insert File if FileMatchText is EXCLUDEFROMFILETRANSFERS
            # # ----------------------------------------------------------------
            # if wsheetinfo["FileMatchText"] == "EXCLUDEFROMFILETRANSFERS":
            #     flatten_filename = ""
            #     TableNameRaw = wsheetinfo["ObjectName"]
            #     if self.need_flatten and useImportView is False:
            #         try:
            #             if self.has_fn_create_flatten_custom:
            #                 self.runlog.log(f"Creating {self.source_name} custom flatten query.")
            #                 flatten_filename = self.fn_create_flatten_custom(source_name=self.source_name, table_name=TableName.lower(), table_name_raw=TableNameRaw, col_list=col_list, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, worksheet=wstable)
            #             else:
            #                 self.runlog.log("Creating basic flatfile flatten insert query.")
            #                 flatten_filename = create_flatten_insert(source_name=self.source_name, table_name=TableName.lower(), table_name_raw=TableNameRaw, col_list=col_list, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)
            #         except Exception as e:
            #             self.runlog.log(f"ERROR: Can't create Flatten Query\n{e}")
            #             break
            #
            #         self.config_resources.append(["sources", flatten_filename])
            #
            #     # ----------------------------------------------------------------
            #     # don't include flatten in import SQL if no flatten is created
            #     # ----------------------------------------------------------------
            #     if self.need_flatten and flatten_filename != "" and useImportView is False:
            #         if copyinto_filename != "":
            #             sources_obj.append("importSql", [{"sortOrder": 2, "sqlFileName": flatten_filename, "saveResults": False}])
            #         else:
            #             sources_obj.append("importSql", [{"sortOrder": 1, "sqlFileName": flatten_filename, "saveResults": False}])

        # ----------------------------------------------------------------
        # Create End Config
        # ----------------------------------------------------------------
        self.create_config_end()

        return

    # =======================================================================
    # create overall config for KIP
    # =======================================================================
    def create_config_KIP(self, file_date_regex:str, copyffoptions:str):

        # ----------------------------------------------------------------
        # initialize
        # ----------------------------------------------------------------
        self.load_source_functions()
        self.read_dd_file()

        # ----------------------------------------------------------------
        # create configs per worksheet
        # ----------------------------------------------------------------
        for worksheet in self.wslist:
            print_section(msg=f"Working on {worksheet}", runlog=self.runlog)

            # ----------------------------------------------------------------
            # read worksheet info
            # ----------------------------------------------------------------
            try:
                wsheetinfo = self.read_worksheet_info(worksheet=worksheet)
            except Exception as err:
                self.runlog.log(f"Failed to read worksheet, exiting {worksheet} config creation process.")
                self.runlog.log(f"ERROR: {err}")
                continue

            wstable = wsheetinfo["wstable"]
            TableName = wsheetinfo["TableName"]
            col_list = wsheetinfo["col_list"]
            FileMatchText = wsheetinfo["FileMatchText"]
            SourceTableName = wsheetinfo["SourceTableName"]
            ImportViewName = wsheetinfo["ImportViewName"]
            CreateFlattenView = wsheetinfo["CreateFlattenView"]
            primary_keys_list = wsheetinfo["primary_keys_list"]
            primary_key_DDL = wsheetinfo["primary_key_DDL"]
            phone_cols = wsheetinfo["phone_cols"]
            MaterializeView = wsheetinfo["MaterializeView"]
            StandardizationIndicator = wsheetinfo["StandardizationIndicator"]
            RawAudienceIndicator = wsheetinfo["RawAudienceIndicator"]
            email_cols = wsheetinfo["email_cols"]

            useImportView = False
            if len(ImportViewName) > 0:
                useImportView = True

            # if sheet is for flatten view, create flatten view and skip the rest
            if CreateFlattenView == 1:
                # set ViewName and TableName
                if TableName.startswith("vw_"):
                    ViewName = TableName
                    TableName = TableName.lower().replace("vw_","")
                else:
                    # append vw_ if not in TableName
                    ViewName = "vw_" + TableName

                self.runlog.log(f"{TableName} is a flatten view. Not creating usual artifacts.")
                self.runlog.log(f"Creating {ViewName}")

                # run create flatten view function
                flattenViewName = create_flatten_view(view_name=ViewName, pk_list=primary_keys_list, phone_cols=phone_cols, source_table_name=SourceTableName, col_list=col_list, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name)
                self.data_resources.append(["stage", flattenViewName])

                # create table and business rule if materialize view is 1
                if MaterializeView == 1:
                    self.runlog.log("Creating stage table and business rule to materialize view to table")
                    # create stage DDL
                    Stage_DDL, StageArchive_DDL = create_stage_DDL(table_name=TableName, col_list=col_list, pk_str=primary_key_DDL, phone_col_list=phone_cols, std_ind=StandardizationIndicator, rawaud_ind=RawAudienceIndicator, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name, email_col_list=email_cols, omit_file_cols=True, create_archive_tables=self.create_archive_tables)
                    self.data_resources.append(["stage", TableName.lower()])

                    # add archive table to deployment list
                    if StageArchive_DDL != "":
                        self.data_resources.append(["stage", f"{TableName.lower()}_archive"])

                    # create insert overwrite business rule
                    self.runlog.log("Creating materialize view business rule.")
                    logmsg = "Please manually add this to the business rule file of the source table of the view"
                    self.runlog.log("*"*(len(logmsg)+6))
                    self.runlog.log(f"** {logmsg} **")
                    self.runlog.log("*"*(len(logmsg)+6))
                    # define column name list
                    select_cols = []
                    for col in col_list:
                        select_cols.append(f"\t{col[1]}")

                    # define bus rule query
                    vw_insertoverwrite_query = Document()
                    vw_insertoverwrite_query.newline(f"INSERT OVERWRITE INTO STAGE.{TableName.upper()}(")
                    vw_insertoverwrite_query.newlinelist(select_cols)
                    vw_insertoverwrite_query.append(",")
                    vw_insertoverwrite_query.newline("\tDWINSERTDATE,")
                    vw_insertoverwrite_query.newline("\tDWUPDATEDATE")
                    vw_insertoverwrite_query.newline(")")
                    vw_insertoverwrite_query.newline("SELECT")
                    vw_insertoverwrite_query.newlinelist(select_cols)
                    vw_insertoverwrite_query.append(",")
                    vw_insertoverwrite_query.newline("\tcurrent_timestamp,")
                    vw_insertoverwrite_query.newline("\tcurrent_timestamp")
                    vw_insertoverwrite_query.newline(f"FROM STAGE.{ViewName};")

                    # write out Rule Query to file
                    output_folder = f"{self.database_folder}ForReferenceOnly{os.sep}{ViewName}_BusRules{os.sep}"
                    filewrite(folder=output_folder, filename=f"{ViewName}_2_4 MATERIALIZE VIEW RULE QUERY.sql", content=vw_insertoverwrite_query.out())

                    # define business rule
                    vw_busrule = BusRules()

                    vw_insertoverwrite_rule = {}
                    vw_insertoverwrite_rule["ruleName"] = f"Materialize_{TableName}"
                    vw_insertoverwrite_rule["runOrder"] = 2
                    vw_insertoverwrite_rule["runPosition"] = 4
                    vw_insertoverwrite_rule["ruleQuery"] = vw_insertoverwrite_query.out_str()


                    vw_busrule.add_rule(vw_insertoverwrite_rule)
                    vw_busrule.out(table_name=ViewName, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name)

                continue

            # ----------------------------------------------------------------
            # Initialize Business Rule File
            # ----------------------------------------------------------------
            bus_rules = BusRules()

            # ----------------------------------------------------------------
            # Create Sources File
            # ----------------------------------------------------------------
            sources_obj = Sources()

            # ----------------------------------------------------------------
            # Create CopyInto File
            # ----------------------------------------------------------------
            copyinto_filename = ""

            # ----------------------------------------------------------------
            # set CustomFileFormatOptions to empty string if no custom options provided
            # ----------------------------------------------------------------
            CustomFileFormatOptions = ""
            if copyffoptions is None:
                CustomFileFormatOptions = ""
            else:
                CustomFileFormatOptions = f" {copyffoptions}"

            # ----------------------------------------------------------------
            # don't create copy into file if instructed to exclude from file transfers or SourceTableName is not empty
            # ----------------------------------------------------------------
            if FileMatchText.upper() != "EXCLUDEFROMFILETRANSFERS" and len(SourceTableName) < 1 and useImportView is False:
                if self.has_fn_create_copyinto_custom:
                    self.runlog.log(f"Creating {self.source_name} custom copy into.")
                    try:
                        copyinto_filename = self.fn_create_copyinto_custom(client=self.client, source_name=self.source_name, table_name=TableName.lower(), col_list=col_list, file_match_text=FileMatchText, file_date_regex=file_date_regex, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, custom_fileformat_options=CustomFileFormatOptions, worksheet=wstable)
                    except:
                        copyinto_filename = self.fn_create_copyinto_custom(client=self.client, source_name=self.source_name, table_name=TableName.lower(), col_list=col_list, file_match_text=FileMatchText, file_date_regex=file_date_regex, field_delimiter="", version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, field_enclosed_by="", custom_fileformat_options=CustomFileFormatOptions, worksheet=wstable)
                else:
                    copyinto_filename = self.create_copyinto_JSON(table_name=TableName.lower(), file_match_text=FileMatchText, file_date_regex=file_date_regex, custom_fileformat_options=CustomFileFormatOptions)

                if copyinto_filename != None:
                    self.config_resources.append(["sources", copyinto_filename])

            # ----------------------------------------------------------------
            # Create Import Raw DDL File
            # ----------------------------------------------------------------
            TableNameRaw = ""
            if self.need_import_raw and FileMatchText.upper() != "EXCLUDEFROMFILETRANSFERS" and useImportView is False:

                if self.has_fn_create_importraw_DDL_custom:
                    self.runlog.log(f"Creating {self.source_name} custom Import RAW table DDL.")
                    TableNameRaw = self.fn_create_importraw_DDL_custom(table_name=TableName.lower(), version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name)
                else:
                    self.runlog.log("Creating Import RAW table DDL.")
                    self.runlog.log("")
                    TableNameRaw = create_importraw_DDL(table_name=TableName.lower(), version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name)

                self.data_resources.append(["import", TableNameRaw])

            # ----------------------------------------------------------------
            # Create Flatten Insert File
            # ----------------------------------------------------------------
            flatten_filename = ""
            if self.need_flatten and useImportView is False:
                try:
                    if self.has_fn_create_flatten_custom:
                        self.runlog.log(f"Creating {self.source_name} custom flatten query.")
                        flatten_filename = self.fn_create_flatten_custom(source_name=self.source_name, table_name=TableName.lower(), table_name_raw=TableNameRaw, col_list=col_list, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, worksheet=wstable)
                    else:
                        self.runlog.log("Creating flatten query.")
                        flatten_filename = create_flatten(source_name=self.source_name, table_name=TableName.lower(), table_name_raw=TableNameRaw, col_list=col_list, version=self.dts, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client)
                except Exception as e:
                    self.runlog.log(f"ERROR: Can't create Flatten Query\n{e}")
                    break

                self.config_resources.append(["sources", flatten_filename])

            # ----------------------------------------------------------------
            # don't include flatten in import SQL if no flatten is created
            # ----------------------------------------------------------------
            if self.need_flatten and flatten_filename != "" and useImportView is False:
                if copyinto_filename != "":
                    sources_obj.append("importSql", [{"sortOrder": 2, "sqlFileName": flatten_filename, "saveResults": False}])
                else:
                    sources_obj.append("importSql", [{"sortOrder": 1, "sqlFileName": flatten_filename, "saveResults": False}])

            # ----------------------------------------------------------------
            # Create Delete Raw File
            # ----------------------------------------------------------------
            deleteraw_filename = ""
            if self.need_flatten and useImportView is False and TableNameRaw != "":
                self.runlog.log(f"Creating delete raw query.")
                deleteraw_filename = create_delete_rawtable_query(table_name=TableName.lower(), table_name_raw=TableNameRaw, db_folder=self.database_folder, runlog=self.runlog, repo_root_folder=self.repo_root_folder, client=self.client, source_name=self.source_name)

                self.config_resources.append(["sources", deleteraw_filename])

            if deleteraw_filename != "":
                if copyinto_filename != "":
                    sources_obj.append("importSql", [{"sortOrder": self.deleteraw_order, "sqlFileName": deleteraw_filename, "saveResults": False}])
                else:
                    sources_obj.append("importSql", [{"sortOrder": 2, "sqlFileName": deleteraw_filename, "saveResults": False}])

            # ----------------------------------------------------------------
            # Create Base Config
            # ----------------------------------------------------------------
            self.create_base_config(dd_file=self.dd_file, bus_rules=bus_rules, sources_obj=sources_obj, wsheetinfo=wsheetinfo, copyinto_filename=copyinto_filename)

        # ----------------------------------------------------------------
        # Create End Config
        # ----------------------------------------------------------------
        self.create_config_end()

        return

    # =======================================================================
    # create rawaudience only
    # =======================================================================
    def create_config_aud(self):
        # ----------------------------------------------------------------
        # initialize
        # ----------------------------------------------------------------
        self.load_source_functions()
        self.read_dd_file()
        # ----------------------------------------------------------------
        # create configs per worksheet
        # ----------------------------------------------------------------
        for worksheet in self.wslist:
            print_section(msg=f"Working on {worksheet}", runlog=self.runlog)
            # ----------------------------------------------------------------
            # read worksheet info
            # ----------------------------------------------------------------
            try:
                wsheetinfo = self.read_worksheet_info(worksheet=worksheet, audonly=True)
            except Exception as err:
                self.runlog.log(f"WARNING: {err}")

            # ----------------------------------------------------------------
            # Create Base Config
            # ----------------------------------------------------------------
            self.create_base_config_aud(dd_file=self.dd_file, wsheetinfo=wsheetinfo)

        # ----------------------------------------------------------------
        # Create End Config
        # ----------------------------------------------------------------
        self.create_config_end(audonly=True)

        return

    def create_config_5x(self):
        # load source creator file
        self.has_source_functions = False
        self.has_main = False
        try:
            # ----------------------------------------------------------------
            # load source specific functions file
            # ----------------------------------------------------------------
            functions_plugin_name = f"SourcePlugins.{self.source_name.capitalize()}.{self.source_name.capitalize()}_generate_configs"

            self.runlog.log(f"Try to load {functions_plugin_name}")
            functions_plugin = import_module(functions_plugin_name)

            self.has_source_functions = True

            self.runlog.log("")
            self.runlog.log(f"Imported {functions_plugin_name} into Config class.")

            # ----------------------------------------------------------------
            # try to load main
            # ----------------------------------------------------------------
            self.has_main = False
            try:
                self.fn_main = getattr(functions_plugin, "main")
                self.runlog.log(f"{indent}{functions_plugin_name} main function loaded.")
                self.has_main = True
            except:
                self.runlog.log(f"{indent}No main function found in {functions_plugin_name}.")

        except Exception as e:
            self.runlog.log(f"WARNING: {e}")
            self.has_source_functions = False
            self.runlog.log("")
            self.runlog.log(f"No {functions_plugin_name} found.")

        try:
            # ----------------------------------------------------------------
            # load versions file
            # ----------------------------------------------------------------
            versions_plugin_name = f"SourcePlugins.{self.source_name.capitalize()}.{self.source_name.capitalize()}_versions"

            self.runlog.log(f"Try to load {versions_plugin_name}")
            versions_plugin_name = import_module(versions_plugin_name)

            self.has_source_versions = True

            self.runlog.log("")
            self.runlog.log(f"Imported {versions_plugin_name} into Config class.")

            # ----------------------------------------------------------------
            # create versions variable
            # ----------------------------------------------------------------
            self.source_versions = []
            if self.has_source_versions:
                try:
                    self.source_versions = versions_plugin_name.versions
                except:
                    self.source_versions = []

            # -----------------------------------------------------------------
            # create versions menu
            # -----------------------------------------------------------------
            if len(self.source_versions)>0:
                # menu prompt
                menu = MenuPrompt()
                for v in self.source_versions:
                    menu.addChoice(name=v, description=f"v{v}")
                version = menu.prompt()
            else:
                version = "1.0.0"

        except Exception as e:
            self.runlog.log(f"WARNING: {e}")
            self.has_source_functions = False
            self.runlog.log("")
            self.runlog.log(f"No {functions_plugin_name} found.")

        if self.has_main and self.has_source_versions:
            argv=[f"--input {self.dd_file}",f"--client {self.client}",f"--feature {self.source_name}",f"--version {version}"]
            self.runlog.log(f"Arguments: {argv}")
            try:
                self.fn_main(argv=argv)
            except Exception as err:
                self.runlog.log(f"ERROR: {err}")