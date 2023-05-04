from PyQt5.QtCore import QObject, QRunnable
from back import *

class HeavyTaskThread(QRunnable): # Thread for heavy task
    def __init__(self, param1, param2, param3): # Constructor
        super().__init__()  
        # Store constructor arguments (re-used for processing)
        self.noMasks = param1 
        self.original_image = param2
        self.backend = param3

    def run(self):
        # Perform heavy task here
        self.backend.initImageProcessing(self.noMasks, self.original_image)