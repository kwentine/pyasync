class Task(object):
    
    def __init__(self, coroutine):
        self.coroutine = coroutine
        self.next = None

    def run(self):
        try:
            future = self.coroutine.send(self.next)

            def on_result(f):
                self.next = f.get_result()
                self.run()

            future.add_done_callback(on_result)
        except StopIteration as e:
            return e.args[0]



class Future(object):

    def __init__(self):
        self.callbacks = []

    def add_done_callback(self, callback):
        self.callbacks.append(callback)

    def set_result(self, result):
        self.result = result
        for callback in self.callbacks:
            callback(self)

    def get_result(self):
        return self.result



        
