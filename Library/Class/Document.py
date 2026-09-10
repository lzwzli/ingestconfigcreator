class Document:
    def __init__(self):
        self.Doc = ""

    def newline(self, str:str):
        if len(self.Doc)<1:
            self.Doc += str
        else:
            self.Doc += f"\n{str}"

    def append(self, str:str):
        self.Doc += str

    def newlinelist(self, str_list:list, padding:str=""):
        # add a new line for each item in list
        for str in str_list:
            self.newline(f"{padding}{str},")
        # remove last comma
        self.Doc = self.Doc[:-1]

    def trimend(self, num_char_to_trim:int):
        # remove the last num_char_to_trim characters
        self.Doc = self.Doc[:0-num_char_to_trim]

    # output document string
    def out(self):
        return self.Doc

    # output document string without newline and tabs for use in JSON
    def out_str(self, trim_dbl_esc=1):
        self.Doc_str = self.Doc
        self.Doc_str = self.Doc_str.replace("\t","")
        self.Doc_str = self.Doc_str.replace("\n"," ")

        if trim_dbl_esc == 1:
            self.Doc_str = self.Doc_str.replace("  "," ")

        return self.Doc_str

    def replace(self, findstr:str, replacestr:str):
        self.Doc = self.Doc.replace(findstr, replacestr)

        return
