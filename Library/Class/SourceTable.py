from Library.FunctionFiles.Functions import *
import pandas as pd

class SourceTable:
    def __init__(self, workbook:str, worksheet:str, runlog:object):
        self.runlog = runlog
        try:
            self.worksheet = pd.read_excel(workbook, sheet_name=worksheet)
        except:
            raise Exception(f"ERROR: {worksheet} not found. Moving on to next table.")

        self.tableinfo_init()
        return

    def tableinfo_init(self):
        # initialize variables
        self.TableInfo = {}

        TableInfoArray = self.worksheet[["TableInfo", "InfoValue"]].dropna(how='all').to_numpy()

        for infoitem in TableInfoArray:
            self.TableInfo[infoitem[0]] = infoitem[1]

        return self.TableInfo

    def tableinfo(self):
        return self.TableInfo

    def table_name(self):
        # store table info in variables
        # TableName. Exit loop if TableName not found or if it is empty.
        try:
            TableName = str(self.TableInfo["TableName"]).strip()

            if TableName == "nan":
                # raise Exception so it tries to get the SnowflakeTableName
                raise Exception
            
            self.runlog.log(f"TableName = {TableName}")
        except:
            try:
                TableName = str(self.TableInfo["SnowflakeTableName"]).strip()
                self.runlog.log(f"SnowflakeTableName = {TableName}")
            except:
                self.runlog.log(f"ERROR: TableName or SnowflakeTableName not found in TableInfo section.")
                self.runlog.log(f"Exiting config creation for {self.worksheet}.")
                self.runlog.log("")
                TableName = "nan"
                raise Exception

        if TableName == "nan":
            self.runlog.log(f'ERROR: TableName or SnowflakeTableName empty or set to "nan" in TableInfo section.')
            self.runlog.log(f"Exiting config creation for {self.worksheet}.")
            raise Exception

        return TableName

    def filereceiptcheck(self):
        # FileReceiptCheck
        try:
            FileReceiptCheck = validate(input_val=str(self.TableInfo["FileReceiptCheck"]).strip().replace("nan", "0"),values=[0,1])
        except:
            self.runlog.log("WARNING: FileReceiptCheck not found in TableInfo section. Defaulting to 0.")
            self.runlog.log("")
            FileReceiptCheck = 0

        return FileReceiptCheck

    def threshold(self):
        # Threshold
        try:
            Threshold = validate(input_val=str(self.TableInfo["Threshold"]).strip().replace("nan", "0"),values=["int"])
        except:
            self.runlog.log("Threshold not found in TableInfo section. Defaulting to 0.")
            self.runlog.log("")
            Threshold = 0

        return Threshold

    def standardization_ind(self):
        # StandardizationIndicator
        try:
            StandardizationIndicator = validate(input_val=str(self.TableInfo["StandardizationIndicator"]).strip().replace("nan", "0"),values=[0,1])
        except:
            self.runlog.log("WARNING: StandardizationIndicator not found in TableInfo section. Defaulting to 0.")
            self.runlog.log("")
            StandardizationIndicator = 0

        return StandardizationIndicator

    def standardization_sheet(self):
        StandardizationSheet = ""
        try:
            StandardizationSheet = str(self.TableInfo["StandardizationSheet"]).strip().replace("nan", "0")
        except:
            StandardizationSheet = str(self.table_name()) + "_STANDARDIZATION"
            self.runlog.log(f"WARNING: StandardizationSheet not found in TableInfo section. Assuming {StandardizationSheet}.")
            self.runlog.log("")

        return StandardizationSheet

    def rawaudience_ind(self):
        # RawAudienceIndicator
        try:
            RawAudienceIndicator = validate(input_val=str(self.TableInfo["RawAudienceIndicator"]).strip().replace("nan", "0"),values=[0,1])
        except:
            self.runlog.log("WARNING: RawAudienceIndicator not found in TableInfo section. Defaulting to 0.")
            self.runlog.log("")
            RawAudienceIndicator = 0

        return RawAudienceIndicator

    def rawaudience_sheet(self):
        RawAudienceSheet = ""
        try:
            RawAudienceSheet = str(self.TableInfo["RawAudienceSheet"]).strip().replace("nan", "0")
        except:
            RawAudienceSheet = str(self.table_name()) + "_RAWAUDIENCE"
            self.runlog.log(f"WARNING: RawAudienceSheet not found in TableInfo section. Assuming {RawAudienceSheet}.")
            self.runlog.log("")

        return RawAudienceSheet

    def sourcedate_ind(self):
        # SourceDateIndicator
        try:
            SourceDateIndicator = str(self.TableInfo["SourceDateIndicator"]).strip().upper().replace("NAN", "")
        except:
            try:
                SourceDateIndicator = str(self.TableInfo["SourceDate"]).upper().replace("NAN", "")
            except:
                self.runlog.log(f"ERROR: SourceDateIndicator not found.")
                self.runlog.log("")
                SourceDateIndicator = ""

        return SourceDateIndicator

    def filesuffixmap(self):
        # FileSuffixMap. Exit loop if not found or empty.
        try:
            FileSuffixMap = str(self.TableInfo["FileSuffixMap"]).strip()
        except:
            self.runlog.log(f"ERROR: FileSuffixMap not found in TableInfo section. Exiting config creation for {self.worksheet}")
            self.runlog.log("")
            raise Exception

        if FileSuffixMap == "nan":
            self.runlog.log(f'ERROR: FileSuffixMap empty or set to "nan" in TableInfo section.')
            self.runlog.log(f"Exiting config creation for {self.worksheet}.")
            raise Exception

        return FileSuffixMap

    def filematchtext(self):
        # FileMatchText. Exit loop if not found or empty.
        try:
            FileMatchText = str(self.TableInfo["FileMatchText"]).strip()
        except:
            self.runlog.log(f"ERROR: FileMatchText not found in TableInfo section. Exiting config creation for {self.worksheet}")
            self.runlog.log("")
            raise Exception

        if FileMatchText == "nan":
            self.runlog.log(f'ERROR: FileMatchText empty or set to "nan" in TableInfo section.')
            self.runlog.log(f"Exiting config creation for {self.worksheet}.")
            raise Exception

        return FileMatchText

    def create_keyhash(self):
        # Create Keyhash indicator
        try:
            CreateKeyhash = validate(input_val=str(self.TableInfo["CreateKeyhash"]).strip().replace("nan", "0"),values=[0,1])
            self.runlog.log(f"CreateKeyhash = {CreateKeyhash} for {self.table_name()}")
        except:
            try:
                CreateKeyhash = validate(input_val=str(self.TableInfo["CreateKeyHash"]).replace("nan", "0"),values=[0,1])
                self.runlog.log(f"CreateKeyhash = {CreateKeyhash} for {self.table_name()}")
            except:
                self.runlog.log("WARNING: CreateKeyhash not found in TableInfo section. Defaulting to 0.")
                self.runlog.log("")
                CreateKeyhash = 0
                raise Exception

        if CreateKeyhash == "1":
            pk = self.primary_keys()
            keyhash = "SHA2("
            for key in pk:
                keyhash += f"IFNULL(TO_CHAR({key}), '') || '-' ||"
            keyhash = keyhash[:-10]
            keyhash += ", 512) AS KEYHASH"
        else:
            keyhash = ""

        return CreateKeyhash, keyhash

    def columns(self):
        self.columnsArray = self.worksheet[["SourceColumnName", "ColumnName", "DataType"]].dropna(how='all').to_numpy()
        colitemArray = []
        colidx = 1
        for col in self.columnsArray:
            try:
                colitemArray.append([col[0],col[1].replace(" ","").strip(),col[2]])
            except Exception as e:
                raise Exception(f"Column {colidx} (Row {colidx+1} in DD) needs attention")
            colidx += 1
        self.columnsArray = colitemArray
        # .to_numpy()
        return self.columnsArray

    def primary_keys(self):
        try:
            pk_list = qlookup(df=self.worksheet, lookup_col="PrimaryKey", return_col="ColumnName", runlog=self.runlog)
        except Exception as e:
            self.runlog.log(f"ERROR: {e}")
        return pk_list

    def primary_keys_string(self):
        pk_columns = self.primary_keys()

        # generate concatenated Primary Key columns string
        primary_keys = ""
        for pk in pk_columns:
            primary_keys += f"{str(pk.strip()).upper()},"

        # strip out command new line character from last row
        primary_keys = primary_keys[:-1]

        # create primary key string for use in Stage DDL
        return primary_keys, f"PRIMARY KEY ({primary_keys})"

    def old_columns(self):
        old_cols=[]
        new_cols = self.new_columns()
        all_cols = self.worksheet["ColumnName"].dropna(how='all').tolist()
        for col in all_cols:
            if col not in new_cols:
                old_cols.append(col)

        return old_cols

    def new_columns(self):
        return qlookup(df=self.worksheet, lookup_col="IsNew", return_col="ColumnName", runlog=self.runlog)

    def check_schema_drift(self):
        try:
            newcols = self.new_columns()
            oldcols = []
            if len(newcols) > 0:
                oldcols = self.old_columns()
                schemadrift = 1
            else:
                schemadrift = 0
        except Exception as e:
            raise Exception(e)

        return [schemadrift,oldcols]

    def phone_columns(self):
        phone_col_return = []

        try:
            phone_col_list = qlookup(df=self.worksheet, lookup_col="IsPhone", return_col="ColumnName", runlog=self.runlog)
            phone_col_return = [p.upper() for p in phone_col_list]
        except Exception as e:
            self.runlog.log(f"WARNING: IsPhone column not found ")

        return phone_col_return

    def dlp_columns(self):
        dlp_col_return = []

        try:
            dlp_col_list = qlookup(df=self.worksheet, lookup_col="IsDLP", return_col="ColumnName", runlog=self.runlog)
            dlp_col_return = [p.upper() for p in dlp_col_list]
        except Exception as e:
            self.runlog.log(f"WARNING: IsDLP column not found ")

        return dlp_col_return

    def email_columns(self):
        email_col_return = []

        try:
            email_col_list = qlookup(df=self.worksheet, lookup_col="IsEmail", return_col="ColumnName", runlog=self.runlog)
            email_col_return = [e.upper() for e in email_col_list]
        except Exception as e:
            self.runlog.log(f"WARNING: IsEmail column not found.")

        return email_col_return

    def salesforce_object_name(self):
        # Salesforce Object Name. Exit loop if not found or empty.
        try:
            SalesforceObjectName = str(self.TableInfo["SalesforceObjectName"]).strip()
        except:
            SalesforceObjectName = "<fill in Salesforce Object Name>"
            self.runlog.log(f"WARNING: SalesforceObjectName not found in TableInfo section. Using default value.")
            self.runlog.log("")

        if SalesforceObjectName == "nan":
            SalesforceObjectName = "<fill in Salesforce Object Name>"
            self.runlog.log(f"WARNING: SalesforceObjectName not found in TableInfo section. Using default value.")
            self.runlog.log("")

        return SalesforceObjectName

    def dynamics_entity_name(self):
        # Dynamics Entity Name. Exit loop if not found or empty.
        try:
            DynamicsEntityName = str(self.TableInfo["DynamicsEntityName"]).strip()
        except:
            DynamicsEntityName = "<fill in Dynamics Entity Name>"
            self.runlog.log(f"WARNING: DynamicsEntityName not found in TableInfo section. Using default value.")
            self.runlog.log("")

        if DynamicsEntityName == "nan":
            DynamicsEntityName = "<fill in Dynamics Entity Name>"
            self.runlog.log(f'WARNING: DynamicsEntityName not found in TableInfo section. Using default value.')
            self.runlog.log("")

        return DynamicsEntityName

    def pk_case_sensitive(self):
        # PKCaseSensitive. Exit loop if not found or empty.
        try:
            PKCaseSensitive = str(self.TableInfo["PKCaseSensitive"]).strip()
            if PKCaseSensitive.upper() == "Y" or PKCaseSensitive == "1":
                return True
            else:
                return False
        except:
            self.runlog.log(f"WARNING: PKCaseSensitive not found in TableInfo section. Assuming False.")
            self.runlog.log("")

        return
