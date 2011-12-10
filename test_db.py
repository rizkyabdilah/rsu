import redis
import kyotocabinet
import random
import sys

r = redis.Redis(host = 'localhost', port = 11211)

REDIS_SETGET = False
REDIS_HSET = False
KYOTO = False
TOKYO = False

NUM_ENTRIES = 1000000000
MAX_VAL = 12000000

if len(sys.argv) != 2 or sys.argv[1] not in ('redis-normal', 'redis-hashes', 'kyoto', 'tokyo'):
    print 'Specify a test: redis-normal, redis-hashes, kyoto, tokyo'
    sys.exit(2)
    
if sys.argv[1] == 'redis-normal':
    REDIS_SETGET = True
elif sys.argv[1] == 'redis-hashes':
    REDIS_HSET = True
elif sys.argv[1] == 'kyoto':
    KYOTO = True
elif sys.argv[1] == 'tokyo':
    TOKYO = True

if REDIS_SETGET or REDIS_HSET:
    p = r.pipeline()
elif KYOTO:
    k = kyotocabinet.DB()
    if not k.open("/tmp/casket.kch", kyotocabinet.DB.OWRITER | kyotocabinet.DB.OCREATE):
        print "cannot open db"
        sys.exit(2)
    
for i in range(0, NUM_ENTRIES):
    value = random.randint(0, MAX_VAL)
    if REDIS_SETGET:
        r.set(str(i), value)
    elif REDIS_HSET:
        bucket = int(i / 513)
        p.hset(bucket, i, value)
    elif KYOTO:
        k.set(str(i), value)

    if i % (NUM_ENTRIES/10) == 0:
        if REDIS_SETGET or REDIS_HSET:
            p.execute()
            p = r.pipeline()
        print i

# one final clear out
if REDIS_SETGET or REDIS_HSET:
    p.execute()

# get size
if (REDIS_SETGET or REDIS_HSET):
    size = int(r.info()['used_memory'])
elif KYOTO:
    size = k.size()

print '%s bytes, %s MB' % (size, size / 1024 / 1024)
