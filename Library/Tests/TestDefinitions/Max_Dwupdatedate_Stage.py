active = True
order = 5
testname ="Max Dwupdatedate - Stage"
expectedresult = 0
testquery = ("SELECT\n"
             "\tCASE\n"
             "\t\tWHEN MAXDWUPD < DATEADD(DAY, -1, CURRENT_DATE())\n"
             "\t\tTHEN 1\n"
             "\t\tELSE 0\n"
             "\tEND AS STAGERECORDSOLD\n"
             "FROM (\n"
             "\tSELECT MAX(DWUPDATEDATE) AS MAXDWUPD\n"
             "\tFROM stage.{table_name}\n"
             ");")