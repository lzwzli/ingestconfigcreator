def fn_sources_append(worksheet:object, db_folder:str, sources_obj:object, runlog:object, repo_root_folder:str, client:str, source_name:str):
    runlog.log("Running Eloqua specific sources append function")

    # get table name
    table_name = worksheet.table_name().upper()

    # add additional key value pairs if its campaigns or emails
    if table_name.endswith('EMAIL') or table_name.endswith('CAMPAIGN'):
        runlog.log("Adding key pairs for Email and Campaign object")
        sources_obj.append("isRestApiSource",True)
        sources_obj.append("apiCount",10)
        sources_obj.append("apiDepth","complete")
        sources_obj.append("timeoutSeconds",100)
        if table_name.endswith('EMAIL'):
            sources_obj.append("eloquaObjectName", "emails")
        elif table_name.endswith('CAMPAIGN'):
            sources_obj.append("eloquaObjectName", "campaigns")

    # add additional key value pairs for CONTACT
    elif table_name.endswith('CONTACT'):
        runlog.log("Adding key pairs for CONTACT object")
        sources_obj.append("eloquaObjectName", "contacts")
        sources_obj.append("eloquaObjectParentId", "")
        sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/contact.json")

    # add additional key value pairs for EMAILCLICKTHROUGH
    elif table_name.endswith('EMAILCLICKTHROUGH'):
        runlog.log("Adding key pairs for EMAILCLICKTHROUGH object")
        sources_obj.append("eloquaObjectName", "activities")
        sources_obj.append("eloquaObjectParentId", None)
        sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/emailclickthrough.json")

    # add additional key value pairs for EMAILOPEN
    elif table_name.endswith('EMAILOPEN'):
        runlog.log("Adding key pairs for EMAILOPEN object")
        sources_obj.append("eloquaObjectName", "activities")
        sources_obj.append("eloquaObjectParentId", None)
        sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/emailopen.json")

    # add additional key value pairs for EMAILSEND
    elif table_name.endswith('EMAILSEND'):
        runlog.log("Adding key pairs for EMAILSEND object")
        sources_obj.append("eloquaObjectName", "activities")
        sources_obj.append("eloquaObjectParentId", None)
        sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/emailsend.json")

    # add additional key value pairs for FORMSUBMIT
    elif table_name.endswith('FORMSUBMIT'):
        runlog.log("Adding key pairs for FORMSUBMIT object")
        sources_obj.append("eloquaObjectName", "activities")
        sources_obj.append("eloquaObjectParentId", None)
        sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/formsubmit.json")

    # add additional key value pairs for BOUNCEBACK
    elif table_name.endswith('BOUNCEBACK'):
        runlog.log("Adding key pairs for BOUNCEBACK object")
        sources_obj.append("eloquaObjectName", "activities")
        sources_obj.append("eloquaObjectParentId", None)
        sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/bounceback.json")

    # add additional key value pairs for PAGEVIEW
    elif table_name.endswith('PAGEVIEW'):
        runlog.log("Adding key pairs for PAGEVIEW object")
        sources_obj.append("eloquaObjectName", "activities")
        sources_obj.append("eloquaObjectParentId", None)
        sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/pageview.json")

    # add additional key value pairs for SUBSCRIBE
    elif table_name.endswith('SUBSCRIBE'):
        runlog.log("Adding key pairs for SUBSCRIBE/UNSUBSCRIBE object")
        sources_obj.append("eloquaObjectName", "activities")
        sources_obj.append("eloquaObjectParentId", None)
        if table_name.endswith('UNSUBSCRIBE'):
            sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/unsubscribe.json")
        else:
            sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/subscribe.json")

    # add additional key value pairs for WEBVISIT
    elif table_name.endswith('WEBVISIT'):
        runlog.log("Adding key pairs for WEBVISIT object")
        sources_obj.append("eloquaObjectName", "activities")
        sources_obj.append("eloquaObjectParentId", None)
        sources_obj.append("eloquaExportDefinitionFileName", "definitions/exports/webvisit.json")
    return
