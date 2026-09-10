from Library.FunctionFiles.BasicFunctions import *

# ----------------------------------------------------------------
# get column array
# ----------------------------------------------------------------
def getDDLcolumns(col_list:list, ddl_type:str, phone_col_list:list=[], email_col_list:list=[]):
    collist = []
    if ddl_type == "import":
        for row in col_list:
            if str(row[2]).upper() == "VARIANT":
                collist.append(f"\t{str(row[1]).upper()}\tVARIANT")
            else:
                collist.append(f"\t{str(row[1]).upper()}\tVARCHAR(16777216)")
    elif ddl_type == "stage":
        for row in col_list:
            collist.append(f"\t{str(row[1]).upper()}\t{str(row[2])}")
            # this part was added with the intention of adding comments for phone and email columns. Commenting it out temporarily until proper decision on how to tag PII is had
            # if row[1].upper() in phone_col_list:
            #     collist.append(f"\t{str(row[1]).upper()}\t{str(row[2])}")
            # elif row[1].upper() in email_col_list:
            #     collist.append(f"\t{str(row[1]).upper()}\t{str(row[2])}")
            # else:
            #     collist.append(f"\t{str(row[1]).upper()}\t{str(row[2])}")
    else:
        raise Exception(f"ERROR: DDLtype not valid. Only \"import\" or \"stage\" allowed.")
    return collist

# ----------------------------------------------------------------
# create phone formatter business rule
# ----------------------------------------------------------------
def create_phone_formatter_busrule(table_name:str, pk_list:list, phone_cols:list, platform:str = "Prefect", import_view_name:str=""):
    if len(import_view_name)>0:
        import_table_name = import_view_name
    else:
        import_table_name = table_name

    PFQuery = ""
    PFBusRule = {}

    RuleNameKey = "ruleName"
    RunOrderKey = "runOrder"
    RunPositionKey = "runPosition"
    RuleQueryKey = "ruleQuery"

    if platform == "Snaplogic":
        RuleNameKey = RuleNameKey.upper()
        RunOrderKey = RunOrderKey.upper()
        RunPositionKey = RunPositionKey.upper()
        RuleQueryKey = RuleQueryKey.upper()

    runorder = 1
    if "ARCHTICS" in table_name.upper():
        runorder = 3

    PFBusRule[RuleNameKey] = f"{table_name}_1_4"
    PFBusRule[RunOrderKey] = runorder
    PFBusRule[RunPositionKey] = 4

    # set phone columns
    ph_set_query = ""
    ph_from_query = ""
    for ph in phone_cols:
        ph_set_query += f" dest.{ph}formatted = sor.{ph}formatted,"
        ph_from_query += f" public.fn_phoneformatter(stg.{ph}) as {ph}formatted,"

    # trim last comma
    ph_set_query = ph_set_query[:-1]
    ph_from_query = ph_from_query[:-1]

    # set primary keys
    pk_string = ""
    pk_join = ""
    pk_sor_where = ""
    pk_set_where = ""
    for pk in pk_list:
        pk_string += f" stg.{pk},"
        pk_join += f" stg.{pk} = imp.{pk} AND "
        pk_sor_where += f" imp.{pk} is not null AND "
        pk_set_where += f" dest.{pk} = sor.{pk} AND "

    # trim trailing characters
    pk_string = pk_string[:-1]
    pk_join = pk_join[:-5]
    pk_sor_where = pk_sor_where[:-5]
    pk_set_where = pk_set_where[:-5]

    PFQuery += f"UPDATE stage.{table_name} dest"
    PFQuery += f" SET"
    PFQuery += ph_set_query
    PFQuery += " FROM (SELECT DISTINCT"
    PFQuery += f"{pk_string}, "
    PFQuery += ph_from_query
    PFQuery += " FROM"
    PFQuery += f" stage.{table_name} stg"
    PFQuery += f" LEFT JOIN"
    PFQuery += f" import.{import_table_name} imp"
    PFQuery += f" ON{pk_join}"
    PFQuery += f" WHERE"
    PFQuery += pk_sor_where
    PFQuery += ") sor"
    PFQuery += " WHERE"
    PFQuery += pk_set_where
    PFQuery += ";"

    PFBusRule[RuleQueryKey] = PFQuery

    return PFBusRule

# ----------------------------------------------------------------
# create keyhash work table business rule
# ----------------------------------------------------------------
def create_keyhash_worktable_busrule(table_name:str, keyhash:str, runlog:object, platform:str = "Prefect"):
    runlog.log(f"Create keyhash table for {table_name}")

    RuleNameKey = "ruleName"
    RunOrderKey = "runOrder"
    RunPositionKey = "runPosition"
    RuleQueryKey = "ruleQuery"

    if platform == "Snaplogic":
        RuleNameKey = RuleNameKey.upper()
        RunOrderKey = RunOrderKey.upper()
        RunPositionKey = RunPositionKey.upper()
        RuleQueryKey = RuleQueryKey.upper()

    WTQuery = ""
    WTBusRule = {}

    WTBusRule[RuleNameKey] = f"{table_name}_1_1"
    WTBusRule[RunOrderKey] = 1
    WTBusRule[RunPositionKey] = 1

    WTQuery += f"CREATE OR REPLACE TABLE TMP.{table_name.upper()}_KEYHASH AS "
    WTQuery += f"SELECT *, {keyhash} "
    WTQuery += f"FROM IMPORT.{table_name.upper()}"

    WTBusRule[RuleQueryKey] = WTQuery

    return WTBusRule

# ----------------------------------------------------------------
# Create Import Raw ddl
# ----------------------------------------------------------------
def create_importraw_DDL(table_name:str, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str):
    # initialize Import Raw DDL document
    ImportRawDDL = Document()

    # create table_name_raw
    table_name_raw = f"{table_name.lower()}_raw"

    # create import Raw DDL per table
    ImportRawDDL.append(f"/*{table_name_raw} (Import) grantObjectName={table_name_raw} version={version} generated by config generator */")
    ImportRawDDL.newline(f"CREATE TABLE IF NOT EXISTS import.{table_name_raw}")
    ImportRawDDL.newline("(")
    ImportRawDDL.newline("\tFILEDATE VARCHAR NOT NULL,")
    ImportRawDDL.newline("\tFILENAME VARCHAR NOT NULL,")
    ImportRawDDL.newline("\tFILEROWNUMBER VARCHAR NOT NULL,")
    ImportRawDDL.newline("\tJSONDATA VARIANT,")
    ImportRawDDL.newline("\tDW_CREATED_DATE TIMESTAMP_LTZ NOT NULL DEFAULT CURRENT_TIMESTAMP(),")
    ImportRawDDL.newline("\tDW_CREATED_BY VARCHAR(100) NOT NULL DEFAULT CURRENT_USER()")
    ImportRawDDL.newline(");")

    # define output folder and filename
    filename = f"{table_name.lower()}_raw.sql"

    output_folder = f"{db_folder}data_repo{os.sep}import{os.sep}"

    # write import DDL to file
    filewrite(folder=output_folder, filename=filename, content=ImportRawDDL.out())
    print_section_detail(msg=f"IMPORT RAW DDL - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}import{os.sep}{client.upper()}{os.sep}"

        # write import DDL to file
        filewrite(folder=datarepo_folder, filename=filename, content=ImportRawDDL.out())
        print_section_detail(msg=f"IMPORT RAW DDL - {filename}\nCreated in: {datarepo_folder}", runlog=runlog)

    return table_name_raw

# ----------------------------------------------------------------
# Create Import DDL
# ----------------------------------------------------------------
def create_import_DDL(table_name:str, col_list:list, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str):
    # initialize Import DDL Document
    ImportDDL = Document()

    # IMPORT - read column list and create column list for table creation
    importcolumns = getDDLcolumns(col_list=col_list, ddl_type="import")

    # create complete import DDL per table
    ImportDDL.append(f"/*{table_name} (Import) grantObjectName={table_name} version={version} generated by config generator */")
    ImportDDL.newline(f"CREATE OR REPLACE TABLE IMPORT.{table_name}")
    ImportDDL.newline("(")
    ImportDDL.newline("\tFILEDATE\tVARCHAR(16777216),")
    ImportDDL.newline("\tFILENAME\tVARCHAR(16777216),")
    ImportDDL.newline("\tFILEROWNUMBER\tNUMBER(38, 0),")
    ImportDDL.newlinelist(importcolumns)
    ImportDDL.newline(");")

    # define output folder and filename
    filename = f"{table_name}.sql"
    output_folder = f"{db_folder}data_repo{os.sep}import{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=ImportDDL.out())
    print_section_detail(msg=f"IMPORT DDL - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}import{os.sep}{client.upper()}{os.sep}"
        filewrite(folder=datarepo_folder, filename=filename, content=ImportDDL.out())
        print_section_detail(msg=f"IMPORT DDL - {filename}\nCreated in: {datarepo_folder}", runlog=runlog)

    return

# ----------------------------------------------------------------
# Create Stage DDL
# ----------------------------------------------------------------
def create_stage_DDL(table_name:str, col_list:list, pk_str:str, phone_col_list:list, std_ind:int, rawaud_ind:int, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str, email_col_list:list=[], omit_file_cols:bool=False, create_archive_tables:list=[]):
    indent = " " * 3

    # STAGE - read column list and datatype and create column list for table creation
    stagecolumns = getDDLcolumns(col_list=col_list, ddl_type="stage", phone_col_list=phone_col_list, email_col_list=email_col_list)

    # add phone columns to stage column list suffixed with "formatted"
    if rawaud_ind == "1" and len(phone_col_list) > 0:
        runlog.log(f"Phone columns count = {len(phone_col_list)}")
        runlog.log(f"{indent}Adding phone columns")
        for phone_cols_key in phone_col_list:
            stagecolumns.append(f"\t{phone_cols_key.upper()}formatted\tVARCHAR")
    elif rawaud_ind != "1" and len(phone_col_list) > 0:
        runlog.log("Phone columns found, but not creating them as RawAudienceIndicator = 0")

    # if standardizationindicator is true, add standardizationrowid column
    if std_ind == "1":
        stagecolumns.append("\tSTANDARDIZATIONROWID\tNUMBER(38,0)")

    # if rawaudienceindicator is true, add rawaudienceid column
    if rawaud_ind == "1":
        stagecolumns.append("\tRAWAUDIENCEID\tNUMBER(38,0)")

    # add dwinsert and update date columns
    stagecolumns.append("\tDWINSERTDATE\tTIMESTAMP_LTZ(9)")
    stagecolumns.append("\tDWUPDATEDATE\tTIMESTAMP_LTZ(9)")

    # initialize Stage DDL document
    StageDDL = Document()

    # create complete import DDL per table
    StageDDL.append(f"/*{table_name} (Stage) grantObjectName={table_name} version={version} generated by config generator */")
    StageDDL.newline(f"CREATE TABLE IF NOT EXISTS STAGE.{table_name.upper()}")
    StageDDL.newline("(")
    if omit_file_cols is False:
        StageDDL.newline("\tFILEDATE\tVARCHAR(16777216),")
        StageDDL.newline("\tFILENAME\tVARCHAR(16777216),")
        StageDDL.newline("\tFILEROWNUMBER\tNUMBER(38, 0),")

    # add KEYHASH column if primary key contains KEYHASH
    if "KEYHASH" in pk_str:
        StageDDL.newline("\tKEYHASH\tVARCHAR(16777216),")

    StageDDL.newlinelist(stagecolumns)

    if pk_str != "PRIMARY KEY ()":
        StageDDL.append(",")
        StageDDL.newline(f"\t{pk_str}")
    StageDDL.newline(");")

    # define output folder and filename
    filename = f"{table_name}.sql"
    output_folder = f"{db_folder}data_repo{os.sep}stage{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=StageDDL.out())
    print_section_detail(msg=f"STAGE DDL - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # create archive table if create_archive is True
    StageArchiveDDL = ""
    if table_name.lower() in create_archive_tables or table_name.upper() in create_archive_tables:
        filename_archive = f"{table_name}archive.sql"
        StageArchiveDDL = StageDDL.out().replace(f"STAGE.{table_name.upper()}", f"STAGE.{table_name.upper()}ARCHIVE")

        # get index of Primary Key string
        pkchar_start_idx = StageArchiveDDL.index("PRIMARY KEY")

        # remove Primary Key definition. Have a -3 to also trim the comma and new line
        StageArchiveDDL = StageArchiveDDL[:pkchar_start_idx-3]+"\n);"

        filewrite(folder=output_folder, filename=filename_archive, content=StageArchiveDDL)
        print_section_detail(msg=f"STAGE ARCHIVE DDL - {filename_archive}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}stage{os.sep}{client.upper()}{os.sep}"
        filewrite(folder=datarepo_folder, filename=filename, content=StageDDL.out())
        print_section_detail(msg=f"STAGE DDL - {filename}\nCreated in: {datarepo_folder}", runlog=runlog)

        # create archive table if create_archive is True
        if table_name.lower() in create_archive_tables or table_name.upper() in create_archive_tables:
            filewrite(folder=datarepo_folder, filename=filename_archive, content=StageArchiveDDL)
            print_section_detail(msg=f"STAGE ARCHIVE DDL - {filename_archive}\nCreated in: {datarepo_folder}", runlog=runlog)

    # return StageDDL
    return StageDDL.out(), StageArchiveDDL

# ----------------------------------------------------------------
# Create flatten
# ----------------------------------------------------------------
def create_flatten(source_name:str, table_name:str, table_name_raw:str, col_list:list, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str):
    # initialize Flatten Document
    Flatten = Document()
    insertcolumns = []

    # import source specific flattenjson
    try:
        # load source specific flatten file
        flatten_plugin_name = f"SourcePlugins.{source_name.capitalize()}.Flatten_{source_name.capitalize()}"
        flatten_plugin = import_module(flatten_plugin_name)
        flattenjson = getattr(flatten_plugin, "flattenjson")
        runlog.log(f"Using {flatten_plugin_name} to generate FlattenJSON CTE.")
    except:
        runlog.log(f"{indent}{flatten_plugin_name} not found. Using basic flatten to generate FlattenJSON CTE.")
        runlog.log("")
        # load basic flatten
        try:
            flatten_mod = import_module("Library.Flatten_basic")
            flattenjson = getattr(flatten_mod, "flattenjson")
        except:
            runlog.log(f"ERROR: Flatten basic not found. Terminating processing.")
            raise Exception

    # create column list for insert and json sections
    for col in col_list:
        insertcolumns.append(f"\t{str(col[1]).upper()}")

    # initialize elements of insert statement
    Flatten.append(f"/*{table_name} Flatten Insert version={version} generated by config generator */")
    Flatten.newline(f"INSERT INTO import.{table_name.lower()}")
    Flatten.newline("(")
    Flatten.newline("\tFILEDATE,")
    Flatten.newline("\tFILENAME,")
    Flatten.newline("\tFILEROWNUMBER,")
    Flatten.newlinelist(insertcolumns)
    Flatten.newline(")")
    Flatten.newline(f"WITH FLATTENJSON AS")
    Flatten.newline("(")
    Flatten.newline(flattenjson(table_name, table_name_raw, col_list))
    Flatten.newline(")")
    Flatten.newline("SELECT")
    Flatten.newline("\tFILEDATE,")
    Flatten.newline("\tFILENAME,")
    Flatten.newline("\tFILEROWNUMBER,")
    Flatten.newlinelist(insertcolumns)
    Flatten.newline("FROM FLATTENJSON;")

    # define output folder and filename
    filename = f"{table_name.lower()}-flatten.sql"

    # define folder output path
    output_folder = f"{db_folder}config_repo{os.sep}sources{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=Flatten.out())
    print_section_detail(msg=f"FLATTEN - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        configrepo_folder = f"{repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{client.upper()}{os.sep}{source_name.lower()}{os.sep}sources{os.sep}"
        filewrite(folder=configrepo_folder, filename=filename, content=Flatten.out())
        print_section_detail(msg=f"FLATTEN - {filename}\nCreated in: {configrepo_folder}", runlog=runlog)

    return filename

# ----------------------------------------------------------------
# Create truncate query
# ----------------------------------------------------------------
def create_truncate_query(table_name:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str):
    # initialize query document
    query = Document()

    # write query
    query.append(f"TRUNCATE TABLE &database.IMPORT.{table_name.upper()};")

    # define output folder and filename
    filename = f"{table_name.lower()}-truncate.sql"
    output_folder = f"{db_folder}config_repo{os.sep}sources{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=query.out())
    print_section_detail(msg=f"TRUNCATE - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        configrepo_folder = f"{repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{client.upper()}{os.sep}{source_name.lower()}{os.sep}sources{os.sep}"
        filewrite(folder=configrepo_folder, filename=filename, content=query.out())
        print_section_detail(msg=f"TRUNCATE - {filename}\nCreated in: {configrepo_folder}", runlog=runlog)

    return filename

# ----------------------------------------------------------------
# create delete from raw table query
# ----------------------------------------------------------------
def create_delete_rawtable_query(table_name:str, table_name_raw:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str):
    # initialize query document
    query = Document()

    # write query
    query.append(f"DELETE FROM &database.IMPORT.{table_name_raw.upper()} raw")
    query.newline(f"WHERE")
    query.newline("\tTO_TIMESTAMP(RPAD(raw.FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') <")
    query.newline("\t(")
    query.newline(f"\t\tSELECT DATEADD(DAY, -7, IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01')))")
    query.newline(f"\t\tFROM &database.STAGE.{table_name.upper()}")
    query.newline("\t)")
    query.newline(";")

    # define output folder and filename
    filename = f"{table_name_raw.lower()}-delete.sql"
    output_folder = f"{db_folder}config_repo{os.sep}sources{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=query.out())
    print_section_detail(msg=f"DELETE RAW - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        configrepo_folder = f"{repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{client.upper()}{os.sep}{source_name.lower()}{os.sep}sources{os.sep}"
        filewrite(folder=configrepo_folder, filename=filename, content=query.out())
        print_section_detail(msg=f"DELETE RAW - {filename}\nCreated in: {configrepo_folder}", runlog=runlog)

    return filename

# ----------------------------------------------------------------
# Create merge SP
# ----------------------------------------------------------------
def create_merge_sp(table_name:str, pk_list:list, col_list:list, db_folder:str, runlog:object, std_ind:str, repo_root_folder:str, client:str, source_name:str, create_keyhash:str="0", pk_case_sensitive:bool=False):
    # define output folder and filename
    filename = f"sp_mergeinto{table_name.lower()}.sql"
    output_folder = f"{db_folder}data_repo{os.sep}stage{os.sep}"

    runlog.log(f"MERGEINTO - {filename}")

    # set pk_case_sensitive
    if pk_case_sensitive is not True:
        pk_case_sensitive = False

    # get data type for pk
    pk_type_list = []
    for col in col_list:
        for pk in pk_list:
            # if pk matches column name, put column list into new list
            if pk == col[1]:
                pk_type_list.append(col)

    # define SP name
    merge_sp_name = f"stage.sp_mergeinto{table_name.lower()}()"
    # initialize merge query document
    mergesp = Document()

    # write query
    mergesp.append(f"/* sp_MergeInto{table_name.upper()} (stage) grantobjectname=stage.sp_MergeInto{table_name.upper()} version=1 */")
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

    if std_ind == "1":
        mergesp.newline(
            f"\t\tMERGE INTO STAGE.{table_name.upper()} dest USING TMP.{table_name.upper()}RawAudience sor ON")
    else:
        mergesp.newline(
            f"\t\tMERGE INTO STAGE.{table_name.upper()} dest USING TMP.{table_name.upper()}Unique sor ON")

    if create_keyhash == "1":
        mergesp.newline(f"\t\t\tdest.KEYHASH = sor.KEYHASH")
    else:
        for pk in pk_type_list:
            # if pk is string, lower
            if "VARCHAR" in pk[2].upper() and pk_case_sensitive is False:
                runlog.log("   PK is not case sensitive")
                mergesp.newline(f"\t\t\tlower(dest.{pk[1]}) = lower(sor.{pk[1]}) AND")
            else:
                runlog.log("   PK is case sensitive")
                mergesp.newline(f"\t\t\tdest.{pk[1]} = sor.{pk[1]} AND")

        mergesp.trimend(4)

    mergesp.newline("\t\tWHEN MATCHED AND")
    mergesp.newline("\t\t(")

    if create_keyhash == "1":
        mergesp.newline(f"\t\t\tNOT EQUAL_NULL(dest.KEYHASH, sor.KEYHASH) OR")

    mergesp.newline(f"\t\t\tNOT EQUAL_NULL(dest.FILEDATE, sor.FILEDATE) OR")
    mergesp.newline(f"\t\t\tNOT EQUAL_NULL(dest.FILENAME, sor.FILENAME) OR")
    mergesp.newline(f"\t\t\tNOT EQUAL_NULL(dest.FILEROWNUMBER, sor.FILEROWNUMBER) OR")

    for row in col_list:
        mergesp.newline(f"\t\t\tNOT EQUAL_NULL(dest.{row[1]}, sor.{row[1]}) OR")

    # add standardizationrowid and rawudienceid column if table is customer source
    if std_ind == "1":
        mergesp.newline("\t\t\tNOT EQUAL_NULL(dest.STANDARDIZATIONROWID, sor.STANDARDIZATIONROWID) OR")
        mergesp.newline("\t\t\tNOT EQUAL_NULL(dest.RAWAUDIENCEID, sor.RAWAUDIENCEID)")
    else:
        mergesp.trimend(3)

    mergesp.newline("\t\t)")
    mergesp.newline("\t\tTHEN UPDATE SET")

    mergesp.newline(f"\t\t\tdest.FILEDATE = sor.FILEDATE,")
    mergesp.newline(f"\t\t\tdest.FILENAME = sor.FILENAME,")
    mergesp.newline(f"\t\t\tdest.FILEROWNUMBER = IFNULL(sor.FILEROWNUMBER,0),")

    if create_keyhash == "1":
        mergesp.newline(f"\t\t\tdest.KEYHASH = sor.KEYHASH,")

    for row in col_list:
        mergesp.newline(f"\t\t\tdest.{row[1]} = sor.{row[1]},")

    # add standardizationrowid and rawudienceid column if table is customer source
    if std_ind == "1":
        mergesp.newline("\t\t\tdest.STANDARDIZATIONROWID = sor.STANDARDIZATIONROWID,")
        mergesp.newline("\t\t\tdest.RAWAUDIENCEID = sor.RAWAUDIENCEID,")

    mergesp.newline("\t\t\tdest.DWUPDATEDATE = now()")
    mergesp.newline("\t\tWHEN NOT MATCHED THEN INSERT")
    mergesp.newline("\t\t(")

    mergesp.newline(f"\t\t\tFILEDATE,")
    mergesp.newline(f"\t\t\tFILENAME,")
    mergesp.newline(f"\t\t\tFILEROWNUMBER,")

    if create_keyhash == "1":
        mergesp.newline(f"\t\t\tKEYHASH,")
    for row in col_list:
        mergesp.newline(f"\t\t\t{row[1]},")

    # add standardizationrowid and rawudienceid column if table is customer source
    if std_ind == "1":
        mergesp.newline("\t\t\tSTANDARDIZATIONROWID,")
        mergesp.newline("\t\t\tRAWAUDIENCEID,")

    mergesp.newline("\t\t\tDWUPDATEDATE,")
    mergesp.newline("\t\t\tDWINSERTDATE")

    mergesp.newline("\t\t) VALUES")
    mergesp.newline("\t\t(")

    mergesp.newline(f"\t\t\tIFNULL(NULLIF(sor.FILEDATE,''),'19000101'),")
    mergesp.newline(f"\t\t\tsor.FILENAME,")
    mergesp.newline(f"\t\t\tIFNULL(sor.FILEROWNUMBER,0),")

    if create_keyhash == "1":
        mergesp.newline(f"\t\t\tsor.KEYHASH,")

    for row in col_list:
        mergesp.newline(f"\t\t\tsor.{row[1]},")

    # add standardizationrowid and rawudienceid column if table is customer source
    if std_ind == "1":
        mergesp.newline("\t\t\tsor.STANDARDIZATIONROWID,")
        mergesp.newline("\t\t\tsor.RAWAUDIENCEID,")

    mergesp.newline("\t\t\tnow(),")
    mergesp.newline("\t\t\tnow()")
    mergesp.newline("\t\t);")

    mergesp.newline(f"\tRETURN 'FINISHED CALLING STORED PROCEDURE sp_MergeInto{table_name.upper()}';")
    mergesp.newline("\tEND;")
    mergesp.newline("$$;")

    # write output file
    filewrite(folder=output_folder, filename=filename, content=mergesp.out())
    runlog.log(f"   Created in: {output_folder}")

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}stage{os.sep}{client.upper()}{os.sep}"
        filewrite(folder=datarepo_folder, filename=filename, content=mergesp.out())
        runlog.log(f"   Created in: {output_folder}")

    return merge_sp_name

# ----------------------------------------------------------------
# Create unique tmp table SP
# ----------------------------------------------------------------
def create_unique_sp(table_name:str, pk_list:list, col_list:list, db_folder:str, runlog:object, std_ind:str, repo_root_folder:str, client:str, source_name:str, import_view_name:str="", create_keyhash:str="0", pk_case_sensitive:bool=False):
    def split_schema_table(table_name:str):
        # if table_name has schema, split it up
        if "." in table_name:
            table_name_list = table_name.split(".")
            table_schema = table_name_list[0].upper()
            tablename_noschema = table_name_list[1].upper()
        else:
            table_schema = "IMPORT"
            tablename_noschema = table_name.upper()

        return table_schema, tablename_noschema

    def remove_chars(input:str, char_to_remove:list):
        query_str=input
        for char in char_to_remove:
            query_str = f"REPLACE({query_str},'{char}','')"

        return query_str

    # map import table name to either table or view
    if len(import_view_name)>0:
        table_schema, tablename_noschema = split_schema_table(import_view_name)
    else:
        table_schema, tablename_noschema = split_schema_table(table_name)

    import_table_name = tablename_noschema

    # if audience table, map to melissa tmp table
    if std_ind == "1":
        table_schema = "TMP"
        import_table_name = f"{import_table_name.upper()}melissa"

    # define SP name
    unique_sp_name = f"tmp.sp_createtable{table_name.lower()}unique()"

    # initialize unique query document
    uniquesp = Document()

    # write query
    uniquesp.append(f"/* sp_CreateTable{table_name.upper()}Unique (tmp) grantobjectname=tmp.sp_CreateTable{table_name.upper()}Unique version=1 */")
    uniquesp.newline("!set exit_on_error=true;")
    uniquesp.newline("!set variable_substitution=true;")
    uniquesp.newline("")
    uniquesp.newline(f"CREATE OR REPLACE PROCEDURE {unique_sp_name}")
    uniquesp.newline("\treturns varchar not null")
    uniquesp.newline("\tlanguage sql")
    uniquesp.newline("\texecute as caller")
    uniquesp.newline("AS")
    uniquesp.newline("$$")
    uniquesp.newline("\tBEGIN")
    uniquesp.newline(f"\t\tCREATE OR REPLACE TABLE TMP.{table_name.upper()}UNIQUE")
    uniquesp.newline("\t\tAS")
    uniquesp.newline("\t\tSELECT DISTINCT")
    uniquesp.newline("\t\t\tFILEDATE,")
    uniquesp.newline("\t\t\tFILENAME,")
    uniquesp.newline("\t\t\tFILEROWNUMBER,")

    if create_keyhash == "1":
        uniquesp.newline(f"\t\t\tKEYHASH,")

    for row in col_list:
        uniquesp.newline(f"\t\t\t{row[1]},")

    if std_ind == "1":
        uniquesp.newline("\t\t\tSTANDARDIZATIONROWID")
    else:
        # remove trailing comma
        uniquesp.trimend(1)

    uniquesp.newline("\t\tFROM")
    uniquesp.newline("\t\t(")

    uniquesp.newline("\t\t\tSELECT")
    uniquesp.newline("\t\t\t\tIFNULL(TRIM(CAST(FILEDATE AS STRING)), '') FILEDATE,")
    uniquesp.newline("\t\t\t\tIFNULL(TRIM(CAST(FILENAME AS STRING)), '') FILENAME,")
    uniquesp.newline("\t\t\t\tCAST(IFNULL(FILEROWNUMBER,0) AS NUMBER(38,0)) FILEROWNUMBER,")

    # add columns and cast to appropriate datatype
    for row in col_list:
        colname = str(row[1]).upper()
        datatype = str(row[2]).upper()

        if "TIMESTAMP" in datatype or "DATETIME" in datatype:
            if row[1] in pk_list:
                uniquesp.newline(f"\t\t\t\tCAST(to_datetime(IFNULL({colname},'1900-01-01')) AS TIMESTAMP) {colname},")
            else:
                uniquesp.newline(f"\t\t\t\tCAST(to_datetime({colname}) AS TIMESTAMP) {colname},")
        elif row[2].replace(" ","").upper() == "NUMBER(38)" or row[2].replace(" ","").upper() == "NUMBER(38,0)":
            # maintain NULL if its a CLVMODEL table
            if "CLV" in table_name[:3].upper():
                uniquesp.newline(f"\t\t\t\tCAST(IFF({colname} IS NULL, NULL, to_integer({colname})) AS INT) {colname},")
            elif row[1] in pk_list:
                uniquesp.newline(f"\t\t\t\tCAST(to_integer(IFNULL(NULLIF({colname},'NaN'),0)) AS INT) {colname},")
            else:
                uniquesp.newline(f"\t\t\t\tCAST(to_integer(NULLIF({colname},'NaN')) AS INT) {colname},")

        #---------------------------------
        # replacing use of to_money() for clvmodel so it doesn't run into the "e" issue
        #---------------------------------
        # elif "NUMBER(38,2)" in row[2]:
        #     uniquesp.newline(f"\t\t\t\tCAST(to_money({colname}) AS NUMBER(38,2)) {colname},")

        elif "NUMBER" in datatype:
            # maintain NULL if its a CLVMODEL table
            if "CLVMODEL" in table_name.upper():
                uniquesp.newline(f"\t\t\t\tCAST(IFF({colname} IS NULL, NULL, to_double({colname})) AS {row[2]}) {colname},")
            elif row[1] in pk_list:
                replacestr = remove_chars(colname, ["$",","," "])
                uniquesp.newline(f"\t\t\t\tCAST(to_double(IFNULL(NULLIF(NULLIF({replacestr},'NaN'),''),0)) AS {row[2]}) {colname},")
            else:
                replacestr = remove_chars(colname, ["$",","," "])
                uniquesp.newline(f"\t\t\t\tCAST(to_double(IFNULL(NULLIF(NULLIF({replacestr},'NaN'),''),0)) AS {row[2]}) {colname},")

        elif "BOOLEAN" in datatype:
            if row[1] in pk_list:
                uniquesp.newline(f"\t\t\t\tTRY_TO_BOOLEAN(CAST(IFNULL({colname},'0') AS VARCHAR)) {colname},")
            else:
                uniquesp.newline(f"\t\t\t\tTRY_TO_BOOLEAN(CAST({colname} AS VARCHAR)) {colname},")
        elif "VARIANT" in datatype:
            uniquesp.newline(f"\t\t\t\tCAST({colname} AS VARIANT) {colname},")
        # treat everything else as varchar
        else:
            uniquesp.newline(f"\t\t\t\tIFNULL(TRIM(CAST({colname} AS STRING)), '') {colname},")

    if std_ind == "1":
        uniquesp.newline("\t\t\t\tCast(TO_INTEGER(STANDARDIZATIONROWID) AS INT) STANDARDIZATIONROWID,")

    uniquesp.newline("\t\t\t\tROW_NUMBER() OVER")
    uniquesp.newline("\t\t\t\t(PARTITION BY")

    if create_keyhash == "1":
        uniquesp.newline("\t\t\t\t\tKEYHASH")
    else:
        # add primary key columns
        for row in col_list:
            colname = str(row[1]).upper()
            datatype = str(row[2]).upper()
            if row[1] in pk_list:
                if "TIMESTAMP" in datatype or "DATETIME" in datatype:
                    uniquesp.newline(f"\t\t\t\t\tCAST(to_datetime(IFNULL({colname},'1900-01-01')) AS TIMESTAMP),")

                elif "NUMBER(38)" in datatype or "NUMBER(38,0)" in datatype:
                    if "CLV" in table_name[:3].upper():
                        uniquesp.newline(f"\t\t\t\t\tCAST(IFF({colname} IS NULL, NULL, to_integer({colname})) AS INT),")
                    else:
                        uniquesp.newline(f"\t\t\t\t\tCAST(to_integer(IFNULL({colname},0)) AS INT),")

                elif "NUMBER" in datatype:
                    if "CLVMODEL" in table_name.upper():
                        uniquesp.newline(f"\t\t\t\t\tCAST(IFF({colname} IS NULL, NULL, to_double({colname})) AS {row[2]}),")
                    else:
                        replacestr = remove_chars(colname, ["$",","," "])
                        uniquesp.newline(f"\t\t\t\t\tCAST(to_double(IFNULL(NULLIF({replacestr},''),0)) AS {row[2]}),")

                elif "BOOLEAN" in datatype:
                    uniquesp.newline(f"\t\t\t\tTRY_TO_BOOLEAN(CAST(IFNULL({colname},'0') AS VARCHAR)),")

                # treat everything else as varchar
                else:
                    if pk_case_sensitive:
                        uniquesp.newline(f"\t\t\t\t\tIFNULL(TRIM(CAST({colname} AS STRING)), ''),")
                    else:
                        uniquesp.newline(f"\t\t\t\t\tLOWER(IFNULL(TRIM(CAST({colname} AS STRING)), '')),")

        # remove trailing comma
        uniquesp.trimend(1)

    uniquesp.newline("\t\t\t\t\tORDER BY")
    uniquesp.newline("\t\t\t\t\t\tto_datetime(FILEDATE) DESC,")
    uniquesp.newline("\t\t\t\t\t\tFILENAME DESC,")
    uniquesp.newline("\t\t\t\t\t\tFILEROWNUMBER DESC")
    uniquesp.newline("\t\t\t\t) therealrownumber")
    uniquesp.newline("\t\t\tFROM")

    if create_keyhash == "1":
        uniquesp.newline(f"\t\t\t\tTMP.{import_table_name}_KEYHASH")
    else:
        uniquesp.newline(f"\t\t\t\t{table_schema}.{import_table_name}")

    uniquesp.newline("\t\t) a")
    uniquesp.newline("\t\tWHERE a.therealrownumber = 1;")

    uniquesp.newline(f"\tRETURN 'FINISHED CALLING STORED PROCEDURE sp_CreateTable{table_name.upper()}Unique';")
    uniquesp.newline("\tEND;")
    uniquesp.newline("$$;")

    # define output folder and filename
    filename = f"sp_createtable{table_name.lower()}unique.sql"
    output_folder = f"{db_folder}data_repo{os.sep}tmp{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=uniquesp.out())
    print_section_detail(msg=f"TMPCREATETABLEUNIQUE - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}tmp{os.sep}{client.upper()}{os.sep}"
        filewrite(folder=datarepo_folder, filename=filename, content=uniquesp.out())
        print_section_detail(msg=f"TMPCREATETABLEUNIQUE - {filename}\nCreated in: {datarepo_folder}", runlog=runlog)

    return unique_sp_name

# ----------------------------------------------------------------
# Create upgrade script for stage table
# ----------------------------------------------------------------
def create_schema_drift_script(table_name:str, stage_DDL:str, old_cols:list, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str, std_ind:str):
    table_name = table_name.upper()

    BackupTableName = f"STAGE.{table_name}_BACKUP_{date.today().strftime('%Y%m%d')}"

    Backup_Table_Query = f"CREATE TABLE IF NOT EXISTS {BackupTableName} CLONE STAGE.{table_name};"
    Create_Stage_Query = stage_DDL.replace("CREATE TABLE IF NOT EXISTS", "CREATE OR REPLACE TABLE").replace(f"STAGE.{table_name}", f"STAGE.{table_name} COPY GRANTS")

    Insert_Query = Document()
    Insert_Query.newline(f"INSERT INTO STAGE.{table_name}")
    Insert_Query.newline("(")
    Insert_Query.newline("\tFILEDATE,")
    Insert_Query.newline("\tFILENAME,")
    Insert_Query.newline("\tFILEROWNUMBER,")
    Insert_Query.newline("\tDWINSERTDATE,")
    Insert_Query.newline("\tDWUPDATEDATE,")

    old_columns_indent = []

    for col in old_cols:
        old_columns_indent.append(f"\t{col.upper()}")

    if std_ind == 1 or std_ind == "1":
        old_columns_indent.append(f"\tSTANDARDIZATIONROWID")
        old_columns_indent.append(f"\tRAWAUDIENCEID")

    Insert_Query.newlinelist(old_columns_indent)
    Insert_Query.newline(")")
    Insert_Query.newline("SELECT")
    Insert_Query.newline("\tFILEDATE,")
    Insert_Query.newline("\tFILENAME,")
    Insert_Query.newline("\tFILEROWNUMBER,")
    Insert_Query.newline("\tDWINSERTDATE,")
    Insert_Query.newline("\tDWUPDATEDATE,")
    Insert_Query.newlinelist(old_columns_indent)
    Insert_Query.newline(f"FROM {BackupTableName};")

    Final_Script = Document()
    Final_Script.append("!set variable_substitution=true;")
    Final_Script.newline("--Backup Stage Table")
    Final_Script.newline(Backup_Table_Query)
    Final_Script.newline("")
    Final_Script.newline("--Create Stage Table")
    Final_Script.newline(Create_Stage_Query)
    Final_Script.newline("")
    Final_Script.newline("--Insert Backup Into Stage Table")
    Final_Script.newline(Insert_Query.out())

    # define output folder and filename
    filename = f"Update_stage_{table_name}.sql"
    output_folder = f"{db_folder}data_repo{os.sep}stage{os.sep}upgrade{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=Final_Script.out())

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}stage{os.sep}upgrade{os.sep}{client.upper()}{os.sep}"
        filewrite(folder=datarepo_folder, filename=filename, content=Final_Script.out())

    # trace log
    print_section_detail(msg=f"STAGE Schema Drift script - {filename}\nCreated in: {output_folder}", runlog=runlog)

    return filename

# ----------------------------------------------------------------
# Create flatten view
# ----------------------------------------------------------------
def create_flatten_view(view_name:str, pk_list:list, phone_cols:list, source_table_name:str, col_list:list, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str):
    select_col_list = []
    result_col_list = []
    flatten_table_list = []
    flattendoc = Document()

    # create JSON elements list
    for col in col_list:
        src_col = str(col[0])
        tbl_col = str(col[1]).upper()
        datatype = str(col[2]).upper()

        if '"' in col[0] and "." in col[0]:
            # remove from PK list
            if col[1] in pk_list:
                pk_list.remove(col[1])

            flatten_tbl_col, src_col_fld = src_col.split(".")
            flatten_tbl_col = flatten_tbl_col.strip('"')
            select_col = "\t" + flatten_tbl_col + f'.value:{src_col_fld}::STRING AS {tbl_col}'

            result_col = f"\t{flatten_tbl_col}.{tbl_col}"
            # add formatted phone columns
            if col[1] in phone_cols:
                result_col_list.append(f"\tpublic.fn_phoneformatter({flatten_tbl_col}.{tbl_col}) AS {tbl_col}formatted")

            # add to table list if it doesn't yet exist
            if flatten_tbl_col not in flatten_table_list:
                flatten_table_list.append(flatten_tbl_col)

            select_col_list.append(select_col)
            is_flatten_col = True
        else:
            if "VARIANT" in datatype:
                result_col = f"\tparse_json(T.{src_col}) AS {tbl_col}"

            else:
                result_col = '\tT.' + src_col.replace('"','') + f' AS {tbl_col}'
                # add formatted phone columns
                if col[1] in phone_cols:
                    result_col_list.append(f"\tpublic.fn_phoneformatter(T." + src_col.replace('"','') + f") AS {tbl_col}formatted")

        # build element list
        result_col_list.append(result_col)

    # build CTE
    ctedoc = Document()

    for table in flatten_table_list:
        ctedoc.newline(f"{table} AS (")
        ctedoc.newline(f"SELECT")
        for pk in pk_list:

            ctedoc.newline(f"\tT.{pk},")
        for col in select_col_list:
            if table in col:
                ctedoc.newline(f"{col},")
        ctedoc.trimend(1)
        ctedoc.newline(f"FROM {source_table_name.upper()} T,")
        ctedoc.newline(f"LATERAL FLATTEN(parse_json(T.{table})) {table}")
        ctedoc.newline("),")
    ctedoc.trimend(1)

    # build main query
    flattendoc.append(f"/*{view_name} (Stage) grantObjectName={view_name} version=1 generated by config generator */")
    flattendoc.newline(f"CREATE OR REPLACE VIEW STAGE.{view_name}")
    flattendoc.newline("AS")
    flattendoc.newline("WITH")
    flattendoc.newline(ctedoc.out())
    flattendoc.newline("SELECT")
    flattendoc.newline("\tT.FILEDATE,")
    flattendoc.newline("\tT.FILENAME,")
    flattendoc.newline("\tT.FILEROWNUMBER,")
    flattendoc.newlinelist(result_col_list)
    flattendoc.newline(f"FROM {source_table_name.upper()} T")
    for table in flatten_table_list:
        flattendoc.newline(f"LEFT JOIN {table} ON")
        for pk in pk_list:
            flattendoc.newline(f"\tT.{pk} = {table}.{pk} AND")
        flattendoc.trimend(4)

    # define output folder and filename
    filename = f"{view_name.lower()}.sql"
    output_folder = f"{db_folder}data_repo{os.sep}stage{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=flattendoc.out())
    print_section_detail(msg=f"FLATTEN VIEWS - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}stage{os.sep}{client.upper()}{os.sep}"
        filewrite(folder=datarepo_folder, filename=filename, content=flattendoc.out())
        print_section_detail(msg=f"FLATTEN VIEWS - {filename}\nCreated in: {datarepo_folder}", runlog=runlog)

    return filename