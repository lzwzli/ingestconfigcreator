active = True
order = 4
testname = "PK Dupes No Duplication on ID - Stage"
expectedresult = 0
testquery = ("SELECT COUNT(*) as RCOUNT\n"
           "FROM(\n"
           "\tSELECT {PK_joined},\n\t\tCOUNT(*) as RC\n"
           "\tFROM stage.{table_name}\n"
           "\tGROUP BY {PK_joined}\n"
           "\tHAVING COUNT(*) <> 1\n"
           ");")