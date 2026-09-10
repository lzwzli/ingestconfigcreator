from Library.FunctionFiles.Functions import *

def fanaticsorderdetails_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}FANATICSORDERDETAILS_BusRules{os.sep}"
    runlog.log("Generate Fanatics Order Details Business Rules.")
    runlog.log("")

    fanaticsorderdetails_1_0(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    fanaticsorderdetails_2_0(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def fanaticsorderdetails_1_0(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    # rule 1
    busrule = {}
    busrule["ruleName"] = "FanaticsOrderDetails_1_0"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 0

    rulequerydoc = Document()
    rulequerydoc.newline("TRUNCATE TABLE &database.IMPORT.FANATICSORDERDETAILS;")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="FANATICSORDERDETAILS_1_0 TRUNCATE IMPORT.FANATICSORDERDETAILS RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def fanaticsorderdetails_2_0(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):
    busrule = {}
    busrule["ruleName"] = "FanaticsOrderDetails_2_0"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 0

    rulequerydoc = Document()
    rulequerydoc.newline(f"INSERT INTO &database.IMPORT.FANATICSORDERDETAILS ")
    rulequerydoc.newline(f"SELECT")
    rulequerydoc.newline(f"\tFILEDATE,")
    rulequerydoc.newline(f"\tFILENAME,")
    rulequerydoc.newline(f"\tFILEROWNUMBER,")

    for col in col_list:
        rulequerydoc.newline(f"\t{col[1]},")

    rulequerydoc.trimend(1)

    rulequerydoc.newline(f"FROM &database.IMPORT.FANATICSFEEDIMPORT;")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="FANATICSORDERDETAILS_2_0 INSERT INTO IMPORT.FANATICSORDERDETAILS RULE QUERY.sql", content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return