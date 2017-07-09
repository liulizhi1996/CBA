"""
Description: Definition of class RuleItem, including condset, class label (y in paper), condsupCount, rulesupCount,
    support and confidence.
Input: condset which is a set of items, class label and the dataset.
Output: a ruleitem with its condsupCount, rulesupCount, support and confidence.
Author: CBA Studio
Reference: https://www.cs.uic.edu/~hxiao/courses/cs594-slides.pdf
"""


class RuleItem:
    """
    cond_set: a dict with following fashion:
            {item name: value, item name: value, ...}
        e.g.
            {A: 1, B: 1} (A, B are name of columns, here called "item", and in our code should be numerical index
                          but not string)
    class_label: just to identify the class it belongs to.
    dataset: a list returned by read method. (see read.py)
    cond_sup_count, rule_sup_count, support and confidence are number.
    """
    def __init__(self, cond_set, class_label, dataset):
        self.cond_set = cond_set
        self.class_label = class_label
        self.cond_sup_count, self.rule_sup_count = self._get_sup_count(dataset)
        self.support = self._get_support(len(dataset))
        self.confidence = self._get_confidence()

    # calculate condsupCount and rulesupCount
    def _get_sup_count(self, dataset):
        cond_sup_count = 0
        rule_sup_count = 0
        for case in dataset:
            is_contained = True
            for index in self.cond_set:
                if self.cond_set[index] != case[index]:
                    is_contained = False
                    break
            if is_contained:
                cond_sup_count += 1
                if self.class_label == case[-1]:
                    rule_sup_count += 1
        return cond_sup_count, rule_sup_count

    # calculate support count
    def _get_support(self, dataset_size):
        return self.rule_sup_count / dataset_size

    # calculate confidence
    def _get_confidence(self):
        if self.cond_sup_count != 0:
            return self.rule_sup_count / self.cond_sup_count
        else:
            return 0

    # print out the ruleitem
    def print(self):
        cond_set_output = ''
        for item in self.cond_set:
            cond_set_output += '(' + str(item) + ', ' + str(self.cond_set[item]) + '), '
        cond_set_output = cond_set_output[:-2]
        print('<({' + cond_set_output + '}, ' + str(self.cond_sup_count) + '), (' +
              '(class, ' + str(self.class_label) + '), ' + str(self.rule_sup_count) + ')>')

    # print out rule
    def print_rule(self):
        cond_set_output = ''
        for item in self.cond_set:
            cond_set_output += '(' + str(item) + ', ' + str(self.cond_set[item]) + '), '
        cond_set_output = '{' + cond_set_output[:-2] + '}'
        print(cond_set_output + ' -> (class, ' + str(self.class_label) + ')')


# just for test
if __name__ == '__main__':
    cond_set = {0: 1, 1: 1}
    class_label = 1
    dataset = [[1, 1, 1], [1, 1, 1], [1, 2, 1], [2, 2, 1], [2, 2, 1],
               [2, 2, 0], [2, 3, 0], [2, 3, 0], [1, 1, 0], [3, 2, 0]]
    rule_item = RuleItem(cond_set, class_label, dataset)
    rule_item.print()
    rule_item.print_rule()
    print('condsupCount =', rule_item.cond_sup_count)   # should be 3
    print('rulesupCount =', rule_item.rule_sup_count)   # should be 2
    print('support =', rule_item.support)               # should be 0.2
    print('confidence =', rule_item.confidence)         # should be 0.667
