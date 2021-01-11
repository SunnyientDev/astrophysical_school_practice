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
##global Data_1
##global Data_2

################################################################################# 
def read_file(file_path):
    print(file_path)
    hdulist = pyfits.open(file_path) 
    Data=hdulist[0].data.copy()
    Header  = hdulist[0].header
    hdulist.close
##    Data = Data[::-1]
    return (Data, Header)
    
#################################################################################
def Draw_pic():
    global Data_2
    Data_2 = Data_2*(np.max(Data_1)/np.max(Data_2))
    
    fig_pic = matplotlib.pyplot.figure(1)
    ax = fig_pic.gca()
    matplotlib.pyplot.cla()
    
    if Data_1!=None:
        matplotlib.pyplot.plot(Data_1)
    if Data_2!=None:
        matplotlib.pyplot.plot(Data_2)

    ax.set_xticks(np.arange(0,1360,50))
    matplotlib.pyplot.grid()
    Connect(fig_pic)
    matplotlib.pyplot.rcParams['keymap.fullscreen'] = ' '
    matplotlib.pyplot.rcParams['keymap.grid'] = ' '
    matplotlib.pyplot.show()
   
#################################################################################
def open_file(N):
    global Data_1
    global Data_2
    global Header
    Name = filedialog.askopenfilename()
    if N==1:
        Data_1, Header = read_file(Name)
##        Data_1 = Data_1[::-1]
    if N==2:
        Data_2, Header = read_file(Name)
        Draw_pic()
    
###################################################################################
def save_to_file(Data, Header):
##    new_name, extension = os.path.splitext(Name)
    new_name = '_align'+'.fits'
    hdu = pyfits.PrimaryHDU(Data, Header)
    hdulist = pyfits.HDUList([hdu])
    hdulist.writeto(new_name, clobber = True, output_verify='ignore')
    print("Data saved to " + new_name)
    print ('\r')
#################################################################################
def Connect(fig_pic):
    cid = fig_pic.canvas.mpl_connect('key_press_event', press)
#################################################################################    
def press(event):
    global Data_2
    if event is not None and (event.key=='right' or event.key=='alt+right'):
        Data_2 = np.roll(Data_2, 1)
        Draw_pic()

    if event is not None and (event.key=='left' or event.key=='alt+left'):
        Data_2 = np.roll(Data_2, -1)
        Draw_pic()
        
#################################################################################
##tools window
root = Tk()
root.title("WL solution")
root.configure(background = 'grey')
root.geometry('176x150')
root.resizable(width=False, height=False)

Open_file = Button(root, text = "1", width=5, height=1, command = lambda: open_file(1))
Open_file.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

Open_file_2 = Button(root, text = "2", width=5, height=1, command = lambda: open_file(2))
Open_file_2.grid(row=0, column=1, columnspan=2, padx=5, pady=5)

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

Fit_B = Button(root, text = "Fit & save", width=22, height=1, command = lambda: save_to_file(Data_2, Header))
Fit_B.grid(row=2, column=0, columnspan=4, padx=6, pady=5)

Clone_B = Button(root, text = "Clone for files", width=22, height=1, command = lambda: clone())
Clone_B.grid(row=3, column=0, columnspan=4, padx=3, pady=5)

mainloop()

