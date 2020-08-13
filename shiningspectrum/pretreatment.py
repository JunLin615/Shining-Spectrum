# -*- coding: utf-8 -*-
"""
@Time:2020/8/10 18:45
@Auth"JunLin615
@File:pretreatment.py
@IDE:PyCharm
@Motto:With the wind light cloud light mentality, do insatiable things
@email:ljjjun123@gmail.com 
"""

import numpy as np
from rampy import baseline as bl
from rampy import smooth as st
from peakutils.baseline import baseline as blp
import pywt

"""
pretreatment用于对光谱数据进行预处理。
Pretreatment is used to preprocess spectral data.

smooth(x,y,Lambda,threshold):smooth函数用于对输入数据进行平滑处理，采取一次小波平滑加一次SG平滑。
                            Smooth function is used to smooth the input data, which adopts 
                            one wavelet smoothing plus one whittaker smoothing.
                            
baseline(x, y, roi, polynomial_order):baseline函数用于光谱背景光的去除。The baseline function is used to remove the spectral background light.

autbaseline(x, y, deg=3, max_it, tol):
"""

def smooth(x, y, Lambda=10 ** 0.5, threshold=0.07):
    """
    smooth函数用于对输入数据进行平滑处理，采取一次小波平滑加一次SG平滑。
    :param x: 待滤波函数横轴，type:numpy.ndarray，shape:(:,)
    :param y: 待滤波数据纵轴
    :param Lambda: whittaker滤波参数
    :param threshold: 小波过滤阈值
    :return: x:原x;datarec:滤波后数据，type:numpy.ndarray，shape:(:,)
    """
    w = pywt.Wavelet('db8')
    maxlev = pywt.dwt_max_level(len(y), w.dec_len)

    # 小波分解
    coeffs = pywt.wavedec(y, 'db8', level=maxlev)

    # 对噪声滤波
    for i in range(1, len(coeffs)):
        coeffs[i] = pywt.threshold(coeffs[i], threshold * max(coeffs[i]))

    # 小波重构
    datarec = pywt.waverec(coeffs, 'db8')

    # 使用SG滤波进行再次平滑
    # datarec = rampy.smooth(x, datarec.T, method="savgol", window_length=window_length, polyorder=polyorder)
    # 再做一次whittaker平滑，效果比再做一次SG好
    datarec = st(x, datarec.T, method="whittaker", Lambda=Lambda)

    return x, datarec


def baseline(x, y, roi=np.array([[0, 100], [200, 220], [280, 290], [420, 430], [480, 500]]), polynomial_order=3):
    """
    baseline用于对输入数据进行背景去除，需要手动指定非峰位置，对于较矮的宽峰较多的时效果要好于autbaseline，适合数据量小的实验阶段使用。
    :param x: 未去除背景的数据x
    :param y: 未去除背景的数据y
    :param rio: 手动指定的非峰x段落列表，type:numpy,ndarrayshape:(a,b),
                eg:rio = np.array([[0,100],[200,220]])表示x=0到x=100处的光谱不对应峰值
    :param polynomial_order:多项式你拟合的阶数，默认为3
    :return:x:原x;ycalc_poly:去除背景后的y,type:numpy.ndarray，shape:(:,);base_poly,背景数据，type:numpy.ndarray，shape:(:,)
    """

    ycalc_poly, base_poly = bl(x, y, roi, 'poly', polynomial_order=polynomial_order)
    ycalc_poly = ycalc_poly[:, 0].T
    base_poly = base_poly[:, 0].T

    return x, ycalc_poly, base_poly


def autbaseline(x, y, deg=3, max_it=200, tol=None):
    """
    autbaseline函数为baseline函数的自动版本，不需要手动指定非峰位置，调试好后适用于采用单一光谱仪的自动化产品之中。
    :param x:
    :param y:
    :param deg:type:int (default: 3),拟合数据基线时的多项式阶数，阶数过低会导致背景去除不彻底，过高会导致过拟合
    :param max_it: type:int (default: 200)拟合时执行迭代的最大次数
    :param tol: type:float (default: 1e-3)，收敛误差，当两次迭代间的结果之差小于‘tol’，停止迭代。
    :return: x:原x;y_r:去除背景后的y,type:numpy.ndarray，shape:(:,),y_base,背景数据，type:numpy.ndarray，shape:(:,)
    """
    y_base = blp(y, deg=deg, max_it=max_it, tol=tol)
    y_r = y - y_base
    return x, y_r, y_base
