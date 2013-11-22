from collections import namedtuple
from collections import OrderedDict
from Queue import Queue


class LifoDictQueue(Queue):
    """
    A specialized LIFO queue that implements an OrderedDict.
    Accepts Task objects to help assign a specific key to a task.
    Values are stored as arrays of tasks to be performed for a given key.
    """
    def _init(self, maxsize):
        self.queue = OrderedDict()
        self._items = 0

    def _get(self):
        task_slot = self.queue.popitem(last=True)
        if len(task_slot[1]) is 1:
            self._items -= 1
            task = Task(task_slot[0], task_slot[1][0])
            return task
        else:
            tasks = task_slot[1]
            last_task = tasks.pop(len(tasks) - 1)
            self._items -= len(tasks) + 1
            for item in tasks:
                task_item = Task(task_slot[0], item)
                self._put(task_item)
            task = Task(task_slot[0], last_task)
            return task

    def _put(self, task):
        if hasattr(task, 'key'):
            key = task.key
            properties = task.properties
        else:
            key = hash(task)
            properties = task
        try:
            self.queue[key].append(properties)
        except KeyError:
            self.queue.update({key: []})
            self.queue[key].append(properties)

        self._items += 1

    def _qsize(self, len=len):
        return self._items

    def updateTaskKey(self, task_key, new_key):
        """
        Modify the path of a task in the queue. Specify the task_id and the
        new_id to change the path.
        """
        self.queue[new_key] = self.queue.pop(task_key)


Task = namedtuple("Task", "key properties")
