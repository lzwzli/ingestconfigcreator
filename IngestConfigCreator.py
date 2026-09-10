from IngestConfigCreatorPrefect import *
from IngestConfigCreator5x import *
from IngestConfigCreatorAud import *
from Library.Class.MenuPrompt import *
from Library.FunctionFiles.Functions import *
from version import *

def ingestconfigcreator():

    print(f"Ingest Config Creator version {version}")
    print("")

    # -----------------------------------------------------------------------
    # ask for ICP
    # -----------------------------------------------------------------------
    load_runProfile = "init"
    runProfileDict = {}
    sourceType = ""
    while load_runProfile == "init" or (load_runProfile.upper() != "Y" and load_runProfile.upper() != "N"):
        load_runProfile = input("Load creator profile (.icp file)? [Y/N]: ")

    if load_runProfile.upper() == "Y":
        print("Select config creator profile from dialog. Dialog may be hidden behind other windows.")
        runProfilePath = fileDialog(title="Select config creator profile", filetype=("Ingest Config Profile", ".icp"))
        runProfile = str(open(runProfilePath, "r").read())
        runProfileList = runProfile.split("\n")

        # parse ICP
        runProfileDict = getProfileDict(profilelist=runProfileList)
        print(f'::Loaded profile from "{runProfilePath}"')

        # get source type
        sourceType = loadProfileVars(runProfileDict, varname="sourcetype")

    # -----------------------------------------------------------------------
    # ICP not loaded
    # -----------------------------------------------------------------------
    if load_runProfile.upper() == "N" or (sourceType != "KIP" and sourceType != "FF" and sourceType.lower() != "5x"):
        # menu prompt
        menu = MenuPrompt()
        menu.addChoice(name="KIP", description="Create ingest resources for API or non flat file sources. Requires:\n   - data dictionary Excel file for the source")
        menu.addChoice(name="FF", description="Create ingest resources for Flat File source. Requires:\n   - data dictionary Excel file for the source")
        menu.addChoice(name="AUD", description="Create RawAudience config resources and test queries only. Requires:\n   - data dictionary Excel file for the source")
        #menu.addChoice(name="5x", description="Create ingest resources for 5x sources. Requires:\n   - data dictionary Excel file for the source")
        sourceType = menu.prompt()

    # -----------------------------------------------------------------------
    # run appropriate function based on source type
    # -----------------------------------------------------------------------
    if sourceType == "KIP":
        ingestconfigcreator_prefect(srcType="KIP", runProfileDict=runProfileDict)
    elif sourceType == "FF":
        ingestconfigcreator_prefect(srcType="FF", runProfileDict=runProfileDict)
    elif sourceType.lower() == "5x":
        ingestconfigcreator_5x(srcType="5x", runProfileDict=runProfileDict)
    elif sourceType == "AUD":
        ingestconfigcreator_aud(srcType="AUD", runProfileDict=runProfileDict)

if __name__ == "__main__":
    ingestconfigcreator()