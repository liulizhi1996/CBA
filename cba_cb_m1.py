"""
Description: The implementation of a naive algorithm for CBA-CB: M1. The class Classifier includes the set of selected
    rules and default_class, which can be expressed as <r1, r2, ..., rn, default_class>. Method classifier_builder_m1
    is the main method to implement CBA-CB: M1.
Input: a set of CARs generated from rule_generator (see cab_rg.py) and a dataset got from pre_process
    (see pre_processing.py)
Output: a classifier
Author: CBA Studio
Reference: http://www.docin.com/p-586554186.html
"""
import cba_rg
from functools import cmp_to_key
import sys


# check the rule whether covers the data case (a line in table with the class label at the end of list) or not
# if covers (LHS of rule is the same as the data case, and they belongs to the same class), return True;
# else if LHSs are the same while the class labels are different, return False;
# else (LHSs are different), return None
def is_satisfy(datacase, rule):
    for item in rule.cond_set:
        if datacase[item] != rule.cond_set[item]:
            return None
    if datacase[-1] == rule.class_label:
        return True
    else:
        return False


class Classifier:
    """
    This class is our classifier. The rule_list and default_class are useful for outer code.
    """
    def __init__(self):
        self.rule_list = list()
        self.default_class = None
        self._error_list = list()
        self._default_class_list = list()

    # insert a rule into rule_list, then choose a default class, and calculate the errors (see line 8, 10 & 11)
    def insert(self, rule, dataset):
        self.rule_list.append(rule)             # insert r at the end of C
        self._select_default_class(dataset)     # select a default class for the current C
        self._compute_error(dataset)            # compute the total number of errors of C

    # select the majority class in the remaining data
    def _select_default_class(self, dataset):
        class_column = [x[-1] for x in dataset]
        class_label = set(class_column)
        max = 0
        current_default_class = None
        for label in class_label:
            if class_column.count(label) >= max:
                max = class_column.count(label)
                current_default_class = label
        self._default_class_list.append(current_default_class)

    # compute the sum of errors
    def _compute_error(self, dataset):
        if len(dataset) <= 0:
            self._error_list.append(sys.maxsize)
            return

        error_number = 0

        # the number of errors that have been made by all the selected rules in C
        for case in dataset:
            is_cover = False
            for rule in self.rule_list:
                if is_satisfy(case, rule):
                    is_cover = True
                    break
            if not is_cover:
                error_number += 1

        # the number of errors to be made by the default class in the training set
        class_column = [x[-1] for x in dataset]
        error_number += len(class_column) - class_column.count(self._default_class_list[-1])
        self._error_list.append(error_number)

    # see line 14 and 15, to get the final classifier
    def discard(self):
        # find the first rule p in C with the lowest total number of errors and drop all the rules after p in C
        index = self._error_list.index(min(self._error_list))
        self.rule_list = self.rule_list[:(index+1)]
        self._error_list = None

        # assign the default class associated with p to default_class
        self.default_class = self._default_class_list[index]
        self._default_class_list = None

    # just print out all selected rules and default class in our classifier
    def print(self):
        for rule in self.rule_list:
            rule.print_rule()
        print("default_class:", self.default_class)


# sort the set of generated rules car according to the relation ">", return the sorted rule list
def sort(car):
    def cmp_method(a, b):
        if a.confidence < b.confidence:     # 1. the confidence of ri > rj
            return 1
        elif a.confidence == b.confidence:
            if a.support < b.support:       # 2. their confidences are the same, but support of ri > rj
                return 1
            elif a.support == b.support:
                if len(a.cond_set) < len(b.cond_set):   # 3. both confidence & support are the same, ri earlier than rj
                    return -1
                elif len(a.cond_set) == len(b.cond_set):
                    return 0
                else:
                    return 1
            else:
                return -1
        else:
            return -1

    rule_list = list(car.rules)
    rule_list.sort(key=cmp_to_key(cmp_method))
    return rule_list


# main method of CBA-CB: M1
def classifier_builder_m1(cars, dataset):
    classifier = Classifier()
    cars_list = sort(cars)
    for rule in cars_list:
        temp = []
        mark = False
        for i in range(len(dataset)):
            is_satisfy_value = is_satisfy(dataset[i], rule)
            if is_satisfy_value is not None:
                temp.append(i)
                if is_satisfy_value:
                    mark = True
        if mark:
            temp_dataset = list(dataset)
            for index in temp:
                temp_dataset[index] = []
            while [] in temp_dataset:
                temp_dataset.remove([])
            dataset = temp_dataset
            classifier.insert(rule, dataset)
    classifier.discard()
    return classifier


# just for test
if __name__ == '__main__':
    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    minsup = 0.15
    minconf = 0.6
    cars = cba_rg.rule_generator(dataset, minsup, minconf)
    classifier = classifier_builder_m1(cars, dataset)
    classifier.print()

    print()
    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    cars.prune_rules(dataset)
    cars.rules = cars.pruned_rules
    classifier = classifier_builder_m1(cars, dataset)
    classifier.print()
