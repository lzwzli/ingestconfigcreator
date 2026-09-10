import snowflake.connector as snow
from Library.FunctionFiles.Functions import *
from connection_info import *

# Tests
class testsMain:
    def __init__(self, runlog:object):
        # define variables
        self.runlog = runlog

        #resultJSON
        self.resultJSONList = []

    def connect(self, sf_user:str, snow_db:str, snow_role:str):
        # create Snowflake connection
        self.runlog.log("::Connecting to Snowflake using info from connection_info.py:")
        self.runlog.log(f"User={sf_user}, Account={sf_account}, Warehouse={sf_warehouse}, Role={snow_role}, Database={snow_db}")
        self.database = snow_db.upper()
        self.client = self.database.replace("QA","").replace("DEV","")
        try:
            self.conn = snow.connect(
                user=sf_user,
                account=sf_account,
                warehouse=sf_warehouse,
                authenticator='externalbrowser',
                role = snow_role,
                database = snow_db
            )

        except Exception as e:
            self.runlog.log(f"ERROR: {e}")
            sys.exit()
        self.runlog.log("::Connected to Snowflake.")

    def executeTests(self, tests_to_run:list, log_folder:str, results_filename:str):
        print_section(msg="Executing tests", runlog=self.runlog)

        # define result output file name
        results_JSON_filename = f"{results_filename} Results.json"

        # try to run queries
        try:
            with self.conn.cursor() as cur:

                # initialize counts
                testcount = 0
                skipcount = 0
                passcount = 0
                failcount = 0

                # run each test query
                for testquery in tests_to_run:
                    #testJSON
                    testJSON = {}

                    # get test name
                    testsplit = testquery.split("\n")
                    for str_val in testsplit:
                        if "--" in str_val:
                            testname = str_val
                            break

                    # exit if tests has already been run
                    if self.runlog.check(testname):
                        skipcount = skipcount + 1
                        self.runlog.log(f"{testname} has already been run.")
                        self.runlog.log("")
                        continue

                    # log test name
                    self.runlog.log(f"{testname}")
                    self.runlog.append("::Parsing test --> ")
                    nl = "\n"
                    # if test name does not contain '|' which means it didn't have an expected result column, inject one
                    testnameparts = testname.lstrip("--").split("|")

                    # testname only has name, no expected results
                    if len(testnameparts) == 1:
                        testnameoutput = testnameparts[0]
                        testexpectedresult = "0"

                        #testJSON
                        testJSON["testname"] = testnameoutput
                        testJSON["expectedresult"] = ""

                    # test name has name and expected results
                    elif len(testnameparts) == 2:
                        testnameoutput = testnameparts[0].strip()
                        testexpectedresult = testnameparts[1].strip()

                        #testJSON
                        testJSON["testname"] = testnameoutput
                        testJSON["expectedresult"] = testexpectedresult.replace("Expected Result:","")

                    else:
                        raise Exception("testname has more than 2 parts")

                    # increment test count
                    testcount = testcount + 1

                    #testJSON
                    testJSON["database"] = self.database

                    # replace '&' placeholder variables
                    testquery = testquery.strip("\n").split("\n",1)[1]
                    testquery = testquery.replace("&database", self.database)\
                                .replace("&leagueDBName", self.database)\
                                .replace("&teamAbbr", self.client)

                    # try to run query
                    self.runlog.append(f"Running test --> ")
                    execfail = False
                    execerror = ""
                    res_count = 0

                    testJSON["query"] = testquery

                    try:
                        # run query
                        cur.execute(testquery)

                        # get result rows
                        res = cur.fetchmany(100)
                        res_count = len(res)

                    except Exception as e:
                        errormsg = str(e).replace("\n","")
                        execerror = f"ERROR: {errormsg}"
                        execfail = True
                        res = [execerror]

                    # log completion
                    if execfail:
                        self.runlog.log("Completed with Errors")
                    else:
                        self.runlog.log("Completed")

                    # set pass fail
                    result = ""

                    # extract result number
                    resultNum = ""
                    re_offset = " " * 8

                    # query failed to run
                    if execfail:
                        result = execerror

                    # no result
                    elif res_count==0:
                        self.runlog.append("::Result is empty --> ")
                        resOne = "N/A"
                        try:
                            resultStr, passcount, failcount = self.parseResults(exp_result=testexpectedresult, result=resOne, pass_count=passcount, fail_count=failcount)
                            result = f"{resOne} {resultStr}"
                        except Exception as e:
                            self.runlog.log(f"ERROR: {e}\n")
                            self.runlog.log(f"Query Result: \n{resOne}")
                            continue

                    # result only has one row
                    elif res_count==1:
                        self.runlog.append("::Result has single row --> ")
                        resOne = str(res[0]).strip()\
                                            .replace("(","")\
                                            .replace(")","")\
                                            .replace(",","")

                        # extract value
                        if "'" in resOne:
                            resOne = resOne.split("'")[1]

                        try:
                            resultStr, passcount, failcount = self.parseResults(exp_result=testexpectedresult, result=resOne, pass_count=passcount, fail_count=failcount)
                            result = f"{resOne} {resultStr}"
                        except Exception as e:
                            self.runlog.log(f"ERROR: {e}\n")
                            self.runlog.log(f"Query Result: \n{resOne}")
                            continue

                    # result has multiple rows
                    else:
                        # result less than 10 rows. Process result
                        if res_count <= 10:
                            self.runlog.append(f"::Result has {res_count} rows --> ")

                            # process result
                            for re in res:

                                # convert to string
                                re = str(re)

                                # extract value
                                if "'" in re:
                                    re = re.split("'")[1]
                                result = f"{result}\n{re_offset}{re}"

                            # remove leading offset
                            result = result[len(re_offset) + 1:]
                            try:
                                # parse and append result string
                                resultStr, passcount, failcount = self.parseResults(exp_result=testexpectedresult,
                                                                                    result=result, pass_count=passcount,
                                                                                    fail_count=failcount)
                                result = f"{result}\n{re_offset}{resultStr}"
                            except Exception as e:
                                self.runlog.log(f"ERROR: {e}")
                                self.runlog.log(f"Query Result: \n{resOne}")
                                continue

                        # result is more than 10 rows. Don't process result
                        else:
                            self.runlog.append(f"::Result has more than {res_count} rows --> ")

                            # set result message
                            resOne = "N/A"
                            try:
                                resultStr, passcount, failcount = self.parseResults(exp_result=testexpectedresult,
                                                                                    result=resOne, pass_count=passcount,
                                                                                    fail_count=failcount)
                                result = f"Result > 10 rows. Run in Snowflake for full results. {resultStr}"
                            except Exception as e:
                                self.runlog.log(f"ERROR: {e}\n")
                                self.runlog.log(f"Query Result: \n{resOne}")
                                continue


                    # log results
                    self.runlog.log(f"RESULT: {result}")
                    self.runlog.log("")

                    # build result for result log. Remove new line, offset and extra comma before pass/fail string
                    resultlogresult = result.replace(f"\n{re_offset}", ", ").replace(", ("," (")

                    #testJSON
                    testJSON["result"] = resultlogresult

                    #resultJSON
                    self.resultJSONList.append(testJSON)

                self.runlog.log("::All tests executed.")

                #resultJSON
                resultJSON = json.dumps(self.resultJSONList)

                print_section(msg="Results", runlog=self.runlog)

                # write results
                filewrite(folder=log_folder, filename=results_JSON_filename, content=resultJSON)

                # count pass fail
                self.runlog.log(f"Found:    {len(tests_to_run)}")
                # add skip count if it is more than 0
                if skipcount >0:
                    self.runlog.log(f"Skipped*: {skipcount}")

                self.runlog.log(f"Ran:      {testcount}")
                self.runlog.log(f"Pass:     {passcount}")
                self.runlog.log(f"FAIL:     {failcount}")

                # add skip count explanation
                if skipcount > 0:
                    self.runlog.log("")
                    self.runlog.log("*Skipped tests are due to duplicate test names or empty lines at end of test file.*")

                return results_JSON_filename

        except Exception as e:
            self.runlog.log(f"ERROR: {e}")
        finally:
            # close connection
            self.conn.close()

    # parse results
    def parseResults(self, exp_result:str, result:str, pass_count:int, fail_count:int):

        # return N/A increment fail count if result is N/A
        if result == "N/A":
            result = "(Unknown)"
            fail_count += 1
            return result, pass_count, fail_count

        # start parsing real results
        self.runlog.log("Parsing result")

        # parse expected result
        if "\n" not in exp_result:

            # parse the expected result if it contains ':'
            if ":" in exp_result:
                exp_result_num = exp_result.split(":")[1]
            # otherwise, assume expected result is a singular value
            elif len(exp_result) > 0:
                exp_result_num = exp_result
            # fallback to 0 if expected result is empty
            else:
                exp_result_num = 0

            # parse the operator in exp result num
            if ">" in exp_result_num:
                exp_op = ">"
                expected = exp_result_num.replace(">", "")
            elif ">=" in exp_result_num:
                exp_op = ">="
                expected = exp_result_num.replace(">=","")
            elif "<" in exp_result_num:
                exp_op = "<"
                expected = exp_result_num.replace("<","")
            elif "<=" in exp_result_num:
                exp_op = "<="
                expected = exp_result_num.replace("<=","")
            else:
                exp_op = "=="
                expected = exp_result_num.replace(",", "")
                if len(expected)<1:
                    expected = "0"
        else:
            expected = "0"

        # if result is a single row, conclude result based on expected result
        if "\n" not in result:
            parsedResult = result.split(":")
            if len(parsedResult) > 1:
                resultNum = parsedResult[1].strip()\
                    .replace("(","")\
                    .replace(")","")\
                    .replace(",","")
            else:
                resultNum = parsedResult[0]

            # conclude result
            resultNum = int(resultNum)

            # try to cast "expected" as number
            if expected.isnumeric():
                expected = int(expected)

                if ((exp_op == "==" and resultNum == expected)
                        or (exp_op == "<" and resultNum < expected)
                        or (exp_op == "<=" and resultNum <= expected)
                        or (exp_op == ">" and resultNum > expected)
                        or (exp_op == ">=" and resultNum >= expected)):
                    result = "(Pass)"
                    pass_count = pass_count + 1
                else:
                    result = "(FAIL)"
                    fail_count = fail_count + 1
            else:
                result = "(Unknown)"

        # if result is multi-row, check if result is more than 2 rows. If not, compare the result number of each row. Pass if match
        else:
            if result.count("\n") > 1:
                result = ""
                return result, pass_count, fail_count

            # get each row
            resultList = result.split("\n")
            resultTally = 0

            # parse each row
            for re in resultList:
                # remove trailing spaces and commas
                re=re.strip().strip(",")

                parsedResult = re.split(":")

                # get result number
                resultNum = 0
                # if result has a string before the number, i.e. import: 0
                if len(parsedResult) > 1:
                    if parsedResult[1].strip().isnumeric():
                        resultNum = int(parsedResult[1].strip())

                # result is just a single number
                else:
                    if parsedResult[0].strip().isnumeric():
                        resultNum = int(parsedResult[0].strip())

                # get the absolute number of the diff between resultTally and resultNum
                resultTally = abs(resultTally - resultNum)

            # conclude result
            if resultTally == 0:
                result = "(Pass)"
                pass_count = pass_count + 1
            else:
                result = "(FAIL)"
                fail_count = fail_count + 1

        return result, pass_count, fail_count