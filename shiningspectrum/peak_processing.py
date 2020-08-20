# -*- coding: utf-8 -*-
"""
@Time:2020/8/14 21:26
@Auth"JunLin615
@File:peak_processing.py
@IDE:PyCharm
@Motto:With the wind light cloud light mentality, do insatiable things
@email:ljjjun123@gmail.com 
"""

from scipy.signal import find_peaks
import numpy as np
import math

def search_peaks(x_data, y_data, height=0.1, distance=10):
    """
    从给定的光谱数据中寻找峰值
    Look for peaks in the given spectral data

    :param x_data: 光谱数据x数据，Spectral X-axis data

    :param y_data:谱数据y数据，Spectral Y-axis data

    :param height:峰值高度阈值.Peak height threshold

    :param distance:峰之间的最小水平距离，如果距离小于指定值，会从高度低的峰开始删除，直到满足限制。
                    The minimum horizontal distance between peaks. If the distance is less than the specified value,
                     it is removed from the peak at a lower height until the limit is met.

    :return:一个包含峰值中心坐标和峰值的二维列表。A two-dimensional list containing the peak center coordinates and the peaks.
            peaks[x][0]为该峰的中心坐标，peaks[x][1]为对应峰值。peaks [x][0] is the central coordinate of the peak, and peaks[x][1] is the corresponding peak.
    """
    # 寻找指定物质的峰，返回峰值中心列表

    prominence = np.mean(y_data)
    peak_list = find_peaks(y_data, height=height, prominence=prominence, distance=distance)

    peaks = []
    for i in peak_list[0]:
        peak = (x_data[i], y_data[i])
        peaks.append(peak)

    return peaks


def search_database_peaks(all_spectrum, height=0.1, distance=10):
    """
    输入一个字典，确定字典中的物质的峰，返回由物质CAS号和峰值中心列表所构成键值对组成的字典。
    Enter a dictionary, determine the peak of a substance in the dictionary, and return a dictionary consisting of
    the key value pairs of the substance CAS number and the peak center list.

    :param all_spectrum:格式与database.read_all()函数或者database.read_custom函数返回值格式一致。
                        The format is the same as that of the database.read_all() function or
                        the database.read_custom function return value.

    :param height:峰值高度阈值.Peak height threshold

    :param distance:峰之间的最小水平距离，如果距离小于指定值，会从高度低的峰开始删除，直到满足限制。
                    The minimum horizontal distance between peaks. If the distance is less than the specified value,
                     it is removed from the peak at a lower height until the limit is met.

    :return:返回由物质CAS号和峰值中心列表所构成键值对组成的字典。Returns a dictionary consisting of the key value pairs of
            the substance CAS number and the peak center list.
    """
    # 寻找已知物质的峰，返回由物质CAS号和峰值中心列表所构成键值对组成的字典。
    peaks_database = {}

    for key in list(all_spectrum.keys()):
        x_data = all_spectrum[key][0]
        y_data = all_spectrum[key][1]

        peaks = search_peaks(x_data, y_data, height=height, distance=distance)
        peaks_database.update({key: peaks})

    return peaks_database


def compare_peaks(peaks_database, peaks, abs_tol=5):
    """
    将peaks的每个峰与peaks_database中的各个物质的峰进行比较，寻找重合的峰。
    Compare each peak of peaks to the peaks of each material in PEaks_database to find overlapping peaks.

    :param peaks_database:由物质CAS号和峰值中心列表所构成键值对组成的字典。A dictionary consisting of the key value pairs of
            the substance CAS number and the peak center list.

    :param peaks:一个包含峰值中心坐标和峰值的二维列表。可以使用peak_processing.search_peaks()函数获得。
                A two-dimensional list containing the peak center coordinates and the peaks.
                It is available using the peak_processes.search_peaks () function.

    :param abs_tol:比较两个峰的中心值，当二者的区别大于abs_tol,将认为两个峰不重合。比如1000和1001的区别，为1
                    Compare the central values of the two peaks when the difference between them is
                    greater than abs_tol,the two peaks will be considered to coincide.
                    The difference between 1000 and 1001, for example, is 1

    :return:一个双层字典。第一层以物质的CAS号为key，第二层包含未知物质与该物质的峰重合情况。
            A double dictionary.The first layer takes the CAS number of the substance as the key, and the second layer
            contains the peak coincidence of the unknown substance and the substance.
    """
    # print('peaks_database:\n'.format(peaks_database))
    # print('peaks:\n'.format(peaks))
    coincide_information = {}

    for key in list(peaks_database.keys()):

        # 待测物与key物质重叠的峰
        coincide_list = []

        for peak_d in peaks_database[key]:

            for peak in peaks:
                # print('{}物质峰{}与待测物峰{}比较'.format(key,peak_d[0],peak[0]))
                if math.isclose(peak[0], peak_d[0], abs_tol=abs_tol):
                    coincide_list.append([peak_d[0], peak[0]])

        coincide_information.update(
            {key: {'coincide_list': coincide_list, 'coincide_number': [len(peaks_database[key]), len(coincide_list)]}})

    return coincide_information


def judge_matter(coincide_information, criterion=0.99):
    """
    判断是否含有某种物质。
    Determine if it contains a substance.

    :param coincide_information:peak_processing.compare_peaks()函数的返回值。peak_processing.compare_peaks()函数的返回值。
    :param criterion:
    :return:
    """
    contain_dict = {}
    for key in list(coincide_information.keys()):
        coincide_number = coincide_information[key]['coincide_number']
        key_criterion = coincide_number[1] / coincide_number[0]
        if key_criterion >= criterion:
            contain_dict.update({key: key_criterion})
    return contain_dict





