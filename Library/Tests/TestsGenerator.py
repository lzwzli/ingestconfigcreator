import glob
from Library.Tests.TestsFunctions import *
from Library.FunctionFiles.Functions import *

def createTest(client:str, table_name:str, pk_list:list, col_list:list, db_folder:str, runlog:object):
    runlog.log(f"Creating tests for {table_name}:")

    testFile = Document()
    output_folder = f"{db_folder}Tests{os.sep}{table_name.upper()}{os.sep}"

    # get list of tests
    testDefinitionsFolder = f"{os.getcwd()}{os.sep}Library{os.sep}Tests{os.sep}TestDefinitions{os.sep}*.py"
    testFiles = glob.glob(testDefinitionsFolder)

    # get test file name
    testList = []
    for testFilesItem in testFiles:
        testList.append(testFilesItem.split(os.sep)[-1].replace(".py",""))

    # load and generate tests
    testDefList = []
    for testListItem in testList:
        # import test file
        testPackage = f"Library.Tests.TestDefinitions.{testListItem}"
        testDef = import_module(testPackage)

        # add active tests to testDeflist
        if testDef.active:
            testDefList.append([testDef.order, testDef.testname, testDef.expectedresult, testDef.testquery])

    # filter out inactive tests and order test list
    testIndex = 1
    testDefListOrdered = []
    while len(testDefList) > len(testDefListOrdered):
        for testDefListItem in testDefList:
            # add test to ordered list if order matches index
            if testDefListItem[0] == testIndex:
                # add test elements [testname, expectedresult, testquery]
                testDefListOrdered.append([testDefListItem[1], testDefListItem[2], testDefListItem[3]])

        testIndex += 1

    # generate tests based on ordered list
    for testDefListOrderedItem in testDefListOrdered:
        test_name = testDefListOrderedItem[0]
        exp_result = testDefListOrderedItem[1]
        query_template = testDefListOrderedItem[2]

        runlog.log(f"- {test_name}")

        queryDef = createTestDef(client=client, table_name=table_name, pk_list=pk_list, col_list=col_list, test_name=test_name, exp_result=exp_result, query_template=query_template)
        testFile.newline(queryDef)

    # write tests out to file
    filewrite(folder=output_folder, filename=f"{table_name.upper()} Tests Queries.sql", content=testFile.out())

    return testFile.out()