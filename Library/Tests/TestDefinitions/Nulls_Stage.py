active = True
order = 2
testname = "Nulls - Stage"
expectedresult = 0
testquery = ("SELECT COUNT(*) as count\n"
           "FROM stage.{table_name}\n"
           "WHERE {Col_isnull}"
           ";")