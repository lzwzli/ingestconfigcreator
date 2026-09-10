def table_append_columns(table_name:str, pk_list:list, col_list:list):
    table_name = table_name.upper()

    col_list_list = col_list

    if table_name == "ARCHTICSATTENDANCE":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERADDRESS":
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERALTERNATEID":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERATTRIBUTES":
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERREP":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERS":
        col_list_list.append(["", "EMAIL", "VARCHAR"])
        col_list_list.append(["", "FIRSTNAME", "VARCHAR"])
        col_list_list.append(["", "MIDDLENAME", "VARCHAR"])
        col_list_list.append(["", "LASTNAME", "VARCHAR"])
        col_list_list.append(["", "ADDRESS1", "VARCHAR"])
        col_list_list.append(["", "ADDRESS2", "VARCHAR"])
        col_list_list.append(["", "CITY", "VARCHAR"])
        col_list_list.append(["", "STATE", "VARCHAR"])
        col_list_list.append(["", "ZIP", "VARCHAR"])
        col_list_list.append(["", "COUNTRY", "VARCHAR"])
        col_list_list.append(["", "PHONEDAY", "VARCHAR"])
        col_list_list.append(["", "COMPANYNAME", "VARCHAR"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERTRACE":
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSDONATION":
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSHELDSEATS":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSINVOICELINEITEM":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSJOURNAL":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSLISTCODE":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSMEMBERSHIPS":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSNOTE":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSPAYMENTSCHEDULEDETAILS":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSPROMOCODE":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSRETAILNONTICKET":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSSOLICITATIONS":
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSTICKETEXCHANGE":
        col_list_list.append(["", "SELLERCUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "SELLERRAWAUDIENCEID", "NUMBER(38,0)"])
        col_list_list.append(["", "BUYERCUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "BUYERRAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSTICKETEXPANDED":
        col_list_list = [["", "KEYHASH", "VARCHAR"]] + col_list_list
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])
        pk_list = ["KEYHASH"]

    return pk_list, col_list_list

def unique_sp_append_columns(table_name:str, pk_list:list, col_list:list):
    col_list_list = col_list

    if table_name == "ARCHTICSATTENDANCE":
        sp_tablename = "TMP.ARCHTICSATTENDANCE"

    elif table_name == "ARCHTICSCUSTOMERADDRESS":
        sp_tablename = "TMP.ARCHTICSCUSTOMERADDRESSCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERALTERNATEID":
        sp_tablename = "TMP.ARCHTICSCUSTOMERALTERNATEIDCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERATTRIBUTES":
        sp_tablename = "TMP.ARCHTICSCUSTOMERATTRIBUTESCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERREP":
        sp_tablename = "TMP.ARCHTICSCUSTOMERREPCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSCUSTOMERS":
        sp_tablename = table_name
        col_list_list.append(["", "EMAIL", "VARCHAR"])
        col_list_list.append(["", "PREFIX", "VARCHAR"])
        col_list_list.append(["", "FIRSTNAME", "VARCHAR"])
        col_list_list.append(["", "MIDDLENAME", "VARCHAR"])
        col_list_list.append(["", "LASTNAME", "VARCHAR"])
        col_list_list.append(["", "SUFFIX", "VARCHAR"])
        col_list_list.append(["", "FULLNAME", "VARCHAR"])
        col_list_list.append(["", "ADDRESS1", "VARCHAR"])
        col_list_list.append(["", "ADDRESS2", "VARCHAR"])
        col_list_list.append(["", "ADDRESS3", "VARCHAR"])
        col_list_list.append(["", "CITY", "VARCHAR"])
        col_list_list.append(["", "STATE", "VARCHAR"])
        col_list_list.append(["", "ZIP", "VARCHAR"])
        col_list_list.append(["", "COUNTRY", "VARCHAR"])
        col_list_list.append(["", "PHONEDAY", "VARCHAR"])
        col_list_list.append(["", "COMPANYNAME", "VARCHAR"])

    elif table_name == "ARCHTICSCUSTOMERTRACE":
        sp_tablename = "TMP.ARCHTICSCUSTOMERTRACECUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSDONATION":
        sp_tablename = "TMP.ARCHTICSDONATIONCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSHELDSEATS":
        sp_tablename = "TMP.ARCHTICSHELDSEATSCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSINVOICELINEITEM":
        sp_tablename = "TMP.ARCHTICSINVOICELINEITEMCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSJOURNAL":
        sp_tablename = "TMP.ARCHTICSJOURNALCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSLISTCODE":
        sp_tablename = "TMP.ARCHTICSLISTCODECUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSMEMBERSHIPS":
        sp_tablename = "TMP.ARCHTICSMEMBERSHIPSCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSNOTE":
        sp_tablename = "TMP.ARCHTICSNOTECUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSPAYMENTSCHEDULEDETAILS":
        sp_tablename = "TMP.ARCHTICSPAYMENTSCHEDULEDETAILSCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSPROMOCODE":
        sp_tablename = "TMP.ARCHTICSPROMOCODECUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSRETAILNONTICKET":
        sp_tablename = "TMP.ARCHTICSRETAILNONTICKETCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSSOLICITATIONS":
        sp_tablename = "TMP.ARCHTICSSOLICITATIONSCUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "CUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "RAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSTICKETEXCHANGE":
        sp_tablename = "TMP.ARCHTICSTICKETEXCHANGECUSTOMERNAMEIDJOINED"
        col_list_list.append(["", "SELLERCUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "SELLERRAWAUDIENCEID", "NUMBER(38,0)"])
        col_list_list.append(["", "BUYERCUSTOMERNAMEID", "NUMBER(38,0)"])
        col_list_list.append(["", "BUYERRAWAUDIENCEID", "NUMBER(38,0)"])

    elif table_name == "ARCHTICSTICKETEXPANDED":
        sp_tablename = "TMP.ARCHTICSTICKETEXPANDED"
        pk_list = ["KEYHASH"]
        col_list_list = [["", "KEYHASH", "VARCHAR"]] + col_list_list

    else:
        sp_tablename = table_name

    return sp_tablename, pk_list, col_list_list