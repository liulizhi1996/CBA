"""
Description: Recursive minimal entropy partitioning, to discretize continuous-valued attributes. We use the supervised
    algorithm presented in Fayyad & Irani (1993) and introduced in Dougherty, Kohavi & Sahami (1995) section 3.3.
    We also refer to a F# code on GitHub (https://gist.github.com/mathias-brandewinder/5650553).
Input: a data table with several rows but only two column, the first column is continuous-valued (numerical) attributes,
    and the second column is the class label of each data case (categorical).
    e.g. data = [[1.0, 'Yes'], [0.5, 'No'], [2.0, 'Yes']]
Output: a list of partition boundaries of the range of continuous-valued attribute in ascending sort order.
    e.g. walls = [0.5, 0.8, 1.0], thus we can separate the range into 4 intervals: <=0.5, 0.5<*<=0.8, 0.8<*<=1.0 & >=1.0
Author: CBA Studio
Reference:
    1. Multi-Interval Discretization of Continuous-Valued Attributes for Classification Learning, Fayyad & Irani, 1993
    2. Supervised and Unsupervised Discretization of Continuous Features, Dougherty, Kohavi & Sahami, 1995
    3. http://www.clear-lines.com/blog/post/Discretizing-a-continuous-variable-using-Entropy.aspx
"""
import math


# A block to be split
# It has 4 member:
#   data: the data table with a column of continuous-valued attribute and a column of class label
#   size: number of data case in this table
#   number_of_classes: obviously, the number of class in this table
#   entropy: entropy of dataset
class Block:
    def __init__(self, data):
        self.data = data
        self.size = len(data)
        classes = set([x[1] for x in data])     # get distinct class labels in this table
        self.number_of_classes = len(set(classes))
        self.entropy = calculate_entropy(data)


# Calculate the entropy of dataset
# parameter data: the data table to be used
def calculate_entropy(data):
    number_of_data = len(data)
    classes = set([x[1] for x in data])
    class_count = dict([(label, 0) for label in classes])
    for data_case in data:
        class_count[data_case[1]] += 1      # count the number of data case of each class
    entropy = 0
    for c in classes:
        p = class_count[c] / number_of_data
        entropy -= p * math.log2(p)         # calculate information entropy by its formula, where the base is 2
    return entropy


# Compute Gain(A, T: S) mentioned in Dougherty, Kohavi & Sahami (1995), i.e. entropy gained by splitting original_block
#   into left_block and right_block
# original_block: the block before partition
# left_block: the block split which its value below boundary
# right_block: the block above boundary
def entropy_gain(original_block, left_block, right_block):
    gain = original_block.entropy - \
            ((left_block.size / original_block.size) * left_block.entropy +
            (right_block.size / original_block.size) * right_block.entropy)
    return gain


# Get minimum entropy gain required for a split of original_block into 2 blocks "left" and "right", see Dougherty,
#   Kohavi & Sahami (1995)
# original_block: the block before partition
# left_block: the block split which its value below boundary
# right_block: the block above boundary
def min_gain(original_block, left_block, right_block):
    delta = math.log2(math.pow(3, original_block.number_of_classes) - 2) - \
            (original_block.number_of_classes * original_block.entropy -
             left_block.number_of_classes * left_block.entropy -
             right_block.number_of_classes * right_block.entropy)
    gain_sup = math.log2(original_block.size - 1) / original_block.size + delta / original_block.size
    return gain_sup


# Identify the best acceptable value to split block
# block: a block of dataset
# Return value: a list of (boundary, entropy gain, left block, right block) or
#   None when it's unnecessary to split
def split(block):
    candidates = [x[0] for x in block.data]     # candidates is a list of values can be picked up as boundary
    candidates = list(set(candidates))          # get different values in table
    candidates.sort()                           # sort ascending
    candidates = candidates[1:]                 # discard smallest, because by definition no value is smaller

    wall = []       # wall is a list storing final boundary
    for value in candidates:
        # split by value into 2 groups, below & above
        left_data = []
        right_data = []
        for data_case in block.data:
            if data_case[0] < value:
                left_data.append(data_case)
            else:
                right_data.append(data_case)

        left_block = Block(left_data)
        right_block = Block(right_data)

        gain = entropy_gain(block, left_block, right_block)
        threshold = min_gain(block, left_block, right_block)

        # minimum threshold is met, the value is an acceptable candidate
        if gain >= threshold:
            wall.append([value, gain, left_block, right_block])

    if wall:    # has candidate
        wall.sort(key=lambda wall: wall[1], reverse=True)   # sort descending by "gain"
        return wall[0]      # return best candidate with max entropy gain
    else:
        return None         # no need to split


# Top-down recursive partition of a data block, append boundary into "walls"
# block: a data block
def partition(block):
    walls = []

    # inner recursive function, accumulate the partitioning values
    # sub_block: just a data block
    def recursive_split(sub_block):
        wall_returned = split(sub_block)        # binary partition, get bin boundary
        if wall_returned:                       # still can be spilt
            walls.append(wall_returned[0])      # record this partitioning value
            recursive_split(wall_returned[2])   # recursively process left block
            recursive_split(wall_returned[3])   # recursively split right block
        else:
            return                              # end of recursion

    recursive_split(block)      # call inner function
    walls.sort()                # sort boundaries descending
    return walls


# just for test
if __name__ == '__main__':
    import random

    test_data = []
    for i in range(100):
        test_data.append([random.random(), random.choice(range(0, 2))])
        test_data.append([random.random() + 1, random.choice(range(2, 4))])
        test_data.append([random.random() + 2, random.choice(range(4, 6))])
        test_data.append([random.random() + 3, random.choice(range(6, 8))])

    test_block = Block(test_data)
    test_walls = partition(test_block)
    print(test_walls)        # should be [1+e, 2+e, 3+e], where e is a number very close to 0
