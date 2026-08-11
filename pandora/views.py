from tkinter import *
from tkinter import ttk
from .widgets import VerticalScrolledFrame, CollectionWidget, TaskWidget

class AgendaView(ttk.Frame):

    def update_agenda(self):
        pass
    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)

        agenda_list = ttk.LabelFrame(self, text="Agenda list")
        agenda_list.grid(column=0, row=0, sticky=(N,W,E,S))
        agenda_list.columnconfigure(0, weight=1)
        agenda_list.rowconfigure(0, weight=1)

        self.agenda_list_scroll = VerticalScrolledFrame(agenda_list)
        self.agenda_list_scroll.grid(sticky=(N,W,E,S))

        calendar_frame = ttk.LabelFrame(self, text="Calendar Soon TM")
        calendar_frame.grid(column=1, row=0, sticky=(N,W,E,S))

class CollectionView(ttk.Frame):

    def create_collection_dialog(self, *args):
        t = Toplevel(self)
        t.title("Create a collection")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        task_name = StringVar()
        ttk.Label(t, text="Collection name:").grid(column=0, row=1)
        ttk.Entry(t, textvariable=task_name).grid(column=1, row=1)
        ttk.Button(t, text="Ok", command=lambda: self.callbacks["create_collection"](t, task_name.get())).grid(column=2, row=2)

    def edit_collection_dialog(self, collection):
        t = Toplevel(self)
        t.title("Edit a collection")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        task_name = StringVar()
        task_name.set(collection.name)
        ttk.Label(t, text="Collection name:").grid(column=0, row=1)
        ttk.Entry(t, textvariable=task_name).grid(column=1, row=1)
        ttk.Button(t, text="Ok", command=lambda: self.callbacks["edit_collection"](t, task_name.get(), collection.id)).grid(column=2, row=2)

    def delete_collection_dialog(self, collection):
        t = Toplevel(self)
        t.title("Delete this collection?")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        ttk.Label(t, text="Are you sure?").grid(column=0, row=1)
        ttk.Button(t, text="Ok", command=lambda: self.callbacks["delete_collection"](t, collection.id)).grid(column=2, row=2)

    def update_collection(self, collections):
        for w in self.collection_list_frame.interior.winfo_children():
            w.destroy()
        for c in collections:
            item = CollectionWidget(self.collection_list_frame.interior, c.name, c.id)
            item.set_edit_cmd(self.edit_collection_dialog)
            item.set_del_cmd(self.delete_collection_dialog)
            item.set_open_cmd(lambda x : self.callbacks["open_collection"](x))
            item.pack(expand=True, fill="x")

    def update_task(self, tasks):
        for w in self.task_list_frame.interior.winfo_children():
            w.destroy()
        for t in tasks:
            item = TaskWidget(self.task_list_frame.interior, t.name, t.id, t.progress, t.status) 
            item.set_edit_cmd(self.edit_task_dialog)
            item.set_del_cmd(self.delete_task_dialog)
            item.set_new_cmd(self.create_subtask_dialog)
            item.pack(expand=True, fill="x")

    def update_subtasks(self, subtasks, task_id):
        filtered_subtasks = [subtask for subtask in subtasks if subtask.task_id == task_id]
        for w in self.task_list_frame.interior.winfo_children():
            print(w.id)
            print(task_id)
            if w.id == task_id:
                w.set_subtasks(filtered_subtasks)

    def create_task_dialog(self):
        t = Toplevel(self)
        t.title("Create a task")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        task_name = StringVar()
        ttk.Label(t, text="Task name:").grid(column=0, row=1)
        ttk.Entry(t, textvariable=task_name).grid(column=1, row=1)
        ttk.Button(t, text="Ok", command=lambda: self.callbacks["create_task"](t, task_name.get())).grid(column=2, row=2)

    def delete_task_dialog(self, task):
        t = Toplevel(self)
        t.title("Delete this task?")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        ttk.Label(t, text="Are you sure?").grid(column=0, row=1)
        ttk.Button(t, text="Ok", command=lambda: self.callbacks["delete_task"](t, task.id)).grid(column=2, row=2)

    def edit_task_dialog(self, task):
        t = Toplevel(self)
        t.title("Edit a task")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        task_name = StringVar()
        task_name.set(task.name)
        ttk.Label(t, text="Task name:").grid(column=0, row=1)
        ttk.Entry(t, textvariable=task_name).grid(column=1, row=1)
        ttk.Button(t, text="Ok", command=lambda: self.callbacks["edit_task"](t, task_name.get(), task.id)).grid(column=2, row=2)
        

    def create_subtask_dialog(self, task):
        t = Toplevel(self)
        t.title("Create a subtask")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        task_name = StringVar()
        task_name.set(task.name)
        ttk.Label(t, text="Subtask name:").grid(column=0, row=1)
        ttk.Entry(t, textvariable=task_name).grid(column=1, row=1)
        ttk.Button(t, text="Ok", command=lambda: self.callbacks["create_subtask"](t, task_name.get(), task.id)).grid(column=2, row=2)

    def edit_subtask_dialog(self):
        pass

    def delete_subtask_dialog(self):
        pass


    def __init__(self, parent, callbacks):
        super().__init__(parent)
        self.callbacks = callbacks
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        list_frame = ttk.Frame(self)
        list_frame.grid(column=0, row=0, sticky=(N,W,E,S))

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        list_frame.rowconfigure(1, weight=8)

        list_header = ttk.Frame(list_frame)
        list_header.grid(column=0, row=0, sticky=(N,W,E,S))
        
        header_label = ttk.Label(list_header, text="Collections")
        header_label.grid(column=1, row=0, sticky=(N,W,E,S))

        list_add_btn = ttk.Button(list_header, text="+", command=self.create_collection_dialog)
        list_add_btn.grid(column=3, row=3, sticky=(E,S))

        
        self.collection_list_frame = VerticalScrolledFrame(list_frame)
        self.collection_list_frame.grid(column=0, row=1, sticky=(N,W,E,S))

      
        task_frame = ttk.Frame(self)
        task_frame.grid(column=1, row=0, sticky=(N,W,E,S))
        task_frame.columnconfigure(0, weight=1)
        task_frame.rowconfigure(0, weight=1)
        task_frame.rowconfigure(1, weight=12)
        task_control_frame = ttk.LabelFrame(task_frame, text="Controls")
        task_control_frame.grid(column=0, row=0, sticky=(N,W,E,S))
        
        create_task_bttn = ttk.Button(task_control_frame, text="+", command=self.create_task_dialog)
        create_task_bttn.grid(column=0,row=0,sticky=(N,W,E,S))
        
        self.task_list_frame = VerticalScrolledFrame(task_frame)
        self.task_list_frame.grid(column=0, row=1, sticky=(N,W,E,S))
