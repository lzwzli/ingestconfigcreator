import argparse

from Library.Class.DataTester.RunTestsFromFile import *
from Library.Class.Logger import *
from Library.FunctionFiles.Functions import *
from version import *

def RunTests():

    # ----------------------------------------------------------------
    # try import dependencies
    # ----------------------------------------------------------------
    try:
        import snowflake.connector
    except ModuleNotFoundError:
        print("Please run 'pip install snowflake-connector-python' to install dependency package.")
        sys.exit(1)

    runlog = Logger()
    runlog.log(f"Data Tester version {version}. Released {releasedate}.")
    runlog.log("FUNCTION: Run tests from a test definition file.")
    runlog.log("")

    # parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--testfile", help="input path to test definition file")
    parser.add_argument("--filter", help="enter index range of tests or test string search")
    parser.add_argument("--sf_user", help="enter snowflake user")
    parser.add_argument("--client", help="enter client name")
    parser.add_argument("--db", help="enter database name")
    parser.add_argument("--role", help="enter snowflake role")
    args = parser.parse_args()

    # define variables
    testfilepath = args.testfile
    filter = args.filter
    sf_user = args.sf_user
    client = args.client
    database = args.db
    role = args.role

    # ask for run profile
    load_runProfile = "init"
    while load_runProfile == "init" or (load_runProfile.upper() != "Y" and load_runProfile.upper() != "N"):
        load_runProfile = input("Load run profile (.dtp file)? [Y/N]: ")

    if load_runProfile.upper() == "Y":
        print("Select run profile from dialog. Dialog may be hidden behind other windows.")
        runProfilePath = fileDialog(title="Select run profile", filetype=("Data Tester Profile", ".dtp"))
        runProfile = str(open(runProfilePath, "r").read())
        runProfileList = runProfile.split("\n")

        # get profile variable dictionary
        runProfileDict = {}
        runProfileDict = getProfileDict(profilelist=runProfileList)

        # load profile variables
        client = loadProfileVars(runProfileDict, varname="client")
        database = loadProfileVars(runProfileDict, varname="database")
        sf_user = loadProfileVars(runProfileDict, varname="sf_user")
        role = loadProfileVars(runProfileDict, varname="role")
        testfilepath = loadProfileVars(runProfileDict, varname="testfilepath")
        filter = loadProfileVars(runProfileDict, varname="filter")

        runlog.log(f'::Loaded profile from "{runProfilePath}"')

        # confirm database to run tests against
        confirmdatabase = input(f"Run tests using {database}? [Y/N]: ")

        # clear database if confirm is N
        if confirmdatabase.upper() == "N":
            database = None

    # ask for arguments
    # test file
    while testfilepath is None or testfilepath == "":
        print("Select SQL test definition file from dialog. Dialog may be hidden behind other windows.")
        testfilepath = fileDialog(filetype=("SQL", ".sql"), title="Select SQL test definition file")
        # exit if no file provided when user hits cancel
        if testfilepath == "":
            runlog.log("ERROR: No File Selected. Exiting.")
            sys.exit()
        else:
            runlog.log(f"Test definition file: '{testfilepath}'")

    # client
    while client is None or client == "":
        client = input("Enter client name: ")

    client = client.upper()

    # database
    while database is None or database == "":
        database = input("Enter database name to run test(s) against: ")

    database = database.upper()

    # sf username
    while sf_user is None or sf_user == "":
        sf_user = input("Enter Snowflake user (email): ")

    # role
    while role is None or role == "":
        role = input("Enter Snowflake role to use to run test(s) with: ")

    # tests to run
    while filter is None:
        filter = input("[Optional] Enter index range of tests (i.e. 1-4) or test string search: ")

    if filter == "":
        filter = "0"

    # define output folder for logs
    outputfolder = outputTestFolder(testfilepath)

    # log
    runlog.log(f"::Test Definition File = {testfilepath}")
    runlog.log(f"::Filter = {filter}")
    runlog.log(f"::Client = {client}")
    runlog.log(f"::Database = {database}")
    runlog.log(f"::User = {sf_user}")
    runlog.log(f"::Role = {role}")
    runlog.log("")

    # Error out if client and database don't match
    if client.lower() not in database.lower():
        print(f'ERROR: Database "{database}" is incorrect for Client "{client}" !')
        sys.exit()

    # generate command with variables
    runlog.log("::Direct Command:")
    runlog.log(f"python .\\RunTests.py --db \"{database}\" --role \"{role}\" --testfile \"{testfilepath}\" --filter \"{filter}\"")
    runlog.log("")

    # generate run profile file
    if load_runProfile.upper() == "N":
        profilename = f"DataTesterProfile_{client}_{database}_RunTests.dtp"
        dtplogmsg = CreateDTP(profilename=profilename, client=client, database=database, role=role, testfilepath=testfilepath, outputfolder=outputfolder, sf_user=sf_user, testfilter=filter)

        runlog.log(dtplogmsg)

    # instantiate runTests class
    runTest = RunTestsFromFile(runlog)
    runTest.setTestsInfo(client=client, database=database, sf_user=sf_user, role=role, test_file_path=testfilepath, filter=filter)

    # initialize variable
    outputfolder = ""
    filename = ""
    resultsJSONfilename = ""

    # try to run tests
    try:
        outputfolder, filename, resultsJSONfilename = runTest.execTests()

    except Exception as e:
        runlog.log(f"ERROR: {str(e)}")
        outputfolder = outputFolder(testfilepath)

    # create log
    runlog_filename = f"{filename} Run Log.txt"
    runlog.log("")
    runlogmsg = runlog.out()

    # write log
    filewrite(folder=outputfolder, filename=runlog_filename, content=runlogmsg)

    print(f"Test Output \"{resultsJSONfilename}\" and \"{runlog_filename}\" created in: {outputfolder}\n")

if __name__ == '__main__':
    RunTests()