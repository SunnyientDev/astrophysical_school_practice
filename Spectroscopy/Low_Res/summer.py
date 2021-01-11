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
Data = []

#################################################################################

#################################################################################
def Draw_pic():
    global Data
    fig_pic = matplotlib.pyplot.figure(1)
    matplotlib.pyplot.cla()
    Scale = np.ones(Data.shape[0])
    Scale[0] = float(E_0.get())
    Scale[1] = float(E_1.get())
    Scale[2] = float(E_2.get())
    Scale[3] = float(E_4.get())
    Scale[4] = float(E_5.get())
    Scale[5] = float(E_6.get())
    Scale[6] = float(E_7.get())
    Scale[7] = float(E_8.get())
    Scale[8] = float(E_9.get())
    Scale[9] = float(E_10.get())
    Scale[10] = float(E_11.get())
    Scale[11] = float(E_12.get())
    Scale[12] = float(E_l.get())
##    Scale[13] = float(E_0.get())
    

    for ii in range(0, Data.shape[0]-1):
        matplotlib.pyplot.plot(Data[ii]*Scale[ii])

##    matplotlib.pyplot.plot(np.sum(Data*Scale[:, None], 0))

#################################################################################
##
##    
##    matplotlib.pyplot.plot(Data)
##    for ii
    matplotlib.pyplot.show()

def read_file(file_path):
    print(file_path)
    hdulist = pyfits.open(file_path) 
    img=hdulist[0].data.copy()
    Header  = hdulist[0].header
    hdulist.close
##    Data = Data[::-1]
    return (img)

###################################################################################
def open_list():
    global Data
    Loc_Data =[]
    where = filedialog.askdirectory(initialdir=os.getcwd())
    dir_list = os.listdir(where)
    for f in dir_list:
        if ('.fit' in f) or ('.fits' in f):
            img=read_file(where +'/'+ f)
            img=img-min(img)
            Loc_Data.append(img)

    Data = np.asarray(Loc_Data)
    Draw_pic()

#####################################################################################
        
#################################################################################
##tools window
root = Tk()
root.title("WL solution")
root.configure(background = 'grey')
root.geometry('176x650')
root.resizable(width=False, height=False)

Open_file = Button(root, text = "Dir", width=22, height=1, command = lambda: open_list())
Open_file.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

Label_0 = Label(root, width=9, justify='right', bg = "grey", text = "0:")
Label_0.grid(row=1, column=0, padx=5, pady=5, sticky=E)
E_0 = Entry(root, width=6, justify='left')
E_0.insert (0,'1')
E_0.grid(row=1, column=1, padx=0, pady=5, sticky=W)

Label_1 = Label(root, width=9, justify='right', bg = "grey", text = "1:")
Label_1.grid(row=2, column=0, padx=5, pady=5, sticky=E)
E_1 = Entry(root, width=6, justify='left')
E_1.insert (0,'1')
E_1.grid(row=2, column=1, padx=0, pady=5, sticky=W)

Label_2 = Label(root, width=9, justify='right', bg = "grey", text = "2:")
Label_2.grid(row=3, column=0, padx=5, pady=5, sticky=E)
E_2 = Entry(root, width=6, justify='left')
E_2.insert (0,'1')
E_2.grid(row=3, column=1, padx=0, pady=5, sticky=W)

##Label_3 = Label(root, width=9, justify='right', bg = "grey", text = "3:")
##Label_3.grid(row=4, column=0, padx=5, pady=5, sticky=E)
##E_3 = Entry(root, width=2, justify='left')
##E_3.insert (0,'1')
##E_3.grid(row=4, column=1, padx=0, pady=5, sticky=W)

Label_4 = Label(root, width=9, justify='right', bg = "grey", text = "4:")
Label_4.grid(row=5, column=0, padx=5, pady=5, sticky=E)
E_4 = Entry(root, width=6, justify='left')
E_4.insert (0,'1')
E_4.grid(row=5, column=1, padx=0, pady=5, sticky=W)

Label_5 = Label(root, width=9, justify='right', bg = "grey", text = "5:")
Label_5.grid(row=6, column=0, padx=5, pady=5, sticky=E)
E_5 = Entry(root, width=6, justify='left')
E_5.insert (0,'1')
E_5.grid(row=6, column=1, padx=0, pady=5, sticky=W)

Label_6 = Label(root, width=9, justify='right', bg = "grey", text = "6:")
Label_6.grid(row=7, column=0, padx=5, pady=5, sticky=E)
E_6 = Entry(root, width=6, justify='left')
E_6.insert (0,'1')
E_6.grid(row=7, column=1, padx=0, pady=5, sticky=W)

Label_7 = Label(root, width=9, justify='right', bg = "grey", text = "7:")
Label_7.grid(row=8, column=0, padx=5, pady=5, sticky=E)
E_7 = Entry(root, width=6, justify='left')
E_7.insert (0,'1')
E_7.grid(row=8, column=1, padx=0, pady=5, sticky=W)

Label_8 = Label(root, width=9, justify='right', bg = "grey", text = "8:")
Label_8.grid(row=9, column=0, padx=5, pady=5, sticky=E)
E_8 = Entry(root, width=6, justify='left')
E_8.insert (0,'1')
E_8.grid(row=9, column=1, padx=0, pady=5, sticky=W)

Label_9 = Label(root, width=9, justify='right', bg = "grey", text = "9:")
Label_9.grid(row=10, column=0, padx=5, pady=5, sticky=E)
E_9 = Entry(root, width=6, justify='left')
E_9.insert (0,'1')
E_9.grid(row=10, column=1, padx=0, pady=5, sticky=W)

Label_10 = Label(root, width=9, justify='right', bg = "grey", text = "10:")
Label_10.grid(row=11, column=0, padx=5, pady=5, sticky=E)
E_10 = Entry(root, width=6, justify='left')
E_10.insert (0,'1')
E_10.grid(row=11, column=1, padx=0, pady=5, sticky=W)

Label_11 = Label(root, width=9, justify='right', bg = "grey", text = "11:")
Label_11.grid(row=12, column=0, padx=5, pady=5, sticky=E)
E_11 = Entry(root, width=6, justify='left')
E_11.insert (0,'1')
E_11.grid(row=12, column=1, padx=0, pady=5, sticky=W)

Label_12 = Label(root, width=9, justify='right', bg = "grey", text = "12:")
Label_12.grid(row=13, column=0, padx=5, pady=5, sticky=E)
E_12 = Entry(root, width=6, justify='left')
E_12.insert (0,'1')
E_12.grid(row=13, column=1, padx=0, pady=5, sticky=W)

Label_l = Label(root, width=9, justify='right', bg = "grey", text = "lamp:")
Label_l.grid(row=14, column=0, padx=5, pady=5, sticky=E)
E_l = Entry(root, width=6, justify='left')
E_l.insert (0,'1')
E_l.grid(row=14, column=1, padx=0, pady=5, sticky=W)



Fit_B = Button(root, text = "redraw", width=22, height=1, command = lambda: Draw_pic())
Fit_B.grid(row=15, column=0, columnspan=4, padx=6, pady=5)

mainloop()

