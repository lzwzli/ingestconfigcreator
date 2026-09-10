from Library.FunctionFiles.Functions import *

def fanaticsuserdetails_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}FANATICSUSERDETAILS_BusRules{os.sep}"
    runlog.log("Generate Fanatics User Details Business Rules.")
    runlog.log("")

    fanaticsuserdetails_1_0(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    fanaticsuserdetails_2_0(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def fanaticsuserdetails_1_0(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # rule 1
    busrule = {}
    busrule["ruleName"] = "FanaticsUserDetails_1_0"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 0

    rulequerydoc = Document()
    rulequerydoc.newline("TRUNCATE TABLE &database.IMPORT.FANATICSUSERDETAILS;")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="FANATICSUSERDETAILS_1_0 TRUNCATE IMPORT.FANATICSUSERDETAILS RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def fanaticsuserdetails_2_0(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    busrule = {}
    busrule["ruleName"] = "fanaticsuserDetails_2_0"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 0

    rulequerydoc = Document()
    rulequerydoc.newline(f"INSERT INTO &database.IMPORT.FANATICSUSERDETAILS ")
    rulequerydoc.newline(f"SELECT")
    rulequerydoc.newline(f"\tFILEDATE,")
    rulequerydoc.newline(f"\tFILENAME,")
    rulequerydoc.newline(f"\tFILEROWNUMBER,")

    for col in col_list:
        rulequerydoc.newline(f"\t{col[1]},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline(f"FROM &database.IMPORT.FANATICSFEEDIMPORT;")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="FANATICSUSERDETAILS_2_0 INSERT INTO IMPORT.FANATICSUSERDETAILS RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return