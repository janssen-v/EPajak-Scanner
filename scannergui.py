from tkinter import *
from tkinter.filedialog import asksaveasfilename
from tkinter.ttk import *
import epajakscanner

form_list = []


def scan_qr():
    epajakscanner.main()


def save_file():
    filepath = asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("Comma Separated Value", "*.csv"), ("All Files", "*.*")],
    )
    if not filepath:
        return
    epajakscanner.export_csv(filepath, form_list)


window = Tk()
window.title("E-Pajak QR Scanner")
window.rowconfigure(0, minsize=200, weight=1)
window.columnconfigure(0, minsize=80, weight=1)
frm_buttons = Frame(window, relief=RAISED, border=2)
btn_scan = Button(frm_buttons, text="Scan QR")
btn_stop = Button(frm_buttons, text="Stop Scan")
btn_save = Button(frm_buttons, text="Save as...", command=save_file)

btn_scan.grid(row=0, column=0, sticky="ew", padx=80, pady=5)
btn_stop.grid(row=1, column=0, sticky="ew", padx=80, pady=5)
btn_save.grid(row=2, column=0, sticky="ew", padx=80)
frm_buttons.grid(row=0, column=0, sticky="ns")

window.mainloop()
