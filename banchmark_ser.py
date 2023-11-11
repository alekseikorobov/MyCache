# import pickle
# import hashlib
# data = {'key': 'value', 'list': [1, 2, 3]}
# serialized_data = pickle.dumps(data)
# hash_string = hashlib.sha256(serialized_data).hexdigest()
# print(hash_string)


# сравним скорость сереалзиации

import time
from my_cache_async import cache_stor

start = time.time()
for i in range(1000000):
    res = cache_stor.generate_hash(1,2,3,[1,'2'*100,3],[1,[1,'2'*100,'3'*100],3])
end = time.time() - start
print(end)


start = time.time()
for i in range(1000000):
    res = cache_stor.generate_hash_new(1,2,3,[1,'2'*100,3],[1,[1,'2'*100,'3'*100],3])
end = time.time() - start
print(end)