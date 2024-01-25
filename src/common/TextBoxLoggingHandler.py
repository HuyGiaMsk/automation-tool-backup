import logging
import tkinter as tk


class TextBoxLoggingHandler(logging.Handler):

    def __init__(self, textbox):
        super().__init__()
        self.textbox = textbox

    def emit(self, record: str):
        msg = self.format(record)
        self.textbox.config(state=tk.NORMAL)
        self.textbox.insert(tk.END, msg + '\n')
        self.textbox.config(state=tk.DISABLED)
        self.textbox.see(tk.END)
