import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *

# Pirated from: https://stackoverflow.com/questions/16188420/tkinter-scrollbar-for-frame
class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)


class CollectionWidget(ttk.Frame):
    def __init__(self, parent, name, id):
        super().__init__(parent)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.id = id
        self.name = name
        self["borderwidth"] = 2
        self["relief"] = "raised"
        ttk.Label(self, text=name).grid(column=0, row=0, sticky=(N,W,E,S))
        self.edit_bttn = ttk.Button(self, text="Edit")
        self.edit_bttn.grid(column=1,row=0, sticky=(N,W,E,S))
        self.del_bttn = ttk.Button(self, text="X")
        self.del_bttn.grid(column=2, row=0, sticky=(N,W,E,S))
        self.open_bttn = ttk.Button(self, text=">")
        self.open_bttn.grid(column=3, row=0, sticky=(N,W,E,S))


    def set_edit_cmd(self, callback):
        self.edit_bttn.configure(command=lambda : callback(self))
    
    def set_del_cmd(self, callback):
        self.del_bttn.configure(command=lambda : callback(self))

    def set_open_cmd(self, callback):
        self.open_bttn.configure(command=lambda : callback(self))

class SubTaskWidget(ttk.Frame):
    def __init__(self, parent, name, id, progress, status):
        super().__init__(parent)
        self.id = id
        self.name = name
        self["borderwidth"] = 2
        self["relief"] = "raised"

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)

        ttk.Label(self, text=f"Title: {name}").grid(column=0, row=0, sticky=(N,W,E,S))
        ttk.Label(self, text=f"Progress: {progress}").grid(column=1, row=0, sticky=(N,W,E,S))
        ttk.Label(self, text=f"Status: {status}").grid(column=2, row=0, sticky=(N,W,E,S))

        self.edit_bttn = ttk.Button(self, text="Edit")
        self.edit_bttn.grid(column=3,row=0, sticky=(N,W,E,S))
        self.del_bttn = ttk.Button(self, text="X")
        self.del_bttn.grid(column=4, row=0, sticky=(N,W,E,S))

    def set_edit_cmd(self, callback):
        self.edit_bttn.configure(command=lambda : callback(self))
    
    def set_del_cmd(self, callback):
        self.del_bttn.configure(command=lambda : callback(self))


class TaskWidget(ttk.Frame):
    def __init__(self, parent, name, id, progress, status):
        super().__init__(parent)
        
        self.id = id
        self.name = name
        self.expanded = False
        self.subtasks = []

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self["borderwidth"] = 2
        self["relief"] = "raised"
        ttk.Label(self, text=f"Title: {name}").grid(column=0, row=0, sticky=(N,W,E,S))
        ttk.Label(self, text=f"Progress: {progress}").grid(column=1, row=0, sticky=(N,W,E,S))
        ttk.Label(self, text=f"Status: {status}").grid(column=2, row=0, sticky=(N,W,E,S))
        self.edit_bttn = ttk.Button(self, text="Edit")
        self.edit_bttn.grid(column=3,row=0, sticky=(N,W,E,S))
        self.del_bttn = ttk.Button(self, text="X")
        self.del_bttn.grid(column=4, row=0, sticky=(N,W,E,S))
        self.new_bttn = ttk.Button(self, text="+")
        self.new_bttn.grid(column=5, row=0, sticky=(N,W,E,S))
        self.open_bttn = ttk.Button(self, text=">", command=self.set_open_cmd)
        self.open_bttn.grid(column=6, row=0, sticky=(N,W,E,S))

        self.subtask_window = VerticalScrolledFrame(self)
        self.refresh_subtask_list()

    def set_subtasks(self, subtasks):
        print("hellooo")
        print(subtasks)
        self.subtasks = subtasks
        self.refresh_subtask_list()
    
    def refresh_subtask_list(self):
        for t in self.subtask_window.interior.winfo_children():
            t.destroy()
        if not self.expanded:
            if not self.subtasks:
                no_tasks = ttk.Frame(self.subtask_window.interior)
                no_tasks.grid(sticky=(N,W,E,S))
                ttk.Label(no_tasks, text="Add some sub-tasks!").grid(sticky=(N,W,E,S))
            else:
                for t in self.subtasks:
                    print(t)
                    SubTaskWidget(self.subtask_window.interior, t.name, t.id, t.progress, t.status).grid()

    def set_edit_cmd(self, callback):
        self.edit_bttn.configure(command=lambda : callback(self))
    
    def set_del_cmd(self, callback):
        self.del_bttn.configure(command=lambda : callback(self))

    def set_new_cmd(self, callback):
        self.new_bttn.configure(command=lambda : callback(self))

    def set_open_cmd(self):
        if self.expanded:
            self.subtask_window.grid_forget()
        else:
            self.refresh_subtask_list()
            self.subtask_window.grid(column=0, row=1, columnspan=7, sticky=(N,W,E,S))
        self.expanded = not self.expanded
        
