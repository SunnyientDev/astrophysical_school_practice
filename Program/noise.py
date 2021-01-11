from matplotlib import pyplot as plt
import scipy as sp
import numpy as np
from scipy.special import erf as erf
from scipy.ndimage.filters import gaussian_filter
import pylab as P
import pyfits

#константы
exp=1800 #время интегрирования (копим сигнал от объекта)
RNoise = 8.2 #дробовой шум приемника (шум считывания)
TEGS = 0.1   #темновой ток приемника (скорость термогенерации [электронов/(пиксль*секунда)])

#шумы примника
#шум считывания
RN = RNoise*np.random.standard_normal(500) #создаем массив для шума считывания длиной 500 пикслей и заполняем случайными значениями 

#горячие пиксели
BP = np.zeros(500) ##массив для горячиех пикселей
#положения и значения горячих пикселей
BP[80]=80
BP[200]=200
BP[400]=50
##BP[600]=1000
##BP[1000]=3000
##BP[1200]=200

#темновой ток и шум темнового тока приемника
TEC = np.ones(500)*TEGS*exp #темновой ток за время интегрирования
TEN = np.sqrt(TEGS*exp)*np.random.standard_normal(500) #шум темнового тока (Пуассоновский шум)

#bias - ток смещения примника. необхоим чтобы не было отрицательных сначений
bias = np.ones(500)*1000 #уровень bias = 1000

#из bias и шумов формируем темновой кадр - суммы всех сигналов и шумов в отсутствие сигнала от источника
Dark = bias+RN+TEC+TEN+BP 

#цикл для получения усредненного темного кадра, среднее ищем для 10 кадров
SDark = np.zeros(500)
for ii in range(10):
    RN = RNoise*np.random.standard_normal(500)                #обновляем занчения случайного шума считывания
    TEN = np.sqrt(TEGS*exp)*np.random.standard_normal(500)    #то же самое для шума темнового тока
    SDark = SDark + bias+RN+TEC+TEN+BP                        #получаем сумму старых темновых кадров + новый темновой кадр
    
SDark=SDark/10                                                #получаем усредненный темновой кадр

#рисуем картинку
X = np.arange(0,500) #массив для координаты X.
plt.plot(X, Dark, 'b', label='Dark')
plt.plot(X, SDark, 'g', label='Super Dark')
plt.legend()
plt.show()

#три звезды - делаем их из гауссиан
Gauss1 = exp*2*np.exp(-(((X-100)**2)/100))
Gauss2 = exp*6*np.exp(-(((X-250)**2)/100))
Gauss3 = exp*0.3*np.exp(-(((X-400)**2)/100))
Stars = Gauss1 + Gauss2 + Gauss3
Stars_Poisson = np.random.poisson(lam = Stars, size=None)
#рисуем картинку
plt.plot(X, Stars, 'r', label='Stars')
plt.plot(X, Stars_Poisson+100, 'r', label='Stars+Poisson')
plt.legend()
plt.show()

#шум + звезды
Real_Image = Stars_Poisson + bias + TEC + BP + RNoise*np.random.standard_normal(500) + np.sqrt(TEGS*exp)*np.random.standard_normal(500)
#рисуем картинку
plt.plot(X, Real_Image, 'r', label='Stars + Noise')
plt.legend()
plt.show()

#вычитаем из реального изображения темновые кадры (одиночный и средний)
plt.plot(X, Real_Image-Dark, 'r', label='Stars + Noise-Dark')
plt.plot(X, Real_Image-SDark+100, 'b', label='Stars + Noise-SDark')
plt.legend()
plt.show()



    
##
##ech = np.zeros((3, 500))
##
##Continuum = 100
##Cont = np.ones(500)*Continuum
##Gauss1 = -Continuum*0.7*np.exp(-(((X-100)**2)/500))
##Gauss2 = -Continuum*0.7*np.exp(-(((X-250)**2)/500))
##Gauss3 = -Continuum*0.4*np.exp(-(((X-300)**2)/500))
##Lines = Cont + Gauss1 + Gauss2 + Gauss3
##Noise = np.random.poisson(lam = Lines, size=None)
##R_Stars = Noise + RN+BP
##ech[0 , :] = R_Stars
##plt.plot(ech[0 , :], 'g', label= 'Stars')
##
####ech[0 , :] = R_Stars
##
##Continuum = 1000
##Cont = np.ones(500)*Continuum
##Gauss1 = -Continuum*0.7*np.exp(-(((X-100)**2)/500))
##Gauss2 = -Continuum*0.7*np.exp(-(((X-250)**2)/500))
##Gauss3 = -Continuum*0.4*np.exp(-(((X-300)**2)/500))
##Lines = Cont + Gauss1 + Gauss2 + Gauss3
##Noise = np.random.poisson(lam = Lines, size=None)
##R_Stars = Noise + RN+BP
##ech[1 , :] = R_Stars
##plt.plot(ech[1 , :], 'b', label= 'Stars')
##
##Continuum = 500
##Cont = np.ones(500)*Continuum
##Gauss1 = -Continuum*0.7*np.exp(-(((X-100)**2)/500))
##Gauss2 = -Continuum*0.7*np.exp(-(((X-250)**2)/500))
##Gauss3 = -Continuum*0.4*np.exp(-(((X-300)**2)/500))
##Lines = Cont + Gauss1 + Gauss2 + Gauss3
##Noise = np.random.poisson(lam = Lines, size=None)
##R_Stars = Noise + RN+BP
##ech[2 , :] = R_Stars
##plt.plot(ech[2 , :], 'r', label= 'Stars')
##
##
##
##
####hdu.writeto('model.fits', clobber=True)    
##
##plt.show()

##Sum = np.zeros(2000)
##for ii in range(10):
##    bias = np.ones(2000)*100
##    RN = RNoise*np.random.standard_normal(2000)
##    TEC = np.ones(2000)*0.1*exp
##    TEN = np.sqrt(0.1*exp)*np.random.standard_normal(2000)
##    R_Stars = Stars*Resp+bias+RN+TEC+TEN+BP
##    Dark_C = (R_Stars-SDark)
##    Flat_C = Dark_C/SFlat
##    Sum = Sum + Flat_C
##    
##Sum = Sum/10


### the histogram of the data with histtype='step'
##n, bins, patches = plt.hist(RN, 100, normed=False, facecolor='green', alpha=0.75)
####P.setp(patches, 'facecolor', 'g', 'alpha', 0.75)
##plt.xlabel('value')
##plt.ylabel('number')
##plt.grid()
##plt.ylim(-1, max(n)+1)


##
####plt.plot(X, Flat_C, 'b', label= 'x10 Exp')
##plt.plot(X, Sum, 'r', label= 'Sum of 10')
####plt.plot(X, Flat_C, 'g', label= '/Flat')
####plt.plot(X, Stars, 'g', label= 'Stars')
####plt.plot(X, RN+TEC+TEN-100, 'k', label= 'noise')
####Z = gaussian_filter(Out,0.28)
##
##SDark = np.zeros(2000)
##for ii in range(10):
##    bias = np.ones(2000)*100
##    RN = RNoise*np.random.standard_normal(2000)
##    TEC = np.ones(2000)*0.1*exp*10
##    TEN = np.sqrt(0.1*exp*10)*np.random.standard_normal(2000)
##    SDark = SDark + bias+RN+TEC+TEN+BP
##    
##SDark=SDark/10
##
##Gauss1 = 100*10*np.exp(-(((X-250)**2)/500))
##Gauss2 = 100*10*np.exp(-(((X-1000)**2)/500))
##Gauss3 = 100*10*np.exp(-(((X-1750)**2)/500))
##Stars = Gauss1 + Gauss2 + Gauss3
##
##R_Stars = Stars*Resp+bias+RN+TEC+TEN+BP
##Dark_C = (R_Stars-SDark)
##Flat_C = Dark_C/SFlat
##
##plt.plot(X, Flat_C/10, 'b', label= 'Exp x 10')
##




####кусок для флэтов
##Flat = np.ones(2000)*10000
##Vign = 1 - 0.4/1000000*(X-1000)**2
##NonU = np.ones(2000)+ 0.008*np.random.standard_normal(2000)
##Resp = Vign*NonU
##FF = Flat*Resp

##SFlat = np.zeros(2000)
##for ii in range(10):
##    bias = np.ones(2000)*100
##    RN = RNoise*np.random.standard_normal(2000)
##    TEC = np.ones(2000)*0.1*exp
##    TEN = np.sqrt(0.1*exp)*np.random.standard_normal(2000)
##    SFlat = SFlat + (bias+RN+TEC+TEN+BP+FF-SDark)
##
##SFlat = SFlat /10
##SFlat = SFlat/max(SFlat)
