active = True
order = 3
testname ="Import to Stage"
expectedresult = 0
testquery = ("SELECT COUNT(*) as RCOUNT\n"
           "FROM (\n"
           "\tSELECT * FROM import.{table_name} a\n"
           "\tLEFT JOIN stage.{table_name} b\n"
           "\tON {PK_joins}\n"
           "\tWHERE b.{PK_col1} IS NULL\n"
           ");")