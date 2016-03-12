import optparse
import traceback
import multiprocessing
import tkinter as tk
from tkinter import ttk
from tkinter import *
import sqlprocessor as sp
from functools import partial
from db import getDbConnection
from db import DBConnectionPane


class SummarizeCommandPane(tk.Frame):
    GLOBAL_AVERAGE_UNIT_PRICE = 1466.0

    BUTTON_LABELS  = ["All Area Types", "EEZ", "Highseas", "LME", "RFMO", "Global"]

    SUMMARY_TABLES = [None,
                      "allocation_result_eez",
                      "allocation_result_high_seas",
                      "allocation_result_lme",
                      "allocation_result_rfmo",
                      "allocation_result_global"]

    def __init__(self, parent, dbPane, isVerticallyAligned=False, descriptions=None):
        tk.Frame.__init__(self, parent)
        self.dbPane = dbPane

        cmdFrame = ttk.Labelframe(parent, text='Summarize', width=100, height=100)
        cmdFrame.grid(column=0, row=0, sticky=(N, W))
        cmdFrame.columnconfigure(0, weight=1)
        cmdFrame.rowconfigure(0, weight=1)

        row = 0
        column = 0

        for i in range(len(SummarizeCommandPane.BUTTON_LABELS)):
            if i == 0:
                color = "red"
            else:
                color = "blue"

            if isVerticallyAligned:
                row += 1
            else:
                column += 1

            if descriptions:
                self.createCommandButton(cmdFrame, SummarizeCommandPane.BUTTON_LABELS[i], SummarizeCommandPane.SUMMARY_TABLES[i], row, column, color, descriptions[i])
            else:
                self.createCommandButton(cmdFrame, SummarizeCommandPane.BUTTON_LABELS[i], SummarizeCommandPane.SUMMARY_TABLES[i], row, column, color)

        for child in cmdFrame.winfo_children(): child.grid_configure(padx=5, pady=5)

        parent.add(cmdFrame)

    def createCommandButton(self, parent, buttonText, summaryTable, gRow, gColumn, color, commandDescription=None):
        if summaryTable:
            tk.Button(parent, text=buttonText, fg=color, command=partial(self.kickoffSqlProcessor, summaryTable)).grid(
                column=gColumn, row=gRow, sticky=E)
        else:
            tk.Button(parent, text=buttonText, fg=color, command=self.summarizeAll).grid(column=gColumn, row=gRow, sticky=E)

        if commandDescription:
            tk.Label(parent, text=commandDescription).grid(column=gColumn+1, row=gRow, sticky=W)

    def postAggregationOperations(self, summaryTable):
        opts = self.dbPane.getDbOptions()
        dbConn = getDbConnection(optparse.Values(opts))

        print("Updating allocation data unit price...")
        opts['sqlfile'] = "sql/update_allocation_data_unit_price.sql"
        if 'threads' not in opts or opts['threads'] == 0:
            opts['threads'] = 8
        sp.process(optparse.Values(opts))
        dbConn.execute("UPDATE allocation.allocation_data SET unit_price = %s WHERE unit_price IS NULL" % SummarizeCommandPane.GLOBAL_AVERAGE_UNIT_PRICE)
        dbConn.execute("VACUUM ANALYZE allocation.allocation_data")

        print("Vacuum and analyze target summary table(s)...")
        if summaryTable:
            dbConn.execute("VACUUM ANALYZE allocation.%s" % summaryTable)
        else:
            # if input summaryTable = None, it's really the signal to vacuum analyze all summary tables
            for tab in SummarizeCommandPane.SUMMARY_TABLES:
                if tab:
                    dbConn.execute("VACUUM ANALYZE allocation.%s" % tab)

        dbConn.close()

    def kickoffSqlProcessor(self, summaryTable, isPostOpsRequired=True):
        opts = self.dbPane.getDbOptions()
        dbConn = getDbConnection(optparse.Values(opts))
        dbConn.execute("TRUNCATE allocation.%s" % summaryTable)
        opts['sqlfile'] = "sql/summarize_%s.sql" % summaryTable
        if 'threads' not in opts or opts['threads'] == 0:
            opts['threads'] = 8
        sp.process(optparse.Values(opts))

        if isPostOpsRequired:
            self.postAggregationOperations(summaryTable)

    def summarizeAll(self):
        for summaryTable in SummarizeCommandPane.SUMMARY_TABLES:
            if summaryTable:
                self.kickoffSqlProcessor(summaryTable, False)
        self.postAggregationOperations(None)


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        mainPane = ttk.Panedwindow(master, orient=VERTICAL)
        dbPane = DBConnectionPane(mainPane, "DB Connection", True)
        SummarizeCommandPane(mainPane, dbPane, False, None)
        mainPane.pack(expand=1, fill='both')


# ===============================================================================================
# ----- MAIN
def main():
    root = tk.Tk()
    root.title("Summarization")
    app = Application(master=root)
    app.mainloop()


if __name__ == "__main__":
    try:
        multiprocessing.freeze_support()
        main()
    except SystemExit as x:
        sys.exit(x)
    except Exception:
        strace = traceback.extract_tb(sys.exc_info()[2])[-1:]
        lno = strace[0][1]
        print('Unexpected Exception on line: {0}'.format(lno))
        print(sys.exc_info())
        sys.exit(1)

        # CommandPane(parent, True, ['Summarize data for all marine layers',
        #                            'Summarize data for marine layer 1',
        #                            'Summarize data for marine layer 2',
        #                            'Summarize data for marine layer 3',
        #                            'Summarize data for marine layer 4',
        #                            'Summarize data for marine layer 6'])