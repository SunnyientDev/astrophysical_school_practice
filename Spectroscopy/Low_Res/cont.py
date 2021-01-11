'''
утилита для построения дисперсионной функции по линиям газонаполненной лампы
1) открыть файл с экстрагированным спектром лампы
2) клавиша m - отметить линию, затем необходимо ввести длину волны в терминале + enter. появится отметка.
3) клавиша d - удалить отметку.
4) клавиша f - фитировать дисперсионную функцию (длина волны от пикселя). используется полином Чебышева указанного порядка.
порядок полинома не должен превышать (количество точек-1).
5) клавиша r - фитировать ДФ (разница фитирования и измерения от пикселя).
6) клавиша d - удалить точку на дисперсионной функции, сделать повторное фитирование.
7) клавиша g - вернуться к спектру лампы с отметками линий
8) поле rebin позволяет задать коэффициент для интерполяции. при 1 количество точек не изменяется. для спектров с низкой дискретизацией
рекомендуется значение больше 1.
9) для интерполяции, линеаризации спектра и сохранения в файл нужно нажать кнопку 'Fit and save'
10) для клонирования дисперсионной функции, инттерпояции и линеаризации дургих спектров нажмите кнопку Clone и выберите их (ctrl).
Новые файлы будут сохранены с добавлением к имени "_WCS".

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
interp_order = 1 ##order of spline for interpolation and linearization
FWHM = 2
features=[]
Pic = 'G'

################################################################################# 
def read_file(file_path):
    print(file_path)
    hdulist = pyfits.open(file_path) 
    Data=hdulist[0].data.copy()
    Header  = hdulist[0].header
    hdulist.close
    Data = Data[::-1]
    return (Data, Header)
    
#################################################################################
def Draw_pic(Data, Name, fig, feat):
    global Pic
    Pic = 'G'
    fig_pic = matplotlib.pyplot.figure(fig)
    matplotlib.pyplot.cla()
    matplotlib.pyplot.plot(Data)
    matplotlib.pyplot.title(Name)
    if feat==1:
        for ii in range(0,len(features)):
            x_coo = features[ii][0]
##            WL = features[ii][1]
            y_coo = features[ii][1]
            currentAxis = matplotlib.pyplot.gca()
            currentAxis.plot(x_coo, y_coo, 'go')
##            currentAxis.annotate(WL, xy=(x_coo,y_coo),rotation=90,horizontalalignment='center',  verticalalignment='left',  color='g')
    Connect(fig_pic)
##    print(matplotlib.pyplot.rcParams['keymap.fullscreen'])
    matplotlib.pyplot.rcParams['keymap.fullscreen'] = ' '
##    print(matplotlib.pyplot.rcParams['keymap.grid'])
    matplotlib.pyplot.rcParams['keymap.grid'] = ' '
    matplotlib.pyplot.show()

#################################################################################
##def solution(C): #2d chebyshev polynom calculation
##    shift = C[0]
##    C = np.delete(C,0)
##    return lambda X:(np.polynomial.chebyshev.chebval(X, C)-shift)

def fit(Mode):
    global Pic
##    features=([20, 8000],[51, 7500],[89.6, 7000],[128.3, 6500],[182.5, 6000],[256, 5500],[345, 5000],[484.2, 4500],[670, 4000])
    X=np.array(features)[:, 0]
    W=np.array(features)[:, 1]
    X_full = np.arange(0,Data.shape[0],1)

    z = np.polyfit(X, W, int(Order_E.get()))
    p=np.poly1d(z)
    W_full = p(X_full)
    
    matplotlib.pyplot.cla()
    currentAxis = matplotlib.pyplot.gca()
    currentAxis.set_xlim([0, np.max(X_full)])

    if Mode=='F':
        Pic = 'F'        
        currentAxis.plot(X, W, 'go')
        currentAxis.plot(X_full, W_full, 'b-')
        matplotlib.pyplot.plot(Data)
##        currentAxis.set_xlabel("Position(pix)")
##        currentAxis.set_ylabel("WL(A)")
        
##    matplotlib.pyplot.title(label_data)
    matplotlib.pyplot.draw()
    return Data/W_full
    
#################################################################################
def Add_solution(_Data, _Header, _Name):
    C = fit('F')
            
    fig_pic = matplotlib.pyplot.figure(2)
    matplotlib.pyplot.cla()
    currentAxis = matplotlib.pyplot.gca()
    currentAxis.plot(C, 'r') ##plot old spec
##    currentAxis.plot(WL_rebin, Data_rebin, 'g') ##plot rebin spec
    matplotlib.pyplot.show()
    
##write data to file
    save_to_file(C, _Name, _Header)

#################################################################################
def save_to_file(_data, _name, _header):
##        Header['WCSDIM'] = 1    
##        Header['LTM1_1'] = 1
##        Header['WAT0_001'] = 'system=equispec'
##    _header['WAT1_001'] = 'wtype=linear label=Wavelength units=angstroms'
##    _header['DCLOG1']  = 'Transform'
##    _header['DC-FLAG'] = 0
##    _header['CTYPE1'] = 'LINEAR'
##    _header['CRVAL1'] = CRVAL
##    _header['CRPIX1'] = 1
##    _header['CDELT1'] = CDELT
##    _header['CD1_1']  = CDELT

    new_name, extension = os.path.splitext(_name)
    new_name = new_name+'_cont'+'.fits'
    hdu = pyfits.PrimaryHDU(_data, _header)
    hdulist = pyfits.HDUList([hdu])
    hdulist.writeto(new_name, clobber = True, output_verify='ignore')
    print("Data saved to " + new_name)
    print ('\r')
    
#################################################################################
def get_max(x_coo):
    ROI =  Data[x_coo-FWHM:x_coo+FWHM]
    j = ROI.argmax() #get maximum pixel
    return (x_coo+j-FWHM, ROI.max(), ROI.min())

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

#################################################################################
def mark_feature(x_coo):
    global features
    x_coo = x_coo.round()
    x_coo, _max, _min = get_max(x_coo) #search max pixel near click (x_coo, max, min)
    print('Max=', x_coo)
##    offset = center(x_coo, _max, _min)
##    if x_coo!=0:
##        x_coo=round(x_coo+offset,3)
##        print('x=',x_coo)
##    WL = input("Enter wavelegnth: ")
        
    features.append([x_coo, _max])
    features = sorted(features)
    
    currentAxis = matplotlib.pyplot.gca()
    currentAxis.plot(x_coo, _max, 'go')   
##    currentAxis.annotate(WL, xy=(x_coo,_max+1),rotation=90,horizontalalignment='center',  verticalalignment='left',  color='g')
    matplotlib.pyplot.draw()

#################################################################################
def del_feature(x_coo):
    local=np.array(features)[:, 0]
    local=(local-x_coo)**2
    nearest = np.argmin(local)
##    print(features[nearest])
    del features[nearest]
    if Pic=='G':
        Draw_pic(Data, Name, 1, 1)
    if Pic=='R':
        fit('R')
    if Pic=='F':
        fit('F')
    
#################################################################################
def open_file():
    global Data
    global Header
    global Name
    Name = filedialog.askopenfilename()
    Data, Header = read_file(Name)
    Draw_pic(Data, Name, 1, 0)
    
#################################################################################
def clone():
    _list = filedialog.askopenfilenames(parent=root,title='Choose a files')
    file_list = _list.split(' ')
##    print(len(file_list) )
    for _Name in file_list:
##        print (_Name)
        _Data, _Header = read_file(_Name)
        Add_solution(_Data, _Header, _Name)
#################################################################################
def Connect(fig_pic):
    cid = fig_pic.canvas.mpl_connect('key_press_event', press)
#################################################################################    
def press(event):
    if event is not None and (event.key=='m' or event.key=='alt+m') and Pic=='G':
        mark_feature(event.xdata)

    if event is not None and (event.key=='d' or event.key=='alt+d'):
        try:
            del_feature(event.xdata)
        except:
            pass
        
    if event is not None and (event.key=='r' or event.key=='alt+r'):
        try:
            disp_param = fit('R')
##                mode='fit'
        except:
            print('unable fit')
            pass

    if event is not None and (event.key=='f' or event.key=='alt+f'):
        try:
            disp_param = fit('F')
##                mode='fit'
        except:
            print('unable fit')
            pass
        
    if event is not None and (event.key=='g' or event.key=='alt+g'):
        Draw_pic(Data, Name, 1, 1)
        
#################################################################################
##tools window
root = Tk()
root.title("WL solution")
root.configure(background = 'grey')
root.geometry('176x150')
root.resizable(width=False, height=False)

Open_file = Button(root, text = "Arc lamp", width=22, height=1, command = lambda: open_file())
Open_file.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

Label_1 = Label(root, width=9, justify='right', bg = "grey", text = "Disp. order:")
Label_1.grid(row=1, column=0, padx=5, pady=5, sticky=E)

Order_E = Entry(root, width=2, justify='left')
Order_E.insert (0,'3')
Order_E.grid(row=1, column=1, padx=0, pady=5, sticky=W)

Label_2 = Label(root, width=4, justify='right', bg = "grey", text = "Rebin:")
Label_2.grid(row=1, column=2, padx=0, pady=5, sticky=E)

Rebin_E = Entry(root, width=2, justify='left')
Rebin_E.insert (0,'1')
Rebin_E.grid(row=1, column=3, padx=5, pady=5, sticky=W)

Fit_B = Button(root, text = "Fit & save", width=22, height=1, command = lambda: Add_solution(Data, Header, Name))
Fit_B.grid(row=2, column=0, columnspan=4, padx=6, pady=5)

Clone_B = Button(root, text = "Clone for files", width=22, height=1, command = lambda: clone())
Clone_B.grid(row=3, column=0, columnspan=4, padx=3, pady=5)

mainloop()

