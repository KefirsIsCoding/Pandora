from tkinter import *
from tkinter import ttk
from pandora.models import Task, Collection, SubTask
from pandora.db import SqliteDb
from pandora.views import AgendaView, CollectionView

class Pandora:

    def create_collection(self, root, name):
        Collection.save(self.db, name)
        root.destroy()
        self.refresh_collections()


    def edit_collection(self, root, name, id):
        Collection.edit(self.db, name, id)
        root.destroy()
        self.refresh_collections()

    def delete_collection(self, root, id):
        Collection.delete(self.db, id)
        root.destroy()
        self.refresh_collections()

    def open_collection(self, collection):
        self.selected_collection = collection.id
        self.refresh_collections()

    def create_task(self, root, name):
        Task.save(self.db, name, self.selected_collection)
        root.destroy()
        self.refresh_collections()

    def edit_task(self, root, name, id):
        Task.edit(self.db, name, id)
        root.destroy()
        self.refresh_collections()

    def delete_task(self, root, id):
        Task.delete(self.db, id)
        root.destroy()
        self.refresh_collections()


    def create_subtask(self, root, name, task_id):
        SubTask.save(self.db, name, task_id)
        root.destroy()
        self.refresh_collections()

    def edit_subtask(self, root, name, progress, status, id, task_id):
        SubTask.edit(self.db, name, progress, status, id)
        root.destroy()
        self.refresh_collections()

        
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

        self.agenda_view = AgendaView(notebook)
        notebook.add(self.agenda_view, text="Agenda")

        collection_callbacks = {
                "create_collection": lambda x,y: self.create_collection(x,y),
                "edit_collection": lambda x,y,z: self.edit_collection(x,y,z),
                "delete_collection": lambda x,y: self.delete_collection(x,y),
                "open_collection": lambda x: self.open_collection(x),
                "create_task" : lambda x,y: self.create_task(x,y),
                "edit_task": lambda x,y,z: self.edit_task(x,y,z),
                "delete_task": lambda x,y: self.delete_task(x,y),
                "create_subtask": lambda x,y,z: self.create_subtask(x,y,z),
        }

        self.collection_view = CollectionView(notebook, collection_callbacks)
        notebook.add(self.collection_view, text="Collections")
        self.selected_collection = None
        self.selected_task = None
        self.refresh_collections()
        self.root = root 


    @property
    def collections(self):
        return [Collection(id, name) for id, name in Collection.get_all(self.db)]

    @property
    def tasks(self):
        if self.selected_collection:
            return [
                Task(id, name, status, progress, collection_id) for
                id, name, status, progress, collection_id in
                Task.get_all_in_collection(self.db, self.selected_collection)
            ]
        return []

    @property
    def subtasks(self):
        if self.selected_task:
            return [
                SubTask(id, name, task_id, status, progress) for
                id, name, status, progress, task_id in
                SubTask.get_all(self.db)
            ]
        return []


    def refresh_collections(self):
        self.collection_view.refresh(self.collections, self.tasks, self.subtasks)

    def mainloop(self):
        self.root.mainloop()



if __name__ == "__main__":
    app = Pandora()
    app.mainloop()
