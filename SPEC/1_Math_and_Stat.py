'''
утилита для математических операций с фитс-кадрами
1) необходимо указать первый операнд: один файл или папку с файлами
2) выбрать оператор
3) указать второй операнд: файл или константу
4) для вычисления среднего или медианного среднего для нескольких файлов
необходимо указать папку с файлами и тип усреднения
5) для визуализации результата - отметить поле Show result
6) для всех операндов и результата вычисляются простейшие статистики: максимум,
минимум, среднее, медианное среднее

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
import warnings
import os
from tkinter import *

warnings.simplefilter("ignore")
matplotlib.pyplot.ion()

#################################################################################
Operand_1=[]
Operand_2=[]
Combine_list=[]

low=0.2
high=1.0

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
    matplotlib.pyplot.draw()

#################################################################################
def Get_Stat(Data):
    print ("Min= " + str(np.min(Data)))
    print ("Max= " + str(np.max(Data)))
    print ("Mean= " + str(np.mean(Data)))
    print ("Median= " + str(np.median(Data)))
    print ('\r')
#################################################################################
def Math():
    global Operand_1
    Operator = OP.get()
    SOP = Second_Operand()
    for f in Operand_1:
        print("Operand 1")
        try:
            Data, Header = (read_file(f, 1, 1))
        except IOError:
                print ("Can't open file:", f)
        try:
            if (Operator==1):
                Data = Data+SOP
                Name = "Add"
            elif (Operator==2):
                Data = Data-SOP
                Name = "Subtract"
            elif (Operator==3):
                Data = Data*SOP
                Name = "Multiply"
            elif (Operator==4):
                Data = Data/SOP
                Name = "Divide"
        except: print("Math error")
        print ("Result of " + Name)
        Get_Stat(Data)
        if Show_frame.get(): Draw_pic(Data, Name, 3)

        Data = np.float32(Data)
        
        new_name, extension = os.path.splitext(f)
        new_name = new_name+'_'+Name+'.fits'
        Header['HISTORY'] = Name
        hdu = pyfits.PrimaryHDU(Data, Header)
        hdulist = pyfits.HDUList([hdu])
        hdulist.writeto(new_name, clobber = True, output_verify='ignore')
        print("Data saved to " + new_name)
        print ('\r')         
                
################################################################################
def Second_Operand():
    global Operand_2
    if (len(Operand_2)>0): ##use file
        print("Operand 2 = " + Operand_2[0])
        Data, Header = read_file(Operand_2[0], 1, 2)
    else: ##use constant
        Data = float(Const.get())
        try:
            matplotlib.pyplot.close(2)
        except: pass
        print("Operand 2 = " + str(Data))
    return Data

################################################################################
def Combine():
    global Combine_list
    all_data = []
    Num = len(Combine_list)
    for f in Combine_list:
        Num=Num-1
        try:
            if (Num>0): all_data.append(read_file(f, 0, 0)[0])
            else: all_data.append(read_file(f, 1, 1)[0])
        except IOError:
                print ("Can't open file:", f)
                
    all_data=np.asarray(all_data)
    
    if (Mode.get()==1):
        out = np.mean(all_data, 0)
        Name = "Mean"
        print ("Mean")
    if (Mode.get()==2):
        out = np.median(all_data, 0)
        Name = "Median"
        print ("Median")
    Get_Stat(out)
    if Show_frame.get(): Draw_pic(out, Name, 2)

    file_name = filedialog.asksaveasfilename(defaultextension = "fits", initialfile = Name)

    out = np.float32(out)
    
    hdu = pyfits.PrimaryHDU(out)
    hdulist = pyfits.HDUList([hdu])
    prihdr = hdulist[0].header
    prihdr['HISTORY'] = Name
    hdulist.writeto(file_name, clobber = True)
    print("Data saved to " + file_name)
    print ('\r')
    
#################################################################################
def Do_It():
    if (OP.get()!=0): ##Math
        if (len(Operand_1)>0    and OP.get()>0)  : Math()
        else: print ("check parameters")
    else:             ##Combine
        if (len(Combine_list)>1 and Mode.get()>0): Combine()
        else: print ("check parameters")

#################################################################################
def open_file(Pass):
    if (Pass==1):
        global Operand_1
        Operand_1=[]
        file_path = filedialog.askopenfilename()
        Operand_1.append(file_path)
    else:
        global Operand_2
        Operand_2=[]
        file_path = filedialog.askopenfilename()
        Operand_2.append(file_path)
        
def open_list(Pass):
    if (Pass==1):
        global Operand_1
        Operand_1=[]
        where = filedialog.askdirectory(initialdir=os.getcwd())
        dir_list = os.listdir(where)
        for f in dir_list:
            if ('.fit' in f):
                Operand_1.append(str(where+'/'+f))
    else:
        global Combine_list
        Combine_list=[]
        where = filedialog.askdirectory(initialdir=os.getcwd())
        dir_list = os.listdir(where)
        for f in dir_list:
            if ('.fit' in f):
                Combine_list.append(str(where+'/'+f))
        OP_None.select()

#################################################################################
def Set_Const(sv):
    global Operand_2
    Operand_2=[]
def Set_Combine():
    OP_None.select()
#################################################################################
##tools window
root = Tk()
root.title("Math and Stat")
root.configure(background = 'grey')
root.geometry('262x280')
root.resizable(width=False, height=False)

##set operand 1 frame
O1_frame = LabelFrame(root, text="Operand 1", width=260, height=230, bg = "grey", bd=2)
O1_frame.grid(row=0, column=0, columnspan=2, sticky=W, padx=6, pady=3)

Open_file = Button(O1_frame, text = "File", width=12, height=1, command = lambda: open_file(1))
Open_file.grid(row=0, column=0, padx=3, pady=2)

Label_1 = Label(O1_frame, width=5, justify='center', bg = "grey", text = "OR")
Label_1.grid(row=0, column=1, padx=3, pady=2)
    
Open_dir = Button(O1_frame, text = "Directory", width=12, height=1, command = lambda: open_list(1))
Open_dir.grid(row=0, column=2, padx=3, pady=2)

##set operator frame
OP_frame = LabelFrame(root, text="Operator", width=254, height=293, bg = "grey", bd=2)
OP_frame.grid(row=1, column=0, columnspan=2, sticky=W, padx=6, pady=3)

OP = IntVar()
OP_Add = Radiobutton(OP_frame, text="Add",      bg = "grey", width=2, variable=OP, value=1)
OP_Add.grid(row=0, column=0, sticky=W, padx=2, pady=1)

OP_Sub = Radiobutton(OP_frame, text="Subtract", bg = "grey", width=5, variable=OP, value=2)
OP_Sub.grid(row=0, column=1, sticky=W, padx=2, pady=1)

OP_Mul = Radiobutton(OP_frame, text="Multiply", bg = "grey", width=5, variable=OP, value=3)
OP_Mul.grid(row=0, column=2, sticky=W, padx=2, pady=1)

OP_Div = Radiobutton(OP_frame, text="Divide",   bg = "grey", width=5, variable=OP, value=4)
OP_Div.grid(row=0, column=3, sticky=W, padx=2, pady=1)

OP_None = Radiobutton(OP_frame, text="None  ",  bg = "grey", width=5, variable=OP, value=0)
OP_None.grid(row=1, column=0, columnspan=4, sticky=E, padx=2, pady=1)
OP_None.select()

##set operand 2 frame
O2_frame = LabelFrame(root, text="Operand 2", width=254, height=293, bg = "grey", bd=2)
O2_frame.grid(row=2, column=0, columnspan=2, sticky=W, padx=6, pady=3)

Open_file = Button(O2_frame, text = "File", width=12, height=1, command = lambda: open_file(2))
Open_file.grid(row=0, column=0, padx=3, pady=2)

Label_1 = Label(O2_frame, width=5, justify='center', bg = "grey", text = "OR")
Label_1.grid(row=0, column=1, padx=3, pady=2)

sv = StringVar()
sv.trace("w", lambda name, index, mode, sv=sv: Set_Const(sv))  
Const = Entry(O2_frame, width=15, justify='left', textvariable=sv)
Const.insert (0,'0.0')
Const.grid(row=0, column=2, padx=3, pady=2)

##set combine frame
C_frame = LabelFrame(root, text="Combine files from directory", width=300, height=293, bg = "grey", bd=2)
C_frame.grid(row=3, column=0, columnspan=2, sticky=W,  padx=6, pady=3)

Open = Button(C_frame, text = "Directory", width=12, height=1, command = lambda: open_list(2))
Open.grid(row=0, column=0, padx=3, pady=2)

Mode = IntVar()
RB_mean   = Radiobutton(C_frame, text="mean",   bg = "grey", width=6, variable=Mode, value=1, command = Set_Combine)
RB_mean.grid(row=0, column=1, padx=1, pady=2)
RB_median = Radiobutton(C_frame, text="median", bg = "grey", width=6, variable=Mode, value=2, command = Set_Combine)
RB_median.grid(row=0, column=2, sticky=E, padx=2, pady=2)

##show and do!
Show_frame = IntVar()
Show = Checkbutton(root, bg = "grey", text = 'Show result', variable=Show_frame)
Show.grid(row=4, column=0, sticky=W, padx=3, pady=3)

Make = Button(root, text = "Do it!", width=12, height=1, command = lambda: Do_It())
Make.grid(row=4, column=1, sticky=E, padx=6, pady=3)

mainloop()

