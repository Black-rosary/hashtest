

def read_ints(f):
    line = f.readline().strip()
    if not line:
        return False
    data = line.split(' ')
    return [int(v) for v in data]