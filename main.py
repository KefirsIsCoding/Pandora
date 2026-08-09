from tkinter import *
from tkinter import ttk

class AgendaView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        agenda_frame = ttk.Frame(parent)
        agenda_frame.grid(column=0, row=0, sticky=(N, W, E, S))
        # Set up all agenda needed specifics
        # Agenda list and 

class CollectionView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        collection_frame = ttk.Frame(parent)
        collection_frame.grid(column=0, row=0, sticky=(N, W, E, S))

class Pandora:
    def __init__(self):
        # Initialize the models views controllers

        root = Tk()
        root.title("Pandora")
        root.geometry("900x900")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        mainframe = ttk.Frame(root)
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        notebook = ttk.Notebook(mainframe)
        notebook.grid(column=0, row=0, sticky=(N, W, E, S))
        agenda_view = AgendaView(notebook)
        notebook.add(agenda_view, text="Agenda")
        collection_view = CollectionView(notebook)
        notebook.add(collection_view, text="Collections")
        self.root = root 

    def mainloop(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = Pandora()
    app.mainloop()
