class WTF(object):
    def __init__(self):
         print("I ")

    def __del__(self):
         print("D ")


print(WTF() is WTF())
print(id(WTF()) == id(WTF()))




l = [1, 2, 3]
g = (x for x in l if l.count(x) > 0)
l = [1]
print(list(g))

array_1 = [1,2,3,4]
g1 = (x for x in array_1)
l1 = [x for x in array_1]
array_1 = [1,2,3,4,5]
print(list(g1))

array_2 = [1,2,3,4]
g2 = (x for x in array_2)
l2 = [x for x in array_2]
array_2[:] = [1,2,3,4,5]
print(list(g2))
print(list(l2))