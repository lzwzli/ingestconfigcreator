from Library.Class.Document import *

def columnsString(col_list:list, pk_list:list):
    nonPkColumnsString = ""
    pkColumnsString = ""
    pkJoinCondition = ""
    pkDistinctCountString = ""
    pkListAgg = ""
    pkResultSelectString = ""
    pkResultOrderString = ""
    columnsSelectCastString = ""
    pkCol1 = ""
    pkIsnull = ""
    colIsnull = ""

    for row in col_list:
        colName = row[1]
        # colNameUpper = row[1].upper()

        # add all columns to select cast string
        columnsSelectCastString = f"{columnsSelectCastString}IFNULL(CAST({colName} AS STRING), '') AS {colName},\n\t"

        # first pk column
        if len(pk_list)>0:
            pkCol1 = pk_list[0]

        # build col is null for is null query
        colIsnull = f"{colIsnull}\n\t{colName} IS NULL OR"

        # if column is part of primary keys, add to pk variables
        if colName in pk_list:
            # build pk string
            pkColumnsString = f"{pkColumnsString}\n\t\t{colName},"

            # build pk join condition
            pkJoinCondition = f"{pkJoinCondition}\n\ta.{colName} = b.{colName} AND"

            # build pk string for distinct count
            pkDistinctCountString = f"{pkDistinctCountString} || {colName}_import || {colName}_stage"

            # build pk string for listagg
            pkListAgg = f"{pkListAgg} || '{colName}_import' || ' = '|| {colName}_import || ' ; '||'{colName}_stage' || = || {colName}_stage ||' ; '"

            # build pk select string for pivot query
            pkResultSelectString = f"{pkResultSelectString}a.{colName} AS {colName}_import, b.{colName} AS {colName}_stage,\n\t"

            # build pk order string for pivot query
            pkResultOrderString = f"{pkResultOrderString}{colName}_import, {colName}_stage, "

            # build pk is null for is null query
            pkIsnull = f"{pkIsnull}\n\t{colName} IS NULL OR"

        # if column is not part of primary keys, add to non pk variables
        else:
            nonPkColumnsString = f"{nonPkColumnsString}{colName}, "

    # trim leading and ending characters
    columnsSelectCastString = columnsSelectCastString[:-3]
    pkColumnsString = pkColumnsString[:-1]
    pkJoinCondition = pkJoinCondition[:-4]
    pkDistinctCountString = pkDistinctCountString[4:]
    pkListAgg = pkListAgg[4:]
    pkListAgg = f"{pkListAgg}|| spacer"
    pkResultSelectString = pkResultSelectString[:-2]
    pkResultOrderString = pkResultOrderString[:-2]
    nonPkColumnsString = nonPkColumnsString[:-2]
    pkIsnull = pkIsnull[:-3]
    colIsnull = colIsnull[:-3]

    return columnsSelectCastString, pkColumnsString, pkJoinCondition, pkDistinctCountString, pkListAgg, pkResultSelectString, pkResultOrderString, nonPkColumnsString, pkCol1, pkIsnull, colIsnull


def createTestDef(client:str, table_name:str, pk_list:list, col_list:list, test_name:str, exp_result:str, query_template:str):
    # get columns strings
    columnsSelectCastString, pkColumnsString, pkJoinCondition, pkDistinctCountString, pkListAgg, pkResultSelectString, pkResultOrderString, nonPkColumnsString, pkCol1, pkIsnull, colIsnull = columnsString(pk_list=pk_list, col_list=col_list)

    testQuery = query_template \
        .replace("{table_name}", table_name) \
        .replace("{PK_joined}", pkColumnsString) \
        .replace("{PK_import_data}", pkColumnsString) \
        .replace("{PK_joins}", pkJoinCondition) \
        .replace("{final_vars}", columnsSelectCastString) \
        .replace("{UNPIVOT_vars}", nonPkColumnsString) \
        .replace("{result_query_top_line}", pkResultSelectString) \
        .replace("{pks_not_matching}", pkListAgg) \
        .replace("{distinct_count_statement_vars}", pkDistinctCountString) \
        .replace("{result_order}", pkResultOrderString) \
        .replace("{client}", client) \
        .replace("{PK_col1}", pkCol1) \
        .replace("{PK_isnull}", pkIsnull) \
        .replace("{Col_isnull}", colIsnull)

    # make sure query ends with ';'
    if ";" not in testQuery[-5:]:
        testQuery = testQuery + ";"

    testDef = Document()

    fullTestName = f"--{table_name.upper()}_{test_name} | Expected Result:{exp_result}"

    testDef.newline(fullTestName)
    testDef.newline(testQuery)
    testDef.newline("")

    return testDef.out()

