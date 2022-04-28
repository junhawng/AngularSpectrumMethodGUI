from ctypes import resize
import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk,Image
  
 
LARGEFONT =("Verdana", 35)

class tkinterApp(tk.Tk):
     
    # __init__ function for class tkinterApp
    def __init__(self, *args, **kwargs):
         
        # __init__ function for class Tk
        tk.Tk.__init__(self, *args, **kwargs)
        
        self.geometry('1000x700')
        # creating a container
        container = tk.Frame(self) 
        container.pack(side = "top", fill = "both", expand = True)
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
  
        # initializing frames to an empty array
        self.frames = {} 
  
        # iterating through a tuple consisting
        # of the different page layouts
  
        frame = StartPage(container, self)
  
            # initializing frame of that object from
            # startpage, page1, page2 respectively with
            # for loop
        self.frames[StartPage] = frame
  
        frame.grid(row = 0, column = 0, sticky ="nsew")
  
        self.show_frame(StartPage)
  
    # to display the current frame passed as
    # parameter
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
  
# first window frame startpage
  
class StartPage(tk.Frame):
    def wavelength_to_rgb(self, wavelength, gamma=0.8):

        wavelength = float(wavelength)
        if wavelength >= 380 and wavelength <= 440:
            attenuation = 0.3 + 0.7 * (wavelength - 380) / (440 - 380)
            R = ((-(wavelength - 440) / (440 - 380)) * attenuation) ** gamma
            G = 0.0
            B = (1.0 * attenuation) ** gamma
        elif wavelength >= 440 and wavelength <= 490:
            R = 0.0
            G = ((wavelength - 440) / (490 - 440)) ** gamma
            B = 1.0
        elif wavelength >= 490 and wavelength <= 510:
            R = 0.0
            G = 1.0
            B = (-(wavelength - 510) / (510 - 490)) ** gamma
        elif wavelength >= 510 and wavelength <= 580:
            R = ((wavelength - 510) / (580 - 510)) ** gamma
            G = 1.0
            B = 0.0
        elif wavelength >= 580 and wavelength <= 645:
            R = 1.0
            G = (-(wavelength - 645) / (645 - 580)) ** gamma
            B = 0.0
        elif wavelength >= 645 and wavelength <= 750:
            attenuation = 0.3 + 0.7 * (750 - wavelength) / (750 - 645)
            R = (1.0 * attenuation) ** gamma
            G = 0.0
            B = 0.0
        else:
            R = 0.0
            G = 0.0
            B = 0.0
        R *= 255
        G *= 255
        B *= 255
        return (int(B), int(G), int(R))
    def fileSelector(self):
        global file
        file = filedialog.askopenfilename(initialdir = '/Users/junju/OneDrive/School/Homework/Year 2/Semester 2/ESE 438/HW6', title = 'Select Mask Image')
    def updateText(self):
        label2.config(text = "File Loaded. Proceed with analysis")
    def processImage(self):

        label2.config(text = "Processing...")
        #initialize Variables
        global lamb, k, z, gain, colorFormatIntensity, lamText, zText, gainText
        lamb = 700*10**(-9)
        lamb = int(lamText.get(1.0, "end-1c"))*10**-9
        t = 1/lamb
        omega = 2*np.pi/t
        k = 2*np.pi/lamb
        #Distance of measurement away from mask (in m)
        z = 0.05
        z = float(zText.get(1.0, "end-1c"))*.01
        gain = 0.05
        gain = float(gainText.get(1.0, "end-1c"))
        mask = cv2.imread(file, 0)
        pixWidthX = len(mask[0])
        pixWidthY = len(mask)

        #Angular Spectrum Method Function
        fft_m = np.fft.fft2(mask)
        m = np.fft.fftshift(fft_m)


        kx = 2*np.pi*np.fft.fftshift(np.fft.fftfreq(pixWidthX, d = (5.6*10**(-3))/pixWidthX))
        ky = 2*np.pi*np.fft.fftshift(np.fft.fftfreq(pixWidthY, d = (5.6*10**(-3))/pixWidthY))
        kx, ky = np.meshgrid(kx, ky)
        kz = np.sqrt(k**2 - kx**2 - ky**2)

        colorRGB = self.wavelength_to_rgb(lamb*10**9)


        newM = np.fft.ifft2(np.fft.ifftshift(m * np.exp(1j * kz * z)))
        intensity = np.real(newM * np.conjugate(newM)) * gain
        intensity = np.array(intensity, dtype = np.float32)
        colorFormatIntensity = cv2.cvtColor(intensity ,cv2.COLOR_GRAY2RGB)

        for i in range(pixWidthX):
            for j in range(pixWidthY):
                for k in range(0, 3):
                    colorFormatIntensity[i][j][k] = colorRGB[k] *colorFormatIntensity[i][j][k]/255
        cv2.imwrite('/Users/junju/OneDrive/School/Homework/Year 2/Semester 2/ESE 438/HW6/new.png', colorFormatIntensity )

    def updateImage(self):
        global canvas, img
        label2.config(text = "Simulation Complete!")
        img = ImageTk.PhotoImage(Image.open('/Users/junju/OneDrive/School/Homework/Year 2/Semester 2/ESE 438/HW6/new.png').resize((512,512), Image.ANTIALIAS))
        canvas.create_image(0, 0, anchor= 'nw',image = img)
        canvas.update()
    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return("break")
    def __init__(self, parent, controller):
        global file, label2, canvas, img , lamText, gainText, zText

        tk.Frame.__init__(self, parent)
        # label of frame Layout 2
        label = ttk.Label(self, text ="Angular Spectrum Method GUI", font = LARGEFONT,)
         
        # putting the grid in its place by using
        label.grid(row = 0, column = 1)

        label2 = ttk.Label(self, text = "Please load an image file")
        label2.grid(row = 1, column = 1)
        canvas = tk.Canvas(self, width = 512, height = 512)
        canvas.grid(row = 2, column = 1)

        button1 = ttk.Button(self, text ="Load Image",command = lambda : [self.fileSelector(), self.updateText(), self.processImage(), self.updateImage()])
     
        # putting the button in its place by
        # using grid
        button1.grid(row = 3, column = 0)
        
        button2 = ttk.Button(self, text ="Run Image",command = lambda : [self.processImage(), self.updateImage()])

        button2.grid(row = 3, column = 2)
        lamLabel = ttk.Label(self, text = "Wavelength (nm)").grid(row = 4, column = 0)
        gainLabel = ttk.Label(self, text = "Gain (Default .05)").grid(row = 4, column = 1)
        zLabel = tk.Label(self, text = "Distance Z from source (cm)").grid(row = 4, column = 2)

        lamText = tk.Text(self, height = 1, width = 7)
        lamText.grid(row = 5, column = 0)
        lamText.bind("<Tab>", self.focus_next_widget)
        lamText.insert(tk.END, "650")
        gainText = tk.Text(self, height = 1, width = 7)
        gainText.grid(row = 5, column = 1)
        gainText.bind("<Tab>", self.focus_next_widget)
        gainText.insert(tk.END, ".01")
        zText = tk.Text(self, height = 1, width = 7)
        zText.grid(row = 5, column = 2)
        zText.bind("<Tab>", self.focus_next_widget)
        zText.insert(tk.END, "20")

        
    

  

  


  
# Driver Code
app = tkinterApp()
app.mainloop()