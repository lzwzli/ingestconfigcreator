from Library.FunctionFiles.Functions import *

# Create FLATTENJSON CTE for use in Flatten SQL Insert query
def flattenjson(table_name:str, table_name_raw:str, col_list:list):
    jsonelements = []
    flattendoc = Document()

    # initialize table from
    from_table = f"FROM &database.IMPORT.ONETRUSTNEP_RAW raw"

    # create column lists for CTEs
    OTcols = []
    audcols = []
    purcols = []

    for col in col_list:
        src_col = col[0]
        tbl_col = col[1]

        # OT
        if "OT." in src_col:
            OTcols.append(src_col.replace("OT.", ""))
        elif "aud." in src_col:
            audcols.append(src_col.replace("aud.", ""))
        elif "pur." in src_col:
            purcols.append(src_col.replace("pur.", ""))

    # build OT CTE query
    OTquery = Document()

    OTquery.newline("\t\tSELECT")
    OTquery.newline("\t\t\traw.FILEDATE,")
    OTquery.newline("\t\t\traw.FILENAME,")
    OTquery.newline("\t\t\traw.FILEROWNUMBER,")
    for col in OTcols:
        OTquery.newline(f"\t\t\traw.JSONDATA:{col}::STRING AS {col},")
    OTquery.newline("\t\t\traw.JSONDATA:DataElements::VARIANT AS DataElements,")
    OTquery.newline("\t\t\traw.JSONDATA:Purposes::VARIANT AS Purposes")
    OTquery.newline("\t\tFROM(")
    OTquery.newline(f"\t\t\tSELECT *")
    OTquery.newline(f"\t\t\t{from_table}")
    OTquery.newline("\t\t) raw")

    # build DE CTE query
    DEquery = Document()

    DEquery.newline("\t\tSELECT")
    DEquery.newline("\t\t\tID,")
    DEquery.newline("\t\t\tele.Value:Name::STRING AS Name,")
    DEquery.newline("\t\t\tele.Value:Value::STRING AS Value")
    DEquery.newline("\t\tFROM OT,")
    DEquery.newline("\t\tTABLE(flatten(INPUT => OT.DataElements, OUTER=>True)) ele")

    # build DE_pivot_result query
    DEpivotresult = Document()

    DEpivotresult.newline("\t\tSELECT")
    DEpivotresult.newline("\t\t\tID,")
    for col in audcols:
        DEpivotresult.newline(f"\t\t\t{col},")
    DEpivotresult.trimend(1)
    DEpivotresult.newline("\t\tFROM DE")
    DEpivotresult.newline("\t\t\tPivot(")
    DEpivotresult.newline("\t\t\t\tMAX(Value) FOR Name IN(")
    for col in audcols:
        DEpivotresult.newline(f"\t\t\t\t\t'{col}',")
    DEpivotresult.trimend(1)
    DEpivotresult.newline("\t\t\t\t)")
    DEpivotresult.newline("\t\t\t)")
    DEpivotresult.newline("\t\t\tAS DEPivot(")
    DEpivotresult.newline("\t\t\t\tID,")
    for col in audcols:
        DEpivotresult.newline(f"\t\t\t\t{col},")
    DEpivotresult.trimend(1)
    DEpivotresult.newline("\t\t\t)")

    # build AudienceInfo query
    Audinfo = Document()

    Audinfo.newline("\t\tSELECT *")
    Audinfo.newline("\t\tFROM DE_Pivot_Result")

    # build Purposes query
    pur = Document()

    pur.newline("\t\tSELECT")
    pur.newline("\t\t\tOT.ID,")
    for col in purcols:
        pur.newline(f"\t\t\tpur_fl.value:{col}::STRING AS {col},")
    pur.trimend(1)
    pur.newline("\t\tFROM OT,")
    pur.newline("\t\tTABLE(flatten(INPUT => OT.Purposes)) pur_fl")

    # build final query
    endquery = Document()

    endquery.newline("\tSELECT")
    endquery.newline("\t\tOT.FILEDATE,")
    endquery.newline("\t\tOT.FILENAME,")
    endquery.newline("\t\tOT.FILEROWNUMBER,")
    for col in col_list:
        endquery.newline(f"\t\t{col[0]} AS {col[1]},")
    endquery.trimend(1)
    endquery.newline("\tFROM OT")
    endquery.newline("\tINNER JOIN AudienceInfo aud ON OT.Id = aud.ID")
    endquery.newline("\tINNER JOIN Purposes pur ON OT.Id = pur.ID")

    # build final query
    finalquery = Document()

    finalquery.newline("\tWITH OT AS (")
    finalquery.newline(OTquery.out())
    finalquery.newline("\t),")
    finalquery.newline("\tDE AS (")
    finalquery.newline(DEquery.out())
    finalquery.newline("\t),")
    finalquery.newline("\tDE_Pivot_Result AS (")
    finalquery.newline(DEpivotresult.out())
    finalquery.newline("\t),")
    finalquery.newline("\tAudienceInfo AS (")
    finalquery.newline(Audinfo.out())
    finalquery.newline("\t),")
    finalquery.newline("\tPurposes AS (")
    finalquery.newline(pur.out())
    finalquery.newline("\t)")
    finalquery.newline(endquery.out())

    return finalquery.out()