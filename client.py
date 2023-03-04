import datetime
import redis

BREAKPOINT = 1602251400

PORTS = [
    [7000, 7001, 7002],
    [7003, 7004, 7005],
]


def fetch_from_shard(from_time, to_time, interval, shard):
    for port in PORTS[shard]:
        print(port)
        try:
            res = {}
            conn = redis.StrictRedis(host='localhost', port=port, db=0, password='pass_word').ts()
            for key in ['temperature', 'pressure', 'humidity']:
                data = conn.range(
                    key,
                    from_time=from_time, 
                    to_time=to_time, 
                    aggregation_type='first',
                    bucket_size_msec=60*interval
                )
                for el in data:
                    if not res.get(el[0]):
                        res[el[0]] = {key: el[1]}
                    else:
                        res[el[0]].update({key: el[1]})

            return res
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            continue
    
    raise redis.exceptions.ConnectionError('No connection')


def fetch_from_shards(from_time, to_time, interval):
    right_remaining = interval*60 - BREAKPOINT % (interval*60)

    if right_remaining > to_time - BREAKPOINT:
        data = fetch_from_shard(from_time, to_time, interval, shard=0)
    else:
        data = fetch_from_shard(from_time, to_time, interval, shard=0)
        data.update(
            fetch_from_shard(BREAKPOINT + right_remaining, to_time, interval, shard=1)
        )

    return data

# interval = 160 (9600s)
# 1556092800 -> 1602249600
# 1602259200 -> 1648147200

while True:
    inp = input('> ')
    if inp == 'exit':
        break
    
    try:
        inp = [int(el) for el in inp.split(' ')]
        from_time = int(datetime.datetime(day=inp[0], month=inp[1], year=inp[2]).timestamp())
        to_time = int(datetime.datetime(day=inp[3], month=inp[4], year=inp[5]).timestamp())

        if from_time > to_time: raise ValueError

        interval = int(inp[6])

        if interval < 10:
            print('interval must be less than 10')
            continue

    except (IndexError, ValueError) as e:
        print('Wrong arguments')
        continue


    if from_time <= BREAKPOINT < to_time:
        res = fetch_from_shards(from_time, to_time, interval)
    elif to_time <= BREAKPOINT:
        res = fetch_from_shard(from_time, to_time, interval, shard=0)
    else:
        res = fetch_from_shard(from_time, to_time, interval, shard=1)

    print(res)
