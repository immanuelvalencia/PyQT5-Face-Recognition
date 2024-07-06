
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QWidget, QVBoxLayout, QPushButton, QFileDialog , QLabel, QTextEdit, QMessageBox
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
import recogimg, recogvid
import cv2, sys, os, random, string
from imutils import paths
import face_recognition
import pickle
from ui_window import *

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        

        self.web_timer = QTimer()
        self.web_timer.timeout.connect(self.recogVid)

        self.vid_timer = QTimer()
        self.vid_timer.timeout.connect(self.recogVid) 

        self.encode_timer = QTimer()
        self.encode_timer.timeout.connect(self.encodeVid) 

        self.ui.runVideo.clicked.connect(self.vid_control_timer)
        self.ui.runWeb.clicked.connect(self.web_control_timer)
        self.ui.runImage.clicked.connect(self.getImage)
        self.ui.encodeCap.clicked.connect(self.encodeCap)
        self.ui.encodeWeb.clicked.connect(self.encode_control_timer)
        self.ui.encodeBut.clicked.connect(self.encode)

    def encode(self):
        self.ui.status_body.setText("Processing")

        imagePaths = list(paths.list_images("bin/dataset"))

        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []
        # loop over the image paths
        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            print("[INFO] processing image {}/{}".format(i + 1,
                len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]

            # load the input image and convert it from RGB (OpenCV ordering)
            # to dlib ordering (RGB)
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input image
            boxes = face_recognition.face_locations(rgb,
                model="cnn")

            # compute the facial embedding for the face
            encodings = face_recognition.face_encodings(rgb, boxes)

            # loop over the encodings
            for encoding in encodings:
                # add each encoding + name to our set of known names and
                # encodings
                knownEncodings.append(encoding)
                knownNames.append(name)

        # dump the facial encodings + names to disk
        print("[INFO] serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open("bin/encodings.pickle", "wb")
        f.write(pickle.dumps(data))
        f.close()
        self.ui.status_body.setText("Done Encoding")





    def encodeVid(self):
        global captured
        ret, webframe = self.cap.read()
        captured = webframe
        webframe = cv2.cvtColor(webframe, cv2.COLOR_BGR2RGB)
        height, width, channel = webframe.shape
        step = channel * width
        qImg = QImage(webframe.data, width, height, step, QImage.Format_RGB888)
        self.ui.display.setPixmap(QPixmap.fromImage(qImg))

    def encodeCap(self):
        username = self.ui.name.text()
        path = "bin/dataset/"
        dirname = path + username
        filename = path + username + "/" + randomString() + ".jpg"
        print(filename)

        if len(username) != 0 and self.encode_timer.isActive():
        
            if not os.path.exists(dirname):
                os.mkdir(dirname)
                cv2.imwrite(filename,captured)
            else:    
                cv2.imwrite(filename,captured)

        else:
            if len(username) == 0:
                QMessageBox.information(self, "Error" , "Enter name")

            elif not self.encode_timer.isActive():
                QMessageBox.information(self, "Error" , "Start Webcam")

    def encode_control_timer(self):
    
        if self.vid_timer.isActive() or self.web_timer.isActive():
                QMessageBox.information(self, "Error" , "Face Recognition is still active \nPlease stop before running")

        else:
            if not self.encode_timer.isActive():
                self.cap = cv2.VideoCapture(0)
                self.encode_timer.start(20)
                self.ui.encodeWeb.setText("Stop")

            else:
                self.encode_timer.stop()
                self.cap.release()
                self.ui.display.setPixmap(QtGui.QPixmap("bin/resources/profile.png"))
                self.ui.encodeWeb.setText("Webcam")

    def getImage(self):

        if self.encode_timer.isActive() or self.web_timer.isActive() or self.vid_timer.isActive():
            QMessageBox.information(self, "Error" , "Webcam is still active \nPlease stop webcam before running")
        else:
            self.ui.status_body.setText("Loading File")
            fname,ftype = QFileDialog.getOpenFileName(self, 'Open Image',
                                                '/home', "Image files (*.jpg *.gif *.png *.jpeg)")
            frame = recogimg.run(fname)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.ui.display.setPixmap(QPixmap.fromImage(qImg))
            self.ui.status_body.setText("Done")

    def recogVid(self):
        (grabbed, frame) = self.cap.read()
        if grabbed == True:
            frame = recogvid.run(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            step = channel * width
            qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
            self.ui.display.setPixmap(QPixmap.fromImage(qImg))

        else:
            self.ui.display.setPixmap(QtGui.QPixmap("bin/resources/profile.png"))

    def web_control_timer(self):

        if self.vid_timer.isActive():
                QMessageBox.information(self, "Error" , "Video is still active \nPlease stop video before running")

        elif self.encode_timer.isActive():
            QMessageBox.information(self, "Error" , "Webcam is still active \nPlease stop webcam before running")
        
        else:
            if not self.web_timer.isActive():
                self.cap = cv2.VideoCapture(0)
                print("test")
                self.web_timer.start(20)
                self.ui.runWeb.setText("Stop")
            else:
                self.web_timer.stop()
                self.cap.release()
                self.ui.runWeb.setText("Webcam")
                self.ui.display.setPixmap(QtGui.QPixmap("bin/resources/profile.png"))

    def vid_control_timer(self):


        if self.web_timer.isActive() or self.encode_timer.isActive():

            QMessageBox.information(self, "Error" , "Webcam is still active \nPlease stop webcam before running")

        
        else:

            if not self.vid_timer.isActive():

                self.ui.status_body.setText("Loading File")
                fname,ftype = QFileDialog.getOpenFileName(self, 'Open Video',
                                                    '/home', "Image files (*.mp4 *.mkv *.flv *.webm)")
                self.cap = cv2.VideoCapture(fname)
                print("test")
                self.vid_timer.start(20)
                self.ui.runVideo.setText("Stop")
                self.ui.status_body.setText("Done")

            else:
                self.vid_timer.stop()
                self.cap.release()
                self.ui.runVideo.setText("Video")
                self.ui.display.setPixmap(QtGui.QPixmap("bin/resources/profile.png"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
