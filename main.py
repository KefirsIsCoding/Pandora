from tkinter import *
from tkinter import ttk
from pandora.models import Task, Collection, SubTask
from pandora.db import SqliteDb
from pandora.views import AgendaView, CollectionView

class Pandora:

    def create_collection(self, root, name):
        Collection.save(self.db, name)
        self.collections = [Collection(id, name) for id, name in Collection.get_all(self.db)]
        root.destroy()
        self.collection_view.update_collection(self.collections)

    def edit_collection(self, root, name, id):
        Collection.edit(self.db, name, id)
        self.collections = [Collection(id, name) for id, name in Collection.get_all(self.db)]
        root.destroy()
        self.collection_view.update_collection(self.collections)

    def delete_collection(self, root, id):
        Collection.delete(self.db, id)
        self.collections = [Collection(id, name) for id, name in Collection.get_all(self.db)]
        root.destroy()
        self.collection_view.update_collection(self.collections)

    def open_collection(self, collection):
        self.active_collection = collection.id
        self.tasks = [
                    Task(id, name, status, progress, collection_id) for id, name, status, progress, collection_id in Task.get_all_in_collection(self.db, collection.id)
        ]
        self.collection_view.update_task(self.tasks)

    def create_task(self, root, name):
        Task.save(self.db, name, self.active_collection) 
        self.tasks = [
            Task(id, name, status, progress, collection_id) for id, name, status, progress, collection_id in Task.get_all_in_collection(self.db, self.active_collection)
        ]
        root.destroy()
        self.collection_view.update_task(self.tasks)

    def edit_task(self, root, name, id):
        Task.edit(self.db, name, id)
        self.tasks = [
            Task(id, name, status, progress, collection_id) for id, name, status, progress, collection_id in Task.get_all_in_collection(self.db, self.active_collection)
        ]
        root.destroy()
        self.collection_view.update_task(self.tasks)

    def delete_task(self, root, id):
        Task.delete(self.db, id)
        self.tasks = [
            Task(id, name, status, progress, collection_id) for id, name, status, progress, collection_id in Task.get_all_in_collection(self.db, self.active_collection)
        ]
        root.destroy()
        self.collection_view.update_task(self.tasks)


    def create_subtask(self, root, name, task_id):
        SubTask.save(self.db, name, task_id)
        self.subtasks = [
            SubTask(id, name, task_id, status, progress) for id, name, status, progress, task_id in SubTask.get_all_in_task(self.db, task_id)
        ]
        root.destroy()
        self.collection_view.update_subtasks(self.subtasks, task_id)

    def edit_subtask(self, root, name, progress, status, id, task_id):
        SubTask.edit(self.db, name, progress, status, id)
        self.subtasks = [
                SubTask(id, name, task_id, status, progress) for id, name, status, progress, task_id in SubTask.get_all_in_task(self.db, task_id)
        ]
        root.destroy()
        self.collection_view.update_subtasks(self.subtasks, task_id)

        
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
        self.active_collection = None
        self.collections = [Collection(id, name) for id, name in Collection.get_all(self.db)]
        self.collection_view.update_collection(self.collections)
        self.tasks = []
        self.subtasks = []
        self.root = root 

    def mainloop(self):
        self.root.mainloop()



if __name__ == "__main__":
    app = Pandora()
    app.mainloop()
