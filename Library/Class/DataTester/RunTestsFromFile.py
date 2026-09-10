from Library.Class.DataTester.TestDefinitionFile import *
from Library.Class.DataTester.TestsMain import *
from Library.Class.DataTester.TestResultsPage import *

# class to run tests given a test definition file
class RunTestsFromFile:
    def __init__(self, runlog:object):
        self.runlog = runlog
        return

    def setTestsInfo(self, client:str, database:str, sf_user:str, role:str, test_file_path:str, filter:str):
        self.testfilepath = test_file_path
        self.database = database
        self.sf_user = sf_user
        self.role = role
        self.filter = filter
        self.client = client

    def execTests(self):
        # validate parameters
        if self.database is None:
            raise Exception("Database not set")
        elif self.client.lower() not in self.database.lower():
            raise Exception("Client and Database do not match")

        if self.sf_user is None:
            raise Exception("Snowflake user is not set"
                            )
        if self.role is None:
            raise Exception("Snowflake role is not set")

        if self.testfilepath is None:
            raise Exception("Test file path is not set")

        if self.filter is None:
            raise Exception("Filter is not set")

        # read test definition file
        testlist = DefinitionFile(file_path=self.testfilepath, runlog=self.runlog)

        # define output folders
        outputfolder = outputTestFolder(self.testfilepath)

        # get filename
        filename = os.path.basename(os.path.abspath(self.testfilepath)).split(".")[0]

        # parse test file to get tests to run
        teststorun, query_params = testlist.parsetest(self.filter)

        self.runlog.log(f"::{len(teststorun)} tests found and will be executed.")
        if len(teststorun) == 0:
            self.runlog.log("No tests found. Exiting.")
            sys.exit()

        # create Tests class
        tester = testsMain(self.runlog)

        # connect to Snowflake
        tester.connect(sf_user=self.sf_user, snow_db=self.database, snow_role=self.role)

        # run tests
        resultsJSONfilename = tester.executeTests(tests_to_run=teststorun, log_folder=outputfolder, results_filename=filename)
        resultJSONfilepath = outputfolder + resultsJSONfilename

        # ======================================
        # Create Results HTML
        # ======================================
        headerSeparator = "=" * 50
        self.runlog.log(headerSeparator)
        self.runlog.log(f"::Start creating results page for {self.database} using:")
        self.runlog.log(f"Test results json: {resultJSONfilepath}")
        self.runlog.log(f"Test file: {self.testfilepath}")
        self.runlog.log(headerSeparator)

        page = ResultPage(sf_user=self.sf_user, runlog=self.runlog)
        page.setPageInfo(client=self.client, result_file_path=resultJSONfilepath)
        publishOutputFolderPath = page.buildAndPublish()

        self.runlog.log(f"::Test Result html saved to {publishOutputFolderPath}")

        return outputfolder, filename, resultsJSONfilename