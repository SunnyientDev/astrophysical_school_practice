'''
утилита для построения простейшего анализа спектров
1) открыть файл со спектром
2) добавить планковскую кривую для АЧТ с заданой температурой
3) клавиша с - отметить локальный уровень континуума.
4) клавиша l - отметить линию.
5) клавиша d - удалить линию.


'''

import pyfits
import numpy as np
from scipy.optimize import curve_fit
from scipy import interpolate
from scipy import optimize
import matplotlib
import matplotlib.pyplot
import matplotlib.cm as cm
from matplotlib.patches import Rectangle
import warnings
import os
from tkinter import *

warnings.simplefilter("ignore")
matplotlib.pyplot.ion()

#################################################################################
Continuum = []
Lines = []
################################################################################# 
def read_file(file_path):
    print(file_path)
    hdulist = pyfits.open(file_path) 
    Data=hdulist[0].data.copy()
    Header  = hdulist[0].header
    hdulist.close
    del Continuum [:]
    del Lines[:]
    return (Data, Header)
    
#################################################################################
def Draw_pic(Data, WL, Name):
    fig_pic = matplotlib.pyplot.figure(1)
    matplotlib.pyplot.cla()
    matplotlib.pyplot.plot(WL, Data, 'b')
    matplotlib.pyplot.title(Name)
    Connect(fig_pic)
    matplotlib.pyplot.rcParams['keymap.fullscreen'] = ' '
    matplotlib.pyplot.rcParams['keymap.grid'] = ' '
    matplotlib.pyplot.show()

def Draw_BB(Temp):
    global BB_curve
    Temp = float(Temp)
    BB = (119.268e32/np.power(WL,5))/(np.exp((0.0143877725e10/Temp)/WL)-1)
    BB = BB/(np.max(BB)/np.max(Data))
    matplotlib.pyplot.gca()
    try:
        BB_curve.pop(0).remove()
    except: pass
    BB_curve = matplotlib.pyplot.plot(WL, BB, 'r')

    matplotlib.pyplot.show()

#################################################################################
def Draw_Crop(Crop_WL, Crop_Data, X_1, Fit_y_1, Mask, Fit_y_2):
    fig_pic = matplotlib.pyplot.figure(2)
    matplotlib.pyplot.cla()
    matplotlib.pyplot.plot(Crop_WL, Crop_Data, 'r')
    matplotlib.pyplot.plot(X_1, Fit_y_1, 'b')
    matplotlib.pyplot.plot(X_1, Mask, 'm')
##    matplotlib.pyplot.plot(X_1, np.std(Mask), 'm')
    matplotlib.pyplot.plot(Crop_WL, Fit_y_2, 'g')
    matplotlib.pyplot.show()
    
######################################################################
#####1D Moffat fitting/center search
##def center(x_coo, y_coo, bckgrnd):
##    ROI =  Data[x_coo-FWHM*2:x_coo+FWHM*2]
##    X=np.arange(0, ROI.shape[0])
##    x0 = int(ROI.shape[0]/2)
##    #moffat fitting
##    #A - amplitude, B,C - coeff of function (width ...), D - background 
##    moffat = lambda x, A, B, C, D, x0: A*(1 + ((x-x0)/B)**2)**(-C)+D
##    p0 = np.array([y_coo, 3, 3, bckgrnd, x0])
##    try:
##        popt, pcov = curve_fit(moffat, X, ROI, p0, maxfev=10000)
##    except RuntimeError:
##        return(0)
##    return (popt[4]-FWHM*2)
    
##    Gauss1 = A*np.exp(-(((x-x0)**2)/(B**2))) + C*x + D

#################################################################################
##def Gauss(A, B, C, D, x0):
##    return lambda x: -A*np.exp(-(((x-x0)**2)/(B**2))) + C*x + D

def Moffat(A, B1, B2, x0):
    return lambda x, C, D: -A*(1 + ((x-x0)/B1)**2)**(-B2)+ C*x + D

def Fit_Lines():
    if len(Continuum)==2 and len(Lines)>0:
        WL_min = min(np.array(Continuum)[:,0])
        WL_max = max(np.array(Continuum)[:,0])        
        Index_max = np.where(WL == WL_max)[0][0]+1
        Index_min = np.where(WL == WL_min)[0][0]
        Sub_Data_1 = Data[Index_min:Index_max]
        Sub_WL_1   =   WL[Index_min:Index_max]
        Sub_Data = Sub_Data_1
        Sub_WL = Sub_WL_1
##        print(np.min(Sub_WL), np.max(Sub_WL))
##        print(WL_min, WL_max)
        C = (np.array(Continuum)[1,1] - np.array(Continuum)[0,1]) / (np.array(Continuum)[1,0] - np.array(Continuum)[0,0])
        D = np.array(Continuum)[1,1] - C*np.array(Continuum)[1,0]
##        print(C, D)
        Fit_y_c = C*Sub_WL + D
        
##        params = (np.array(Lines)[0,1], 3, 0, np.array(Continuum)[0,1], np.array(Lines)[0,0])
##        errorfunction = lambda p: Gauss(*p)(Sub_WL) - Sub_Data
##        p, success = optimize.leastsq(errorfunction, params, maxfev=10000, ftol=0.0005)
##        Fit_y_g = Gauss(*p)(Sub_WL)
##        print(p)

##        params = (np.array(Lines)[0,1], 0.5, 1.5, 0, np.array(Continuum)[0,1], np.array(Lines)[0,0])
        params = (np.array(Lines)[0,1], 0.5, 1.5, np.array(Lines)[0,0])
        X = np.zeros(1)
        while (len(X) != len(Sub_WL)):
            errorfunction = lambda p: Moffat(*p)(Sub_WL, C, D) - Sub_Data
            p, success = optimize.leastsq(errorfunction, params, maxfev=10000, ftol=0.0005)
            Fit_y_m = Moffat(*p)(Sub_WL, C, D)
            X = Sub_WL
            print(p)
            Mask = Fit_y_m - Sub_Data
            Rej = np.std(Mask)
            Sub_WL = Sub_WL[Mask<(Rej*2)]
            Sub_Data = Sub_Data[Mask<(Rej*2)]
            
        Fit_y_m = Moffat(*p)(Sub_WL_1, C, D)
        Mask = Fit_y_m - Sub_Data_1   
##        
####        Draw_Crop(Sub_WL, Sub_Data, Fit_y_g, Fit_y_m)
        Draw_Crop(Sub_WL_1, Sub_Data_1, Sub_WL_1, Fit_y_m, Mask, Fit_y_c)
#################################################################################
def get_line_id (gid):
    x=None
    ax = matplotlib.pyplot.gca()
    for ii in range (0, len(ax.lines)):
        if ax.lines[ii].get_gid()==gid:
            x=ii
    return x

def Del_Line(X,Y):
    try:
        local=np.array(Lines)[:, 0]
        local=(local-X)**2
        nearest = np.argmin(local)
        ax = matplotlib.pyplot.gca()
        ax.lines[get_line_id(str(Lines[nearest][0]))].remove()
        matplotlib.pyplot.show()
        del Lines[nearest]
    except: pass
    
    
#################################################################################
def Mark_Line(X, Y):
##    global Lines
    if (X>min(np.array(Continuum)[:,0]) and X<max(np.array(Continuum)[:,0])):
        Lines.append([X,Y])
        matplotlib.pyplot.gca()
        Lines_curve = matplotlib.pyplot.plot(X, Y, 'r|', markersize=20, mew=2, gid = str(X))
        matplotlib.pyplot.show()
    
#################################################################################    
def Get_continuum(X):
##    global Continuum
    global Cont_curve
    Width = int(FWHM_E.get())
    Index = np.argmin(np.fabs(WL-X))
    
    try:
        Sub_Data = Data[Index-Width:Index+Width]
        Sub_WL   = WL[Index-Width:Index+Width]
        Index = np.argmax(Sub_Data)
        X = Sub_WL[Index]
        Y = Sub_Data[Index]
        Continuum.append([X,Y])
        if len(Continuum)>2:
            del Continuum[0]

        matplotlib.pyplot.gca()
        try:
            Cont_curve.pop(0).remove()
        except: pass
        Cont_curve = matplotlib.pyplot.plot(np.array(Continuum)[:,0], np.array(Continuum)[:,1], 'go-')
        matplotlib.pyplot.show()

    except: pass
        
#################################################################################
def open_file():
    global Data
    global Header
    global Name
    global WL
    Name = filedialog.askopenfilename()
    Data, Header = read_file(Name)
##    print(Header)
    CRVAL = Header['CRVAL1']
    CRPIX = Header['CRPIX1']
    CDELT = Header['CDELT1']
    Length = Header['NAXIS1']
    Start = (1 - CRPIX)*CDELT + CRVAL
    End = Start+(Length-1)*CDELT
    WL = np.linspace(Start, End, Length)
    print("Start:", min(WL), "End:", max(WL), "Dispersion:", CDELT)
##    print(Length, len(WL))
    Draw_pic(Data, WL, Name)
    
#################################################################################
def Connect(fig_pic):
    cid = fig_pic.canvas.mpl_connect('key_press_event', press)
#################################################################################    
def press(event):
    if event is not None and (event.key=='c' or event.key=='alt+c'):
        Get_continuum(event.xdata)

    if event is not None and (event.key=='l' or event.key=='alt+l'):
        Mark_Line(event.xdata, event.ydata)

    if event is not None and (event.key=='d' or event.key=='alt+d'):
        Del_Line(event.xdata, event.ydata)

    if event is not None and (event.key=='f' or event.key=='alt+f'):
        Fit_Lines()
##        try:
##            Fit_Lines()
##        except:
##            print('unable fit')
##            pass
        
#################################################################################
##tools window
root = Tk()
root.title("Spec_View")
root.configure(background = 'grey')
root.geometry('200x150')
root.resizable(width=False, height=False)

Open_file = Button(root, text = "Open file", width=22, height=1, command = lambda: open_file())
Open_file.grid(row=0, column=0, columnspan=2, padx=20, pady=5)

Label_1 = Label(root, width=9, justify='right', bg = "grey", text = "BB temp:")
Label_1.grid(row=1, column=0, padx=5, pady=5, sticky=E)

Order_E = Entry(root, width=5, justify='left')
Order_E.insert (0,'6000')
Order_E.grid(row=1, column=1, padx=0, pady=5, sticky=W)

Fit_B = Button(root, text = "Add Black Body", width=22, height=1, command = lambda: Draw_BB(Order_E.get()))
Fit_B.grid(row=2, column=0, columnspan=2, padx=6, pady=5)

Label_2 = Label(root, width=9, justify='right', bg = "grey", text = "FWHM:")
Label_2.grid(row=3, column=0, padx=5, pady=5, sticky=E)

FWHM_E = Entry(root, width=5, justify='left')
FWHM_E.insert (0,'5')
FWHM_E.grid(row=3, column=1, padx=0, pady=5, sticky=W)

##Clone_B = Button(root, text = "Clone for files", width=22, height=1, command = lambda: clone())
##Clone_B.grid(row=3, column=0, columnspan=2, padx=3, pady=5)

mainloop()

