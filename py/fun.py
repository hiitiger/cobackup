quick_sort = lambda l: quick_sort([x for x in l[1:] if x <= l[0]]) + [l[0]] + quick_sort([x for x in l[1:] if x > l[0]]) if l else []

# print(quick_sort([]))
# print(quick_sort([2]))
# print(quick_sort([13, 21, 3, 4, 24, 523, 23]))