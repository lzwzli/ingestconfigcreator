import pandas as pd
from Library.FunctionFiles.Functions import *

class StdSheet:
    def __init__(self, workbook:str, worksheet:str, bus_rule_obj:object, runlog:object, db_folder:str, platform:str= "Snaplogic"):
        self.runlog = runlog
        self.busrule_obj = bus_rule_obj
        self.ddfile = workbook
        self.db_folder = db_folder

        self.RuleNameKey = "ruleName"
        self.RunOrderKey = "runOrder"
        self.RunPositionKey = "runPosition"
        self.RuleQueryKey = "ruleQuery"

        if platform == "Snaplogic":
            self.RuleNameKey = self.RuleNameKey.upper()
            self.RunOrderKey = self.RunOrderKey.upper()
            self.RunPositionKey = self.RunPositionKey.upper()
            self.RuleQueryKey = self.RuleQueryKey.upper()

        # store original value
        worksheet_ori = worksheet

        try:
            self.worksheet = pd.read_excel(workbook, sheet_name=worksheet)
        except:
            try:
                worksheet = worksheet.replace("STANDARDIZAION", "Standardization")
                self.worksheet = pd.read_excel(workbook, sheet_name=worksheet)
            except:
                try:
                    worksheet = worksheet.replace("Standardization", "standardization")
                    self.worksheet = pd.read_excel(workbook, sheet_name=worksheet)
                except:
                    raise Exception(f"ERROR: {worksheet_ori} not found. Attempts at other variations also failed. Moving on to next table.")

        # get info key value pairs
        # initialize Info dictionary
        self.Info = {}

        InfoArray = self.worksheet[["InfoKey", "InfoValue"]].dropna(how='all').to_numpy()
        for item in InfoArray:
            self.Info[item[0]] = item[1]
        return

    # get import table value
    def import_table(self):
        ImportTableName = str(self.Info["ImportTableName"]).strip()

        return ImportTableName

    # get stage table value
    def stage_table(self):
        StageTableName = str(self.Info ["StageTableName"]).strip()

        return StageTableName

    # get JoinTable values
    def join_tables(self):
        JoinTableList = []
        JoinKeys = ["B","C","D"]
        for key in JoinKeys:
            try:
                JoinTable = self.Info[f"JoinTable{key}"]
                JoinTableName, JoinTableCondition = JoinTable.split(",")
                JoinTableList.append([key,1,JoinTableName.strip(),JoinTableCondition.strip()])
            except:
                JoinTableList.append([key,0,"",""])

        return JoinTableList

    # get list of standardization fields
    def fields(self):
        fieldsarray = self.worksheet[["Field", "PrimaryField", "SecondaryField", "TertiaryField"]].to_numpy()

        return fieldsarray

    # helper function to check for nan and wrap it with ifnull
    def checknan(self, input:str):
        if input != "nan":
            # if input value has a dot, assume its intentional. Use value as is
            if "." in input:
                col = f"IFNULL(TRIM({input}),'')"
            # otherwise, append with main import table alias A
            else:
                col = f"IFNULL(TRIM(A.{input}),'')"
        else:
            col = f"''"

        return col

    # helper function to check for nan and wrap it with nullif
    def checknan_nullif(self, input:str):
        if input != "nan":
            # if input value has a dot, assume its intentional. Use value as is
            if "." in input:
                col = f"(NULLIF({input},'')"
            # otherwise, append with main import table alias A
            else:
                col = f"NULLIF(A.{input},'')"
        else:
            col = f"NULL"

        return col

    # generate column list
    def columns_string(self):
        fldarr = self.fields()
        select_columns = ""
        fullname = ""
        join_columns = ""
        rownum_columns = "row_number() over (partition by "
        build_fullname = True
        has_fullname_exp = False
        for fld in fldarr:
            # initialize column variable
            col = ''
            # store value of primary column
            col1 = self.checknan_nullif(str(fld[1]))
            # store value of secondary column
            col2 = self.checknan_nullif(str(fld[2]))
            # store value of tertiary column
            col3 = self.checknan_nullif(str(fld[3]))
            # build coalesce query based on column data availability
            # all 3 columns have values
            if col1 != 'NULL' and col2 != 'NULL' and col3 != 'NULL':
                col = f"COALESCE({col1},{col2},{col3},'')"
            # only primary and secondary have values
            elif col1 != 'NULL' and col2 != 'NULL' and col3 == 'NULL':
                col = f"COALESCE({col1},{col2},'')"
            # only primary have values
            elif col1 != 'NULL' and col2 == 'NULL' and col3 == 'NULL':
                col = self.checknan(str(fld[1]))
            # no columns have values
            else:
                col = "''"

            # map columns to column names
            if fld[0] == "RAWEMAIL":
                select_columns += f"\n\t\t{col} as \"EmailAddress\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWPREFIX":
                select_columns += f"\n\t\t{col} as \"RawPrefix\", "
            elif fld[0] == "RAWFULLNAME" and col != "''":
                if has_fullname_exp is False:
                    select_columns += f"\n\t\t{col} as \"FullName\", "
                    rownum_columns += f"\n\t\t\tLOWER({col}),"
                    build_fullname = False
            elif fld[0] == "RAWFIRSTNAME":
                select_columns += f"\n\t\t{col} as \"RawFirstName\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
                if build_fullname:
                    fullname += f"{col} || "
            elif fld[0] == "RAWMIDDLENAME":
                select_columns += f"\n\t\t{col} as \"RawMiddleName\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
                if build_fullname:
                    if col == "''":
                        fullname += "' '"
                    else:
                        fullname += f"IFNULL(NULLIF(' ' || {col} || ' ','  '),' ')"
            elif fld[0] == "RAWLASTNAME":
                select_columns += f"\n\t\t{col} as \"RawLastName\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"

                if build_fullname:
                    #full name
                    fullname += f" || {col}"
                    fullname_clause = f"IFNULL({fullname},'')"
                    select_columns += f"\n\t\t{fullname_clause} as \"FullName\", "
                    rownum_columns += f"\n\t\t\tLOWER({fullname_clause}),"
                    has_fullname_exp = True

            elif fld[0] == "RAWSUFFIX":
                select_columns += f"\n\t\t{col} as \"RawSuffix\", "
            elif fld[0] == "RAWCOMPANY":
                select_columns += f"\n\t\t{col} as \"CompanyName\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWADDRESS1":
                select_columns += f"\n\t\t{col} as \"AddressLine1\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWADDRESS2":
                select_columns += f"\n\t\t{col} as \"AddressLine2\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWADDRESS3":
                select_columns += f"\n\t\t{col} as \"AddressLine3\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWCITY":
                select_columns += f"\n\t\t{col} as \"City\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWSTATE":
                select_columns += f"\n\t\t{col} as \"State\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWZIP":
                select_columns += f"\n\t\t{col} as \"PostalCode\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWCOUNTRY":
                select_columns += f"\n\t\t{col} as \"Country\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"
            elif fld[0] == "RAWPHONE":
                select_columns += f"\n\t\t{col} as \"PhoneNumber\", "
                rownum_columns += f"\n\t\t\tLOWER({col}),"


            # build join columns
            if str(fld[0]) != "nan":
                if str(fld[0])=="RAWFULLNAME" and build_fullname:
                    join_columns += f"TRIM(LOWER({fullname_clause})) = TRIM(LOWER(IFNULL(TRIM(std.{fld[0]}),''))) \n\t\tAND "
                else:
                    join_columns += f"LOWER({col}) = LOWER(IFNULL(TRIM(std.{fld[0]}),'')) \n\t\tAND "

        join_columns = join_columns[:-8]
        rownum_columns = rownum_columns[:-1]

        rownum_columns += "\n\t\torder by 1 desc) rownumber"

        return select_columns, join_columns, rownum_columns

    # create standardization query for sources file
    def std_query(self):
        # instantiate standardization query document
        queryDoc = Document()

        col_select=["RecordID", "EmailAddress", "RawPrefix", "RawFirstName", "RawMiddleName", "RawLastName", "FullName", "RawSuffix", "CompanyName", "AddressLine1", "AddressLine2", "AddressLine3", "City", "State", "PostalCode", "Country", "PhoneNumber", "StandardizationDate"]
        # get columns string for select, joins and rownum
        select_cols, join_cols, rownum_cols = self.columns_string()

        # provide std columns to bus rules for purpose of std fakeout rules
        self.busrule_obj.set_std_cols(select_columns=select_cols, join_columns=join_cols, rownum_columns=rownum_cols)

        # if "RawFullName" in select_cols:
        #     col_select = ["RecordID", "EmailAddress", "RawPrefix", "FullName", "RawFirstName", "RawMiddleName", "RawLastName", "RawSuffix", "CompanyName", "AddressLine1", "AddressLine2", "AddressLine3", "City", "State", "PostalCode", "Country", "PhoneNumber", "StandardizationDate"]

        # get join tables
        join_tables = self.join_tables()
        self.join_clause = ""
        self.join_count = 0
        for table in join_tables:
            if table[1] == 1:
                self.join_clause += f"\tLEFT JOIN {table[2]} {table[0]} ON \n\t\t{table[3]}\n"
                self.join_count += 1

        # start building query document
        queryDoc.append("SELECT")
        queryDoc.newline("\tRoute,")

        # add select columns
        for col in col_select:
            queryDoc.newline(f"\t\"{col}\",")

        # remove trailing comma
        queryDoc.trimend(1)

        queryDoc.newline("FROM")
        queryDoc.newline("(")
        queryDoc.newline("\tSELECT")
        queryDoc.newline("\t\tABS((random() % 5)) Route,")
        queryDoc.newline("\t\tto_char(current_timestamp(),'YYYYMMDDHHMISSFF3') || cast(row_number() over (partition by 1 order by 1) as string) as \"RecordID\",")
        queryDoc.append(f"{select_cols}")
        queryDoc.newline("\t\tto_char(current_timestamp(),'YYYY-MM-DD HH24:MI:SS.FF3') as \"StandardizationDate\", ")
        queryDoc.newline(f"\t\t{rownum_cols}")
        queryDoc.newline(f"\tFROM IMPORT.{str(self.import_table())} A")

        # if there are join tables, add join clause
        if self.join_count > 0:
            queryDoc.newline(self.join_clause)
            queryDoc.trimend(1)

        queryDoc.newline("\tLEFT JOIN STAGE.STANDARDIZATION std ON ")
        queryDoc.newline(f"\t\t{join_cols}")
        queryDoc.newline("\tWHERE std.RAWFIRSTNAME IS NULL")
        queryDoc.newline(") sub")
        queryDoc.newline("WHERE sub.rownumber = 1 &limitCode;")

        return queryDoc

    # create query for standardization business rule
    def busrule_query(self):
        table = str(self.import_table())
        tablename_clean = table.replace("vw_","").upper()
        select_cols, join_cols, rownum_cols = self.columns_string()
        output_folder = f"{self.db_folder}ForReferenceOnly{os.sep}{tablename_clean}_BusRules{os.sep}"

        # instantiate business rule query document
        queryDoc = Document()

        queryDoc.append(f"CREATE OR REPLACE TABLE TMP.{table}melissa AS")
        queryDoc.newline(f"SELECT A.*, IFNULL(std.standardizationrowid,0) standardizationrowid")
        queryDoc.newline(f"FROM IMPORT.{table} A")

        # if there are join tables, add join clause
        if self.join_count > 0:
            queryDoc.newline(self.join_clause)
            queryDoc.trimend(1)

        queryDoc.newline(f"LEFT JOIN STAGE.STANDARDIZATION std ON ")
        queryDoc.newline(join_cols)
        queryDoc.newline(";")

        # set output string function to not trim double space
        trimdoublespace = 0

        # write out Rule Query to file
        filewrite(folder=output_folder, filename=f"{tablename_clean}_1_1 CREATE TMP MELISSA RULE QUERY.sql", content=queryDoc.out())

        return queryDoc.out_str(trimdoublespace)

    # create standardization business rule
    def create_std_busrule(self):
        table = str(self.import_table())
        rulename = table.replace("vw_","")
        StdBusRule = {}
        StdBusRule[self.RuleNameKey] = f"{rulename}_1_1"
        StdBusRule[self.RunOrderKey] = 1
        StdBusRule[self.RunPositionKey] = 1
        StdBusRule[self.RuleQueryKey] = self.busrule_query()

        # add to business rule object
        self.busrule_obj.add_rule(StdBusRule)

        return
