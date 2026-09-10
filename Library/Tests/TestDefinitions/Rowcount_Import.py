active = True
order = 1
testname = "Rowcount - Import"
expectedresult = ">0"
testquery = ("SELECT COUNT(*) as RCOUNT\n"
           "FROM import.{table_name};")