from Library.FunctionFiles.Functions import *

custom_filedate = "TO_CHAR(REGEXP_SUBSTR(REPLACE(SPLIT_PART(SPLIT_PART('METADATA$FILENAME,', '/', -1), '_', 2),'-',''), '[0-9]{14}', 1, 1))"

def fn_sources_append(worksheet:object, db_folder:str, sources_obj:object, runlog:object, repo_root_folder:str, client:str, source_name:str):
    runlog.log("Running Marketo specific sources append function")

    # get table name
    table_name = worksheet.table_name().upper()

    # get table info
    table_info = worksheet.tableinfo()

    # add activityTypeId
    if table_name == 'MARKETOACTIVITY':
        sources_obj.append("endpoint_type", "activities")
        # activitytypeids
        activitytypeids = table_info["marketoActivityTypeIds"]
        activitytypeidsliststr = activitytypeids.replace(" ","").split(",")
        activitytypeidslist = []
        for id in activitytypeidsliststr:
            activitytypeidslist.append(int(id))

        sources_obj.append("marketoActivityTypeIds", activitytypeidslist)

    elif table_name == "MARKETOPERSON" or table_name == "MARKETOUNSUBSCRIBE":
        sources_obj.append("endpoint_type", "leads")
        # leadslistid
        leadslistid = table_info["marketoLeadsListId"]
        leadsfields = table_info["marketoLeadsFields"]
        sources_obj.append("marketoLeadsListId", leadslistid)

        leadsfieldslist = leadsfields.replace(" ","").split(",")

        sources_obj.append("marketoLeadsFields", leadsfieldslist)


    return

def fn_create_merge_sp_marketoactivity(table_name:str, pk_list:list, col_list:list, db_folder:str, runlog:object, std_ind:str, repo_root_folder:str, client:str, source_name:str):
    # define output folder and filename
    filename = f"sp_mergeinto{table_name.lower()}.sql"
    output_folder = f"{db_folder}data_repo{os.sep}stage{os.sep}"

    runlog.log(f"MERGEINTO - {filename}")

    # get data type for pk
    pk_type_list = []
    for col in col_list:
        for pk in pk_list:
            # if pk matches column name, put column list into new list
            if pk == col[1]:
                pk_type_list.append(col)

    # define source query
    sor = Document()
    sor.newline("\t\t\tSELECT")
    sor.newline("\t\t\t\tu.FILEDATE,")
    sor.newline("\t\t\t\tu.FILENAME,")
    sor.newline("\t\t\t\tu.FILEROWNUMBER,")

    for col in col_list:
        if col[1] == "EMAIL":
            sor.newline("\t\t\t\tpd.EMAIL,")
        else:
            sor.newline(f"\t\t\t\tu.{col[1]},")
    sor.trimend(1)
    sor.newline(f"\t\t\tFROM TMP.{table_name}Unique u")
    sor.newline("\t\t\tLEFT JOIN")
    sor.newline("\t\t\t(")
    sor.newline("\t\t\t\tSELECT")
    sor.newline("\t\t\t\t\tEMAIL,")
    sor.newline("\t\t\t\t\tID")
    sor.newline("\t\t\t\tFROM &database.STAGE.MARKETOPERSON")
    sor.newline("\t\t\t) pd")
    sor.newline("\t\t\tON u.LEADID = pd.ID")

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

    mergesp.newline(
        f"\t\tMERGE INTO STAGE.{table_name.upper()} dest USING (\n{sor.out()}\n\t\t) sor ON")

    for pk in pk_type_list:
        # if pk is string, lower
        if "VARCHAR" in pk[2].upper():
            mergesp.newline(f"\t\t\tlower(dest.{pk[1]}) = lower(sor.{pk[1]}) AND")
        else:
            mergesp.newline(f"\t\t\tdest.{pk[1]} = sor.{pk[1]} AND")

    mergesp.trimend(4)

    mergesp.newline("\t\tWHEN MATCHED AND")
    mergesp.newline("\t\t(")

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

# custom merge to handle activitylog
def fn_create_merge_sp_custom(table_name:str, pk_list:list, col_list:list, db_folder:str, runlog:object, std_ind:str, repo_root_folder:str, client:str, source_name:str, create_keyhash:str="0"):
    runlog.log("Running Marketo specific merge sp function")
    if table_name.upper() == "MARKETOACTIVITYLOG":
        merge_sp_name = fn_create_merge_sp_marketoactivity(table_name=table_name, pk_list=pk_list, col_list=col_list, db_folder=db_folder, runlog=runlog, std_ind=std_ind, repo_root_folder=repo_root_folder, client=client, source_name=source_name)
    else:
        merge_sp_name = create_merge_sp(table_name=table_name, pk_list=pk_list, col_list=col_list, db_folder=db_folder, runlog=runlog, std_ind=std_ind, repo_root_folder=repo_root_folder, client=client, source_name="marketo")

    return merge_sp_name

# custom flatten function to bypass activity types table
def fn_create_flatten_custom(source_name:str, table_name:str, table_name_raw:str, col_list:list, version:str, db_folder:str, runlog:object, repo_root_folder:str, client:str, worksheet: object):
    runlog.log("Running Marketo specific flatten function")

    # create flatten if table is not formstack submissions. Submissions gets populated by business rules.
    flatten_filename = ""
    if table_name.upper() != 'MARKETOACTIVITYTYPES':
        flatten_filename = create_flatten(source_name=source_name, table_name=table_name.lower(), table_name_raw=table_name_raw, col_list=col_list, version=version, db_folder=db_folder, runlog=runlog, repo_root_folder=repo_root_folder, client=client)

    return flatten_filename
