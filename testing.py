import itertools

# print(list(itertools.combinations_with_replacement(range(1,4),3)))

list1= ['a','b']
list2= [1,2]
list3=[""]

# print([list(zip(x,list2)) for x in itertools. permutations(list1,len(list2))])

l = [list1, list2,list3]
print(list(itertools.product(*l)))

