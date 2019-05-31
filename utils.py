import time, os, threading
import numpy as np

class Cabinet(object):
    """docstring for Cabinet."""

    def __init__(self):
        super(Cabinet, self).__init__()
        self.identifier = None
        self.counter = 0
        self.file_name = None
        self.thread_handle = None
        self.is_running = False
        self.received_data = []
        self.split_at = None
        self.values_registered = False
        self.exit_save = False

    def __del__(self):
        if self.identifier and not self.exit_save:
            self.counter += 1
            self.file_name = "training/training_data_%s%s.npy" % (self.identifier, self.counter)
            if len(self.received_data) > 100:
                print("Found identifier and data saving file: %s" % self.file_name)
                np.save(self.file_name,self.received_data)
            else:
                print("Not enough data to save")
            self.exit_save = True
        if self.is_running:
            print("Switching is_running to False")
            self.is_running = False
        if self.thread_handle != None:
            print("Trying to join thread")
            self.thread_handle.join()
            self.thread_handle = None
            print("Joined thread")
        else:
            print("Failed to find thread")


    def register_values(self,identifier, counter, split_at):
        if not self.values_registered:
            self.split_at = split_at
            self.values_registered = True
            self.counter = counter
            self.identifier = identifier
            self.file_name = "training/training_data_%s%s.npy" % (identifier, self.counter)
            print("file_name: %s" % self.file_name)
            if not os.path.isdir("training"):
                os.mkdir("training")
        else:
            print("Values already set")


    def watcher(self):
        while True:
            if self.is_running:
                if len(self.received_data) % 500 == 0 and len(self.received_data) != 0:
                    print("Data lenght: ",len(self.received_data))
                    time.sleep(3)
                if len(self.received_data) >= self.split_at:
                    print("Splitting data from list")
                    print("Current lenght:%s" % len(self.received_data))
                    data = self.received_data[:self.split_at]
                    print("Data lenght: %s" % len(data))
                    del self.received_data[:self.split_at]
                    print("new lenght:%s" % len(self.received_data))
                    np.save(self.file_name, data)
                    print("Saved file %s" % self.file_name)
                    self.counter +=1
                    self.file_name = "training/training_data_%s%s.npy" % (self.identifier, self.counter)
            else:
                break
        return 0

    def thread_watcher(self):
        if self.values_registered:
            if not self.is_running:
                self.is_running = True
                self.thread_handle = threading.Thread(target=self.watcher, args=())
                print("Starting Thread with handle: %s" % self.thread_handle)
                self.thread_handle.start()
            else:
                print("Thread running")
        else:
            print("Values not registered")
