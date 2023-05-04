#Libraries
#pyuic5.exe -x p1.ui -o p1.py
import os
from os.path import isfile, join 
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QThreadPool, pyqtSlot
from main import *
import asyncio
from thread import *
import cv2

class Ui_MainWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    
    blurredPath = r'./nueva_blur' # Path to blurred images
    fileList = [] # List of images in blurredPath
    currentIndex = 0 # Current index of fileList
    original_image = '' # Path to original image
    noMasks = 0 # Number of masks

    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs) # Call the inherited classes __init__ method
        self.setupUi(self) # Call the inherited classes setupUi method which does all the heavy lifting
        self.changeStatus() # Change status of hardware

        #---------Original Image---------
        self.graphicsView.setAcceptDrops(True) # Allow drop image in graphicsView
        self.graphicsView.dragEnterEvent = self.dragEnterEvent # Call dragEnterEvent when image is dragged
        self.graphicsView.dropEvent = self.dropEvent # Call dropEvent when image is dropped
        #--------------------------------

        #------------Carousel------------
        self.back.clicked.connect(lambda: self.imageCarousel('previous')) # Call imageCarousel with 'previous' as parameter
        self.next.clicked.connect(lambda: self.imageCarousel('next')) # Call imageCarousel with 'next' as parameter
        #--------------------------------

        self.arrayPushButton = [self.pushButton, self.pushButton_4, self.pushButton_5] # Array of pushButtons
        
        self.pushButton_2.clicked.connect(self.runProgram) # Call runProgram when pushButton_2 is clicked

        self.threadpool = QThreadPool() # Create threadpool
    
    def hardwarestatus(self, pc1, pc2, master): # Change status of hardware
        if master == 1: # If master is connected
            self.pushButton.setStyleSheet("background-color: #2ECC71; color: white; border-radius: 10px;")
        else: # If master is not connected
            self.pushButton.setStyleSheet("background-color: #D0312D; color: white; border-radius: 10px;")
        if pc1 == 1: # If pc1 is connected
            self.pushButton_4.setStyleSheet("background-color: #2ECC71; color: white; border-radius: 10px;")
        else: # If pc1 is not connected
            self.pushButton_4.setStyleSheet("background-color: #D0312D; color: white; border-radius: 10px;")
        if pc2 == 1: # If pc2 is connected
            self.pushButton_5.setStyleSheet("background-color: #2ECC71; color: white; border-radius: 10px;")
        else: # If pc2 is not connected
            self.pushButton_5.setStyleSheet("background-color: #D0312D; color: white; border-radius: 10px;")

    # Drag image from directory
    def dragEnterEvent(self, event): # Drag image from directory
        if event.mimeData().hasUrls(): # If image is dragged
            event.accept() # Accept event
        else: 
            event.ignore()

    # Drop image in application   
    def dropEvent(self, event): # Drop image in application
        urls = event.mimeData().urls()[0] # Get url of image

        image_path = urls.path() # Get path of image
        print(image_path) # Print path of image

        Ui_MainWindow.original_image = image_path # Set original_image as image_path
        self.setImage(image_path, self.graphicsView) # Set image in graphicsView
        self.pushButton_2.setEnabled(True) # Enable pushButton_2
    
    @staticmethod
    def getMaskNumber(): # Get mask number
        return(int(''.join(filter(str.isdigit, Ui_MainWindow.fileList[Ui_MainWindow.currentIndex])))) # Return mask number
    
    # Get images in folder
    @staticmethod
    def getFolderImages(): # Get images in folder
        files = [f for f in os.listdir(Ui_MainWindow.blurredPath) if isfile(join(Ui_MainWindow.blurredPath, f))] # Get images in folder
        files.sort() # Sort images
        Ui_MainWindow.fileList = files # Set fileList as files

    # Set image in Qt Object
    def setImage(self, imagePath, qtObject): 
        try: # Try to set image in Qt Object
            scene = QtWidgets.QGraphicsScene(self) # Create scene
            pixmap = QtGui.QPixmap(imagePath) # Create pixmap
            pixmap = pixmap.scaled(QtCore.QSize(200, 200), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation) # Scale pixmap
            item = QtWidgets.QGraphicsPixmapItem(pixmap) # Create item
            scene.addItem(item) # Add item to scene
            qtObject.setScene(scene) # Set scene in Qt Object
        except Exception as e:print(e) # If error, print error

    def imageCarousel(self, buttonType): # Image carousel
        Ui_MainWindow.getFolderImages() # Get images in folder
        if buttonType == 'next': # If buttonType is next
            if Ui_MainWindow.currentIndex < len(Ui_MainWindow.fileList)-1: # If currentIndex is less than length of fileList
                Ui_MainWindow.currentIndex += 1 # Increase currentIndex
            else: # If currentIndex is equal to length of fileList
                Ui_MainWindow.currentIndex = 0 # Set currentIndex to 0
        elif buttonType == 'previous': # If buttonType is previous
            if Ui_MainWindow.currentIndex > 0: # If currentIndex is greater than 0
                Ui_MainWindow.currentIndex -= 1 #  Decrease currentIndex
            else: # If currentIndex is equal to 0
                Ui_MainWindow.currentIndex = len(Ui_MainWindow.fileList)-1 # Set currentIndex to length of fileList - 1
        if any(char.isdigit() for char in Ui_MainWindow.fileList[Ui_MainWindow.currentIndex]): # If fileList contains a number
            self.label_3.setText(f'Máscara de desenfoque No. {self.getMaskNumber()}') # Set label_3 text as mask number
        else: # If fileList does not contain a number
            self.label_3.setText(f'Imagen original') # Set label_3 text as original image
        self.setImage(f'{Ui_MainWindow.blurredPath}/{Ui_MainWindow.fileList[Ui_MainWindow.currentIndex]}', self.graphicsView_2) # Set image in graphicsView_2

    # Do an asyn call to getFolderImages every second until fileList is not empty
    def continuouslygetFolderImages(self): # Do an asyn call to getFolderImages every second until fileList is not empty
        im = cv2.imread(Ui_MainWindow.original_image) # Read original image
        cv2.imwrite(f'{Ui_MainWindow.blurredPath}/original.bmp', im) # Save original image in blurredPath
        async def asyncGetFolderImages(): # Async function
            while len(Ui_MainWindow.fileList) == 0: # While fileList is empty
                Ui_MainWindow.getFolderImages() # Get images in folder
                await asyncio.sleep(1) #    Wait 1 second
            self.setImage(f'{Ui_MainWindow.blurredPath}/{Ui_MainWindow.fileList[Ui_MainWindow.currentIndex]}', self.graphicsView_2) # Set image in graphicsView_2
            self.label_3.setText(f'Imagen original') # Set label_3 text as original image
            
            self.changeStatus() # Change status of buttons

        def stop(): # Stop async function
            task.cancel() # Cancel task
        
        loop = asyncio.get_event_loop() # Get event loop
        # Timeout after 10 minutes
        loop.call_later(7, stop)
        task = loop.create_task(asyncGetFolderImages()) # Create task

        try: # Try to run task
            loop.run_until_complete(task) # Run task
        except asyncio.CancelledError: # If task was cancelled
            print("Task was cancelled")

    def changeStatus(self): # Change status of buttons
        if len(Ui_MainWindow.original_image) == 0: # If original_image is empty
            self.back.setEnabled(False) 
            self.next.setEnabled(False) 
            self.pushButton_2.setEnabled(False)     
            self.comboBox.setEnabled(True) 
            self.label_3.setText(f'Resultados de desenfoque')
            self.hardwarestatus(0, 0, 0) # Set hardware status to 0
        else: # If original_image is not empty
            self.back.setEnabled(True) # Enable back button
            self.next.setEnabled(True) # Enable next button

    @pyqtSlot()
    def runProgram(self): # Run program
        Ui_MainWindow.noMasks = int(self.comboBox.currentText()) # Set noMasks as comboBox current text
        self.continuouslygetFolderImages() # Do an asyn call to getFolderImages every second until fileList is not empty

        self.comboBox.setEnabled(False) # Disable comboBox
        self.pushButton_2.setEnabled(False) # Disable pushButton_2

        backend = ImageProccessing() # Create backend object
        arrayStatus = backend.getHostsStatus() # Get hosts status
        self.hardwarestatus(arrayStatus[0], arrayStatus[1], arrayStatus[2]) # Set hardware status

        heavy_task_thread = HeavyTaskThread(Ui_MainWindow.noMasks, Ui_MainWindow.original_image, backend) # Create heavy_task_thread
        heavy_task_thread.setAutoDelete(True) # Set heavy_task_thread as auto delete
        self.threadpool.start(heavy_task_thread) # Start heavy_task_thread





if __name__ == "__main__":
    #set stylesheet
    with open('style.qss') as f: 
        style_str = f.read() 
    app = QtWidgets.QApplication([]) # Create application
    window = Ui_MainWindow() # Create window
    window.setStyleSheet(style_str) # Set stylesheet
    window.show() # Show window
    app.exec_() # Execute application
