import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog as fd
from tkinter.constants import *
from datetime import datetime, timedelta
from calendar import monthrange
from .consts import WeekDays, Status, DateChoices
from abc import ABC, abstractmethod
from PIL import Image, ImageTk

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
    def __init__(self, parent, name, id, progress, status, repeat, date):
        super().__init__(parent)
        self.id = id
        self.name = name
        self.progress = progress
        self.status = status
        self.repeat = repeat
        self.date = date
        self["borderwidth"] = 2
        self["relief"] = "raised"

        # Field columns
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=5)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)

        ttk.Label(self, text=f"Title: {name}").grid(column=0, row=0, sticky=(N,W,E,S))
        self.title_f = StringField(self, "Title", name)
        self.title_f.grid(column=0, row=0, sticky=(N,W,E,S))
        self.progress_f = CounterField(self, "Progress", progress)
        self.progress_f.grid(column=1, row=0, sticky=(N,W,E,S))
        self.status_f = ChoiceField(self, "Status", status, [v.name for v in Status])
        self.status_f.grid(column=2, row=0, sticky=(N,W,E,S))
        self.repeat_f = CheckboxField(self, "Repeatable", repeat)
        self.repeat_f.grid(column=3, row=0, sticky=(N,W,E,S))
        self.date_f = DateField(self, "Due", date, [v.value for v in DateChoices])
        self.date_f.grid(column=4, row=0, sticky=(N,W,E,S))

        self.edit_bttn = ttk.Button(self, text="Edit", command=self.edit_subtask)
        self.edit_bttn.grid(column=5,row=0, sticky=(N,W,E,S))
        self.del_bttn = ttk.Button(self, text="X", command=self.delete_subtask)
        self.del_bttn.grid(column=6, row=0, sticky=(N,W,E,S))

        # Need to resolve this stuff better
        self.c_view = self.master.master.master.master.c_view


    def edit_subtask(self):
        self.edit_bttn.configure(command=self.c_view.edit_subtask_dialog(self))
    
    def delete_subtask(self):
        self.del_bttn.configure(command=self.c_view.delete_subtask_dialog(self))


class TaskWidget(ttk.Frame):
    def __init__(self, parent, name, id, status, progress, custom_fields, image, notes=None, linked_task=None):
        super().__init__(parent)
        self.id = id
        self.name = name
        self.expanded = False
        self.subtasks = []
        self.custom_fields = custom_fields
        self.image_path = image
        custom_len = len(self.custom_fields)
        # Fix this res later
        self.c_view = self.master.master.master.master.master

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        ## Field columns
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.columnconfigure(4, weight=1)
        self.columnconfigure(5, weight=1)
        self.columnconfigure(6, weight=1)
        self.columnconfigure(7, weight=1)
        self.columnconfigure(8, weight=1)
        self.columnconfigure(9, weight=1)
        self.columnconfigure(10, weight=1)
        self.columnconfigure(11, weight=1)
        self["borderwidth"] = 2
        self["relief"] = "raised"
        if self.image_path:
            self.image_f = ImageField(self, self.image_path)
            self.image_f.grid(column=0, row=0, sticky=(W))
        self.title = StringField(self, "Title", name)
        self.title.grid(column=1, row=0, sticky=(N,W,E,S))
        for idx, f in enumerate(custom_fields):
            StringField(self, f.name, f.value).grid(column=idx+1, row=0, sticky=(N,W,E,S))
        CounterField(self, "Progress", progress).grid(column=custom_len+2, row=0, sticky=(N,W,E,S))
        ChoiceField(self, "Status", status, [v.name for v in Status]).grid(column=custom_len+3, row=0, sticky=(N,W,E,S))
        self.edit_bttn = ttk.Button(self, text="Edit", command=self.edit_task)
        self.edit_bttn.grid(column=custom_len+4,row=0, sticky=(N,W,E,S))
        self.del_bttn = ttk.Button(self, text="X", command=self.delete_task)
        self.del_bttn.grid(column=custom_len+6, row=0, sticky=(N,W,E,S))
        self.new_bttn = ttk.Button(self, text="+", command=self.create_subtask)
        self.new_bttn.grid(column=custom_len+7, row=0, sticky=(N,W,E,S))
        self.open_bttn = ttk.Button(self, text=">", command=self.open_task_dropdown)
        self.open_bttn.grid(column=custom_len+8, row=0, sticky=(N,W,E,S))

        self.subtask_window = VerticalScrolledFrame(self)
        self.refresh_subtask_list()

    def set_subtasks(self, subtasks):
        self.subtasks = subtasks
        self.refresh_subtask_list()
    
    def refresh_subtask_list(self):
        for t in self.subtask_window.interior.winfo_children():
            t.destroy()
        if not self.expanded:
            if not self.subtasks:
                no_tasks = ttk.Frame(self.subtask_window.interior)
                no_tasks.pack()
                ttk.Label(no_tasks, text="Add some sub-tasks!").pack(expand=True, fill="x")
            else:
                for t in self.subtasks:
                    SubTaskWidget(self.subtask_window.interior, t.name, t.id, t.progress, t.status, t.repeat, t.date).pack(expand=True, fill="x")

    def edit_task(self):
        self.edit_bttn.configure(command=self.c_view.edit_task_dialog(self))
    
    def delete_task(self):
        self.del_bttn.configure(command=self.c_view.delete_task_dialog(self))

    def create_subtask(self):
        self.new_bttn.configure(command=self.c_view.create_subtask_dialog(self))

    def open_task_dropdown(self):
        if self.expanded:
            self.subtask_window.grid_forget()
        else:
            self.refresh_subtask_list()
            self.subtask_window.grid(column=0, row=1, columnspan=7, sticky=(N,W,E,S))
        self.expanded = not self.expanded
        

class AgendaItem(ttk.Frame):
    def __init__(self, parent, task_name, subtasks):
        super().__init__(parent)
        self.a_view = parent.master.master.master.master
        ttk.Label(self, text=f"---{task_name}---").pack(anchor=NW)
        for s_id, sub_data in subtasks.items():
            sub_frame = ttk.Frame(self)
            sub_frame.pack(anchor=NW, padx=25, fill="x")
            sub_frame.columnconfigure(0, weight=5)
            ttk.Label(sub_frame, text=sub_data[0]).grid(column=0, row=0)
            ttk.Label(sub_frame, text=f"Due: {sub_data[2]}").grid(column=1, row=0)
            ttk.Button(sub_frame, text="Done", command=self.finish_task(s_id), state="disabled" if sub_data[1] else "enabled").grid(column=2,row=0)
            ttk.Button(sub_frame, text="X", command=self.cancel_task(s_id)).grid(column=3,row=0)

    def finish_task(self, s_id):
        return lambda: self.a_view.finish_agenda_task(s_id)

    def cancel_task(self, s_id):
        return lambda: self.a_view.cancel_agenda_task(s_id)


class HoverLabel(ttk.Label):
    def __init__(self, parent, info, *args, **kw):
        super().__init__(parent, *args, **kw)
        self.info = info
        self.box = None
        self.bind("<Enter>", lambda x: self.show_info())
        self.bind("<Leave>", lambda x: self.hide_info())

    def show_info(self):
        # TODO: Rewrite this Toplevel is not the solve
        if self.info:
            self.box = tk.Toplevel(self)
            for i in self.info:
                ttk.Label(self.box,text=i).grid()
            self.box.grid()

    def hide_info(self):
        if self.info:
            self.box.destroy()


class Calendar(ttk.Frame):
    def __init__(self, parent, subtask_info):
        super().__init__(parent)
        self.subtask_info = subtask_info
        style = ttk.Style()
        style.configure("TEntry", background='black')
        self["style"] = "TEntry"

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=20)
        self.init_date(datetime.now())
        d_o_w = ["Mon", "Tue", "Wed", "Thr", "Fri", "Sat", "Sun"]
        self.info_row = ttk.Frame(self, style="TEntry")
        self.info_row.grid(row=0, column=0, sticky=(N,W,E,S))
        self.info_row.columnconfigure(0, weight=1)

        self.month_label = ttk.Label(self.info_row, text=self.month)
        self.month_label.grid(row=0, column=0, sticky=(N,W,E,S))
        self.year_label = ttk.Label(self.info_row, text=self.year)
        self.year_label.grid(row=0, column=1, sticky=(N,W,E,S))
        ttk.Button(self.info_row, text="<", command=self.previous_month).grid(row=0, column=2, sticky=(N,W,E,S))
        ttk.Button(self.info_row, text=">", command=self.next_month).grid(row=0, column=3, sticky=(N,W,E,S))
        self.month_day_row = ttk.Frame(self)
        self.month_day_row.grid(row=1, column=0, sticky=(N,W,E,S))

        for i, day in enumerate(d_o_w):
            self.month_day_row.columnconfigure(i, weight=1)
            ttk.Label(self.month_day_row, text=day).grid(row=0, column=i, sticky=(N,W,E,S))
        self.month_view = ttk.Frame(self)
        self.month_view.grid(row=2, column=0, sticky=(N,W,E,S))
        self.month_view.columnconfigure(0, weight=1)
        self.month_view.columnconfigure(1, weight=1)
        self.month_view.columnconfigure(2, weight=1)
        self.month_view.columnconfigure(3, weight=1)
        self.month_view.columnconfigure(4, weight=1)
        self.month_view.columnconfigure(5, weight=1)
        self.month_view.columnconfigure(6, weight=1)
        self.month_view.rowconfigure(0, weight=1)
        self.month_view.rowconfigure(1, weight=1)
        self.month_view.rowconfigure(2, weight=1)
        self.month_view.rowconfigure(3, weight=1)
        self.month_view.rowconfigure(4, weight=1)
        self.month_view.rowconfigure(5, weight=1)
        self.draw_month()

    def refresh(self, subtasks):
        self.subtask_info = subtasks
        self.init_date(datetime.now())
        self.draw_month()


    def draw_month(self):
        for w in self.month_view.winfo_children():
            w.destroy()
        start = self.first_day - timedelta(days=self.get_first_monday_offset())
        weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        weekends = ["Sat", "Sun"]
        for row in range(6):
            for col in range(7):
                info = []
                for s in self.subtask_info.values():
                    for sub in s.values():
                        # 0 name, 1 repeatable, 2 date
                        # YandereDev tier code
                        if sub[2] == "Any":
                            info.append(sub[0])
                        elif sub[2] == "Weekdays" and start.strftime("%a") in weekdays:
                            info.append(sub[0])
                        elif sub[2] == "Weekends" and start.strftime("%a") in weekends:
                            info.append(sub[0])
                        elif sub[2] == "Monthly" and start.day == monthrange(self.date.year, self.date.month)[1]:
                            info.append(sub[0])
                        elif sub[2] == start.isoformat()[0:10]:
                            info.append(sub[0])
                HoverLabel(self.month_view, info, text=start.day).grid(column=col, row=row, sticky=(N,W,E,S))
                start = start + timedelta(days=1)

    def init_date(self, time):
        self.date = time
        self.month = time.strftime("%B")
        self.year = time.strftime("%G")
        self.first_day = (time - timedelta(time.day-1))

    def next_month(self):
        days = monthrange(self.date.year, self.date.month)
        self.init_date(self.date + timedelta(days=days[1]))
        self.month_label["text"] = self.month
        self.year_label["text"] = self.year
        self.draw_month()

    def previous_month(self):
        days = monthrange(self.date.year, self.date.month)
        self.init_date(self.date - timedelta(days=days[1]))
        self.month_label.configure(text=self.month)
        self.year_label.configure(text=self.year)
        self.draw_month()

    def get_first_monday_offset(self):
        for days in WeekDays:
            if self.first_day.strftime("%A") == days.value[1]:
                return days.value[0]

class CustomField(ABC):
    """
    Field widgets that show up on Tasks and Subtasks

    All fields should configure their own layout within their own label
    They should also provide a callable way to edit them
    """
    def __init__(self, parent, name, value):
        self.name = name
        self.value = value

    @abstractmethod
    def create_field():
        pass

class StringField(ttk.Frame, CustomField):
    def __init__(self, parent, name, value):
        super().__init__(parent)
        self.name = name
        self.value = value
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.label = ttk.Label(self, text=f"{name}: {value}")
        self.label.grid(column=0, row=0, sticky=(N,W,E,S))

    def create_field(root, name, value):
        edit_field = ttk.Frame(root)
        edit_field.rowconfigure(0, weight=1)
        edit_field.columnconfigure(0, weight=1)
        edit_field.columnconfigure(1, weight=1)
        description = ttk.Label(edit_field, text=f"{name}: ")
        description.grid(column=0, row=0, sticky=(N,W,E,S))
        value_field = ttk.Entry(edit_field, textvariable=value)
        value_field.grid(column=1, row=0, sticky=(N,W,E,S))
        return edit_field

class CounterField(ttk.Frame, CustomField):
    def __init__(self, parent, name, value):
        super().__init__(parent)
        self.name = name
        self.value = (value.split("/")[0], value.split("/")[1]) if "/" in value else (0,0)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        ttk.Label(self, text=f"{name}: {self.value[0]}/{self.value[1]}").grid(column=0, row=0, sticky=(N,W,E,S))

    def create_field(root, name, val_start, val_end):
        edit_field = ttk.Frame(root)
        edit_field.rowconfigure(0, weight=1)
        edit_field.columnconfigure(0, weight=1)
        edit_field.columnconfigure(1, weight=1)
        description = ttk.Label(edit_field, text=f"{name}: ")
        description.grid(column=0, row=0, sticky=(N,W,E,S))
        val_field = ttk.Frame(edit_field)
        val_field.columnconfigure(0, weight=1)
        val_field.rowconfigure(0, weight=1)
        val_field.grid(column=1, row=0, sticky=(N,W,E,S))
        val_start_field = ttk.Entry(val_field, textvariable=val_start)
        val_start_field.grid(column=0, row=0, sticky=(N,W,E,S))
        val_split_field = ttk.Label(val_field, text="/")
        val_split_field.grid(column=1, row=0, sticky=(N,W,E,S))
        val_end_field = ttk.Entry(val_field, textvariable=val_end)
        val_end_field.grid(column=2, row=0, sticky=(N,W,E,S))
        return edit_field


class ChoiceField(ttk.Frame, CustomField):
    def __init__(self, parent, name, value, choices):
        super().__init__(parent)
        self.name = name
        self.value = value
        self.choices = choices
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.label = ttk.Label(self, text=f"{name}: {value}")
        self.label.grid(column=0, row=0, sticky=(W))

    def create_field(root, name, value, choices):
        edit_field = ttk.Frame(root)
        edit_field.rowconfigure(0, weight=1)
        edit_field.columnconfigure(0, weight=1)
        edit_field.columnconfigure(1, weight=1)
        description = ttk.Label(edit_field, text=f"{name}: ")
        description.grid(column=0, row=0, sticky=(N,W,E,S))
        choices = ttk.Combobox(edit_field, textvariable=value, values=choices)
        choices.grid(column=1, row=0, sticky=(N,W,E,S))
        return edit_field

class CheckboxField(ttk.Frame, CustomField):
    def __init__(self, parent, name, value):
        super().__init__(parent)
        self.name = name
        self.value = value
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.label = ttk.Label(self, text=f"{name}: {bool(value)}")
        self.label.grid(column=0, row=0, sticky=(N,W,E,S))

    def create_field(root, name, value):
        edit_field = ttk.Frame(root)
        edit_field.rowconfigure(0, weight=1)
        edit_field.columnconfigure(0, weight=1)
        edit_field.columnconfigure(1, weight=1)
        description = ttk.Label(edit_field, text=f"{name}: ")
        description.grid(column=0, row=0, sticky=(N,W,E,S))
        choices = ttk.Checkbutton(edit_field, variable=value, onvalue=True, offvalue=False)
        choices.grid(column=1, row=0, sticky=(N,W,E,S))
        return edit_field


class DateField(ttk.Frame, CustomField):
    def __init__(self, parent, name, value, choices):
        super().__init__(parent)
        self.name = name
        self.value = value
        self.choices = choices
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.label = ttk.Label(self, text=f"{name}: {value}")
        self.label.grid(column=0, row=0, sticky=(N,W,E,S))

    def create_field(root, name, val_type, val_date, choices):
        edit_field = ttk.Frame(root)
        edit_field.rowconfigure(0, weight=1)
        edit_field.columnconfigure(0, weight=1)
        edit_field.columnconfigure(1, weight=1)
        description = ttk.Label(edit_field, text=f"{name}: ")
        description.grid(column=0, row=0, sticky=(N,W,E,S))
        input_field = ttk.Frame(edit_field)
        input_field.grid(column=1, row=0, sticky=(N,W,E,S))

        date_type_select = ttk.Combobox(input_field, textvariable=val_type, values=choices)
        date_type_select.grid(column=0, row=0, sticky=(N,W,E,S))

        def eval_date_field(val_type, date_box):
            if val_type.get() == "Specific Date":
                date_box.configure(state="enabled")
            else:
                date_box.configure(state="disabled")

        from datetime import datetime, timedelta
        dates = [x.isoformat()[0:10] for x in (datetime.now() + timedelta(days=i) for i in range(365))]
        specific_date_select = ttk.Combobox(input_field, textvariable=val_date, values=dates)
        specific_date_select.grid(column=0, row=1, sticky=(N,W,E,S))
        date_type_select.bind("<<ComboboxSelected>>", lambda x: eval_date_field(val_type, specific_date_select))
        return edit_field

                              


class ImageField(ttk.Frame, CustomField):
    def __init__(self, parent, path):
        super().__init__(parent)
        self.path = path 
        image = Image.open(self.path)
        image = image.resize((100, 100), Image.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        label = ttk.Label(self, image=photo)
        label.photo = photo
        label.grid()

    def create_field(root, value):
        edit_field = ttk.Frame(root)
        edit_field.rowconfigure(0, weight=1)
        edit_field.columnconfigure(0, weight=1)
        edit_field.columnconfigure(1, weight=1)
        description = ttk.Label(edit_field, text=f"Select image: ")
        description.grid(column=0, row=0, sticky=(N,W,E,S))
        def read_file():
            f = fd.askopenfile()
            filename = f.name.split("/")[-1]
            if filename.endswith(".png") or filename.endswith(".jpg"):
                value.set(f.name)
        add_btn = ttk.Button(edit_field, text="+", command=read_file)
        add_btn.grid(column=1, row=0, sticky=(N,W,E,S))
        return edit_field

class NoteField(ttk.Frame, CustomField):
    def __init__(self, value):
        pass

    def create_field(value):
        
        pass

class TasklinkField(ttk.Frame, CustomField):
    def __init__(self, value):
        pass

    def create_field(value):
        """ Dropdown list of all tasks?"""
        pass
