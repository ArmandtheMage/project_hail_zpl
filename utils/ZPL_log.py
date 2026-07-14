import logging
from tkinter import END as tk_END
from tkinter.scrolledtext import ScrolledText

class ZPLLogger(logging.Logger):
    
    def __init__(self, name, log_widget=None):
        super().__init__(name)
        self.log_widget = log_widget

    #def funzione agganciare il widget di log al logger, (in modo che log scriva sul terminale della gui)
    def set_frame(self, widget : ScrolledText):
        self.log_widget = widget
        self.info("Sistema avviato...")  # Log iniziale per confermare che il logger è attivo

    #def override metodo info (sopra) dove logga non solo nel terminale ma anche nella console della gui
    def info(self, msg, *args, **kwargs):
        super().info(msg, *args, **kwargs)
        if self.log_widget:
            self.log_widget.insert(tk_END, f"{msg}\n")
            self.log_widget.see(tk_END)
            self.log_widget.update()