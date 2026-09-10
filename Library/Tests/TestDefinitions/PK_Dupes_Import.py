active = False
order = 2
testname = "PK Dupes No Duplication on ID - Import"
expectedresult = 0
testquery = ("SELECT COUNT(*) as RCOUNT\n"
           "FROM(\n"
           "\tSELECT {PK_joined}, COUNT(*) as count\n"
           "\tFROM import.{table_name}\n"
           "\tGROUP BY {PK_joined}\n"
           "\tHAVING COUNT(*) <> 1\n"
           ");")