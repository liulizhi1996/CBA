"""
Description: The following code implements an improved version of the algorithm, called CBA-CB: M2. It contains three
    stages. For stage 1, we scan the whole database, to find the cRule and wRule, get the set Q, U and A at the same
    time. In stage 2, for each case d that we could not decide which rule should cover it in stage 1, we go through d
    again to find all rules that classify it wrongly and have a higher precedence than the corresponding cRule of d.
    Finally, in stage 3, we choose the final set of rules to form our final classifer.
Input: a set of CARs generated from rule_generator (see cab_rg.py) and a dataset got from pre_process
    (see pre_processing.py)
Output: a classifier
Author: CBA Studio
"""
import ruleitem
import cba_cb_m1
from functools import cmp_to_key


class Classifier_m2:
    """
    The definition of classifier formed in CBA-CB: M2. It contains a list of rules order by their precedence, a default
    class label. The other member are private and useless for outer code.
    """
    def __init__(self):
        self.rule_list = list()
        self.default_class = None
        self._default_class_list = list()
        self._total_errors_list = list()

    # insert a new rule into classifier
    def add(self, rule, default_class, total_errors):
        self.rule_list.append(rule)
        self._default_class_list.append(default_class)
        self._total_errors_list.append(total_errors)

    # discard those rules that introduce more errors. See line 18-20, CBA-CB: M2 (Stage 3).
    def discard(self):
        index = self._total_errors_list.index(min(self._total_errors_list))
        self.rule_list = self.rule_list[:(index + 1)]
        self._total_errors_list = None

        self.default_class = self._default_class_list[index]
        self._default_class_list = None

    # just print out rules and default class label
    def print(self):
        for rule in self.rule_list:
            rule.print_rule()
        print("default_class:", self.default_class)


class Rule(ruleitem.RuleItem):
    """
    A class inherited from RuleItem, adding classCasesCovered and replace field.
    """
    def __init__(self, cond_set, class_label, dataset):
        ruleitem.RuleItem.__init__(self, cond_set, class_label, dataset)
        self._init_classCasesCovered(dataset)
        self.replace = set()

    # initialize the classCasesCovered field
    def _init_classCasesCovered(self, dataset):
        class_column = [x[-1] for x in dataset]
        class_label = set(class_column)
        self.classCasesCovered = dict((x, 0) for x in class_label)


# convert ruleitem of class RuleItem to rule of class Rule
def ruleitem2rule(rule_item, dataset):
    rule = Rule(rule_item.cond_set, rule_item.class_label, dataset)
    return rule


# finds the highest precedence rule that covers the data case d from the set of rules having the same class as d.
def maxCoverRule_correct(cars_list, data_case):
    for i in range(len(cars_list)):
        if cars_list[i].class_label == data_case[-1]:
            if cba_cb_m1.is_satisfy(data_case, cars_list[i]):
                return i
    return None


# finds the highest precedence rule that covers the data case d from the set of rules having the different class as d.
def maxCoverRule_wrong(cars_list, data_case):
    for i in range(len(cars_list)):
        if cars_list[i].class_label != data_case[-1]:
            temp_data_case = data_case[:-1]
            temp_data_case.append(cars_list[i].class_label)
            if cba_cb_m1.is_satisfy(temp_data_case, cars_list[i]):
                return i
    return None


# compare two rule, return the precedence.
#   -1: rule1 < rule2, 0: rule1 < rule2 (randomly here), 1: rule1 > rule2
def compare(rule1, rule2):
    if rule1 is None and rule2 is not None:
        return -1
    elif rule1 is None and rule2 is None:
        return 0
    elif rule1 is not None and rule2 is None:
        return 1

    if rule1.confidence < rule2.confidence:     # 1. the confidence of ri > rj
        return -1
    elif rule1.confidence == rule2.confidence:
        if rule1.support < rule2.support:       # 2. their confidences are the same, but support of ri > rj
            return -1
        elif rule1.support == rule2.support:
            if len(rule1.cond_set) < len(rule2.cond_set):   # 3. confidence & support are the same, ri earlier than rj
                return 1
            elif len(rule1.cond_set) == len(rule2.cond_set):
                return 0
            else:
                return -1
        else:
            return 1
    else:
        return 1


# finds all the rules in u that wrongly classify the data case and have higher precedences than that of its cRule.
def allCoverRules(u, data_case, c_rule, cars_list):
    w_set = set()
    for rule_index in u:
        # have higher precedences than cRule
        if compare(cars_list[rule_index], c_rule) > 0:
            # wrongly classify the data case
            if cba_cb_m1.is_satisfy(data_case, cars_list[rule_index]) == False:
                w_set.add(rule_index)
    return w_set


# counts the number of training cases in each class
def compClassDistr(dataset):
    class_distr = dict()

    if len(dataset) <= 0:
        class_distr = None

    dataset_without_null = dataset
    while [] in dataset_without_null:
        dataset_without_null.remove([])

    class_column = [x[-1] for x in dataset_without_null]
    class_label = set(class_column)
    for c in class_label:
        class_distr[c] = class_column.count(c)
    return class_distr


# sort the rule list order by precedence
def sort_with_index(q, cars_list):
    def cmp_method(a, b):
        # 1. the confidence of ri > rj
        if cars_list[a].confidence < cars_list[b].confidence:
            return 1
        elif cars_list[a].confidence == cars_list[b].confidence:
            # 2. their confidences are the same, but support of ri > rj
            if cars_list[a].support < cars_list[b].support:
                return 1
            elif cars_list[a].support == cars_list[b].support:
                # 3. both confidence & support are the same, ri earlier than rj
                if len(cars_list[a].cond_set) < len(cars_list[b].cond_set):
                    return -1
                elif len(cars_list[a].cond_set) == len(cars_list[b].cond_set):
                    return 0
                else:
                    return 1
            else:
                return -1
        else:
            return -1

    rule_list = list(q)
    rule_list.sort(key=cmp_to_key(cmp_method))
    return set(rule_list)


# get how many errors the rule wrongly classify the data case
def errorsOfRule(rule, dataset):
    error_number = 0
    for case in dataset:
        if case:
            if cba_cb_m1.is_satisfy(case, rule) == False:
                error_number += 1
    return error_number


# choose the default class (majority class in remaining dataset)
def selectDefault(class_distribution):
    if class_distribution is None:
        return None

    max = 0
    default_class = None
    for index in class_distribution:
        if class_distribution[index] > max:
            max = class_distribution[index]
            default_class = index
    return default_class


# count the number of errors that the default class will make in the remaining training data
def defErr(default_class, class_distribution):
    if class_distribution is None:
        import sys
        return sys.maxsize

    error = 0
    for index in class_distribution:
        if index != default_class:
            error += class_distribution[index]
    return error


# main method, implement the whole classifier builder
def classifier_builder_m2(cars, dataset):
    classifier = Classifier_m2()

    cars_list = cba_cb_m1.sort(cars)
    for i in range(len(cars_list)):
        cars_list[i] = ruleitem2rule(cars_list[i], dataset)

    # stage 1
    q = set()
    u = set()
    a = set()
    mark_set = set()
    for i in range(len(dataset)):
        c_rule_index = maxCoverRule_correct(cars_list, dataset[i])
        w_rule_index = maxCoverRule_wrong(cars_list, dataset[i])
        if c_rule_index is not None:
            u.add(c_rule_index)
        if c_rule_index:
            cars_list[c_rule_index].classCasesCovered[dataset[i][-1]] += 1
        if c_rule_index and w_rule_index:
            if compare(cars_list[c_rule_index], cars_list[w_rule_index]) > 0:
                q.add(c_rule_index)
                mark_set.add(c_rule_index)
            else:
                a.add((i, dataset[i][-1], c_rule_index, w_rule_index))
        elif c_rule_index is None and w_rule_index is not None:
            a.add((i, dataset[i][-1], c_rule_index, w_rule_index))

    # stage 2
    for entry in a:
        if cars_list[entry[3]] in mark_set:
            if entry[2] is not None:
                cars_list[entry[2]].classCasesCovered[entry[1]] -= 1
            cars_list[entry[3]].classCasesCovered[entry[1]] += 1
        else:
            if entry[2] is not None:
                w_set = allCoverRules(u, dataset[entry[0]], cars_list[entry[2]], cars_list)
            else:
                w_set = allCoverRules(u, dataset[entry[0]], None, cars_list)
            for w in w_set:
                cars_list[w].replace.add((entry[2], entry[0], entry[1]))
                cars_list[w].classCasesCovered[entry[1]] += 1
            q |= w_set

    # stage 3
    rule_errors = 0
    q = sort_with_index(q, cars_list)
    data_cases_covered = list([False] * len(dataset))
    for r_index in q:
        if cars_list[r_index].classCasesCovered[cars_list[r_index].class_label] != 0:
            for entry in cars_list[r_index].replace:
                if data_cases_covered[entry[1]]:
                    cars_list[r_index].classCasesCovered[entry[2]] -= 1
                else:
                    if entry[0] is not None:
                        cars_list[entry[0]].classCasesCovered[entry[2]] -= 1
            for i in range(len(dataset)):
                datacase = dataset[i]
                if datacase:
                    is_satisfy_value = cba_cb_m1.is_satisfy(datacase, cars_list[r_index])
                    if is_satisfy_value:
                        dataset[i] = []
                        data_cases_covered[i] = True
            rule_errors += errorsOfRule(cars_list[r_index], dataset)
            class_distribution = compClassDistr(dataset)
            default_class = selectDefault(class_distribution)
            default_errors = defErr(default_class, class_distribution)
            total_errors = rule_errors + default_errors
            classifier.add(cars_list[r_index], default_class, total_errors)
    classifier.discard()

    return classifier


# just for test
if __name__ == "__main__":
    import cba_rg

    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    minsup = 0.15
    minconf = 0.6
    cars = cba_rg.rule_generator(dataset, minsup, minconf)
    classifier = classifier_builder_m2(cars, dataset)
    classifier.print()

    print()
    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    cars.prune_rules(dataset)
    cars.rules = cars.pruned_rules
    classifier = classifier_builder_m2(cars, dataset)
    classifier.print()
