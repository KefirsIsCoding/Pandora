from tkinter import *
from tkinter import ttk
from pandora.models import Task, Collection, SubTask, Agenda
from pandora.db import SqliteDb
from pandora.views import AgendaView, CollectionView
from pandora.consts import Status

class Pandora:

    def create_collection(self, root, name):
        Collection.save(self.db, name)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def edit_collection(self, root, name, id):
        Collection.edit(self.db, name, id)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def delete_collection(self, root, id):
        Collection.delete(self.db, id)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def open_collection(self, collection):
        self.selected_collection = collection.id
        self.refresh_collections()
        self.refresh_agendas()

    def create_task(self, root, name):
        Task.save(self.db, name, self.selected_collection)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def edit_task(self, root, name, fields, image, id):
        Task.edit(self.db, name, id, fields, image)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def delete_task(self, root, id):
        Task.delete(self.db, id)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def create_subtask(self, root, name, rep, date, task_id):
        SubTask.save(self.db, name, task_id, rep, date)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def edit_subtask(self, root, id, name, progress, status, rep, date):
        SubTask.edit(self.db, id, name, progress, status, rep, date)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def delete_subtask(self, root, id):
        SubTask.delete(self.db, id)
        root.destroy()
        self.refresh_collections()
        self.refresh_agendas()

    def finish_agenda_task(self, s_id):
        SubTask.set_status(self.db, s_id, Status.DONE.name)
        self.refresh_collections()
        self.refresh_agendas()

    def cancel_agenda_task(self, s_id):
        SubTask.set_status(self.db, s_id, Status.BACKLOG.name)
        self.refresh_collections()
        self.refresh_agendas()

    def __init__(self):
        self.db = SqliteDb.set_up()
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
        agenda_callbacks = {
                "finish_task": lambda s_id: self.finish_agenda_task(s_id),
                "cancel_task": lambda s_id: self.cancel_agenda_task(s_id),
        }
        self.agenda_view = AgendaView(notebook,self.agendas, agenda_callbacks)
        notebook.add(self.agenda_view, text="Agenda")

        collection_callbacks = {
                "create_collection": lambda x,y: self.create_collection(x,y),
                "edit_collection": lambda x,y,z: self.edit_collection(x,y,z),
                "delete_collection": lambda x,y: self.delete_collection(x,y),
                "open_collection": lambda x: self.open_collection(x),
                "create_task" : lambda x,y: self.create_task(x,y),
                "edit_task": lambda x,y,z,a,b: self.edit_task(x,y,z,a,b),
                "delete_task": lambda x,y: self.delete_task(x,y),
                "create_subtask": lambda root, name, rep, date, t_id: self.create_subtask(root, name, rep, date, t_id),
                "edit_subtask":
                lambda root, s_id, name, progress, status, rep, date: self.edit_subtask(root, s_id, name, progress, status, rep, date),
                "delete_subtask": lambda root, subtask_id: self.delete_subtask(root, subtask_id)

        }

        self.collection_view = CollectionView(notebook, collection_callbacks)
        notebook.add(self.collection_view, text="Collections")
        self.selected_collection = None
        self.refresh_collections()
        self.refresh_agendas()
        self.root = root 


    @property
    def collections(self):
        return Collection.get_all(self.db)

    @property
    def tasks(self):
        if self.selected_collection:
            return Task.get_all_in_collection(self.db, self.selected_collection)
        return []

    @property
    def subtasks(self):
        return SubTask.get_all(self.db)

    @property
    def agendas(self):
        return Agenda.get_agenda_list(self.db)


    def refresh_collections(self):
        self.collection_view.refresh(self.collections, self.tasks, self.subtasks)

    def refresh_agendas(self):
        self.agenda_view.refresh(self.agendas)

    def mainloop(self):
        self.root.mainloop()



if __name__ == "__main__":
    app = Pandora()
    app.mainloop()
