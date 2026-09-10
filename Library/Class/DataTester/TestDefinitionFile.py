import sys

# Input file
class DefinitionFile:
    def __init__(self, file_path:str, runlog:object):
        self.runlog = runlog
        try:
            self.testfile = str(open(file_path, "r").read())
        except Exception as e:
            self.runlog.log(f"ERROR: {e}")
            sys.exit()

        return

    def parsetest(self, value:str):
        self.runlog.log("::Getting tests from definition file")
        # get tests split by ;\n
        tests = self.testfile.split(";\n")

        # parse input
        # initialize variables
        range = []
        val_list = []
        test_list_return = []

        # check if value is a non zero number, i.e 3
        if str(value) != "0" and value.isnumeric():
            range.insert(0, value)

        # check if value is a range of numbers, i.e. 3-5 or 3 - 5
        elif str(value).replace(" ","").replace("-","").isnumeric():
            range = str(value).split("-")

        # else leave range and val_list empty
        # if it is one or more comma separated string values, i.e. contact, questions
        else:
            val_list = str(value).split(",")

        #--------------
        # find tests
        #--------------
        # return all tests if value is 0
        if str(value) == "0":
            test_list_return = tests

        # if range is not empty, then either return specific index of test or return a range
        elif len(range)>0:
            # if range only has one value, return the top N tests
            if len(range) == 1:
                idx = int(range[0])
                test_list_return = tests[0:idx]

            # if range has 2 values, return tests within range
            elif len(range) == 2:
                # set min
                if int(range[0]) == 0:
                    min = 0
                else:
                    min = int(range[0])-1

                # set max
                max = int(range[1])

                # return tests in range
                test_list_return = tests[min:max]

        # if val_list is not empty, return tests that contain values in list
        elif len(val_list)>0:
            testlist = []
            # loop for each test
            for test in tests:
                # loop for each value in val_list
                for val in val_list:
                    # if value string is in test, add test to testlist
                    if val.strip() in test:
                        testlist.append(test)

            test_list_return = testlist

        # return tests that contain value
        else:
            self.runlog.log("Error: torun variable is empty")

        #----------------------------
        # find parameters in query
        #----------------------------
        self.runlog.log(f"Finding parameters in queries")
        test_list_return_final = []
        # dict of parameters in query and their replacement values
        query_params = {}
        for testquery in test_list_return:
            # ask for run specific values
            if "{" in testquery and "}" in testquery:
                querytoparse = testquery

                # while the { character is in querytoparse, keep looping to find parameter values
                while "{" in testquery:

                    # find parameter by keying in on positions of { and }
                    startidx = testquery.index("{") + 1
                    endidx = testquery.index("}")

                    # get parameter
                    param = testquery[startidx:endidx]

                    # if parameter is new, ask for value and replace in query, add key to dict
                    if query_params.get(param) == None:
                        self.runlog.log(f'Query parameter "{param}" found.')

                        # ask for replacement value
                        replaceval = input(f'Please enter value for "{param}": ')
                        self.runlog.log(f'"{param}" replaced with "{replaceval}"')

                        # add parameter and value into list
                        query_params[param] = replaceval

                        # replace parameter with value
                        testquery = testquery.replace("{" + str(param) + "}", str(replaceval))

                        # write remaining string starting from } to querytoparse to continue the while loop
                        querytoparse = querytoparse[endidx:]

                    # if parameter is already in query_params dict, then get key value to replace in query
                    else:
                        replaceval = query_params[param]

                        # replace parameter with value
                        testquery = testquery.replace("{" + str(param) + "}", str(replaceval))

                        # write remaining string starting from } to querytoparse to continue the while loop
                        querytoparse = querytoparse[endidx:]

            # add test query to test_list_return_final
            test_list_return_final.append(testquery)

        return test_list_return_final, query_params

    def findTestByName(self, test_name:str):
        self.runlog.log(f"::Finding test query for {test_name}")
        # get tests split by ;\n
        tests = self.testfile.split(";\n")

        for test in tests:
            if test_name in test:
                testquery = test.strip("\n").strip().split("\n",1)[1]
                return testquery
