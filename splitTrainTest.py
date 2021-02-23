import random
import numpy as np

with open("ratings.csv", "r") as rfile:
    head = rfile.readline()
    lines = rfile.readlines()

a = np.arange(len(lines))
np.random.shuffle(a)
test = a[0:(int(0.1 * len(lines)))]
train = a[(int(0.1 * len(lines))):]

np.sort(test)
np.sort(train)

lines = np.array(lines)
lines_test = lines[test]
lines_train = lines[train]

with open('test.csv', 'w') as fo:
    fo.write(head)
    for line in lines_test:
        fo.write(line)

with open('train.csv', 'w') as fo:
    fo.write(head)
    for line in lines_train:
        fo.write(line)