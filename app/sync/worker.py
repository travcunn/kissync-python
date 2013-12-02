class Worker(object):
    """ Task worker base class. """
    def __init__(self):
        self.__cancelled = False

    def process_task(self, task):
        self._process_task(task)

    def _process_task(self, task):
        """ Override this method to process a task. """
        raise NotImplementedError

    def cancel_task(self):
        """ Sends a signal to the worker to cancel the current task. """
        self.__cancelled = True

    def task_done(self):
        """ Method that should be called after task completion. """
        self.__cancelled = False

    @property
    def cancelled(self):
        """ Returns the status of the current task. """
        return self.__cancelled
