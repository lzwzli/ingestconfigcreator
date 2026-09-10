from Library.FunctionFiles.BasicFunctions import *

# ----------------------------------------------------------------
# Create deployment script calls
# ----------------------------------------------------------------
def create_deployment_scripts(client_name:str, database:str, env:str, source_name:str, repo_name:str, resources:list):
    script = ""
    dataInstallDoc = Document()

    if repo_name == "data":
        for res in resources:
            if "/" in res[0]:
                res_src, res_folder = res[0].split("/")

                # archtics override
                if res_src.upper() == "ARCHTICS-API":
                        res_src = "archtics"

                script += f".\\installComponent.ps1 -cn {client_name} -toDB {database} -env {env} -fr {res_src} -s {res_folder} -c {res[1]} -silent\n"
                dataInstallDoc.newline(f"-fr {res_src.lower()} -s {res_folder} -c {res[1]}")
            else:

                # archtics override
                if source_name.upper() == "ARCHTICS-API":
                        source_name = "archtics"

                script += f".\\installComponent.ps1 -cn {client_name} -toDB {database} -env {env} -fr {source_name.lower()} -s {res[0]} -c {res[1]} -silent\n"
                dataInstallDoc.newline(f"-fr {source_name.lower()} -s {res[0]} -c {res[1]}")

        return script, dataInstallDoc

    elif repo_name == "config":
        for res in resources:
            script += f".\\installConfig.ps1 -cn {client_name} -toDB {database} -env {env} -fr {source_name.lower()} -cf masterimport -s {res[0]} -c {res[1]} -silent\n"

        return script
    else:
        raise Exception(f"{repo_name} not recognized.")
        return

# ----------------------------------------------------------------
# create data tester profile
# ----------------------------------------------------------------
def CreateDTP(profilename:str, client:str, database:str, role:str, testfilepath:str, outputfolder:str, sf_user:str= "", testfilter:str= ""):
    runProfileDoc = Document()
    if sf_user != "":
        runProfileDoc.newline(f"sf_user={sf_user}")
    runProfileDoc.newline(f"client={client}")
    runProfileDoc.newline(f"database={database}")
    runProfileDoc.newline(f"role={role}")
    runProfileDoc.newline(f"testfilepath={testfilepath}")
    if testfilter != "":
        runProfileDoc.newline(f"filter={testfilter}")

    filewrite(folder=outputfolder, filename=profilename, content=runProfileDoc.out())

    return f'Run Profile "{profilename}" created in {outputfolder}'

# ----------------------------------------------------------------
# create config creator profile
# ----------------------------------------------------------------
def CreateICP(profilename:str, sourcetype:str, client:str, database:str, sourcename:str, copyffoptions:str, filedateregex:str, outputfolder:str, fileimportmatch:str= "", delimiter:str= "", enclosedby:str= "", pgpkey:str= ""):
    runProfileDoc = Document()

    runProfileDoc.newline(f"sourcetype={sourcetype}")
    runProfileDoc.newline(f"client={client}")
    runProfileDoc.newline(f"database={database}")
    runProfileDoc.newline(f"sourcename={sourcename}")
    if copyffoptions == None:
        copyffoptions = ""
    runProfileDoc.newline(f"copyffoptions={copyffoptions}")

    if filedateregex == None:
        filedateregex = ""
    runProfileDoc.newline(f"filedateregex={filedateregex}")

    if fileimportmatch == None:
        fileimportmatch = ""
    runProfileDoc.newline(f"fileimportmatch={fileimportmatch}")

    if delimiter == None:
        delimiter = ""
    runProfileDoc.newline(f"delimiter={delimiter}")

    if enclosedby == None:
        enclosedby = ""
    runProfileDoc.newline(f"enclosedby={enclosedby}")

    if pgpkey == None:
        pgpkey = ""
    runProfileDoc.newline(f"pgpkey={pgpkey}")

    filewrite(folder=outputfolder, filename=profilename, content=runProfileDoc.out())

    return f'Creator Profile "{profilename}" created in {outputfolder}'