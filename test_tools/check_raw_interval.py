import os

def name2num(name):
    a = float('0.'+name[18:24]) +3600*int(name[9:11]) + 60 * int(name[12:14]) + int(name[15:17]) 
    return a

# path = '/media/taoyuanipc1/500GDisk/test/raw/'
path = '/home/taoyuanipc1/Desktop/image_test/jpg/'
interval = 1/4 +0.001
print('interval',interval)
l = os.listdir(path)
l.sort()

old_sec = 0
old_i   = ''
for i in l:
    if i > '20210830_15-45-25':
        sec = name2num(i)
        if sec - old_sec > interval:
            print(old_i, i)
        old_i = i
        old_sec = sec
print(l[-1])
# old_sec = ''
# count = 0
# for i in l:
#     if i[:17] == old_sec:
#         count +=1 
#     else:
#         print(old_sec,count)
#         count =1 
#         old_sec = i[:17]

