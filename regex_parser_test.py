from regex_parser import *
import pattern_table
target_list = ["A"]
multi_list = [["A"],["B"],["C"]]
p = pattern_table.make_pattern_table([multi_list,multi_list,multi_list])
result_list = []
print("p is")
for elm in p:
    print(elm)
    tmp_p = []
    for p2 in elm:
        tmp_p.extend(p2)
    print(tmp_p)
    result_list.append(tmp_p)
print(result_list)

quantize = {"min_count" : -1, "max_count" : 2}
quantize2 = {"min_count" : 0, "max_count" : 3}
quantize3 = {"min_count" : -1, "max_count" : 1}
print(pere_expression(None,target_list))
print(pere_expression(None,[[target_list],quantize]))
result = pere_expression(None,[multi_list,quantize])
print("show result")
for i in result:
    print(i)
print("end result")
Pattern_Transform.pere_expression = pere_expression

p1 = [['a'],['b','c'],['a','a'],[],['b','b','c'],['c']]
result1 = pere_expression(None,[p1,quantize])
for p1elm in result1:
    print(p1elm)
print("end p1")
result2 = pere_expression(None,[p1,quantize2])
p2_str = []
for p2elm in result2:
    p2_str.append(str(p2elm))
print("end p2")
p2_nondupl  = sorted(list(set(p2_str)))
for elm in p2_nondupl:
    print(elm)
result3 = pere_expression(None,[p1,quantize3])
for elm in result3:
    print(elm)

result = []
result = parse_pattern("(((AA BB{0,2}){0,2}|XXX YYY)){3}")
print("show result")
for i in result:
  print(i)
  if isinstance(i,list):
    for j in i:
      print(j)