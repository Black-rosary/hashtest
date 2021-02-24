

def read_file_iterator(f):
    n = 0
    while True:
        line = f.readline().strip()
        if not line:
            break
        yield [n, line]
        n += 1
    return [n, False]

def read_ints(f):
    try:
        ret = read_file_iterator(f)
        print(ret)
        if not line:
            return False
        data = line.split(' ')
        return [int(v) for v in data]
    except Exception as e:
        raise Exception("Error %s on line %d" % (e, n))


def read_strings(f):
    try:
        n, line = read_file_iterator(f)
        if not line:
            return False
        data = line.split(' ')
        return [str(v) for v in data]
    except Exception as e:
        raise Exception("Error %s on line %d" % (e, n))