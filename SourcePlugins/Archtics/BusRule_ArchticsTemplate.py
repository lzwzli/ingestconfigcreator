from Library.FunctionFiles.Functions import *

def archticsattendance_busrules(col_list:list, pk:list, bus_rule_obj:object, db_folder:str, runlog:object):
    # ----------------------------------------------------------------
    # Archtics Attendance
    # ----------------------------------------------------------------
    output_folder = f"{db_folder}ForReferenceOnly{os.sep}ArchticsAttendance_BusRules{os.sep}"
    runlog.log("Generate Archtics Attendance Business Rules.")
    runlog.log("")

    archticsattendance_1_1(col_list=col_list, pk=pk, bus_rule_obj=bus_rule_obj, output_folder=output_folder)

    return

def archticsattendance_1_1(col_list:list, pk:list, bus_rule_obj:object, output_folder:str):


    return