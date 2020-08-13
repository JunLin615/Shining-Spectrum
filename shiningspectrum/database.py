# -*- coding: utf-8 -*-
"""
@Time:2020/8/14 1:35
@Auth"JunLin615
@File:database.py
@IDE:PyCharm
@Motto:With the wind light cloud light mentality, do insatiable things
@email:ljjjun123@gmail.com 
"""
import os
import pickle
import re


# 拉曼数据库:raman_database
def read_file(data_path, file_name):
    """
    读取指定文件(只限于txt)
    Read the specified file (txt only)
    :param data_path: 要读取的文件路径，请使用\\而非/或者\。File path to read，Please use \ \ instead of / or\。
    :param file_name:要读取的文件名，带扩展名。The name of the file to read with the extension
    :return:返回读取文件的内容。Returns the contents of the read file.
    """
    # 读取指定文件(只限于txt)
    file = open(data_path + '\\' + file_name, 'r')
    file_data = file.readlines()
    file.close()
    return file_data


def read_file_p(file_name, database_name):
    """
    读取数据库中的.p格式光谱数据文件.
    Read the. P format spectral data file in the database
    :param file_name:要读取的文件名，不带扩展名.The name of the file to read without an extension
    :param database_name:
    :return:
    """
    # 读取数据库中的.p格式光谱数据文件
    path = os.getcwd()
    database_path = path + '\\database_folder\\' + database_name
    data_list = pickle.load(open(database_path + '\\' + file_name + '.p', 'rb'))
    return data_list


def data_extraction(data_list):
    """
    此函数为内联函数，不建议使用！！！
    This function is inline function, not recommended to use!!!

    将.p格式光谱文件对应的列表中提取出光谱数据
    Extract spectral data from the list corresponding to the. P format spectral file

    :param data_list:
    :return:
    """
    # 将.p格式光谱文件对应的列表中提取出光谱数据
    list_x = []
    list_y = []
    for row in data_list[11:-1]:
        row = row.replace('\n', '')
        element = row.split('\t')
        list_x.append(float(element[0]))
        list_y.append(float(element[1]))

    list_spectrum = [list_x, list_y]

    return list_spectrum


def read_data(file_name, database_name):
    """
    从数据库中的.p光谱文件读取数据
    Read data from the. P spectrum file in the database

    如果还未初始化数据库，以及为数据库导入数据，请使用initialization和import_data函数。
    Use the initialization and import_data function if the database has not been initialized and if you are importing data for the database.

    :param file_name: 要读取的文件名，不带扩展名.The name of the file to read without an extension
    :param database_name: 已经建立好的数据库名称。The name of the established database。
    :return:
    """
    # 从数据库中的.p光谱文件读取数据
    data_list = read_file_p(file_name, database_name)
    list_spectrum = data_extraction(data_list)
    return list_spectrum

def existing_database():
    """
    查看已有数据库
    View existing database
    """
    path = os.getcwd()
    database_path = path + '\\database_folder'
    batabase_list = os.listdir(database_path)
    print('已有数据库:\nExisting database：\n{}'.format(batabase_list))


def view_database(database_name, query_criteria='Indexes'):
    """
    查看指定数据库信息
    View specified database information
    :param database_name: 数据库名称。Database name.
    :param query_criteria: 查询条件，'Indexes'查询此数据库包含什么物质。'survey'查询数据库中的数据概括。
                            Query_criteria，'indexes' queries what substances are contained in this database,Summary of
                            data in 'survey' query database
    :return:NONE
    """

    # 查看数据库信息
    path = os.getcwd()
    database_path = path + '\\database_folder\\' + database_name

    database_dictionary = pickle.load(open(database_path + '\\' + 'database_index_file.p', 'rb'))

    documents_owned_list = list(database_dictionary.keys())

    if query_criteria == 'Indexes':
        print('数据库中含有以下物质:\nThe database contains the following substances:\n{}'.format(documents_owned_list))

    elif query_criteria == 'survey':

        print('数据库中含有以下物质:\nThe database contains the following substances:\n{}'.format(documents_owned_list))
        print('\n数据概述:Data overview:\n{}'.format(database_dictionary))


def existence_or_not(file_list, database_name):

    """
    检测file_list中的物质是否存在于数据库中，返回不存在的物质列表
    Check file_ If the substances in the list exist in the database, the list of non-existent substances is returned

    :param file_list: 由CAS号构成的列表.List of CAS numbers.eg:['64-17-5', '67-66-3', '108-90-7', '108-88-3', '108-95-2']
    :param database_name:数据库名称。Database name
    :return:数据库中没有的物质列表.List of substances not in the database.
    """
    # 检测file_list中的物质是否存在于数据库中，返回不存在的物质列表
    path = os.getcwd()
    database_path = path + '\\database_folder\\' + database_name

    database_dictionary = pickle.load(open(database_path + '\\' + 'database_index_file.p', 'rb'))

    documents_owned_list = list(database_dictionary.keys())
    non_existent_list = []
    for file_name in file_list:
        if file_name in documents_owned_list:
            continue
        else:
            non_existent_list.append(file_name)

    return non_existent_list


def read_custom(file_list, database_name):
    """
    按给定的物质列表读取光谱数据
    Read the spectral data according to the given substance list
    :param file_list:由CAS号构成的列表.List of CAS numbers.eg:['64-17-5', '67-66-3', '108-90-7', '108-88-3', '108-95-2']
    :param database_name:数据库名称。Database name
    :return:
    """
    # 按给定的物质列表读取
    non_existent_list = existence_or_not(file_list, database_name)

    if non_existent_list != []:
        raise TypeError('以下物质不存在,请剔除后重试(The following substances do not exist, please remove and try again):{}'.format(
            non_existent_list))

    all_spectrum = {}
    for file_name in file_list:
        list_spectrum = read_data(file_name, database_name)
        all_spectrum.update({file_name: list_spectrum})

    return all_spectrum


def read_all(database_name):
    """
    将指定数据库的全部光谱数据加载到内存。
    Load all spectral data of the specified database into memory.
    :param database_name:数据库名称。Database name
    :return:一个以物质CSA号为键，以光谱数据为值的字典。A dictionary with CSA number as key and spectral data as value.
    """
    # 将整个数据库的光谱数据读取出来

    path = os.getcwd()
    database_path = path + '\\database_folder\\' + database_name

    database_dictionary = pickle.load(open(database_path + '\\' + 'database_index_file.p', 'rb'))

    documents_owned_list = list(database_dictionary.keys())

    all_spectrum = read_custom(documents_owned_list, database_name)

    return all_spectrum


def verification(file_name, data_type, file_data):
    """
    内联函数，不建议调用!!!
    Inline function, not recommended!!!

    数据格式可以参考“标准格式”文件夹
    The data format can refer to the "standard format" folder

    用于检测导入数据是否符合格式要求.
    Used to detect whether the imported data meets the format requirements

    :param file_name:
    :param data_type:
    :param file_data:
    :return:
    """
    # 检测输入数据格式。
    # Input data format detection
    # print(file_data[0] + file_data[10] + file_data[-1])
    print('数据格式可以参考“标准格式”文件夹.The data format can refer to the "标准格式" folder')
    if file_data[0] != '#shining_header\n' or file_data[10] != '#shining_data\n' or file_data[-1] != '#shining_end':
        raise TypeError(
            '{}数据格式错误，请参考标准格式修改导入数据格式。\nData in file {} format error, please refer to the standard format to modify '
            'the imported data format.'.format(
                file_name, file_name))

    input_data_type = re.findall(".*type:(.*)\n.*", file_data[1])

    # 检测数据类型与所选数据库是否对应
    # Detects whether the data type corresponds to the selected database
    if input_data_type[0] != data_type:
        raise TypeError(
            '您导入的文件{}是{}，不是{},请选择正确的光谱数据，或重新选择数据库。\nThe file {} you imported is {}, not {}, please select the correct '
            'spectral data.Or reselect the database.'.format(
                file_name, input_data_type[0], data_type, file_name, input_data_type[0], data_type))


def initialization(database_name='raman_database'):
    """
    这个函数非常重要，请在首次使用shiningspectrum前运行此函数。此函数可以为你建立一个数据库，并建立索引文件。
    This function is very important, please run it before using shiningspectrum for the first time.
    This function can create a database for you, and create index files.

    数据库初始化函数。
    Database initialization function.

    :param database_name:为你的数据库指定一个名称。Give your database a name.
    :return:
    """
    path = os.getcwd()
    database_path = path + '\\database_folder\\' + database_name
    if os.path.exists(database_name):
        print('路径已存在。Path already exists.')
    else:
        os.makedirs(database_path)
        print('创建路径成功。Path created successfully.')

    index_file_path = database_path + '\\database_index_file' + '.p'

    if os.path.exists(index_file_path):
        print('索引文件已存在。Index file already exists')

    else:
        database_index_dic = {}
        pickle.dump(database_index_dic, open(index_file_path, 'wb'))

        print('索引文件创建成功。Index file created successfully.')


def import_data(data_path, database_name='raman_database'):
    """
    为你的数据库导入数据。
    Import data for your database.

    shiningspectrum有自己的数据包装格式，主要由一个表头和一个结尾构成，具体的可以在GitHub上查看shiningspectrum的example文件。
    Shiningspectrum has its own data packaging format, which is mainly composed of a header and an end.
    Specifically, you can view the shiningspectrum example file on GitHub.

    GitHub:https://github.com/JunLin615/Shining-Spectrum.git

    :param data_path:您要导入数据库的数据所在的文件夹路径。The folder path where the data you want to import into the database is located
    :param database_name:要导入数据的数据库名称.The name of the database to import the data.
    :return:
    """
    path = os.getcwd()
    database_path = path + '\\database_folder\\' + database_name

    database_dictionary = pickle.load(open(database_path + '\\' + 'database_index_file.p', 'rb'))

    documents_owned_list = list(database_dictionary.keys())

    file_list = os.listdir(data_path)

    print(file_list)

    for file_name in file_list:

        file_data = read_file(data_path, file_name)

        verification(file_name, database_name, file_data)
        export_name = re.findall(".*:(.*)\n.*", file_data[2])[0]

        if export_name in documents_owned_list:
            print(file_name + 'already exists.')
            continue

        database_dictionary.update({export_name: file_data[1:10]})

        pickle.dump(file_data, open(database_path + '\\' + export_name + '.p', 'wb'))

        print(file_name + 'successfully entered')

    pickle.dump(database_dictionary, open(database_path + '\\' + 'database_index_file.p', 'wb'))

    return database_dictionary




