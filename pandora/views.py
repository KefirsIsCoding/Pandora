from tkinter import *
from tkinter import ttk
from .widgets import VerticalScrolledFrame, CollectionWidget, TaskWidget, AgendaItem, Calendar
from .consts import Status

class AgendaView(ttk.Frame):

    def refresh(self, agendas):
        for w in self.agenda_list_frame.interior.winfo_children():
            w.destroy()
        for t, st in agendas.items():
            item = AgendaItem(self.agenda_list_frame.interior, t, st)
            item.pack(expand=True, fill="x")

    def __init__(self, parent, callbacks):
        super().__init__(parent)
        self.callbacks = callbacks

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.rowconfigure(0, weight=1)
        agenda_list = ttk.LabelFrame(self, text="Agenda list")
        agenda_list.grid(column=0, row=0, sticky=(N,W,E,S))
        agenda_list.columnconfigure(0, weight=1)
        agenda_list.rowconfigure(0, weight=1)

        self.agenda_list_frame = VerticalScrolledFrame(agenda_list)
        self.agenda_list_frame.grid(sticky=(N,W,E,S))

        calendar_frame = ttk.LabelFrame(self, text="Calendar")
        calendar_frame.grid(column=1, row=0, sticky=(N,W,E,S))
        calendar_frame.columnconfigure(0, weight=1)
        calendar_frame.rowconfigure(0, weight=1)
        Calendar(calendar_frame, []).grid(column=0, row=0, sticky=(N,W,E,S))

    def finish_agenda_task(self, s_id):
        self.callbacks["finish_task"](s_id)

    def cancel_agenda_task(self, s_id):
        self.callbacks["cancel_task"](s_id)


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

    def refresh(self, collections, tasks, subtasks):
        self.update_collection(collections)
        self.update_task(tasks)
        for t in tasks:
            self.update_subtasks(subtasks, t.id)

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
            TaskWidget(self.task_list_frame.interior, t.name, t.id, t.progress, t.status).pack(expand=True, fill="x")

    def update_subtasks(self, subtasks, task_id):
        filtered_subtasks = [subtask for subtask in subtasks if subtask.task_id == task_id]
        subtask_callbacks = {name: function for name, function in self.callbacks.items() if "subtask" in name}
        for w in self.task_list_frame.interior.winfo_children():
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

        subtask_name = StringVar()
        subtask_rep = BooleanVar(value=False)
        subtask_date_type = StringVar(value="Any")
        subtask_date_specific = StringVar()
        combox_vals = ["Any", "Weekends", "Weekdays", "Monthly", "Specific Date"]
        from datetime import datetime, timedelta
        dates = [x.isoformat()[0:10] for x in (datetime.now() + timedelta(days=i) for i in range(365))]


        def change_box(s_type, date_w):
            if s_type == "Specific Date":
                date_w.configure(state="enabled")
            else:
                date_w.configure(state="disabled")

        ttk.Label(t, text="Subtask name:").grid(column=0, row=1)
        ttk.Entry(t, textvariable=subtask_name).grid(column=1, row=1)
        ttk.Label(t, text="Repeatable:").grid(column=0, row=2)
        ttk.Checkbutton(t, variable=subtask_rep, onvalue=True, offvalue=False).grid(column=1, row=2)
        ttk.Label(t, text="Due:").grid(column=0, row=3)
        d_type_select = ttk.Combobox(t, textvariable=subtask_date_type, values=combox_vals)
        d_type_select.grid(column=1, row=3)
        date_select = ttk.Combobox(t, textvariable=subtask_date_specific, state="disabled", values=dates)
        date_select.grid(column=1, row=4)
        d_type_select.bind("<<ComboboxSelected>>", lambda x: change_box(subtask_date_type.get(), date_select))
        ttk.Button(t, text="Ok", command=lambda: 
            self.callbacks["create_subtask"](
                t,
                subtask_name.get(), 
                subtask_rep.get(), 
                subtask_date_type.get() if subtask_date_type.get() != "Specific Date" else subtask_date_specific.get(), 
                task.id)).grid(column=2, row=5)

    def edit_subtask_dialog(self, subtask):
        t = Toplevel(self)
        t.title("Edit a subtask")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        subtask_name = StringVar()
        subtask_name.set(subtask.name)

        subtask_progress = StringVar()
        subtask_progress.set(subtask.progress)

        subtask_status = StringVar()
        subtask_status.set(subtask.status)

        subtask_rep = BooleanVar()
        subtask_rep.set(subtask.repeat)

        combox_vals = ["Any", "Weekends", "Weekdays", "Monthly", "Specific Date"]
        subtask_date_type = StringVar()
        subtask_date_specific = StringVar()
        from datetime import datetime, timedelta
        dates = [x.isoformat()[0:10] for x in (datetime.now() + timedelta(days=i) for i in range(365))]


        def change_box(s_type, date_w):
            if s_type == "Specific Date":
                date_w.configure(state="enabled")
            else:
                date_w.configure(state="disabled")

        ttk.Label(t, text="Subtask name:").grid(column=0, row=1)
        ttk.Entry(t, textvariable=subtask_name).grid(column=1, row=1)
        ttk.Label(t, text="Subtask progress:").grid(column=0, row=2)
        ttk.Entry(t, textvariable=subtask_progress).grid(column=1, row=2)
        ttk.Label(t, text="Subtask status:").grid(column=0, row=3)
        ttk.Combobox(t, textvariable=subtask_status, values=[v.name for v in Status]).grid(column=1, row=3)
        ttk.Label(t, text="Repeatable:").grid(column=0, row=4)
        ttk.Checkbutton(t, variable=subtask_rep, onvalue=True, offvalue=False).grid(column=1, row=4)
        ttk.Label(t, text="Due date:").grid(column=0, row=5)
        d_type_select = ttk.Combobox(t, textvariable=subtask_date_type, values=combox_vals)
        d_type_select.grid(column=1, row=5)
        date_select = ttk.Combobox(t, textvariable=subtask_date_specific, values=dates)
        date_select.grid(column=1, row=6)
        d_type_select.bind("<<ComboboxSelected>>", lambda x: change_box(subtask_date_type.get(), date_select))
        if subtask.date in combox_vals:
            subtask_date_type.set(subtask.date)
            date_select.configure(state="disabled")
        else:
            subtask_date_type.set("Specific Date")
            subtask_date_specific.set(subtask.date)

        ttk.Button(t, text="Ok", command=lambda: self.callbacks["edit_subtask"](
            t,
            subtask.id,
            subtask_name.get(),
            subtask_progress.get(),
            subtask_status.get(),
            subtask_rep.get(),
            subtask_date_type.get() if subtask_date_type.get() != "Specific Date" else subtask_date_specific.get()
            )).grid(column=2, row=7)

    def delete_subtask_dialog(self, subtask):
        t = Toplevel(self)
        t.title("Delete this subtask?")
        t.columnconfigure(0, weight=1)
        t.columnconfigure(1, weight=1)
        t.columnconfigure(2, weight=1)

        t.rowconfigure(0, weight=1)
        t.rowconfigure(1, weight=1)
        t.rowconfigure(2, weight=1)

        ttk.Label(t, text="Are you sure?").grid(column=0, row=1)
        ttk.Button(t, text="Ok", command=lambda: self.callbacks["delete_subtask"](t, subtask.id)).grid(column=2, row=2)


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
