from Library.FunctionFiles.Functions import *

custom_filedate = "TO_CHAR(REPLACE(REGEXP_SUBSTR(METADATA$FILENAME, '[0-9]{4}-[0-9]{2}-[0-9]{2}', 1, 1), '_', '-')) "

# ----------------------------------------------------------------
# Update timestamp business rule
# ----------------------------------------------------------------
def busrule_updatelavatimestamps(table_name:str, col_list:list, db_folder:str, bus_rule_obj:object, runlog:object):
    runlog.log(f"Generate {table_name} Business Rules.")
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}{table_name.upper()}_BusRules{os.sep}"

    timestampcols = []
    for col in col_list:
        if "TIMESTAMP" in col[2].upper():
            timestampcols.append(col[1])

    if len(timestampcols) > 0:
        # ----------------------------------------------------------------
        # Rule 0_0
        # ----------------------------------------------------------------
        busrule = {}
        busrule["ruleName"] = f"{table_name.upper()}_0_0"
        busrule["runOrder"] = 0
        busrule["runPosition"] = 0

        rulequerydoc = Document()

        rulequerydoc.append(f"UPDATE &database.import.{table_name}")
        rulequerydoc.newline("SET")
        for tcol in timestampcols:
            # rulequerydoc.newline(f"\t{tcol} = IFF((RIGHT({tcol},5) ILIKE '%-%' OR RIGHT({tcol},5) ILIKE '%+%'), {tcol}, {tcol} || ' -0000'),")
            rulequerydoc.newline(f"\t{tcol} = CASE")
            rulequerydoc.newline(f"\t\tWHEN {tcol} ILIKE '%+00' THEN REPLACE({tcol},'+00','') || ' -0000'")
            rulequerydoc.newline(f"\t\tWHEN (RIGHT({tcol},5) NOT ILIKE '%-%' AND RIGHT({tcol},5) NOT ILIKE '%+%') THEN {tcol} || ' -0000'")
            rulequerydoc.newline(f"\t\tELSE {tcol}")
            rulequerydoc.newline(f"\tEND,")

        rulequerydoc.trimend(1)
        rulequerydoc.newline(";")

        # write out Rule Query to file
        filewrite(folder=output_folder, filename=f"{table_name}_0_0 UPDATE IMPORT.{table_name} TIMESTAMPS RULE QUERY.sql", content=rulequerydoc.out())

        busrule["ruleQuery"] = rulequerydoc.out_str()

        bus_rule_obj.add_rule(busrule)

    return

# ----------------------------------------------------------------
# Append Business Rules
# ----------------------------------------------------------------
def fn_busrules_append(worksheet:object, bus_rule_obj:object, db_folder:str, runlog:object):
    runlog.log("Running Lava specific busrules append function")

    # get table name
    table_name = worksheet.table_name()

    # get columns
    col_list = worksheet.columns()

    busrule_updatelavatimestamps(table_name=table_name, col_list=col_list, db_folder=db_folder, bus_rule_obj=bus_rule_obj, runlog=runlog)

    return