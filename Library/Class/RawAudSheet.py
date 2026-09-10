import pandas as pd
from Library.FunctionFiles.Functions import *
from Library.Class.Document import *
from importlib import import_module

class RawAudSheet:
    def __init__(self, client:str, workbook:str, worksheet:str, source_name:str, table_name:str, bus_rule_obj:object, runlog:object, db_folder:str, platform:str= "Prefect", pk_case_sensitive:bool=False):
        self.client = client
        self.table_name = table_name
        self.busrule_obj = bus_rule_obj
        self.runlog = runlog
        self.db_folder = db_folder
        self.pk_case_sensitive = pk_case_sensitive
        self.output_folder = f"{self.db_folder}ForReferenceOnly{os.sep}{self.table_name}_BusRules{os.sep}"

        # initialize custom function variables
        self.has_source_functions = False
        self.has_fn_ctrl_ra_src_query_custom = False

        # archtics override
        if source_name.upper() == "ARCHTICS-API":
            self.source_name = "archtics"
        else:
            self.source_name = source_name

        self.RuleNameKey = "ruleName"
        self.RunOrderKey = "runOrder"
        self.RunPositionKey = "runPosition"
        self.RuleQueryKey = "ruleQuery"

        if platform == "Snaplogic":
            self.RuleNameKey = self.RuleNameKey.upper()
            self.RunOrderKey = self.RunOrderKey.upper()
            self.RunPositionKey = self.RunPositionKey.upper()
            self.RuleQueryKey = self.RuleQueryKey.upper()

        # store original worksheet value
        worksheet_ori = worksheet

        try:
            self.worksheet = pd.read_excel(workbook, sheet_name=worksheet, skiprows=[0])
        except:
            try:
                worksheet = worksheet.replace("RAWAUDIENCE", "RawAudience")
                self.worksheet = pd.read_excel(workbook, sheet_name=worksheet, skiprows=[0])
            except:
                try:
                    worksheet = worksheet.replace("RawAudience", "rawaudience")
                    self.worksheet = pd.read_excel(workbook, sheet_name=worksheet, skiprows=[0])
                except:
                    raise Exception(f"ERROR: {worksheet_ori} not found. Attempts at other variations also failed. Moving on to next table.")

        # load source functions
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
            functions_plugin_name = f"SourcePlugins.{self.source_name.capitalize()}.Functions_{self.source_name.capitalize()}"

            self.runlog.log(f"Try to load {functions_plugin_name}")
            functions_plugin = import_module(functions_plugin_name)

            self.has_source_functions = True

            self.runlog.log("")
            self.runlog.log(f"Imported {functions_plugin_name} into RawAudSheet class.")

            # ----------------------------------------------------------------
            # try to load custom ctrl_ra_src_query function
            # ----------------------------------------------------------------
            try:
                self.fn_ctrl_ra_src_query_custom = getattr(functions_plugin, "fn_ctrl_ra_src_query_custom")
                self.runlog.log(f"{indent}{functions_plugin_name} fn_ctrl_ra_src_query_custom function loaded.")
                self.has_fn_ctrl_ra_src_query_custom = True
            except:
                self.runlog.log(f"{indent}No fn_ctrl_ra_src_query_custom function found in {functions_plugin_name}.")

        except Exception as e:
            self.runlog.log(f"WARNING: {e}")
            self.has_source_functions = False
            self.runlog.log("")
            self.runlog.log(f"No {functions_plugin_name} found.")

    # helper function to get source value given a raw audience column name
    def src_value(self, rawaud_col_name:str):
        src_col = self.worksheet.query(f'COLUMN_NAME=="{rawaud_col_name}"')["SOURCE_VALUE"].tolist()[0]

        return src_col

    # build raw audience query
    def stg_ra_query(self):
        col_list = ["RAWAUDIENCETABLE", "RAWAUDIENCESOURCE", "RAWAUDIENCESUBSOURCE", "SOURCEACCOUNTID", "SOURCEACCOUNTSECONDARYID"]
        col_list_str = ""

        for col in col_list:
            col_list_str += f"{col}, "
        col_list_str = col_list_str[:-2]

        # source id
        src_acc_id = str(self.src_value("SOURCEACCOUNTID"))
        src_acc_id_val = "''"
        if src_acc_id.strip() != "nan":
            src_acc_id_val = f"CAST(src.{src_acc_id} as string)"
        else:
            raise Exception("SOURCEACCOUNTID value empty.")

        # secondary source id
        sec_acc_id = str(self.src_value("SOURCEACCOUNTSECONDARYID"))
        sec_acc_id_val = "''"
        if sec_acc_id != "nan":
            sec_acc_id_val = f"CAST(src.{sec_acc_id} as string)"

        # build query
        query = ""
        query += "INSERT INTO STAGE.RawAudience ("
        query += col_list_str
        query += ")"
        query += " SELECT "
        query += col_list_str
        query += " FROM (SELECT DISTINCT "
        for col in col_list:
            colval = str(self.src_value(col))
            if colval != "nan":
                if colval == src_acc_id:
                    query += f"{src_acc_id_val} as {col}, "
                elif colval == sec_acc_id:
                    query += f"{sec_acc_id_val} as {col}, "
                elif col == "RAWAUDIENCETABLE" or col == "RAWAUDIENCESOURCE" or col == "RAWAUDIENCESUBSOURCE":
                    query += f"'{colval}' as {col}, "
                elif "(" in colval or ")" in colval:
                    query += f"{colval} as {col}, "
                else:
                    query += f"src.{colval} as {col}, "
            else:
                query += f"'' as {col}, "

        if self.pk_case_sensitive:
            src_acc_id_partition = f"CAST(src.{src_acc_id} as string)"
            sec_acc_id_partition = f"CAST(src.{sec_acc_id} as string)"
        else:
            src_acc_id_partition = f"LOWER(CAST(src.{src_acc_id} as string))"
            sec_acc_id_partition = f"LOWER(CAST(src.{sec_acc_id} as string))"

        if sec_acc_id == "nan":
            query += f"ROW_NUMBER() OVER (PARTITION BY {src_acc_id_partition} ORDER BY {src_acc_id_partition} DESC) rownumber"
        else:
            query += f"ROW_NUMBER() OVER (PARTITION BY {src_acc_id_partition}, {sec_acc_id_partition} ORDER BY {src_acc_id_partition} DESC, {sec_acc_id_partition} DESC) rownumber"

        query += f" FROM TMP.{self.table_name}UNIQUE src"
        query += f" LEFT JOIN STAGE.RAWAUDIENCE rawaud"
        if self.pk_case_sensitive:
            query += f" ON {src_acc_id_val} = rawaud.SOURCEACCOUNTID"
            query += f" AND {sec_acc_id_val} = rawaud.SOURCEACCOUNTSECONDARYID"
        else:
            query += f" ON LOWER({src_acc_id_val}) = LOWER(rawaud.SOURCEACCOUNTID)"
            query += f" AND LOWER({sec_acc_id_val}) = LOWER(rawaud.SOURCEACCOUNTSECONDARYID)"
        query += f" AND LOWER(rawaud.RAWAUDIENCETABLE) = LOWER('{self.src_value('RAWAUDIENCETABLE')}')"
        query += f" WHERE rawaud.RAWAUDIENCEID IS NULL)rawaud_values"
        query += " WHERE rawaud_values.rownumber = 1;"

        # write out Rule Query to file
        filewrite(folder=self.output_folder, filename=f"{self.table_name.upper()}_1_3 INSERT STAGE RAWAUDIENCE RULE QUERY.sql", content=query)

        return query

    # create raw audience business rule
    def create_stg_rawaud_busrule(self):

        RABusRule = {}
        RABusRule[self.RuleNameKey] = f"{self.table_name}_1_3"
        RABusRule[self.RunOrderKey] = 1
        RABusRule[self.RunPositionKey] = 3
        RABusRule[self.RuleQueryKey] = self.stg_ra_query()

        # add to business rules object
        self.busrule_obj.add_rule(RABusRule)
        return

    # build temp raw audience table query
    def tmp_ra_query(self):
        # source id
        src_acc_id = str(self.src_value("SOURCEACCOUNTID"))
        src_acc_id_val = "''"
        if src_acc_id != "nan":
            src_acc_id_val = f"CAST(src.{src_acc_id} as string)"

        # secondary source id
        sec_acc_id = str(self.src_value("SOURCEACCOUNTSECONDARYID"))
        sec_acc_id_val = "''"
        if sec_acc_id != "nan":
            sec_acc_id_val = f"CAST(src.{sec_acc_id} as string)"

        # build query
        query = ""
        query += f"CREATE OR REPLACE TABLE TMP.{self.table_name}RawAudience"
        query += " AS SELECT src.*, rawaud.RAWAUDIENCEID"
        query += f" FROM TMP.{self.table_name}UNIQUE src"
        query += f" INNER JOIN STAGE.RAWAUDIENCE rawaud"
        query += f" ON {src_acc_id_val} = rawaud.SOURCEACCOUNTID"
        query += f" AND {sec_acc_id_val} = rawaud.SOURCEACCOUNTSECONDARYID"
        query += f" AND LOWER(rawaud.RAWAUDIENCETABLE) = LOWER('{self.src_value('RAWAUDIENCETABLE')}');"

        # write out Rule Query to file
        filewrite(folder=self.output_folder, filename=f"{self.table_name.upper()}_2_3 CREATE TMP RAWAUDIENCE RULE QUERY.sql", content=query)

        return query

    # create temp raw audience table business rule
    def create_tmp_rawaud_busrule(self):
        TMPRABusRule = {}
        TMPRABusRule[self.RuleNameKey] = f"{self.table_name}_2_3"
        TMPRABusRule[self.RunOrderKey] = 2
        TMPRABusRule[self.RunPositionKey] = 3
        TMPRABusRule[self.RuleQueryKey] = self.tmp_ra_query()

        # add to business rules object
        self.busrule_obj.add_rule(TMPRABusRule)
        return

    # helper function to check casing and determine if value should be treated as string or column reference
    def col_or_str(self, input_str:str, table_name:str, col_name:str=""):
        col_list_string = ["RAWAUDIENCETABLE", "RAWAUDIENCESOURCE"]
        input_str = input_str.strip()

        if col_name in col_list_string:
            if input_str == "nan" or input_str == "":
                return "''''"
            else:
                return f"'{input_str}'"
        elif input_str == "nan" or input_str == "":
            return "''''"
        elif "(" in input_str or ")" in input_str:
            return input_str
        elif input_str == input_str.upper():
            return f"{table_name}.{input_str}"
        else:
            return f"'{input_str}'"

    # create control rawaudience source query
    def ctrl_ra_src_query(self):
        col_list_all = ["RAWAUDIENCETABLE", "RAWAUDIENCESOURCE", "RAWAUDIENCESUBSOURCE", "SOURCEACCOUNTID", "SOURCEACCOUNTSECONDARYID", "ACCOUNTTYPE", "ORGANIZATION", "MEMBERSHIPLEVEL", "ACCOUNTPIN", "ACCOUNTREPRESENTATIVENAME", "ACCOUNTREPRESENTATIVEPHONE", "SOURCEINSERTDATE", "SOURCEUPDATEDATE", "SALUTATION", "PREFIX", "SUFFIX", "TITLE", "BIRTHDATE", "FIRSTNAME", "MIDDLENAME", "LASTNAME", "GENDER", "METROAREA", "ADDRESS1", "ADDRESS2", "ADDRESS3", "CITY", "STATE", "ZIP", "COUNTRY", "LATITUDE", "LONGITUDE", "DISTANCETOVENUE", "PHONE1", "PHONE2", "PHONE3", "FAXNUMBER", "EMAIL", "EMAIL2", "EMAIL3", "EMAIL4", "CONTACTTYPE"]
        col_list_pii = ["PREFIX", "SUFFIX", "TITLE", "FIRSTNAME", "MIDDLENAME", "LASTNAME", "ADDRESS1", "ADDRESS2", "ADDRESS3", "CITY", "STATE", "ZIP", "COUNTRY", "PHONE1", "PHONE2", "PHONE3", "FAXNUMBER", "EMAIL", "EMAIL2", "EMAIL3", "EMAIL4"]

        tbl_alias = "stg"
        col_logic_list = {}

        # get SOURCEACCOUNTID value
        src_acc_id = self.col_or_str(input_str=str(self.src_value("SOURCEACCOUNTID")), table_name=tbl_alias)

        # get SOURCEACCOUNTSECONDARYID value
        src_acc_secid = self.col_or_str(input_str=str(self.src_value("SOURCEACCOUNTSECONDARYID")), table_name=tbl_alias)

        # create per column logic
        for col in col_list_all:
            # first check if value should be considered string, column name, or expression
            try:
                colval_raw = self.src_value(col)
                colval = self.col_or_str(input_str=colval_raw, table_name=tbl_alias, col_name=col)
            except:
                colval = "''"

            if col == "ORGANIZATION":
                colval = f"COALESCE(std.COMPANYNAME, {colval}, '')"

            elif col == "SOURCEINSERTDATE":
                colval = f"MIN({colval})"

            elif col == "SOURCEUPDATEDATE":
                colval = f"MAX({colval})"

            elif col == "PREFIX":
                colval = f"COALESCE(std.NAMEPREFIX, {colval}, '')"

            elif col == "SUFFIX":
                colval = f"COALESCE(std.NAMESUFFIX, {colval}, '')"

            elif col == "BIRTHDATE":
                colval = f"COALESCE(NULLIF(TRIM({colval}), ''), '1900-01-01')"

            elif col == "COUNTRY":
                colval = f"CASE WHEN UPPER(COALESCE(std.COUNTRYNAME, {colval})) IN ('UNITED STATES OF AMERICA', 'UNITED STATES', 'US', 'USA', '') THEN 'United States of America' ELSE COALESCE(std.COUNTRYNAME, {colval}) END"

            elif col == "DISTANCETOVENUE":
                colval = f"CASE WHEN std.DISTANCETOVENUE = '5265.00000' THEN '-1.00000' ELSE COALESCE(std.DISTANCETOVENUE, {colval}, '0.00000') END"

            elif col == "FIRSTNAME":
                colval = f"COALESCE(std.NAMEFIRST, {colval}, '')"

            elif col == "MIDDLENAME":
                colval = f"COALESCE(std.NAMEMIDDLE, {colval}, '')"

            elif col == "LASTNAME":
                colval = f"COALESCE(std.NAMELAST, {colval}, '')"

            elif col == "PHONE1" or col == "PHONE2" or col == "PHONE3" or col == "FAXNUMBER":
                if colval != "''" and "formatted" not in colval.lower():
                    colval = f"COALESCE(std.PHONENUMBER, {colval}formatted, '')"
                elif colval != "''":
                    colval = f"COALESCE(std.PHONENUMBER, {colval}, '')"
                else:
                    colval = f"COALESCE({colval}, '')"

            # elif col == "PHONE2" or col == "PHONE3" or col == "FAXNUMBER":
            #     if colval != "''" and "formatted" not in colval.lower():
            #         colval = f"COALESCE({colval}formatted, '')"
            #     else:
            #         colval = f"COALESCE({colval}, '')"

            elif col == "EMAIL2" or col == "EMAIL3" or col == "EMAIL4" or col == "CONTACTTYPE":
                colval = f"COALESCE({colval}, '')"

            elif col == "SALUTATION" or col == "GENDER" or col == "ADDRESS1" or col == "ADDRESS2" or col == "ADDRESS3" or col == "CITY" or col == "STATE" or col == "ZIP" or col == "LATITUDE" or col == "LONGITUDE" or col == "EMAIL":
                colval = f"COALESCE(std.{col}, {colval}, '')"

            else:
                colval = colval

            colval = colval.replace(", ,", ", ")

            # build column list with column alias
            col_logic_list[col] = [col, colval]

            #-------------------------------------------------------------------------------
            # 2023-07-17: commenting this out as it was causing issues.
            # # if source column name is the same as standardization, prefix with SRC_
            # if colval_raw == col:
            #     col_logic_list[col] = [f"SRC_{colval_raw}", colval]
            # else:
            #     col_logic_list[col] = [col, colval]
            # -------------------------------------------------------------------------------

        col_logic_list["STANDARDIZATIONROWID"] = ["STANDARDIZATIONROWID", f"{tbl_alias}.STANDARDIZATIONROWID"]
        col_logic_list["VALIDEMAIL"] = ["VALIDEMAIL","COALESCE(CASE WHEN std.RESULTS ILIKE '%ES01%' THEN 1 ELSE 0 END, 0)"]
        col_logic_list["VALIDADDRESS"] = ["VALIDADDRESS","COALESCE(CASE WHEN std.RESULTS ILIKE '%AS01%' OR std.RESULTS ILIKE '%AS02%' OR std.RESULTS ILIKE '%AS03%' THEN 1 ELSE 0 END, 0)"]
        col_logic_list["VALIDPHONE"] = ["VALIDPHONE","COALESCE(CASE WHEN std.RESULTS ILIKE '%PS01%' OR std.RESULTS ILIKE '%PS02%' THEN 1 ELSE 0 END, 0)"]

        # define row number clause for secondary id
        if src_acc_secid == "''''":
            src_acc_secid_partition = ""
        else:
            if self.pk_case_sensitive:
                src_acc_secid_partition = f" CAST({src_acc_secid} as string),"
            else:
                src_acc_secid_partition = f" LOWER(CAST({src_acc_secid} as string)),"

        if self.pk_case_sensitive:
            src_acc_id_partition = f"CAST({src_acc_id} as string)"
        else:
            src_acc_id_partition = f"LOWER(CAST({src_acc_id} as string))"

        col_logic_list["RN"] = ["RN",f"ROW_NUMBER() OVER (PARTITION BY {src_acc_id_partition},{src_acc_secid_partition} LOWER(CAST({tbl_alias}.STANDARDIZATIONROWID as string)) ORDER BY {src_acc_id_partition},{src_acc_secid_partition} LOWER(CAST({tbl_alias}.STANDARDIZATIONROWID as string)))"]

        # build inner select query
        if self.has_fn_ctrl_ra_src_query_custom:
            self.runlog.log(f"\tCreating {self.source_name} custom rawaudience query.")
            src_query = self.fn_ctrl_ra_src_query_custom(table_name=self.table_name, tbl_alias=tbl_alias ,col_list_all=col_list_all , col_logic_list=col_logic_list)
        else:
            self.runlog.log(f"\tCreating standard rawaudience query.")
            src_query = Document()
            src_query.append("SELECT")

            # wrapping with case when to replace any column with "unknown" in its values with empty string to prevent sec. matchpass blowup
            for key, value in col_logic_list.items():
                if key in col_list_pii:
                    src_query.newline(f"\t\t\tCASE WHEN {key} ILIKE '%unknown%' THEN '' ELSE {key} END AS {key},")
                else:
                    src_query.newline(f"\t\t\t{key},")

            src_query.trimend(1)

            src_query.newline("\t\tFROM (")
            # src_query.append("SELECT * FROM (")
            src_query.newline("\tSELECT DISTINCT")

            for col in col_list_all:
                src_query.newline(f"\t\t{col_logic_list[col][1]} AS {col_logic_list[col][0]},")

            src_query.newline(f"\t\t{col_logic_list['STANDARDIZATIONROWID'][1]} AS {col_logic_list['STANDARDIZATIONROWID'][0]},")
            src_query.newline(f"\t\t{col_logic_list['VALIDEMAIL'][1]} AS {col_logic_list['VALIDEMAIL'][0]},")
            src_query.newline(f"\t\t{col_logic_list['VALIDADDRESS'][1]} AS {col_logic_list['VALIDADDRESS'][0]},")
            src_query.newline(f"\t\t{col_logic_list['VALIDPHONE'][1]} AS {col_logic_list['VALIDPHONE'][0]},")
            src_query.newline(f"\t\t{col_logic_list['RN'][1]} AS {col_logic_list['RN'][0]}")
            src_query.newline(f"\tFROM")
            src_query.newline(f"\t\tSTAGE.{self.table_name} {tbl_alias}")
            src_query.newline("\tLEFT JOIN")
            src_query.newline("\t\tSTAGE.STANDARDIZATION std")
            src_query.newline(f"\tON")
            src_query.newline(f"\t\tstg.STANDARDIZATIONROWID = std.STANDARDIZATIONROWID")
            src_query.newline("\tGROUP BY")

            # group_special = ["FIRSTNAME", "MIDDLENAME", "LASTNAME", "GENDER", "CITY", "PHONE1", "PHONE2", "PHONE3", "FAX", "EMAIL"]
            group_except_list = ["SOURCEINSERTDATE", "SOURCEUPDATEDATE"]
            for col in col_list_all:
                # if col in group_special:
                col_name = col_logic_list[col][0]
                col_logic = col_logic_list[col][1]
                if col_name in group_except_list:
                    src_query = src_query
                elif tbl_alias in col_logic or "std" in col_logic:
                    src_query.newline(f"\t\t{col_logic},")
                else:
                    src_query.newline(f"\t\t{col_name},")

            src_query.newline(f"\t\t{tbl_alias}.STANDARDIZATIONROWID,")
            src_query.newline(f"\t\tVALIDEMAIL,")
            src_query.newline("\t\tVALIDADDRESS,")
            src_query.newline("\t\tVALIDPHONE")
            src_query.newline("\t) SUB")
            src_query.newline("WHERE SUB.RN = 1;")

        return src_query.out().replace("'","''")

    # create control rawaudience merge query
    def ctrl_ra_merge_query(self):
        # get source query
        src_query = self.ctrl_ra_src_query()

        # column list

        if self.client.upper() == "KSG":
            merge_col_list = ["sourcequery", "sourcequeryresulttable", "sortorder", "defaultsortorder", "emailsortorder", "namesortorder", "addresssortorder", "socialsortorder", "phonesortorder"]
        else:
            merge_col_list = ["sourcequery", "sourcequeryresulttable", "defaultsortorder", "emailsortorder", "namesortorder", "addresssortorder", "socialsortorder", "phonesortorder"]

        merge_query = Document()

        merge_query.append("MERGE INTO CONTROL.RAWAUDIENCE dest USING")
        merge_query.newline("(")

        merge_query.newline("\tSELECT")
        merge_query.newline(f"\t\t'STAGE.{self.table_name}' AS  rawaudiencetable,")

        for col in merge_col_list:
            if col == "sourcequery":
                merge_query.newline(f"\t\t'{src_query}' AS {col},")
            elif col == "sourcequeryresulttable":
                merge_query.newline(f"\t\t'TMP.RAWAUDIENCE{self.table_name}' AS {col},")
            else:
                merge_query.newline(f"\t\t<SORTORDER> AS {col},")

        merge_query.trimend(1)

        merge_query.newline(f") src")
        merge_query.newline(f"ON")
        merge_query.newline(f"\tdest.rawaudiencetable = src.rawaudiencetable")
        merge_query.newline(f"WHEN MATCHED AND")

        for col in merge_col_list:
            merge_query.newline(f"\tNOT EQUAL_NULL(dest.{col}, src.{col}) OR")
        merge_query.trimend(3)

        merge_query.newline(f"THEN UPDATE SET")

        for col in merge_col_list:
            merge_query.newline(f"\tdest.{col} = src.{col},")

        merge_query.newline(f"\tdest.dwupdatedate = CURRENT_TIMESTAMP()")
        merge_query.newline(f"WHEN NOT MATCHED THEN")
        merge_query.newline(f"INSERT")
        merge_query.newline("(")
        merge_query.newline(f"\trawaudiencetable,")

        for col in merge_col_list:
            merge_query.newline(f"\t{col},")

        merge_query.newline(f"\tdwinsertdate,")
        merge_query.newline(f"\tdwupdatedate")
        merge_query.newline(")")
        merge_query.newline(f"VALUES")
        merge_query.newline("(")
        merge_query.newline("\tsrc.rawaudiencetable,")

        for col in merge_col_list:
            merge_query.newline(f"\tsrc.{col},")

        merge_query.newline("\tCURRENT_TIMESTAMP(),")
        merge_query.newline("\tCURRENT_TIMESTAMP()")
        merge_query.newline(");")

        return merge_query.out()

    # create control rawaudience file
    def ctrl_ra_file(self, db_folder:str, repo_root_folder:str, client:str):

        # get source name
        source_name = self.src_value("RAWAUDIENCESOURCE").replace(" ","")

        # get Merge query
        merge_query = self.ctrl_ra_merge_query()

        ra_file = Document()

        ra_file.append(f"/* control.sources inserts for {source_name} version=1 */")
        ra_file.newline("!set variable_substitution=true;")
        ra_file.newline(merge_query)

        # set file name
        ra_filename = f"control-rawaudience-{self.table_name.lower()}.sql"

        # set output folder
        output_folder = f"{db_folder}data_repo{os.sep}seed_data{os.sep}"
        filewrite(folder=output_folder, filename=ra_filename, content=ra_file.out())

        if repo_root_folder != "":
            datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}seed_data{os.sep}{client.upper()}{os.sep}"
            filewrite(folder=datarepo_folder, filename=ra_filename, content=ra_file.out())

        return ra_filename

    # Create merge to rawaudience SP
    def create_merge_to_rawaudience_sp(self, table_name: str, db_folder: str, runlog: object, repo_root_folder:str, client:str):

        column_list = ["RAWAUDIENCETABLE", "RAWAUDIENCESOURCE", "RAWAUDIENCESUBSOURCE", "SOURCEACCOUNTID", "SOURCEACCOUNTSECONDARYID", "ACCOUNTTYPE", "ORGANIZATION", "MEMBERSHIPLEVEL", "ACCOUNTPIN", "ACCOUNTREPRESENTATIVENAME", "ACCOUNTREPRESENTATIVEPHONE", "SOURCEINSERTDATE", "SOURCEUPDATEDATE", "SALUTATION", "PREFIX", "SUFFIX", "TITLE", "BIRTHDATE", "FIRSTNAME", "MIDDLENAME", "LASTNAME", "GENDER", "METROAREA", "ADDRESS1", "ADDRESS2", "ADDRESS3", "CITY", "STATE", "ZIP", "COUNTRY", "LATITUDE", "LONGITUDE", "DISTANCETOVENUE", "PHONE1", "PHONE2", "PHONE3", "FAXNUMBER", "EMAIL", "EMAIL2", "EMAIL3", "EMAIL4", "CONTACTTYPE", "STANDARDIZATIONROWID", "VALIDEMAIL", "VALIDADDRESS", "VALIDPHONE"]
        # define SP name
        merge_sp_name = f"stage.sp_merge{table_name.lower()}intorawaudience()"
        # initialize merge query document
        mergesp = Document()

        # write query
        mergesp.append(f"/* sp_Merge{table_name.upper()}IntoRawAudience (stage) grantobjectname=stage.sp_Merge{table_name.upper()}IntoRawAudience version=1 */")
        mergesp.newline("!set exit_on_error=true;")
        mergesp.newline("!set variable_substitution=true;")
        mergesp.newline("")
        mergesp.newline(f"CREATE OR REPLACE PROCEDURE {merge_sp_name}")
        mergesp.newline("\treturns varchar not null")
        mergesp.newline("\tlanguage sql")
        mergesp.newline("\texecute as caller")
        mergesp.newline("AS")
        mergesp.newline("$$")
        mergesp.newline("\tBEGIN")

        mergesp.newline(f"\t\tMERGE INTO STAGE.RAWAUDIENCE dest USING TMP.RawAudience{table_name.upper()} sor ON")
        mergesp.newline("\t\t\tlower(dest.RAWAUDIENCETABLE) = lower(sor.RAWAUDIENCETABLE)")
        if self.pk_case_sensitive:
            mergesp.newline("\t\t\tAND dest.SOURCEACCOUNTID = sor.SOURCEACCOUNTID")
            mergesp.newline("\t\t\tAND dest.SOURCEACCOUNTSECONDARYID = sor.SOURCEACCOUNTSECONDARYID")
        else:
            mergesp.newline("\t\t\tAND lower(dest.SOURCEACCOUNTID) = lower(sor.SOURCEACCOUNTID)")
            mergesp.newline("\t\t\tAND lower(dest.SOURCEACCOUNTSECONDARYID) = lower(sor.SOURCEACCOUNTSECONDARYID)")
        mergesp.newline("\t\tWHEN MATCHED AND")
        mergesp.newline("\t\t(")

        for col in column_list:
            mergesp.newline(f"\t\t\tNOT EQUAL_NULL(dest.{col}, sor.{col}) OR")

        mergesp.trimend(3)
        mergesp.newline("\t\t)")
        mergesp.newline("\t\tTHEN UPDATE SET")

        for col in column_list:
            mergesp.newline(f"\t\t\tdest.{col} = sor.{col},")

        mergesp.newline("\t\t\tdest.DWUPDATEDATE = now()")
        mergesp.newline("\t\tWHEN NOT MATCHED THEN INSERT")
        mergesp.newline("\t\t(")

        for col in column_list:
            mergesp.newline(f"\t\t\t{col},")

        mergesp.newline("\t\t\tDWUPDATEDATE,")
        mergesp.newline("\t\t\tDWINSERTDATE")

        mergesp.newline("\t\t) VALUES")
        mergesp.newline("\t\t(")

        for col in column_list:
            mergesp.newline(f"\t\t\tsor.{col},")

        mergesp.newline("\t\t\tnow(),")
        mergesp.newline("\t\t\tnow()")
        mergesp.newline("\t\t);")

        mergesp.newline(f"\tRETURN 'FINISHED CALLING STORED PROCEDURE sp_Merge{table_name.upper()}IntoRawAudience';")
        mergesp.newline("\tEND;")
        mergesp.newline("$$;")

        # define output folder and filename
        filename = f"sp_merge{table_name.lower()}intorawaudience.sql"
        output_folder = f"{db_folder}data_repo{os.sep}stage{os.sep}"
        filewrite(folder=output_folder, filename=filename, content=mergesp.out())

        # write output repo files if repo_root_folder is not empty
        if repo_root_folder != "":
            datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{self.source_name.lower()}{os.sep}stage{os.sep}{client.upper()}{os.sep}"
            filewrite(folder=datarepo_folder, filename=filename, content=mergesp.out())

        # trace log
        print_section_detail(msg=f"MERGEINTO - {filename}\nCreated in: {output_folder}", runlog=runlog)

        return merge_sp_name

    # Create delete orphan from rawaudience SP
    def delete_orphan_from_rawaudience_sp(self, table_name: str, db_folder: str, runlog: object, repo_root_folder:str, client:str):

        # define SP name
        delete_sp_name = f"stage.sp_delete{table_name.lower()}orphansfromrawaudience()"
        # initialize merge query document
        deletesp = Document()

        # write query
        deletesp.append(f"/* sp_Delete{table_name.upper()}OrphansFromRawAudience (stage) grantobjectname=stage.sp_Delete{table_name.upper()}OrphansFromRawAudience version=1 */")
        deletesp.newline("!set exit_on_error=true;")
        deletesp.newline("!set variable_substitution=true;")
        deletesp.newline("")
        deletesp.newline(f"CREATE OR REPLACE PROCEDURE {delete_sp_name}")
        deletesp.newline("\treturns varchar not null")
        deletesp.newline("\tlanguage sql")
        deletesp.newline("\texecute as caller")
        deletesp.newline("AS")
        deletesp.newline("$$")
        deletesp.newline("\tBEGIN")

        deletesp.newline("\t\tDELETE FROM STAGE.RAWAUDIENCE TAR")
        deletesp.newline("\t\tUSING (")
        deletesp.newline("\t\t\tSELECT DISTINCT RA.RAWAUDIENCEID")
        deletesp.newline("\t\t\tFROM STAGE.RAWAUDIENCE RA")
        deletesp.newline(f"\t\t\tLEFT JOIN STAGE.{table_name.upper()} RA_SOURCE")
        deletesp.newline("\t\t\t\tON RA.RAWAUDIENCEID = RA_SOURCE.RAWAUDIENCEID")
        deletesp.newline("\t\t\tWHERE")
        deletesp.newline("\t\t\t\tRA_SOURCE.RAWAUDIENCEID IS NULL")
        deletesp.newline(f"\t\t\t\tAND LOWER(RA.RAWAUDIENCETABLE) = 'stage.{table_name.lower()}'")
        deletesp.newline("\t\t) SRC")
        deletesp.newline("\t\tWHERE")
        deletesp.newline("\t\t\tTAR.RAWAUDIENCEID = SRC.RAWAUDIENCEID")
        deletesp.newline("\t\t\tAND TAR.MERGEDELETEFLAG = 'false';")

        deletesp.newline(f"\tRETURN 'FINISHED CALLING STORED PROCEDURE sp_Delete{table_name.upper()}OrphansFromRawAudience';")
        deletesp.newline("\tEND;")
        deletesp.newline("$$;")

        # define output folder and filename
        filename = f"sp_delete{table_name.lower()}orphansfromrawaudience.sql"
        output_folder = f"{db_folder}data_repo{os.sep}stage{os.sep}"
        filewrite(folder=output_folder, filename=filename, content=deletesp.out())

        # write output repo files if repo_root_folder is not empty
        if repo_root_folder != "":
            datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{self.source_name.lower()}{os.sep}stage{os.sep}{client.upper()}{os.sep}"
            filewrite(folder=datarepo_folder, filename=filename, content=deletesp.out())

        # trace log
        print_section_detail(msg=f"DELETE ORPHANS - {filename}\nCreated in: {output_folder}", runlog=runlog)

        return delete_sp_name

    # Create rawaudience sources file
    def rawaudience_sources(self, table_name: str, db_folder: str, runlog: object, repo_root_folder:str, client:str):

        ra_src = {}
        ra_src["name"] = f"{table_name.upper()}RawAudience"
        ra_src["createHistoryIndicator"] = None
        ra_src["deletesIndicator"] = None
        ra_src["deleteFromSourceSql"] = f"CALL STAGE.sp_Delete{table_name.upper()}OrphansFromRawAudience()"
        ra_src["destinationTable"] = None
        ra_src["destinationTableUnique"] = None
        ra_src["importSql"] = None
        ra_src["isStandardizationSource"] = None
        ra_src["mergeDestinationTable"] = None
        ra_src["mergeToStageSql"] = f"CALL STAGE.sp_Merge{table_name.upper()}IntoRawAudience()"
        ra_src["rawaudienceIndicator"] = None
        ra_src["rowCountCheckOverride"] = None
        ra_src["truncateLoadDestinationTable"] = None
        ra_src["uniqueTableCreateSql"] = None
        ra_src["historyTableCreateSql"] = None

        # define output folder and filename
        filename = f"{table_name.lower()}rawaudience.json"

        # output JSON
        writeJSON(filecontent=ra_src, filename=filename, filetype="sources", client=client, source_name="rawaudience", db_folder=db_folder, repo_root_folder=repo_root_folder, runlog=runlog)
        return
