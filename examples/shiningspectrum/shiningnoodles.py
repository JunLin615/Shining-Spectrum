# -*- coding: utf-8 -*-
"""
@Time:2020/8/20 20:19
@Auth"JunLin615
@File:shiningnoodles.py
@IDE:PyCharm
@Motto:With the wind light cloud light mentality, do insatiable things
@email:ljjjun123@gmail.com 
"""
import os

from scipy import interpolate

from ramannoodles import spectrafit

import numpy as np
import lmfit
from lmfit.models import PseudoVoigtModel

from scipy.signal import find_peaks
import math

from multiprocessing import  Manager, Pool
import time
from shiningspectrum import peak_processing

# ————————————————————————————————————————————————————————————
def clean_spectra(compound):
    """
    清除重复X数据。
    :param compound:
    :return:
    """
    x_comp = compound['x']
    y_comp = compound['y']
    y_comp = spectrafit.subtract_baseline(y_comp)
    # zip x and y values
    comp_data = list(zip(x_comp, y_comp))
    # clean comp1
    comp_data_clean = []
    for i in range(1, len(comp_data) - 1):
        if comp_data[i][0] == comp_data[i - 1][0]:
            pass
        else:
            comp_data_clean.append(comp_data[i])
    return comp_data_clean


def interpolate_spectra(comp_data_clean):
    """
    插值
    :param comp_data_clean:
    :return:
    """
    # unzip data
    x_comp, y_comp = zip(*comp_data_clean)
    # interpolate data
    comp_int = interpolate.interp1d(x_comp, y_comp, kind='cubic')
    # define ranges
    comp_range = np.arange(int(min(x_comp)) + 1, int(max(x_comp)), 1)
    # run interpolations
    y_comp_interp = comp_int(comp_range)
    # zip interpolated values
    comp_data_int = list(zip(comp_range, y_comp_interp))

    return comp_data_int


def sum_spectra(comp1_data_int, comp2_data_int):
    """
    相加
    :param comp1_data_int:
    :param comp2_data_int:
    :return:
    """
    # add the two spectra
    combined = sorted(comp1_data_int + comp2_data_int)
    # add by like
    same_x = {x: 0 for x, _ in combined}
    for name, num in combined:
        same_x[name] += num
    sum_combined = list(map(tuple, same_x.items()))
    # unzip
    x_combined, y_combined = zip(*sum_combined)
    # set as arrays
    x_combined = np.asarray(x_combined)
    y_combined = np.asarray(y_combined)
    return x_combined, y_combined


def combine_spectra(compound_1, compound_2):
    data1 = clean_spectra(compound_1)
    data2 = clean_spectra(compound_2)

    comp1_data_int = interpolate_spectra(data1)
    comp2_data_int = interpolate_spectra(data2)

    x_combined, y_combined = sum_spectra(comp1_data_int, comp2_data_int)

    return x_combined, y_combined


# ————————————————————————————————————————————————————————————
def shining2noodles(all_spectrum):
    list_of_compounds = []
    for key in list(all_spectrum.keys()):
        x = np.array(all_spectrum[key][0])
        y = np.array(all_spectrum[key][1])

        list_of_compounds.append(({"title": key, "x": x, "y": y}))

    return list_of_compounds

class component_testing:

    def __init__(self, height=0.1, prominence_unknow='auto', prominence_know='auto', distance=10, precision=0.03 , peak_algorithm = "noodles"):
        """

        :param height: 峰值高度阈值
        :param prominence_unknow: 对待测物寻峰时，使用的prominence参数，可以是"auto"或者一个浮点数。
        :param prominence_know: 对光谱数据库进行寻峰时，使用的prominence参数，可以是"auto"或者一个浮点数。
        :param distance: 峰之间的最小水平距离，如果距离小于指定值，会从高度低的峰开始删除，直到满足限制。
        :param precision: 比对峰时的精确度，数字越小越精确。
        :param peak_algorithm: 可以定义为"noodles"或“shining”，更改此参数会使用不同的寻峰算法，"shining"速度很快，"noodles"精细一些。
        """
        self.height = height
        self.prominence_unknow = prominence_unknow
        self.prominence_know = prominence_know
        self.distance = distance
        self.precision = precision
        self.peak_algorithm = peak_algorithm

    def run_mp(self, unknown_peaks, known_compound):
        t_start = time.time()
        print("进程{}启动".format(os.getpid()))

        if self.peak_algorithm =="shining":
            peaks = peak_processing.search_peaks(known_compound["x"], known_compound["y"], height=self.height,
                                                 distance=self.distance)
            known_compound_peaks = []
            for i in peaks:
                known_compound_peaks.append(i[0])

        elif self.peak_algorithm =="noodles":

            known_compound_peaks = self.compound_report(known_compound, schema='know')[0]


        #known_compound_peaks = self.compound_report(known_compound, schema='know')[0]

        assignment_matrix = self.compare_unknown_to_known(unknown_peaks, known_compound_peaks, self.precision)

        result_dic = {"known_compound_peaks": known_compound_peaks, "assignment_matrix": assignment_matrix}
        #known_compound_peaks.append(self.compound_report(known_compound))

        #assignment_matrix.append(self.compare_unknown_to_known(unknown_peaks, known_compound, self.precision))

        t_stop = time.time()
        print("进程{}结束，耗时{}".format(os.getpid(), t_stop - t_start))

        return result_dic


    def peak_assignment(self, unknow_compound, known_compound_list, processes_max=7):


        t_start = time.time()
        print("开始寻找未知物峰值。")
        if self.peak_algorithm =="shining":
            peaks = peak_processing.search_peaks(unknow_compound["x"], unknow_compound["y"], height=self.height,
                                                 distance=self.distance)
            unkonw_peak_center = []
            for i in peaks:
                unkonw_peak_center.append(i[0])

        elif self.peak_algorithm =="noodles":

            unkonw_peak_center = self.compound_report(unknow_compound, schema='unknow')[0]

        t_stop = time.time()
        print("未知物寻峰结束，耗时{}".format(t_stop - t_start))

        if len(known_compound_list) > processes_max:
            processes = len(known_compound_list)
        else:
            processes = processes_max
        manager = Manager()


        #known_compound_peaks = manager.list()

        #assignment_matrix = manager.list()
        datalist = []
        po = Pool(processes)
        print("建立进程池")

        for known_compound in known_compound_list:

            datalist.append(po.apply_async(self.run_mp, (unkonw_peak_center, known_compound)))

        po.close()
        po.join()

        print("进程池计算完毕，开始比对")
        print("datalist:{},known_compound_list:{}".format(len(datalist), len(known_compound_list)))

        known_compound_peaks = []

        assignment_matrix = []
        for data_ele_pool in datalist:
            data_ele = data_ele_pool.get()
            known_compound_peaks.append(data_ele["known_compound_peaks"])
            assignment_matrix.append(data_ele["assignment_matrix"])


        unknown_peak_assignments = self.peak_position_comparisons(unkonw_peak_center,
                                                             known_compound_peaks,
                                                             known_compound_list,
                                                             assignment_matrix)

        percentages = self.percentage_of_peaks_found(known_compound_peaks,
                                                assignment_matrix,
                                                known_compound_list)

        return unkonw_peak_center, unknown_peak_assignments, percentages

    def percentage_of_peaks_found(self, known_peaks, association_matrix, list_of_known_compounds):
        """This function takes in a list of classified peaks, and returns a percentage of
        how many of the material's peaks are found in the unknown spectrum.
        This can be used as a metric of confidence."""

        # Handle bad inputs
        if not isinstance(known_peaks, list):
            raise TypeError("""Passed value of `known_peaks` is not a list!
            Instead, it is: """ + str(type(known_peaks)))

        if not isinstance(list_of_known_compounds, list):
            raise TypeError("""Passed value of `list_of_known_compounds` is not a list!
            Instead, it is: """ + str(type(list_of_known_compounds)))

        # Now we need to check the elements within the
        # list_of_known_compounds to make sure they are correct.
        for i, _ in enumerate(list_of_known_compounds):
            if not isinstance(list_of_known_compounds[i], dict):
                raise TypeError("""Passed value within `list_of_known_compounds` is not a dictionary!
                Instead, it is: """ + str(type(list_of_known_compounds[i])))

        if not isinstance(association_matrix, list):
            raise TypeError("""Passed value of `association_matrix` is not a float or int!
            Instead, it is: """ + str(type(association_matrix)))

        percentage_dict = {}
        for i, _ in enumerate(list_of_known_compounds):
            count_number = sum(association_matrix[i])
            percentage_dict[list_of_known_compounds[i]
            ['title']] = (count_number / len(known_peaks[i])) * 100

        return percentage_dict

    def peak_position_comparisons(self,unknown_peaks, known_compound_peaks,
                                  known_compound_list,
                                  association_matrix):
        """This function takes in an association matrix and turns the numbers
        given by said matrix into a text label."""

        # Handling errors in inputs.
        if not isinstance(unknown_peaks, list):
            raise TypeError("""Passed value of `unknown_peaks` is not a list!
            Instead, it is: """ + str(type(unknown_peaks)))

        if not isinstance(known_compound_peaks, list):
            raise TypeError("""Passed value of `known_compound_peaks` is not a list!
            Instead, it is: """ + str(type(known_compound_peaks)))

        if not isinstance(known_compound_list, list):
            raise TypeError("""Passed value of `known_compound_list` is not a list!
            Instead, it is: """ + str(type(known_compound_list)))

        # Now we need to check the elements within the known_compound_list to make sure they are correct.
        for i, _ in enumerate(known_compound_list):
            if not isinstance(known_compound_list[i], dict):
                raise TypeError("""Passed value within `known_compound_list` is not a dictionary!
                Instead, it is: """ + str(type(known_compound_list[i])))

        if not isinstance(association_matrix, list):
            raise TypeError("""Passed value of `association_matrix` is not a float or int!
            Instead, it is: """ + str(type(association_matrix)))

        unknown_peak_assignment = []
        # Step through the unknown peaks to make an assignment for each unknown peak.

        for i, _ in enumerate(unknown_peaks):
            # We might be able to make a small performance improvement if we were to somehow
            # not search the peaks we already had searched, but that seems to not be trivial.
            position_assignment = []
            # We'll need an outer loop that walks through all the different compound positions
            for j, _ in enumerate(known_compound_peaks):
                if association_matrix[j][i] == 1:
                    position_assignment.append(known_compound_list[j]['title'])
                else:
                    pass
            if position_assignment == []:
                position_assignment.append("Unassigned")
            unknown_peak_assignment.append(position_assignment)

        return unknown_peak_assignment

    def compare_unknown_to_known(self, combined_peaks, known_peaks, precision):
        """This function takes in peak positions for the spectrum to be
        analyzed and a single known compound and determines if the peaks
        found in the known compound are present in the unknown spectrum."""

        # Handling errors in inputs.
        if not isinstance(combined_peaks, list):
            raise TypeError("""Passed value of `combined_peaks` is not a list!
            Instead, it is: """ + str(type(combined_peaks)))

        if not isinstance(known_peaks, list):
            raise TypeError("""Passed value of `known_peaks` is not a list!
            Instead, it is: """ + str(type(known_peaks)))

        if not isinstance(precision, (float, int)):
            raise TypeError("""Passed value of `precision` is not a float or int!
            Instead, it is: """ + str(type(precision)))

        assignment_matrix = np.zeros(len(combined_peaks))
        peaks_found = 0
        for i, _ in enumerate(combined_peaks):
            for j, _ in enumerate(known_peaks):
                # instead of If, call peak_1D_score
                if math.isclose(combined_peaks[i], known_peaks[j],
                                rel_tol=precision):
                    # Instead of using a 1, just input the score
                    # from the score calculator.
                    # Bigger is better.
                    # Storing only the second component in the list.
                    assignment_matrix[i] = 1
                    peaks_found += 1
                    continue
                else:
                    pass
            if peaks_found == len(known_peaks):
                continue
            else:
                pass
        return assignment_matrix

    def compound_report(self, compound, schema='know'):
        """
        Wrapper fucntion that utilizes many of the functions
        within spectrafit to give the peak information of a compound
        in shoyu_data_dict.p

        Args:
            compound (dict): a single NIST compound dictionary from shoyu_data_dict.

        Returns:
            peak_centers (list): A list with a peak center value for each peak.
            peak_sigma (list): A list with a sigma value for each peak.
            peak_ampl (list): A list with amplitudes for each peak.
            xmin (float): The minimum wavenumber value in the compound data
            xmax (float): The maximum wavenumber value in the compound data
        """
        # handling errors in inputs
        if not isinstance(compound, dict):
            raise TypeError('Passed value of `compound` is not a dict! Instead, it is: '
                            + str(type(compound)))

        x_data = compound['x']
        y_data = compound['y']
        # subtract baseline
        # y_data = subtract_baseline(y_data)
        # detect peaks
        peaks = self.peak_detect(x_data, y_data, schema=schema)[0]  # prominence = y_data.mean()

        # assign parameters for least squares fit
        mod, pars = self.set_params(peaks)
        # fit the model to the data

        out = self.model_fit(x_data, y_data, mod, pars)

        # export data in logical structure (see docstring)
        fit_peak_data = self.export_fit_data(out)
        # peak_fraction = []
        peak_center = []
        peak_sigma = []
        peak_ampl = []
        # peak_height = []
        for i, _ in enumerate(fit_peak_data):
            # peak_fraction.append(fit_peak_data[i][0])
            # if we ever need lorentzian fraction we can add it
            # right now it may break other functions
            peak_sigma.append(fit_peak_data[i][1])
            peak_center.append(fit_peak_data[i][2])
            peak_ampl.append(fit_peak_data[i][3])
            # peak_height.append(fit_peak_data[i][5])
        xmin = min(x_data)
        xmax = max(x_data)
        return peak_center, peak_sigma, peak_ampl, xmin, xmax

    def peak_detect(self, x_data, y_data, schema='know'):
        """
        利用scipy从输入光谱数据中找到最大值的函数。默认的检测参数是根据在测试期间运行良好的值为用户选择的功能的初始测试;
        但是，仍然可以选择调整参数要达到最好的契合，如果用户选择的话。
        警告:此函数可能返回意外结果或不可靠的数据结果包含nan。在传递数据之前，请删除所有NaN值。

        Args:
            x_data (list like): The x-values of the spectra from which peaks will be detected.
            y_data (list like): The y-values of the spectra from which peaks will be detected.
            height (float): (Optional) The minimum floor of peak-height below which all peaks
                            will be ignored. Any peak that is detected that has a maximum height
                            less than `height` will not be collected. NOTE: This value is highly
                            sensitive to baselining, so the Raman-noodles team recommends ensuring
                            a quality baseline before use.
            prominence (float): (Optional) The prominence of the peak. In short, it's a comparison
                                of the height of a peak relative to adjacent peaks that considers
                                both the height of the adjacent peaks, as well as their distance
                                from the peak being considered. More details can be found in the
                                `peak_prominences` module from scipy.
            distance (float): (Optional) The minimum distance between adjacent peaks.

        Returns:
            peaks (list): A list of the x and y-values (in a tuple) where peaks were detected.
            peak_list (list): An list of the indices of the fed-in data that correspond to the
                              detected peaks as well as other attributes such as the prominence
                              and height.
                              :param x_data:
                              :param y_data:
                              :param schema:
        """

        # find peaks
        if schema == 'unknow':
            if self.prominence_unknow == 'auto':

                peak_list = find_peaks(y_data, height=self.height, prominence=y_data.mean(), distance=self.distance)
            else:
                peak_list = find_peaks(y_data, height=self.height, prominence=self.prominence_unknow,
                                       distance=self.distance)
        elif schema == 'know':
            if self.prominence_know == 'auto':
                peak_list = find_peaks(y_data, height=self.height, prominence=y_data.mean(), distance=self.distance)
            else:
                peak_list = find_peaks(y_data, height=self.height, prominence=self.prominence_know,
                                       distance=self.distance)

        # convert peak indexes to data values
        peaks = []
        for i in peak_list[0]:
            peak = (x_data[i], y_data[i])
            peaks.append(peak)
        return peaks, peak_list

    def set_params(self, peaks):
        """
        This module takes in the list of peaks from the peak detection modules, and then uses
        that to initialize parameters for a set of Pseudo-Voigt models that are not yet fit.
        There is a single model for every peak.

        Args:
            peaks (list): A list containing the x and y-values (in tuples) of the peaks.

        Returns:
            mod (lmfit.models.PseudoVoigtModel or lmfit.model.CompositeModel): This is an array of
                            the initialized Pseudo-Voigt models. The array contains all of the values
                            that are found in `pars` that are fed to an lmfit lorentzian model class.
            pars (lmfit.parameter.Parameters): An array containing the parameters for each peak
                            that were generated through the use of a Lorentzian fit. The pars
                            array contains a center value, a height, a sigma, and an amplitude
                            value. The center value is allowed to vary +- 10 wavenumber from
                            the peak max that was detected in scipy. Some wiggle room was allowed
                            to help mitigate problems from slight issues in the peakdetect
                            algorithm for peaks that might have relatively flat maxima. The height
                            value was allowed to vary between 0 and 1, as it is assumed the y-values
                            are normalized. Sigma is set to a maximum of 500, as we found that
                            giving it an unbound maximum led to a number of peaks that were
                            unrealistic for Raman spectra (ie, they were far too broad, and shallow,
                            to correspond to real data. Finally, the amplitude for the peak was set
                            to a minimum of 0, to prevent negatives.
        """
        # handling errors in inputs
        if not isinstance(peaks, list):
            raise TypeError('Passed value of `peaks` is not a list! Instead, it is: '
                            + str(type(peaks)))
        for i, _ in enumerate(peaks):
            if not isinstance(peaks[i], tuple):
                raise TypeError("""Passed value of `peaks[{}]` is not a tuple.
                 Instead, it is: """.format(i) + str(type(peaks[i])))
        peak_list = []
        for i, _ in enumerate(peaks):
            prefix = 'p{}_'.format(i + 1)
            peak = PseudoVoigtModel(prefix=prefix)
            if i == 0:
                pars = peak.make_params()
            else:
                pars.update(peak.make_params())
            pars[prefix + 'center'].set(peaks[i][0], vary=False)
            pars[prefix + 'height'].set(peaks[i][1], vary=False)
            pars[prefix + 'sigma'].set(50, min=0, max=500)
            pars[prefix + 'amplitude'].set(min=0)
            peak_list.append(peak)
            if i == 0:
                mod = peak_list[i]
            else:
                mod = mod + peak_list[i]
        return mod, pars

    def model_fit(self, x_data, y_data, mod, pars):
        """
        This function takes in the x and y data for the spectrum being analyzed, as well as the model
        parameters that were generated in `lorentz_params` for a single peak, and uses it to generate
        a fit for the model at that one single peak position, then returns that fit.

        Args:
            x_data (list like): The x-values for the spectrum that is being fit.
            y_data (list like): The y-values for the spectrum that is being fit.
            mod (lmfit.model.CompositeModel): This is an array of the initialized Lorentzian models
                            from the `lorentz_params` function. This array contains all of the values
                            that are found in pars, that are fed to an lmfit Lorentzian model class.
            pars (lmfit.parameter.Parameters): An array containing the parameters for each peak that
                            were generated through the use of a Lorentzian fit. The pars array contains
                            a center value, a height, a sigma, and an amplitude value. The center value
                            is allowed to vary +- 10 wavenumber from the peak max that was detected in
                            scipy. Some wiggle room was allowed to help mitigate problems from slight
                            issues in the peakdetect algorithm for peaks that might have relatively
                            flat maxima. The height value was allowed to vary between 0 and 1, as it is
                            assumed the y-values are normalized. Sigma is set to a maximum of 500, as we
                            found that giving it an unbound maximum led to a number of peaks that were
                            unrealistic for Raman spectra (ie, they were far too broad, and shallow, to
                            correspond to real data. Finally, the amplitude for the peak was set to a
                            minimum of 0, to prevent negatives.
            report (boolean): (Optional) This value details whether or not the users wants to receive
                            a report of the fit values. If True, the function will print a report of
                            the fit.
        Returns:
            out (lmfit.model.ModelResult): An lmfit model class that contains all of the fitted values
                            for the input model.
        """
        # handling errors in inputs
        if not isinstance(x_data, (list, np.ndarray)):
            raise TypeError('Passed value of `x_data` is not a list or numpy.ndarray! Instead, it is: '
                            + str(type(x_data)))
        if not isinstance(y_data, (list, np.ndarray)):
            raise TypeError('Passed value of `y_data` is not a list or numpy.ndarray! Instead, it is: '
                            + str(type(y_data)))
        if not isinstance(mod, (lmfit.models.PseudoVoigtModel, lmfit.model.CompositeModel)):
            raise TypeError("""Passed value of `mod` is not a lmfit.models.PseudoVoigtModel or a 
            lmfit.model.CompositeModel! Instead, it is: """ + str(type(mod)))
        if not isinstance(pars, lmfit.parameter.Parameters):
            raise TypeError("""Passed value of `pars` is not a lmfit.parameter.Parameters!
             Instead, it is: """ + str(type(pars)))

        # fit model
        out = mod.fit(y_data, pars, x=x_data)

        return out

    def export_fit_data(self, out):
        """
        This function returns fit information for an input lmfit model set.

        Args:
            out (lmfit.model.ModelResult): An lmfit model class that contains all of the
                            fitted values for the input model class.

        Returns:
            fit_peak_data (numpy array): An array containing both the peak number, as well as the
                            fraction Lorentzian character, sigma, center, amplitude, full-width,
                            half-max, and the height of the peaks. The data can be accessed by the
                            array positions shown here:
                                fit_peak_data[i][0] = p[i]_fraction
                                fit_peak_data[i][1] = p[i]_simga
                                fit_peak_data[i][2] = p[i]_center
                                fit_peak_data[i][3] = p[i]_amplitude
                                fit_peak_data[i][4] = p[i]_fwhm
                                fit_peak_data[i][5] = p[i]_height
        """
        # handling errors in inputs
        if not isinstance(out, lmfit.model.ModelResult):
            raise TypeError('Passed value of `out` is not a lmfit.model.ModelResult! Instead, it is: '
                            + str(type(out)))
        fit_peak_data = []
        for i in range(int(len(out.values) / 6)):
            peak = np.zeros(6)
            prefix = 'p{}_'.format(i + 1)
            peak[0] = out.values[prefix + 'fraction']
            peak[1] = out.values[prefix + 'sigma']
            peak[2] = out.values[prefix + 'center']
            peak[3] = out.values[prefix + 'amplitude']
            peak[4] = out.values[prefix + 'fwhm']
            peak[5] = out.values[prefix + 'height']
            fit_peak_data.append(peak)
        return fit_peak_data
