from Library.FunctionFiles.Functions import *

def archticsmanifest_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics Manifest
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsManifest_BusRules{os.sep}"
    runlog.log("Generate Archtics Manifest Business Rules.")
    runlog.log("")

    archticsmanifest_1_3(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)
    archticsmanifest_2_3(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)


    return

def archticsmanifest_1_3(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 1_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsManifest_1_3"
    busrule["runOrder"] = 1
    busrule["runPosition"] = 3

    rulequerydoc = Document()

    pk_string = create_pk_string(pk)

    rulequerydoc.append("INSERT INTO &database.TMP.MANIFEST_DELETES")
    rulequerydoc.newline("SELECT")
    rulequerydoc.newline("\tS.*,")
    rulequerydoc.newline("\tCURRENT_TIMESTAMP() as DELETEDATETIME")
    rulequerydoc.newline("FROM &database.STAGE.ARCHTICSMANIFEST S")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline(pk_string)
    rulequerydoc.newline("NOT IN (")
    rulequerydoc.newline("\tSELECT DISTINCT")
    rulequerydoc.newline(f"\t{pk_string}")
    rulequerydoc.newline("\tFROM &database.IMPORT.ARCHTICSMANIFEST I")
    rulequerydoc.newline(")")
    rulequerydoc.newline("AND S.MANIFESTID IN (")
    rulequerydoc.newline("\tSELECT DISTINCT MANIFESTID FROM &database.IMPORT.ARCHTICSMANIFEST I")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsManifest_1_3 INSERT INTO TMP.MANIFEST_DELETES RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

def archticsmanifest_2_3(col_list: list, pk: list, bus_rule_obj: object, output_folder: str):
    # ----------------------------------------------------------------
    # Rule 2_3
    # ----------------------------------------------------------------
    busrule = {}
    busrule["ruleName"] = "ArchticsManifest_2_3"
    busrule["runOrder"] = 2
    busrule["runPosition"] = 3

    rulequerydoc = Document()

    pk_string = create_pk_string(pk)

    rulequerydoc.append("DELETE FROM &database.STAGE.ARCHTICSMANIFEST S")
    rulequerydoc.newline("WHERE")
    rulequerydoc.newline(pk_string)
    rulequerydoc.newline("NOT IN (")
    rulequerydoc.newline("\tSELECT DISTINCT")
    rulequerydoc.newline(f"\t{pk_string}")
    rulequerydoc.newline("\tFROM &database.IMPORT.ARCHTICSMANIFEST I")
    rulequerydoc.newline(")")
    rulequerydoc.newline("AND S.MANIFESTID IN (")
    rulequerydoc.newline("\tSELECT DISTINCT MANIFESTID FROM &database.IMPORT.ARCHTICSMANIFEST I")
    rulequerydoc.newline(");")

    # write out Rule Query to file
    filewrite(folder=output_folder, filename="ArchticsManifest_2_3 DELETE FROM STAGE.ARCHTICSMANIFEST RULE QUERY.sql",
              content=rulequerydoc.out())

    busrule["ruleQuery"] = rulequerydoc.out_str()

    bus_rule_obj.add_rule(busrule)

    return

