import os
import pickle
l = [x for x in os.listdir('imgs/') if x.endswith(".raw")]
l.sort()
# print(l)
pickle.dump(l, open('fns.pk','wb'))
