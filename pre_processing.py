"""
Description: Pre-process original data. Firstly, we process the missing values (donated as '?'), discarding this column
    when missing ratio above 50%, or filling blanks when below. We "guess" missing values by simply filling the mode of
    existing values in the same column. And then, for the numerical attribute, we discretizate it by recursive minimal
    entropy partitioning (see rmep.py). For the categorical attribute, we just replace the label with a
    positive integer. For more information, see [1].
Input: a data table with several data case, many attributes and class label in the last column, a list of the name of
    each attribute, and a list of the type of each column.
Output: a data list without numerical values and "str" categorical values.
Author: CBA Studio
Reference:
    1. http://cgi.csc.liv.ac.uk/~frans/KDD/Software/LUCS-KDD-DN/lucs-kdd_DN.html
"""
import rmep


# Identify the mode of a list, both effective for numerical and categorical list. When there exists too many modes
#   having the same frequency, return the first one.
# arr: a list need to find mode
def get_mode(arr):
    mode = []
    arr_appear = dict((a, arr.count(a)) for a in arr)   # count appearance times of each key
    if max(arr_appear.values()) == 1:       # if max time is 1
        return      # no mode here
    else:
        for k, v in arr_appear.items():     # else, mode is the number which has max time
            if v == max(arr_appear.values()):
                mode.append(k)
    return mode[0]  # return first number if has many modes


# Fill missing values in column column_no, when missing values ration below 50%.
# data: original data list
# column_no: identify the column No. of that to be filled
def fill_missing_values(data, column_no):
    size = len(data)
    column_data = [x[column_no] for x in data]      # get that column
    while '?' in column_data:
        column_data.remove('?')
    mode = get_mode(column_data)
    for i in range(size):
        if data[i][column_no] == '?':
            data[i][column_no] = mode              # fill in mode
    return data


# Get the list needed by rmep.py, just glue the data column with class column.
# data_column: the data column
# class_column: the class label column
def get_discretization_data(data_column, class_column):
    size = len(data_column)
    result_list = []
    for i in range(size):
        result_list.append([data_column[i], class_column[i]])
    return result_list


# Replace numerical data with the No. of interval, i.e. consecutive positive integers.
# data: original data table
# column_no: the column No. of that column
# walls: the split point of the whole range
def replace_numerical(data, column_no, walls):
    size = len(data)
    num_spilt_point = len(walls)
    for i in range(size):
        if data[i][column_no] > walls[num_spilt_point - 1]:
            data[i][column_no] = num_spilt_point + 1
            continue
        for j in range(0, num_spilt_point):
            if data[i][column_no] <= walls[j]:
                data[i][column_no] = j + 1
                break
    return data


# Replace categorical values with a positive integer.
# data: original data table
# column_no: identify which column to be processed
def replace_categorical(data, column_no):
    size = len(data)
    classes = set([x[column_no] for x in data])
    classes_no = dict([(label, 0) for label in classes])
    j = 1
    for i in classes:
        classes_no[i] = j
        j += 1
    for i in range(size):
        data[i][column_no] = classes_no[data[i][column_no]]
    return data, classes_no


# Discard all the column with its column_no in discard_list
# data: original data set
# discard_list: a list of column No. of the columns to be discarded
def discard(data, discard_list):
    size = len(data)
    length = len(data[0])
    data_result = []
    for i in range(size):
        data_result.append([])
        for j in range(length):
            if j not in discard_list:
                data_result[i].append(data[i][j])
    return data_result


# Main method here, see Description in detail
# data: original data table
# attribute: a list of the name of attribute
# value_type: a list identifying the type of each column
# Returned value: a data table after process
def pre_process(data, attribute, value_type):
    column_num = len(data[0])
    size = len(data)
    class_column = [x[-1] for x in data]
    discard_list = []
    for i in range(0, column_num - 1):
        data_column = [x[i] for x in data]

        # process missing values
        missing_values_ratio = data_column.count('?') / size
        if missing_values_ratio > 0.5:
            discard_list.append(i)
            continue
        elif missing_values_ratio > 0:
            data = fill_missing_values(data, i)
            data_column = [x[i] for x in data]

        # discretization
        if value_type[i] == 'numerical':
            discretization_data = get_discretization_data(data_column, class_column)
            block = rmep.Block(discretization_data)
            walls = rmep.partition(block)
            if len(walls) == 0:
                max_value = max(data_column)
                min_value = min(data_column)
                step = (max_value - min_value) / 3
                walls.append(min_value + step)
                walls.append(min_value + 2 * step)
            print(attribute[i] + ":", walls)        # print out split points
            data = replace_numerical(data, i, walls)
        elif value_type[i] == 'categorical':
            data, classes_no = replace_categorical(data, i)
            print(attribute[i] + ":", classes_no)   # print out replacement list

    # discard
    if len(discard_list) > 0:
        data = discard(data, discard_list)
        print("discard:", discard_list)             # print out discard list
    return data


# just for test
if __name__ == '__main__':
    test_data = [
        ['red', 25.6, 56, 1],
        ['green', 33.3, 1, 1],
        ['green', 2.5, 23, 0],
        ['blue', 67.2, 111, 1],
        ['red', 29.0, 34, 0],
        ['yellow', 99.5, 78, 1],
        ['yellow', 10.2, 23, 1],
        ['yellow', 9.9, 30, 0],
        ['blue', 67.0, 47, 0],
        ['red', 41.8, 99, 1]
    ]
    test_attribute = ['color', 'average', 'age', 'class']
    test_value_type = ['categorical', 'numerical', 'numerical', 'label']
    test_data_after = pre_process(test_data, test_attribute, test_value_type)
    print(test_data_after)
