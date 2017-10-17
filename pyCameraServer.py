#!/usr/bin/python

import time
import threading
import random
import Queue
from PIL import Image, ImageTk
import Tkinter as tk
import socket
import struct
import io
import tkMessageBox

class GuiPart:
    
    def __init__(self, master, queue, endCommand):
        self.queue = queue
        self.endCommand = endCommand
        
        self.root=master
        self.root.title('My Pictures')

        imageFile = "pi.jpg"
        self.image1 = ImageTk.PhotoImage(Image.open(imageFile))
        w = 640
        h = 480
        x = 0
        y = 0
        self.root.geometry("%dx%d+%d+%d" % (w, h, x, y))

        self.panel1 = tk.Label(self.root, image=self.image1)

        self.panel1.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)
        self.panel1.configure(image=self.image1)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if tkMessageBox.askokcancel("Quit", "Do you want to quit?"):
            self.endCommand()
            self.root.destroy()

    def processIncoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize(  ):
            try:
                self.update_image(self.queue.get(0))
            except Queue.Empty:
                # just on general principles, although we don't
                # expect this branch to be taken in this case
                pass
    def update_image(self, newImage):
        self.image1=newImage
        self.panel1.configure(image=self.image1)

class ThreadedClient:
    def __init__(self, master):
        self.master = master
        self.queue = Queue.Queue(  )
        self.gui = GuiPart(master, self.queue, self.endApplication)

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start(  )

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall(  )

    def periodicCall(self):
        """
        Check every 200 ms if there is something new in the queue.
        """
        self.gui.processIncoming(  )
        if not self.running:
            # This is the brutal stop of the system. You may want to do
            # some cleanup before actually shutting it down.
            import sys
            sys.exit(1)
        self.master.after(200, self.periodicCall)

    def workerThread1(self):
        #set up server
        # Start a socket listening for connections on 0.0.0.0:8000 (0.0.0.0 means
        # all interfaces)
        self.server_socket = socket.socket()
        self.server_socket.bind(('0.0.0.0', 8000))
        self.server_socket.listen(0)

        # Accept a single connection and make a file-like object out of it
        self.connection = self.server_socket.accept()[0].makefile('rb')

        try:
            while self.running:
                # Read the length of the image as a 32-bit unsigned int. If the
                # length is zero, quit the loop
                image_len = struct.unpack('<L', self.connection.read(struct.calcsize('<L')))[0]
                if not image_len:
                    break
                # Construct a stream to hold the image data and read the image
                # data from the connection
                image_stream = io.BytesIO()
                image_stream.write(self.connection.read(image_len))

                image_stream.seek(0)
                
                newPhotoImage=ImageTk.PhotoImage(Image.open(image_stream))
                self.queue.put(newPhotoImage)
        finally:
            self.connection.close()
            self.server_socket.close()

    

    def endApplication(self):
        self.master.destroy()
        self.running = 0



root = tk.Tk(  )

client = ThreadedClient(root)
root.mainloop(  )
