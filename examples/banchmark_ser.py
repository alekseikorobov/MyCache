# сравним скорость сереалзиации

import time
from my_cache.CacheStor import CacheStor
from my_cache.serialise.Serialise import SerialiseBin,SerialiseJson
cache_stor = CacheStor()
start = time.time()
for i in range(1000000):
    res = cache_stor.serialiser.encode(1,2,3,[1,'2'*100,3],[1,[1,'2'*100,'3'*100],3])
end = time.time() - start
print(end)

cache_stor = CacheStor(serialiser=SerialiseJson())
start = time.time()
for i in range(1000000):
    res = cache_stor.serialiser.encode(1,2,3,[1,'2'*100,3],[1,[1,'2'*100,'3'*100],3])
end = time.time() - start
print(end)

# python examples/banchmark_ser.py 
# 2.013641834259033
# 7.040184497833252