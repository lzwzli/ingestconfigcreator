active = True
order = 2
testname = "PK Nulls - Import"
expectedresult = 0
testquery = ("SELECT COUNT(*) as count\n"
           "FROM import.{table_name}\n"
           "WHERE {PK_isnull}"
           ";")