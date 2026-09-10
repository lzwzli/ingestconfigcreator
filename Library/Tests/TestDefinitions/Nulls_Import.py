active = True
order = 2
testname = "Nulls - Import"
expectedresult = 0
testquery = ("SELECT COUNT(*) as count\n"
           "FROM import.{table_name}\n"
           "WHERE {Col_isnull}"
           ";")