class Logger:
    def __init__(self):
        self.runlog_msg = ""
        print(self.runlog_msg)
        return

    def log(self, msg:str):
        self.runlog_msg += f"{msg}\n"
        print(self.runlog_msg)
        return

    def append(self, msg:str):
        self.runlog_msg += f"{msg}\n"
        return

    def out(self):
        if "Error" in self.runlog_msg or "ERROR" in self.runlog_msg:
            self.log("WARNING: Completed with Errors.")
        else:
            self.log("Completed successfully.")

        return self.runlog_msg

    def check(self, checkstring):
        if checkstring in self.runlog_msg:
            return True
        else:
            return False