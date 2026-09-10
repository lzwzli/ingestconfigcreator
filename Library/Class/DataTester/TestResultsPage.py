from datetime import datetime
from Library.FunctionFiles.Functions import *
class ResultDoc:
    def __init__(self):
        return

    def addPageHeader(self, header_html:str):
        self.pageHeaderHtml = header_html
        return

    def addTable(self, table_html:str):
        self.tableHtml = table_html
        return

    def htmlOut(self):
        html = Document()
        html.append(self.pageHeaderHtml.replace("<offset>", ""))
        html.newline(self.tableHtml)
        html.newline('<p style="line-height: 1;"></p>')

        return html.out()

class ResultTable:
    def __init__(self):
        self.Table = []
        return

    def newRow(self):
        newRow = ResultTableRow()
        return newRow

    def insertRow(self, row:object):
        self.Table.append(row.htmlOut())
        return

    def htmlOut(self):
        html = Document()

        tableDeclare = '<table class="collapsed">'
        # column order = Test Name, Test Type, Query, Expected Results, Result, ResultTag
        tableHeaderColGroup = ('\t<colgroup><col class="inbound" style="width: 209.0px;" /></colgroup>\n'
                               '\t<colgroup><col class="inbound" style="width: 200.0px;" /></colgroup>\n'
                               '\t<colgroup><col class="inbound" style="width: 700.0px;" /></colgroup>\n'
                               '\t<colgroup><col class="inbound" style="width: 100.0px;" /></colgroup>\n'
                               '\t<colgroup><col class="inbound" style="width: 150.0px;" /></colgroup>\n'
                               '\t<colgroup><col class="inbound" style="width: 100.0px;" /></colgroup>\n'
                               )
        tableHeaderRow = ('\t<thead><tr class="rowborder">\n'
                          '\t\t<th><div><div><span>Test Name</span></div></div></th>\n'
                          '\t\t<th><strong>&quot;Plain English&quot; Test</strong></th>\n'
                          '\t\t<th><strong>Coded Test</strong></th>\n'
                          '\t\t<th><strong>Expected Result</strong></th>\n'
                          '\t\t<th><div><div><span">Actual Result</span></div></div></th>\n'
                          '\t\t<th><strong>Pass/Fail</strong></th>\n'
                          '\t</tr></thead>')
        tableBodyDeclare = "\t<tbody>"
        tableBodyDeclareClose = "\n\t</tbody>"
        tableClose = "</table>"

        rowHtml = ""
        for row in self.Table:
            rowHtml = rowHtml + row.replace("<offset>","\t\t")

        rowHtml = rowHtml[:-1]

        # build table html output
        html.newline(tableDeclare)
        html.newline(tableHeaderColGroup)
        html.newline(tableHeaderRow)
        html.newline(tableBodyDeclare)
        html.newline(rowHtml)
        html.append(tableBodyDeclareClose)
        html.newline(tableClose)

        return html.out()

class ResultTableRow:
    def __init__(self, col_count:int):
        self.Row = []
        self.Decorator = []
        self.columnCount = col_count
        return

    def createColumns(self):
        colIdx = 0
        columns = []
        while colIdx < self.columnCount:
            col = ResultTableColumn()
            columns.append(col)
            colIdx += 1

        return columns

    def addColumn(self, column:object):
        self.Row.append(column)
        return

    def addDecorator(self, decorator:str):
        self.Decorator.append(decorator)
        return

    def htmlOut(self):
        colHtml = ""
        for col in self.Row:
            colHtml = colHtml + col.htmlOut()

        rowHtml = Document()
        rowHtml.append("<offset><tr")
        for dec in self.Decorator:
            rowHtml.append(" "+dec)
        rowHtml.append(">")
        rowHtml.append(colHtml.replace("<offset>","<offset>\t"))
        rowHtml.newline(f"<offset></tr>\n")

        return rowHtml.out()

    def out(self):
        return self.Row

class ResultTableColumn:
    def __init__(self):
        self.Col = ""
        self.Decorator = []
        return

    def addContent(self, content:str):
        self.Col = self.Col + content
        return

    def addDecorator(self, decorator:str):
        self.Decorator.append(decorator)
        return

    def htmlOut(self):
        html = Document()
        html.newline("<offset><td")
        for dec in self.Decorator:
            html.append(" " + dec)
        html.append(' class="cellpadding">')
        html.newline(f"<offset>\t{self.Col}")
        html.newline("<offset></td>")

        return html.out()

class ResultPageHeader:
    def __init__(self):
        self.Header = []
        return

    def addContent(self, content:str):
        self.Header.append(content)
        return

    def htmlOut(self):
        html = Document()

        # add styles
        html.newline("<head>")
        html.newline("\t<style>")
        html.newline("\t\ttable.collapsed{"
                     "\t\t\tborder-collapse:collapse;"
                     "\t\t}")
        html.newline("")
        html.newline("\tcol.inbound{"
                     "\t\tborder:1px solid black;"
                     "\t}")
        html.newline("")
        html.newline("\ttr.rowborder{"
                     "\t\tborder:1px solid black;"
                     "\t}")
        html.newline("")
        html.newline("\ttr.tablegroup{"
                     "\t\tborder:1px solid black;"
                     "\t\tbackground-color: #cbd6e2;"
                     "\t}")
        html.newline("")
        html.newline("\ttr.rowborder{"
                     "\t\tborder:1px solid black;"
                     "\t}")
        html.newline("")
        html.newline("\tdiv.querycontent{"
                     "\t\twhite-space: pre-wrap;"
                     "\t}")
        html.newline("")
        html.newline("\ttd.cellpadding{"
                     "\t\tpadding-left: 5;"
                     "\t\tpadding-right: 5;"
                     "\t}")
        html.newline("")
        html.newline("\t.title{"
                     "\t\tfont-weight: bold;"
                     "\t\tfont-size: 1.5em;"
                     "\t}")
        html.newline("")
        html.newline("\t.contentstring{"
                     "\t\tfont-size: 1.25em;"
                     "\t}")
        html.newline("\t</style>")
        html.newline("</head>")

        # add header elements
        for head in self.Header:
            if "<title>" in head or "<contentstring>" in head:
                head = head \
                        .replace("<title>",'<offset><span class="title">\n\t') \
                        .replace("</title>", '\n<offset></span>\n') \
                        .replace("<contentstring>", '\n<offset><span class="contentstring">\n\t') \
                        .replace("</contentstring>", '\n<offset></span>')
                html.newline("<offset><p>")
                html.newline(head)
                html.newline("<offset></p>")
            else:
                html.newline("<offset><h3>")
                html.newline(f"<offset>\t{head}")
                html.newline("<offset></h3>")

        return html.out()

class queryContent:
    def __init__(self):
        self.queryDoc = Document()
        return

    def addQuery(self, query:str):
        # remove query name if its in first line
        if '--' in query and query.index('--')==0:
            query = query.strip("\n").strip().split("\n",1)[1]

        self.query = query
        return

    def htmlOut(self):
        self.queryDoc.append('<div class="content-wrapper querycontent">')
        self.queryDoc.newline(f"{self.query}")
        self.queryDoc.newline('<offset></div>')

        return self.queryDoc.out()

class resultTag:
    def __init__(self):
        self.resultDoc = Document()
        return

    def addResult(self, result:str):
        if "pass" in result.lower():
            resultHtml = ('<offset>\t<p style="background-color: #00b300; color: #FFFFFF; height: 50; text-align: center; align-content: center;">PASSED</p>')
        elif "fail" in result.lower():
            resultHtml = ('<offset>\t<p style="background-color: #ff474c; color: #FFFFFF; height: 50; text-align: center; align-content: center;">FAILED</p>')
        else:
            resultHtml = ('<offset>\t<p style="background-color: #0077b6; color: #FFFFFF; height: 50; text-align: center; align-content: center;">ALERT</p>')
        self.result = resultHtml
        return

    def htmlOut(self):
        self.resultDoc.newline(self.result)
        return self.resultDoc.out()

class ResultPage:
    def __init__(self, sf_user:str, runlog:object):
        self.sf_user = sf_user
        self.runlog = runlog
        self.sepCount = 100
        self.sep = "-" * self.sepCount

        # set current datetime
        DTformat = '%Y-%m-%d %I:%M %p'
        DTformatFilename = '%Y%m%d_%I%M%p'
        DTNow = datetime.now()

        self.CurrentDT = DTNow.strftime(DTformat)
        self.CurrentDTFilename = DTNow.strftime(DTformatFilename)

        self.passcount = 0
        self.failcount = 0
        self.alertcount = 0
        self.testcount = 0

        return

    def setPageInfo(self, client:str, result_file_path:str):
        self.client = client
        self.resultFilePath = result_file_path
        self.resultFilename = getFilename(self.resultFilePath)
        return

    def parseResultsJSONFile(self):
        # read results file
        self.runlog.log("::Reading results JSON file")

        # exit if result file is not JSON
        if "json" not in self.resultFilePath.lower():
            self.runlog.log("ERROR: result file is not JSON")
            sys.exit()

        # open file
        try:
            resultsFile = str(open(self.resultFilePath, "r").read())
        except Exception as e:
            self.runlog.log(f"ERROR: {e}")
            sys.exit()

        # convert to python objects
        self.runlog.log("::Loading JSON results file")
        resultJSONList = json.loads(resultsFile)
        self.testcount = len(resultJSONList)

        # database
        self.database = resultJSONList[0]["database"]

        # init resultList
        self.resultList = []

        # parse result row
        self.runlog.log("::Parsing results for:")
        for res in resultJSONList:
            # test name
            fullTestName = res["testname"]
            self.runlog.log(f"::--{fullTestName}")

            if "REGRESSION" in fullTestName:
                regressionTestName = fullTestName.replace("CONTROL-REGRESSION-", "")
                testNameList = [regressionTestName, "Regression", regressionTestName]
            # else its not a regression test name format
            else:
                testNameParts = fullTestName.split("_")
                # map testTable
                try:
                    testTable = testNameParts[0]
                except:
                    testTable = ""

                # map testType
                try:
                    testType = testNameParts[1]
                except:
                    testType = ""

                # map testName
                try:
                    testName = testNameParts[2]
                except:
                    testName = ""

                testNameList = [testTable, testType, testName]

            # set vars
            if len(testNameList) > 2:
                testTable = testNameList[0].strip()
                testType = testNameList[1].strip()
                testName = testNameList[2].strip()
            else:
                testTable = testNameList[0].strip()
                testType = ""
                testName = ""

            # expected result
            self.runlog.log(":::Get expected result")
            expectedResult = res["expectedresult"]

            # result
            self.runlog.log(":::Get query result")
            result = res["result"].strip()

            if "pass" in result.lower():
                self.passcount += 1
            elif "fail" in result.lower() or "error" in result.lower():
                self.failcount += 1
            else:
                self.alertcount += 1

            # test query
            self.runlog.log(":::Get query")
            testQuery = res["query"]

            # add to result list
            self.resultList.append([testTable, testType, testName, expectedResult, testQuery, result])

        self.runlog.log(self.sep)
        return

    def initResultPage(self):
        # initialize confluence page
        self.runlog.log("::Start building output page")

        # build page
        self.page = ResultDoc()
        self.table = ResultTable()
        self.header = ResultPageHeader()
        self.header.addContent(f'Result File:&nbsp;<a href="{self.resultFilePath}" target="_blank">{self.resultFilePath}</a>')
        self.header.addContent(f'<title>Database Tested:</title><contentstring>{self.database.upper()} @ {self.CurrentDT}, </contentstring><title>by:</title><contentstring> {self.sf_user}</contentstring>')
        self.header.addContent("<p></p>")
        self.header.addContent(f'Test Results:'
                               f'<table><tr style="font-size: 13pt;">'
                               f'<td style="border: 2px solid black; padding-left: 5px; padding-right: 5px;">Ran: {self.testcount}</td>'
                               f'<td style="border: 2px solid #00b300; padding-left: 5px; padding-right: 5px;">Passed: {self.passcount}</td>'
                               f'<td style="border: 2px solid #ff474c;padding-left: 5px; padding-right: 5px;">Failed: {self.failcount}</td>'
                               f'<td style="border: 2px solid #0077b6;padding-left: 5px; padding-right: 5px;">Alert: {self.alertcount}</td>'
                               f'</tr></table>')
        self.page.addPageHeader(self.header.htmlOut())
        return

    def buildResultTable(self):
        prevTestTable = ""
        # add each result as a row [testTable, testType, testName, expectedResult, testQuery, result]
        for res in self.resultList:
            testTable = res[0]
            testType = res[1]
            testName = res[2]
            expectedResult = res[3]
            testQuery = res[4]
            result = res[5]

            self.runlog.log(self.sep)
            self.runlog.log(f"::Adding {testTable} results")

            # total column count
            colCount = 6

            # header, add only if test file is not a regression test
            if "regression" not in self.resultFilePath and "Regression" not in self.resultFilePath:
                self.runlog.log(":::Test definition file is not a regression test file, adding header rows per table")
                if testTable != prevTestTable:
                    self.runlog.log(f":::Adding table row header for {testTable}")
                    prevTestTable = testTable
                    # add table header row
                    tHeadRow = ResultTableRow(colCount)
                    tHeadRow.addDecorator('class="tablegroup"')

                    # add columns
                    tHeadCols = tHeadRow.createColumns()

                    # add decorators
                    for col in tHeadCols:
                        col.addDecorator('data-highlight-colour="#f4f5f7"')

                    tHeadColContent = []
                    # add header content
                    tHeadColContent.append(f'<strong>{testTable}</strong>')
                    tHeadColContent.extend(['<br />'])
                    tHeadColContent.append('<strong>Query</strong>')
                    tHeadColContent.extend(['<br />', '<br />', '<br />'])

                    for idx, cont in enumerate(tHeadColContent):
                        tHeadCols[idx].addContent(cont)

                    # add columns to row
                    for col in tHeadCols:
                        tHeadRow.addColumn(col)

                    self.table.insertRow(tHeadRow)
            else:
                self.runlog.log(":::Test defintion file is a regression test file, not adding header rows")

            self.runlog.log(":::Adding result rows")
            # rows
            row = ResultTableRow(colCount)
            rcols = row.createColumns()

            rowContent = [testType, testName]

            # query
            query = queryContent()
            query.addQuery(testQuery)
            rowContent.append(query.htmlOut().replace("<offset>", "<offset>\t"))
            rowContent.append(expectedResult)
            rowContent.append(f'<br />{result}')

            # resultCol
            resultT = resultTag()
            resultT.addResult(result)
            rowContent.append(resultT.htmlOut().replace("<offset>", "<offset>\t"))

            # adding column content
            self.runlog.log(":::Adding content to columns")
            for idx, cont in enumerate(rowContent):
                rcols[idx].addContent(cont)

            # add decorator for Query column
            rcols[2].addDecorator('colspan="1"')

            # add decorator for result tag column
            rcols[5].addDecorator('colspan="1"')

            # add columns to row1
            self.runlog.log(":::Adding columns to row")
            for col in rcols:
                row.addColumn(col)

            # add decorator to row
            row.addDecorator('class="rowborder"')
            # insert rows to table
            self.runlog.log(":::Insert row to table")
            self.table.insertRow(row)
        return

    def addTableToPage(self):
        # add table to page
        self.runlog.log(self.sep)
        self.runlog.log("::Add table to page")
        self.page.addTable(self.table.htmlOut())
        self.runlog.log("::Compose and output page")
        self.pageFinal = self.page.htmlOut()
        return



    def buildAndPublish(self):
        self.parseResultsJSONFile()
        self.initResultPage()
        self.buildResultTable()
        self.addTableToPage()

        # output Html file and log file
        outputFolderPath = outputFolder(self.resultFilePath)
        ResultHtmlFilename = f"{self.resultFilename.replace(".json","")} Test Results_{self.CurrentDTFilename}.html"
        filewrite(folder=outputFolderPath, filename=ResultHtmlFilename, content=self.pageFinal)
        openFile(outputFolderPath + os.sep + ResultHtmlFilename)
        return outputFolderPath