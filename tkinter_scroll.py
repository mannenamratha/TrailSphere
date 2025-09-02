# import tkinter as tk
# from tkinter import ttk


# class Scrollable(ttk.Frame):
#     """
#        Make a frame scrollable with scrollbar on the right.
#        After adding or removing widgets to the scrollable frame,
#        call the update() method to refresh the scrollable area.
#     """

#     def __init__(self, frame, width=16):

#         scrollbar = tk.Scrollbar(frame, width=width)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

#         self.canvas = tk.Canvas(frame, bg='white',yscrollcommand=scrollbar.set)
#         self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#         scrollbar.config(command=self.canvas.yview)

#         self.canvas.bind('<Configure>', self.__fill_canvas)

#         # base class initialization
#         tk.Frame.__init__(self, frame)

#         # assign this obj (the inner frame) to the windows item of the canvas
#         self.windows_item = self.canvas.create_window(
#             0, 0, window=self, anchor=tk.NW)

#     def __fill_canvas(self, event):
#         "Enlarge the windows item to the canvas width"

#         canvas_width = event.width
#         self.canvas.itemconfig(self.windows_item, width=canvas_width)

#     def update(self):
#         "Update the canvas and the scrollregion"

#         self.update_idletasks()
#         self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))


# class FullScreenApp(object):
#     def __init__(self, master, **kwargs):
#         self.master = master
#         pad = 3
#         self._geom = '200x200+0+0'
#         master.geometry("{0}x{1}+0+0".format(master.winfo_screenwidth() -
#                                              pad, master.winfo_screenheight() - pad))
#         master.bind('<Escape>', self.toggle_geom)

#     def toggle_geom(self, event):
#         geom = self.master.winfo_geometry()
#         print(geom, self._geom)
#         self.master.geometry(self._geom)
#         self._geom = geom

#         # set a callback to handle when the window is closed
#         self.root.wm_title("PhotoBooth")
#         self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

#     def videoLoop(self):
#         try:
#             while not self.stopEvent.is_set():
#                 self.frame = self.vs.read()
#                 self.frame = imutils.resize(self.frame, width=300)
#                 image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
#                 image = Image.fromarray(image)
#                 image = ImageTk.PhotoImage(image)
#                 if self.panel is None:
#                     self.panel = tki.Label(image=image)
#                     self.panel.image = image
#                     self.panel.pack(side="left", padx=10, pady=10)
#                 else:
#                     self.panel.configure(image=image)
#                     self.panel.image = image
#         except RuntimeError as e:
#             print("[INFO] caught a RuntimeError")

#     def takeSnapshot(self):
#         # grab the current timestamp and use it to construct the
#         # output path
#         ts = datetime.datetime.now()
#         filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))
#         p = os.path.sep.join((self.outputPath, filename))

#         # save the file
#         cv2.imwrite(p, self.frame.copy())
#         print("[INFO] saved {}".format(filename))

#     def onClose(self):
#         # set the stop event, cleanup the camera, and allow the rest of
#         # the quit process to continue
#         print("[INFO] closing...")
#         self.stopEvent.set()
#         self.vs.stop()
#         self.root.quit()



import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
import imutils
import threading
import datetime
import os

class Scrollable(ttk.Frame):
    """
       Make a frame scrollable with a scrollbar on the right.
       After adding or removing widgets to the scrollable frame,
       call the update() method to refresh the scrollable area.
    """
    def __init__(self, frame, width=16):
        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, expand=False)

        self.canvas = tk.Canvas(frame, bg='white', yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', self.__fill_canvas)

        tk.Frame.__init__(self, frame)  # Initialize frame
        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        "Enlarge the windows item to fit the canvas width"
        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width=canvas_width)

    def update(self):
        "Update the canvas and the scroll region"
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))

class FullScreenApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PhotoBooth")

        pad = 3
        self._geom = '200x200+0+0'
        root.geometry(f"{root.winfo_screenwidth() - pad}x{root.winfo_screenheight() - pad}+0+0")
        root.bind('<Escape>', self.toggle_geom)

        # Video Capture
        self.vs = cv2.VideoCapture(0)  # Open webcam
        self.panel = None
        self.stopEvent = threading.Event()

        # Start video thread
        self.thread = threading.Thread(target=self.videoLoop, daemon=True)
        self.thread.start()

        # Snapshot Button
        btn_snapshot = tk.Button(root, text="Take Snapshot", command=self.takeSnapshot)
        btn_snapshot.pack()

        # Output Path
        self.outputPath = "snapshots"
        if not os.path.exists(self.outputPath):
            os.makedirs(self.outputPath)

        # Handle Close Event
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)

    def toggle_geom(self, event):
        geom = self.root.winfo_geometry()
        self.root.geometry(self._geom)
        self._geom = geom

    def videoLoop(self):
        """Loop to continuously capture frames and display them"""
        try:
            while not self.stopEvent.is_set():
                ret, frame = self.vs.read()
                if not ret:
                    continue

                frame = imutils.resize(frame, width=600)
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image)

                if self.panel is None:
                    self.panel = tk.Label(self.root, image=image)
                    self.panel.image = image
                    self.panel.pack(padx=10, pady=10)
                else:
                    self.panel.configure(image=image)
                    self.panel.image = image
        except RuntimeError as e:
            print("[INFO] RuntimeError:", e)

    def takeSnapshot(self):
        """Capture and save the current frame"""
        ts = datetime.datetime.now()
        filename = f"{ts.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
        filepath = os.path.join(self.outputPath, filename)

        ret, frame = self.vs.read()
        if ret:
            cv2.imwrite(filepath, frame)
            print(f"[INFO] Snapshot saved: {filename}")

    def onClose(self):
        """Stop video stream and close application"""
        print("[INFO] Closing application...")
        self.stopEvent.set()
        self.vs.release()
        self.root.quit()

# Main Application Start
if __name__ == "__main__":
    root = tk.Tk()
    app = FullScreenApp(root)
    root.mainloop()
