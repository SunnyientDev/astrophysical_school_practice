'''
утилита для экстракции спектра из двумерного изображения
дисперсия должна быть ориенитроана горизонтально
1) необходимо указать файл или папку с файлами
2) в окне будет показан первый (или единственый) файл для обработки
3) с помощью мыши + левая кнопка выделяется область экстракции
4) можно указать границы области экстракции непосредственно в полях Extraction area
5) кнопка h - вертикальный биннинг (суммирование строк) выделенной области -> horizontal box
6) кнопка v - горизонтальный биннинг (суммирование столбцов) выделенной области -> vertical box
7) итоговая экстракция (кнопка Extract!) осуществляется только в режиме horizontal box
8) если была указана папка, то экстракция осуществляется для всех файлов в папке, при этом
область экстракции одинаковая для всех файлов.
9) экстрагированный спектр сохранятеся в ту же папку со старым именем "name" + _ex.fits
10) в заголовк результата записываются поля в соответствии с форматом WCS (совместим с IRAF)

контраст и диапазон визуализации регулируются константами
vmin=median-stdv*low, vmax=median+stdv*high
low - определяет нижнюю границу диапазона. чем больше, тем ниже граница
high - опредеяет верхнюю границу диапазона. чем больше, тем выше граница
'''

import pyfits
import numpy as np
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
##Im_Data
file_list=[]
low = 0.9
high = 2.0

################################################################################# 
def read_file(file_path, Draw, fig):
    print(file_path)
    hdulist = pyfits.open(file_path) 
    Data=hdulist[0].data.copy()
    Header  = hdulist[0].header
    hdulist.close
    if (Draw==1):
        Draw_pic(Data, file_path, fig)
    Get_Stat(Data)
    return (Data, Header)
    
#################################################################################
def Draw_pic(Data, Name, fig):
    med=np.median(Data)
    stdv=np.std(Data)
    fig_pic = matplotlib.pyplot.figure(fig)
    matplotlib.pyplot.cla()
    matplotlib.pyplot.imshow(Data, cmap=cm.Greys_r, aspect='equal',
                             norm= matplotlib.colors.Normalize(vmin=med-stdv*low, vmax=med+stdv*high), interpolation='nearest')
    matplotlib.pyplot.title(Name)
    if (fig==1):
        Connect(fig_pic)
    matplotlib.pyplot.draw()

#################################################################################
def Get_Stat(Data):
    print ("Min= " + str(np.min(Data)))
    print ("Max= " + str(np.max(Data)))
    print ("Mean= " + str(np.mean(Data)))
    print ("Median= " + str(np.median(Data)))
    print ('\r')
#################################################################################
def Get_Spectra(Im_Data, X_start, X_end, Y_start , Y_end, Ax, Draw):
    ROI = Im_Data[min(Y_start, Y_end):max(Y_start, Y_end), min(X_start, X_end):max(X_start, X_end)]
    Out = np.sum(ROI,Ax)
    if Draw==1:
        fig_pic = matplotlib.pyplot.figure(2)
        matplotlib.pyplot.cla()
        matplotlib.pyplot.plot(Out)
        matplotlib.pyplot.show()
    return Out

#################################################################################    
def Extract():
    global Im_Data
    X_start = int(SX.get())
    Y_start = int(SY.get())
    X_end   = int(EX.get())
    Y_end   = int(EY.get())
    for f in file_list:
        try:
            Im_Data, Header = read_file(f, 1, 1)
        except IOError:
                print ("Can't open file:", f)
                return
            
        currentAxis = matplotlib.pyplot.gca()
        if len(currentAxis.patches)>0:
            currentAxis.patches[0].remove()
        currentAxis.add_patch(Rectangle((X_start, Y_start), X_end - X_start, Y_end - Y_start, fill=False, ec="blue", gid="rect"))
        matplotlib.pyplot.show()
        Draw=0
        if Show_frame.get(): Draw=1
        Spectra = Get_Spectra(Im_Data, X_start, X_end, Y_start , Y_end, 0, Draw)
        Header['WCSDIM'] = 1
        Header['CTYPE1'] = 'PIXEL'
        Header['CRPIX1'] = 1
        Header['CDELT1'] = 1
        Header['CD1_1']  = 1
        Header['LTM1_1'] = 1
        Header['WAT0_001'] = 'system=equispec'
        Header['WAT1_001'] = 'wtype=linear label=Pixel'
        Header['APNUM1']   = '1 1 ' + str(min(Y_start, Y_end)) + ' ' + str(max(Y_start, Y_end))

        new_name, extension = os.path.splitext(f)
        new_name = new_name+'_ex'+'.fits'
        hdu = pyfits.PrimaryHDU(Spectra, Header)
        hdulist = pyfits.HDUList([hdu])
        hdulist.writeto(new_name, clobber = True, output_verify='ignore')
        print("Data saved to " + new_name)
        print ('\r')
#################################################################################
def Do_It():
    if (len(file_list)>0): 
        Extract()    
    else: print ("File")

#################################################################################
def open_file():
    global file_list
    global Im_Data
    file_list=[]
    file_path = filedialog.askopenfilename()
    file_list.append(file_path)
    Im_Data = read_file(file_path, 1, 1)[0]
    
def open_list():
    global file_list
    global Im_Data
    file_list=[]
    where = filedialog.askdirectory(initialdir=os.getcwd())
    dir_list = os.listdir(where)
    for f in dir_list:
        if ('.fit' in f):
            file_list.append(str(where+'/'+f))
    Im_Data = read_file(file_list[0], 1, 1)[0]
            
#################################################################################
def Connect(fig_pic):
    cid = fig_pic.canvas.mpl_connect('button_press_event', on_press)
    cid = fig_pic.canvas.mpl_connect('button_release_event', on_release)
    cid = fig_pic.canvas.mpl_connect('motion_notify_event', on_motion)
    cid = fig_pic.canvas.mpl_connect('key_press_event', press)
#################################################################################    
def on_press(event):
    if (event.inaxes):
        SX.delete(0, len(SX.get()))
        SY.delete(0, len(SY.get()))
        SX.insert(0, str(int(event.xdata)))
        SY.insert(0, str(int(event.ydata)))
##        print (event.xdata, event.ydata, event.key)

def on_release(event):
    if (event.inaxes):
        EX.delete(0, len(EX.get()))
        EY.delete(0, len(EY.get()))
        EX.insert(0, str(int(event.xdata)))
        EY.insert(0, str(int(event.ydata)))

def on_motion(event):
    if (event.inaxes):
        if event.button==1 :
            X_start = int(SX.get())
            Y_start = int(SY.get())
            X_length = int(event.xdata - X_start)
            Y_length = int(event.ydata - Y_start)
            currentAxis = matplotlib.pyplot.gca()
            if len(currentAxis.patches)>0:
                currentAxis.patches[0].remove()
            currentAxis.add_patch(Rectangle((X_start, Y_start), X_length, Y_length, fill=False, ec="blue", gid="rect"))
            matplotlib.pyplot.show()
        
##        print('you pressed', event.button, event.xdata, event.ydata)
def press(event):
    if event is not None and (event.key=='h' or event.key=='alt+h'):
        X_start = int(SX.get())
        Y_start = int(SY.get())
        X_end   = int(EX.get())
        Y_end   = int(EY.get())
        Get_Spectra(Im_Data, X_start, X_end, Y_start , Y_end, 0, 1)

    if event is not None and (event.key=='v' or event.key=='alt+v'):
        X_start = int(SX.get())
        Y_start = int(SY.get())
        X_end   = int(EX.get())
        Y_end   = int(EY.get())
        Get_Spectra(Im_Data, X_start, X_end, Y_start , Y_end, 1, 1)
        
#################################################################################
##tools window
root = Tk()
root.title("Get Spectra")
root.configure(background = 'grey')
root.geometry('262x280')
root.resizable(width=False, height=False)

##set files for extraction 
Im_frame = LabelFrame(root, text="Image", width=260, height=230, bg = "grey", bd=2)
Im_frame.grid(row=0, column=0, columnspan=2, sticky=W, padx=6, pady=3)

Open_file = Button(Im_frame, text = "File", width=12, height=1, command = lambda: open_file())
Open_file.grid(row=0, column=0, padx=3, pady=2)

Label_1 = Label(Im_frame, width=5, justify='center', bg = "grey", text = "OR")
Label_1.grid(row=0, column=1, padx=3, pady=2)
    
Open_dir = Button(Im_frame, text = "Directory", width=12, height=1, command = lambda: open_list())
Open_dir.grid(row=0, column=2, padx=3, pady=2)

##set extraction area
EA_frame = LabelFrame(root, text="Extraction area", width=254, height=293, bg = "grey", bd=2)
EA_frame.grid(row=1, column=0, columnspan=2, sticky=W, padx=6, pady=3)

Label_SX = Label(EA_frame, width=10, bg = "grey", text = "Start X")
Label_SX.grid(row=0, column=0, sticky=E, padx=3, pady=2)
SX = Entry(EA_frame, width=5, justify='left')
SX.insert (0,'0')
SX.grid(row=0, column=1, padx=3, pady=2)

Label_EX = Label(EA_frame, width=10, bg = "grey", text = "End X")
Label_EX.grid(row=0, column=2, padx=3, pady=2)
EX = Entry(EA_frame, width=5, justify='left')
EX.insert (0,'0')
EX.grid(row=0, column=3, padx=4, pady=2)

Label_SY = Label(EA_frame, width=10, bg = "grey", text = "Start Y")
Label_SY.grid(row=1, column=0, padx=3, pady=2)
SY = Entry(EA_frame, width=5, justify='left')
SY.insert (0,'0')
SY.grid(row=1, column=1, padx=3, pady=2)

Label_EY = Label(EA_frame, width=10, bg = "grey", text = "End Y")
Label_EY.grid(row=1, column=2, padx=3, pady=2)
EY = Entry(EA_frame, width=5, justify='left')
EY.insert (0,'0')
EY.grid(row=1, column=3, padx=4, pady=2)

##show and do!
Show_frame = IntVar()
Show = Checkbutton(root, bg = "grey", text = 'Show result', variable=Show_frame)
Show.grid(row=4, column=0, sticky=W, padx=3, pady=3)

Make = Button(root, text = "Extract!", width=12, height=1, command = lambda: Do_It())
Make.grid(row=4, column=1, sticky=E, padx=6, pady=3)



mainloop()

