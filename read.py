"""
Description: Read initial dataset and decode it into a list. Here we replace all missing value and discretizate
    the numerical values.
Input: initial dataset stored in *.data file, and scheme description stored in *.names file.
Output: a data list after pre-processing.
Author: CBA Studio
"""
import csv


# Read dataset and convert into a list.
# path: directory of *.data file.
def read_data(path):
    data = []
    with open(path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        for line in reader:
            data.append(line)
        while [] in data:
            data.remove([])
    return data


# Read scheme file *.names and write down attributes and value types.
# path: directory of *.names file.
def read_scheme(path):
    with open(path, 'r') as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        attributes = next(reader)
        value_type = next(reader)
    return attributes, value_type


# convert string-type value into float-type.
# data: data list returned by read_data.
# value_type: list returned by read_scheme.
def str2numerical(data, value_type):
    size = len(data)
    columns = len(data[0])
    for i in range(size):
        for j in range(columns-1):
            if value_type[j] == 'numerical' and data[i][j] != '?':
                data[i][j] = float(data[i][j])
    return data


# Main method in this file, to get data list after processing and scheme list.
# data_path: tell where *.data file stores.
# scheme_path: tell where *.names file stores.
def read(data_path, scheme_path):
    data = read_data(data_path)
    attributes, value_type = read_scheme(scheme_path)
    data = str2numerical(data, value_type)
    return data, attributes, value_type


# just for test
if __name__ == '__main__':
    import pre_processing

    test_data_path = '/Users/liulizhi/Desktop/iris.data'
    test_scheme_path = '/Users/liulizhi/Desktop/iris.names'
    test_data, test_attributes, test_value_type = read(test_data_path, test_scheme_path)
    result_data = pre_processing.pre_process(test_data, test_attributes, test_value_type)
    print(result_data)
