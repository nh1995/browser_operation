import itertools

def make_pattern_table(target_list):
    result_list = []
    for multiplicant_list in target_list:
        if len(result_list) < 1:
            for tmp in multiplicant_list:
                result_list.append([tmp])
        else:
            tmp_result_list = []
            for multiplier_list in result_list:
                for multiplicant_value in multiplicant_list:
                    copied_list = multiplier_list.copy()
                    copied_list.append(multiplicant_value)
                    tmp_result_list.append(copied_list)
            result_list = tmp_result_list

    return result_list

listA = ['a','b']
listB = ['x','y','z']
listC = ['1','2']

target_list = []
target_list.append(listA)
target_list.append(listB)
target_list.append(listC)
#print(target_list)
#print(make_pattern_table(target_list))
"""
producted_list =itertools.product(listA,listB,listC)
print(list(producted_list))
producted_list = itertools.product(itertools.product(listA,listB),listC)
print(list(producted_list))
target_list = [listA,listB,listC]
producted_list = []
len(target_list)
for target in target_list:
    if len(producted_list) < 1:
        producted_list = target
    else:
        producted_list = list(itertools.product(producted_list,target))
print("production result.")
print(producted_list)
result_list = []
tmplist = []
result_list = []
for multiplicant_list in target_list:
    if len(result_list) < 1:
        for tmp in multiplicant_list:
            result_list.append([tmp])
    else:
        tmp_result_list = []
        for multiplier_list in result_list:
            for multiplicant_value in multiplicant_list:
                copied_list = multiplier_list.copy()
                copied_list.append(multiplicant_value)
                tmp_result_list.append(copied_list)
        result_list = tmp_result_list
for element in result_list:
    print(element)
"""