from Library.FunctionFiles.Functions import *

need_flatten = True
# ----------------------------------------------------------------
# Create Flatten Insert File
# ----------------------------------------------------------------

# Create FLATTENJSON CTE for use in Flatten SQL Insert query
# contact
def flattenjson_contacts(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()
    # create JSON elements list
    for col in col_list:
        if "TIMESTAMP" in col[2].upper():
            jsonelements.append(f"\t\tTRY_TO_TIMESTAMP(STRIP_NULL_VALUE(raw.JSONDATA:result.elements[0].{col[0]})::STRING) AS {col[1].upper()}")
        elif col[2].upper() == "VARIANT":
            jsonelements.append(f"\t\tSTRIP_NULL_VALUE(raw.JSONDATA:result.elements[0].{col[0]})::VARIANT AS {col[1].upper()}")
        else:
            jsonelements.append(f"\t\tSTRIP_NULL_VALUE(raw.JSONDATA:result.elements[0].{col[0]})::VARCHAR AS {col[1].upper()}")

    flattendoc.append("\tSELECT")
    flattendoc.newline("\t\traw.FILEDATE,")
    flattendoc.newline("\t\traw.FILENAME,")
    flattendoc.newline("\t\traw.FILEROWNUMBER,")
    flattendoc.newlinelist(jsonelements)
    flattendoc.append(",")
    flattendoc.newline("\t\traw.DW_CREATED_DATE,")
    flattendoc.newline("\t\traw.DW_CREATED_BY")
    flattendoc.newline(f"\tFROM (")
    flattendoc.newline(f"\t\tSELECT *")
    flattendoc.newline(f"\t\tFROM &database.IMPORT.{table_name_raw.upper()}")
    flattendoc.newline(f"\t\tWHERE")
    flattendoc.newline("\t\t\tTO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t\t(")
    flattendoc.newline(f"\t\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t\t)")
    flattendoc.newline("\t\t\tAND JSONDATA <> '{}'")
    flattendoc.newline("\t) raw")

    return flattendoc.out()

# survey definitions
def flattenjson_surveydefinitions(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()
    # create JSON elements list
    for col in col_list:
        jsonelements.append(f"\t\traw.JSONDATA:{col[0]}::STRING AS {col[1].upper()}")

    flattendoc.append("\tSELECT")
    flattendoc.newline("\t\traw.FILEDATE,")
    flattendoc.newline("\t\traw.FILENAME,")
    flattendoc.newline("\t\traw.FILEROWNUMBER,")
    flattendoc.newlinelist(jsonelements)
    flattendoc.append(",")
    flattendoc.newline("\t\traw.DW_CREATED_DATE,")
    flattendoc.newline("\t\traw.DW_CREATED_BY")
    flattendoc.newline(f"\tFROM &database.IMPORT.{table_name_raw.upper()} raw")
    flattendoc.newline(f"\tWHERE")
    flattendoc.newline("\t\tTO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t(")
    flattendoc.newline(f"\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t)")

    return flattendoc.out()

# survey questions
def flattenjson_surveyquestions(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()
    # create JSON elements list
    for col in col_list:
        if col[1].upper() == "SURVEYID":
            jsonelements.append(f"\t\tSTRIP_NULL_VALUE(JSONDATA:{col[0]})::VARCHAR AS {col[1].upper()}")
        elif col[1].upper() == "DATAEXPORTTAG" or col[1].upper() == "QUESTIONTYPE" or col[1].upper() == "SELECTOR" or col[1].upper() == "SUBSELECTOR":
            jsonelements.append(f"\t\tSTRIP_NULL_VALUE(questions.value:{col[0]})::VARCHAR AS {col[1].upper()}")
        elif col[1].upper() == "QUESTIONID":
            jsonelements.append(f"\t\tCASE"
                                f"\n\t\t\tWHEN STRIP_NULL_VALUE (questions.value:QuestionType)::VARCHAR = 'Matrix' OR STRIP_NULL_VALUE (questions.value:QuestionType)::VARCHAR = 'MC'"
                                f"\n\t\t\tTHEN COALESCE(questions.key||'_'||choices.key, questions.key, 'N/A')"
                                f"\n\t\t\tELSE"
                                f"\n\t\t\t\tCASE"
                                f"\n\t\t\t\t\tWHEN STRIP_NULL_VALUE (questions.value:QuestionType)::VARCHAR = 'PGR'"
                                f"\n\t\t\t\t\tTHEN COALESCE(questions.key||'_0_GROUP', 'N/A')"
                                f"\n\t\t\t\t\tELSE IFNULL(questions.key,'N/A')"
                                f"\n\t\t\t\tEND"
                                f"\n\t\tEND AS QUESTIONID")
        elif col[1].upper() == "QUESTIONTEXT":
            jsonelements.append(f"\t\tCASE"
                                f"\n\t\t\tWHEN STRIP_NULL_VALUE (questions.value:QuestionType)::VARCHAR = 'Matrix' OR STRIP_NULL_VALUE (questions.value:QuestionType)::VARCHAR = 'MC'"
                                f"\n\t\t\tTHEN STRIP_NULL_VALUE (questions.value:QuestionDescription) || ' ' || REGEXP_REPLACE(REGEXP_REPLACE(STRIP_NULL_VALUE (choices.value:Display)::VARCHAR, '</.*?>') , '<.*?>', ' ')"
                                f"\n\t\t\tELSE STRIP_NULL_VALUE (questions.value:QuestionDescription)"
                                f"\n\t\tEND AS QUESTIONTEXT")
        else:
            jsonelements.append(f"\t\tnull AS {col[1].upper()}")

    flattendoc.append("\tSELECT")
    flattendoc.newline("\t\traw.FILEDATE,")
    flattendoc.newline("\t\traw.FILENAME,")
    flattendoc.newline("\t\traw.FILEROWNUMBER,")
    flattendoc.newlinelist(jsonelements)
    flattendoc.append(",")
    flattendoc.newline("\t\traw.DW_CREATED_DATE,")
    flattendoc.newline("\t\traw.DW_CREATED_BY")
    flattendoc.newline(f"\tFROM (")
    flattendoc.newline(f"\t\tSELECT *")
    flattendoc.newline(f"\t\tFROM &database.IMPORT.QUALTRICSSURVEYDEFINITIONS_RAW")
    flattendoc.newline(f"\t\tWHERE")
    flattendoc.newline("\t\t\tTO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t\t(")
    flattendoc.newline(f"\t\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t\t)")
    flattendoc.newline("\t) raw, LATERAL flatten(JSONDATA:Questions) questions, TABLE(flatten(INPUT => questions.value:Choices, OUTER => TRUE)) choices")

    return flattendoc.out()

# survey responses
def flattenjson_surveyresponses(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()
    # create JSON elements list
    for col in col_list:
        if col[1].upper() == "RESPONSEID":
            jsonelements.append(f"\t\traw.JSONDATA:{col[0]}::STRING AS {col[1].upper()}")
        elif col[1].upper() == "STARTDATE" or col[1].upper() == "ENDDATE" or col[1].upper() == "STATUS" or col[1].upper() == "IPADDRESS" or col[1].upper() == "PROGRESS" or col[1].upper() == "DURATION" or col[1].upper() == "FINISHED" or col[1].upper() == "RECORDEDDATE" or col[1].upper() == "LOCATIONLATITUDE" or col[1].upper() == "LOCATIONLONGITUDE" or col[1].upper() == "USERLANGUAGE" or col[1].upper() == "EMAILID":
            jsonelements.append(f"\t\traw.JSONDATA:values:{col[0]}::STRING AS {col[1].upper()}")
        elif col[1].upper() == "SURVEYID":
            jsonelements.append(f"\t\tSPLIT_PART(SPLIT_PART(raw.FILENAME, '/', -1), '-', 2) AS {col[1].upper()}")
        elif col[1].upper() == "QUESTIONRESPONSE":
            jsonelements.append(f"\t\tCASE"
                                f"\n\t\t\tWHEN SPLIT_PART(fvalues.path, '[', 1)::VARCHAR ILIKE '%_TEXT'"
                                f"\n\t\t\tTHEN STRIP_NULL_VALUE (COALESCE(values_flat.value, fvalues.value))::VARCHAR"
                                f"\n\t\t\tELSE STRIP_NULL_VALUE (COALESCE(labels_flat.value, labels.value))::VARCHAR"
                                f"\n\t\tEND AS QUESTIONRESPONSE")
        elif col[1].upper() == "QUESTIONID":
            jsonelements.append(f"\t\tCASE"
                                f"\n\t\t\tWHEN SPLIT_PART(fvalues.path, '[', 1)::VARCHAR ILIKE 'QID%'"
                                f"\n\t\t\t\tTHEN"
                                f"\n\t\t\t\t\tCASE"
                                f"\n\t\t\t\t\t\tWHEN SPLIT_PART(fvalues.path, '[', 1)::VARCHAR ILIKE '%_TEXT'"
                                f"\n\t\t\t\t\t\t\tTHEN REPLACE(SPLIT_PART(fvalues.path, '[', 1), '_TEXT')::VARCHAR"
                                f"\n\t\t\t\t\t\tWHEN SPLIT_PART(labels.path, '[', 1)::VARCHAR ILIKE '%_NPS_GROUP'"
                                f"\n\t\t\t\t\t\t\tTHEN REPLACE(SPLIT_PART(labels.path, '[', 1), '_NPS_GROUP')::VARCHAR"
                                f"\n\t\t\t\t\t\tWHEN fvalues.path::VARCHAR = labels.path::VARCHAR"
                                f"\n\t\t\t\t\t\t\tTHEN"
                                f"\n\t\t\t\t\t\t\t\tCASE"
                                f"\n\t\t\t\t\t\t\t\t\tWHEN POSITION('_' IN fvalues.key) > 0"
                                f"\n\t\t\t\t\t\t\t\t\t\tTHEN fvalues.key"
                                f"\n\t\t\t\t\t\t\t\t\tWHEN labels_flat.index = values_flat.index AND POSITION('[' IN fvalues.VALUE)"
                                f"\n\t\t\t\t\t\t\t\t\t\tTHEN labels.key || '_' || values_flat.VALUE::VARCHAR"
                                f"\n\t\t\t\t\t\t\t\t\tWHEN POSITION('[' IN fvalues.VALUE) = 0"
                                f"\n\t\t\t\t\t\t\t\t\t\tTHEN labels.key || '_' || fvalues.VALUE::VARCHAR"
                                f"\n\t\t\t\t\t\t\t\tEND"
                                f"\n\t\t\t\t\tEND"
                                f"\n\t\tEND AS QUESTIONID")
        elif col[1].upper() == "CONTACTID":
            jsonelements.append(f"\t\tCASE"
                                f"\n\t\t\tWHEN raw.JSONDATA:values:ContactID IS NOT NULL"
                                f"\n\t\t\tTHEN raw.JSONDATA:values:ContactID::STRING"
                                f"\n\t\t\tELSE NULL"
                                f"\n\t\tEND AS CONTACTID")
        else:
            jsonelements.append(f"\t\traw.JSONDATA:{col[0]}::{col[2]} AS {col[1].upper()}")

    flattendoc.append("\tSELECT")
    flattendoc.newline("\t\traw.FILEDATE,")
    flattendoc.newline("\t\traw.FILENAME,")
    flattendoc.newline("\t\traw.FILEROWNUMBER,")
    flattendoc.newlinelist(jsonelements)
    flattendoc.append(",")
    flattendoc.newline("\t\traw.DW_CREATED_DATE,")
    flattendoc.newline("\t\traw.DW_CREATED_BY")
    flattendoc.newline(f"\tFROM")
    flattendoc.newline(f"\t\t&database.IMPORT.{table_name_raw.upper()} raw,")
    flattendoc.newline("\t\tTABLE(FLATTEN(INPUT => raw.JSONDATA:labels)) labels,")
    flattendoc.newline("\t\tTABLE(FLATTEN(INPUT => labels.value, OUTER => TRUE)) labels_flat,")
    flattendoc.newline("\t\tTABLE(FLATTEN(INPUT => raw.JSONDATA:values)) fvalues,")
    flattendoc.newline("\t\tTABLE(FLATTEN(INPUT => fvalues.value, OUTER => TRUE)) values_flat")
    flattendoc.newline("\tWHERE")
    flattendoc.newline("\t\tTO_TIMESTAMP(RPAD(raw.FILEDATE,14,'0'), 'YYYYMMDDHH24MISS') >")
    flattendoc.newline("\t\t(")
    flattendoc.newline(f"\t\t\tSELECT IFNULL(MAX(TO_TIMESTAMP(RPAD(FILEDATE,14,'0'), 'YYYYMMDDHH24MISS')),TO_TIMESTAMP('1900-01-01'))")
    flattendoc.newline(f"\t\t\tFROM &database.STAGE.{table_name.upper()}")
    flattendoc.newline("\t\t)")

    return flattendoc.out()

# create flatten
def fn_create_flatten_custom(source_name:str, table_name:str, table_name_raw:str, col_list:list, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, worksheet: object):
    runlog.log("Running Qualtrics specific flatten function")

    # initialize Flatten Document
    Flatten = Document()
    insertcolumns = []

    # create column list for insert and json sections
    for col in col_list:
        insertcolumns.append(f"\t{col[1].upper()}")

    # initialize elements of insert statement
    Flatten.append(f"/*{table_name} Flatten Insert version={version} generated by config generator */")
    Flatten.newline(f"INSERT INTO &database.IMPORT.{table_name.upper()}")
    Flatten.newline("(")
    Flatten.newline("\tFILEDATE,")
    Flatten.newline("\tFILENAME,")
    Flatten.newline("\tFILEROWNUMBER,")
    Flatten.newlinelist(insertcolumns)
    Flatten.append(",")
    Flatten.newline("\tDW_CREATED_DATE,")
    Flatten.newline("\tDW_CREATED_BY")
    Flatten.newline(")")
    Flatten.newline(f"WITH FLATTENJSON AS")
    Flatten.newline("(")
    if table_name.upper()=="QUALTRICSCONTACTS":
        Flatten.newline(flattenjson_contacts(table_name, table_name_raw, col_list))
    elif table_name.upper()=="QUALTRICSSURVEYDEFINITIONS":
        Flatten.newline(flattenjson_surveydefinitions(table_name, table_name_raw, col_list))
    elif table_name.upper()=="QUALTRICSSURVEYQUESTIONS":
        Flatten.newline(flattenjson_surveyquestions(table_name, table_name_raw, col_list))
    elif table_name.upper()=="QUALTRICSSURVEYRESPONSES":
        Flatten.newline(flattenjson_surveyresponses(table_name, table_name_raw, col_list))
    Flatten.newline(")")
    Flatten.newline("SELECT")
    Flatten.newline("\tFILEDATE,")
    Flatten.newline("\tFILENAME,")
    Flatten.newline("\tFILEROWNUMBER,")
    Flatten.newlinelist(insertcolumns)
    Flatten.append(",")
    Flatten.newline("\tDW_CREATED_DATE,")
    Flatten.newline("\tDW_CREATED_BY")
    Flatten.newline("FROM FLATTENJSON")

    # add where clause if table is surveyresponses
    if table_name.upper()=="QUALTRICSSURVEYRESPONSES":
        Flatten.newline("WHERE QUESTIONID IS NOT NULL")

    Flatten.newline(";")

    # define output folder and filename
    filename = f"{table_name.lower()}-flatten.sql"
    output_folder = f"{db_folder}config_repo{os.sep}sources{os.sep}"

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        configrepo_folder = f"{repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{client.upper()}{os.sep}{source_name.lower()}{os.sep}sources{os.sep}"

    # write flatten insert to file
    filewrite(folder=output_folder, filename=filename, content=Flatten.out())
    print_section_detail(msg=f"FLATTEN - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        filewrite(folder=configrepo_folder, filename=filename, content=Flatten.out())
        print_section_detail(msg=f"FLATTEN - {filename}\nCreated in: {configrepo_folder}", runlog=runlog)

    return filename

# ----------------------------------------------------------------
# Create CopyInto File
# ----------------------------------------------------------------
def fn_create_copyinto_custom(client:str, source_name:str, table_name:str, col_list:list, file_match_text:str, file_date_regex:str, field_delimiter:str, version:str, db_folder:str, runlog:object, field_enclosed_by:str, custom_fileformat_options:str, repo_root_folder:str, worksheet:object):

    if table_name.upper() == "QUALTRICSSURVEYQUESTIONS":
        return "null"
    elif table_name.upper() == "QUALTRICSCONTACTS":
        # initialize CopyInto Document
        CopyInto = Document()

        # add copy into
        CopyInto.append(f"/*{table_name} Copy Into version={version} generated by config generator */")
        CopyInto.newline("CALL &database.IMPORT.SP_COPYINTOQUALTRICSDYNAMIC('&database', '&feature', '&teamAbbr', '&timestamp');")

    else:
        # initialize CopyInto Document
        CopyInto = Document()

        # format custom_fileformat_options
        custom_fileformat_options = custom_fileformat_options.strip()

        if custom_fileformat_options == "None":
            custom_fileformat_options = ""
        elif custom_fileformat_options != '':
            custom_fileformat_options = f" {custom_fileformat_options}"
        else:
            custom_fileformat_options = ""

        # define stage location path
        stage_location = f"@&database.IMPORT.INGESTSTAGE/&feature/&teamAbbr/&timestamp"

        # initialize elements of the CopyInto statement
        CopyInto.append(f"/*{table_name} Copy Into version={version} generated by config generator */")
        CopyInto.newline(f"COPY INTO &database.IMPORT.{table_name.upper()}_RAW")
        CopyInto.newline("(")
        CopyInto.newline("\tFILEDATE,")
        CopyInto.newline("\tFILENAME,")
        CopyInto.newline("\tFILEROWNUMBER,")
        CopyInto.newline("\tJSONDATA")
        CopyInto.newline(")")
        CopyInto.newline("FROM")
        CopyInto.newline("(")
        CopyInto.newline("\tSELECT")
        CopyInto.newline(f"\t\tREPLACE(REGEXP_SUBSTR(METADATA$filename, '{file_date_regex}', 1, 1), '-', ''),")
        CopyInto.newline("\t\tMETADATA$FILENAME,")
        CopyInto.newline("\t\tMETADATA$FILE_ROW_NUMBER,")
        CopyInto.newline("\t\tPARSE_JSON(T.\"$1\") AS JSONDATA")
        CopyInto.newline("\tFROM ")
        CopyInto.append(f"{stage_location} T")
        CopyInto.newline(")")
        CopyInto.newline(f"PATTERN = '.*{file_match_text}'")
        CopyInto.newline("ON_ERROR = CONTINUE")
        CopyInto.newline("FORCE = FALSE")
        CopyInto.newline("LOAD_UNCERTAIN_FILES = TRUE")
        CopyInto.newline(f"FILE_FORMAT = (TYPE = JSON{custom_fileformat_options})")
        CopyInto.newline(";")

    # define output folder and filename
    filename = f"{table_name.lower()}-copy.sql"
    output_folder = f"{db_folder}config_repo{os.sep}sources{os.sep}"

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        configrepo_folder = f"{repo_root_folder}kagr-configuration{os.sep}prefect{os.sep}{client.upper()}{os.sep}{source_name.lower()}{os.sep}sources{os.sep}"

    # write copyinto to file
    filewrite(folder=output_folder, filename=filename, content=CopyInto.out())
    print_section_detail(msg=f"COPYINTO - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        filewrite(folder=configrepo_folder, filename=filename, content=CopyInto.out())
        print_section_detail(msg=f"COPYINTO - {filename}\nCreated in: {configrepo_folder}", runlog=runlog)

    runlog.log("")

    return filename

# ----------------------------------------------------------------
# Create Import Raw DDL
# ----------------------------------------------------------------
def fn_create_importraw_DDL_custom(table_name:str, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, source_name:str):
    #----------
    # Import Raw
    #----------
    # initialize Import DDL Document
    ImportDDL_Raw = Document()

    # create table_name_raw
    table_name_raw = f"{table_name.upper()}_RAW"

    # create complete import DDL per table
    ImportDDL_Raw.append(f"/*{table_name}_RAW (Import) grantObjectName={table_name.upper()}_RAW version={version} generated by config generator */")
    ImportDDL_Raw.newline(f"CREATE TABLE IF NOT EXISTS IMPORT.{table_name_raw}")
    ImportDDL_Raw.newline("(")
    ImportDDL_Raw.newline("\tFILEDATE\tVARCHAR NOT NULL,")
    ImportDDL_Raw.newline("\tFILENAME\tVARCHAR NOT NULL,")
    ImportDDL_Raw.newline("\tFILEROWNUMBER\tVARCHAR NOT NULL,")
    ImportDDL_Raw.newline("\tJSONDATA\tVARIANT,")
    ImportDDL_Raw.newline("\tDW_CREATED_DATE\tTIMESTAMP_LTZ\tNOT NULL DEFAULT CURRENT_TIMESTAMP(),")
    ImportDDL_Raw.newline("\tDW_CREATED_BY\tVARCHAR(100)\tNOT NULL DEFAULT CURRENT_USER()")
    ImportDDL_Raw.newline(");")

    # define output folder and filename
    filename = f"{table_name.upper()}_RAW.sql"
    output_folder = f"{db_folder}data_repo{os.sep}import{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=ImportDDL_Raw.out())
    print_section_detail(msg=f"IMPORT RAW DDL - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}import{os.sep}{client.upper()}{os.sep}"
        filewrite(folder=datarepo_folder, filename=filename, content=ImportDDL_Raw.out())
        print_section_detail(msg=f"IMPORT RAW DDL - {filename}\nCreated in: {datarepo_folder}", runlog=runlog)

    return table_name_raw

# ----------------------------------------------------------------
# Create Import DDL
# ----------------------------------------------------------------
def fn_create_import_DDL_custom(table_name: str, col_list: list, version: str, db_folder: str, runlog: object, repo_root_folder: str, client: str, source_name: str, data_resources:list):
    #----------
    # Import
    #----------
    # initialize Import DDL Document
    ImportDDL = Document()

    # IMPORT - read column list and create column list for table creation
    importcolumns = getDDLcolumns(col_list=col_list, ddl_type="import")

    # create complete import DDL per table
    ImportDDL.append(
        f"/*{table_name} (Import) grantObjectName={table_name.upper()} version={version} generated by config generator */")
    ImportDDL.newline(f"CREATE OR REPLACE TABLE IMPORT.{table_name.upper()}")
    ImportDDL.newline("(")
    ImportDDL.newline("\tFILEDATE\tVARCHAR(16777216),")
    ImportDDL.newline("\tFILENAME\tVARCHAR(16777216),")
    ImportDDL.newline("\tFILEROWNUMBER\tNUMBER(38, 0),")
    ImportDDL.newlinelist(importcolumns)
    ImportDDL.append(",")
    ImportDDL.newline("\tDW_CREATED_DATE\tTIMESTAMP_LTZ\tNOT NULL,")
    ImportDDL.newline("\tDW_CREATED_BY\tVARCHAR(100)\tNOT NULL")
    ImportDDL.newline(");")

    # define output folder and filename
    filename = f"{table_name.upper()}.sql"
    output_folder = f"{db_folder}data_repo{os.sep}import{os.sep}"
    filewrite(folder=output_folder, filename=filename, content=ImportDDL.out())
    print_section_detail(msg=f"IMPORT DDL - {filename}\nCreated in: {output_folder}", runlog=runlog)

    # write output repo files if repo_root_folder is not empty
    if repo_root_folder != "":
        datarepo_folder = f"{repo_root_folder}data{os.sep}warehouse{os.sep}{source_name.lower()}{os.sep}import{os.sep}{client.upper()}{os.sep}"
        filewrite(folder=datarepo_folder, filename=filename, content=ImportDDL.out())
        print_section_detail(msg=f"IMPORT DDL - {filename}\nCreated in: {datarepo_folder}", runlog=runlog)

    # append data resources
    data_resources.append(["import", table_name.lower()])

    return

# ----------------------------------------------------------------
# Sources Append
# ----------------------------------------------------------------
def fn_sources_append(worksheet:object, db_folder:str, sources_obj:object, runlog:object, repo_root_folder:str, client:str, source_name:str):
    runlog.log("Running Qualtrics specific sources append function")

    # get table name
    table_name = worksheet.table_name()

    if table_name.upper() == "QUALTRICSSURVEYQUESTIONS" or table_name.upper() == "QUALTRICSSURVEYDEFINITIONS":
        sources_obj.append("rowCountCheckOverride", 1)

    elif table_name.upper() == "QUALTRICSCONTACTS":
        sources_obj.replace("getLastDateIndicator", True)
        sources_obj.append("rowCountCheckOverride", 1)

        # define getLastDateProperties values
        getLastDateProperties = {}
        getLastDateProperties["daysBack"] = 1
        getLastDateProperties["lastDateColumn"] = "CREATIONDATE"
        getLastDateProperties["refresh"] = 0
        getLastDateProperties["schema"] = "stage"
        getLastDateProperties["seasonYearIndicator"] = 0
        getLastDateProperties["whereClause"] = ""
        getLastDateProperties["tableName"] = table_name.lower()
        sources_obj.append("getLastDateProperties", getLastDateProperties)

    elif table_name.upper() == "QUALTRICSSURVEYRESPONSES":
        sources_obj.replace("getLastDateIndicator", True)
        sources_obj.append("rowCountCheckOverride", 1)

        # define getLastDateProperties values
        getLastDateProperties = {}
        getLastDateProperties["daysBack"] = 1
        getLastDateProperties["lastDateColumn"] = "RECORDEDDATE"
        getLastDateProperties["refresh"] = 0
        getLastDateProperties["schema"] = "stage"
        getLastDateProperties["seasonYearIndicator"] = 0
        getLastDateProperties["whereClause"] = ""
        getLastDateProperties["tableName"] = table_name.lower()
        sources_obj.append("getLastDateProperties", getLastDateProperties)

    flatten_filename = f"{table_name.lower()}-flatten.sql"

    # if table is survey questions, only add the flatten file if its Snaplogic. For Prefect, flatten is done as part of survey definitions
    if table_name.upper() == "QUALTRICSSURVEYQUESTIONS":
        sources_obj.append("importSql", "NoTruncate")
        sources_obj.append("importSql", "NoFlatten")

    # if table is survey definitions, after survey definitions flatten, add survey questions truncate and flatten
    elif table_name.upper() == "QUALTRICSSURVEYDEFINITIONS":
        sources_obj.append("importSql", [{"sortOrder": 3, "sqlFileName": "qualtricssurveyquestions-truncate.sql"}, {"sortOrder": 4, "sqlFileName": "qualtricssurveyquestions-flatten.sql"}])

    runlog.log("")

    return

# ----------------------------------------------------------------
# Data resources append
# ----------------------------------------------------------------
def fn_dataresources_append(data_resources:list, runlog:object):
    runlog.log("\nAppending custom Qualtrics Dynamic copy into")
    data_resources.append(["qualtrics/import", "SP_COPYINTOQUALTRICSDYNAMIC.sql"])
    data_resources.append(["base/2import", "csv_parse_header_format.sql"])
    data_resources.append(["base/2import", "csv_schema_file_reader_format.sql"])
    return data_resources

# ----------------------------------------------------------------
# Feature custom info
# ----------------------------------------------------------------
def fn_feature_custom_info():
    feature_custom_info_kv = {}
    feature_custom_info = []

    feature_custom_info_kv["key"] = "qualtricsDataCenterId"
    feature_custom_info_kv["value"] = "<get data center id from Account Settings>"

    feature_custom_info.append(feature_custom_info_kv)

    return feature_custom_info