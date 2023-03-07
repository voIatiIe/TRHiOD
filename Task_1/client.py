import datetime
import redis

BREAKPOINT = 1602251400

PORTS = [
    [7000, 7001, 7002],
    [7003, 7004, 7005],
]


class BCOL:
    OK = '\033[92m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def fetch_from_shard(from_time, to_time, interval, shard):
    print(f'Shard {shard}'.center(25, '-'))
    for i, port in enumerate(PORTS[shard]):
        try:
            port_str = f'{port}({"replica" if i else "master"})'
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
            
            print(f'{port_str} -> {BCOL.BOLD}{BCOL.OK}success{BCOL.ENDC}')

            return res
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
            print(f'{port_str} -> {BCOL.BOLD}{BCOL.FAIL}error{BCOL.ENDC}')
            continue
        except redis.exceptions.ResponseError as e:
            print(f'{port_str} -> {BCOL.BOLD}{BCOL.FAIL}not found{BCOL.ENDC}')
            continue
    
    raise redis.exceptions.ConnectionError(f'{BCOL.BOLD}{BCOL.FAIL}Error! (shard {shard}){BCOL.ENDC}')


def fetch_from_shards(from_time, to_time, interval):
    right_remaining = interval*60 - BREAKPOINT % (interval*60)

    if right_remaining > to_time - BREAKPOINT:
        data = fetch_from_shard(from_time, to_time, interval, shard=0)
    else:
        data = fetch_from_shard(from_time, to_time, interval, shard=0)
        data.update(
            fetch_from_shard(BREAKPOINT + right_remaining, to_time, interval, shard=1)
        )
    print('-'*25)

    return data

# > 1 1 2000 1 1 3000 160
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

    if res:
        headers = list(list(res.items())[0][1].keys())
        print(' '*20 + '| timestamp  | ' + ' | '.join(headers))

        for key, data in res.items():
            values = []
            for header in headers:
                value = data[header]

                prefix = ' ' if value >= 0 else ''
                rightadd = 1 if prefix else 0

                rightlen = len(header) - len(str(value)) - rightadd
                value = f'{prefix}{value}{" "*rightlen}'
                values.append(value)

            print(
                f'{datetime.datetime.utcfromtimestamp(key + 3*3600).strftime("%Y-%m-%d %H:%M:%S")}'
                f' | {key} | '
                f'{" | ".join(values)}'
            )
