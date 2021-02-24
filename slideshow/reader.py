
class Reader:

    def __init__(self, filename):
        self.f = open(filename, 'r')
        self.current_line = 0
        self.gen = self.read_line()

    def get_next(self):
        try:
            return next(self.gen)
        except StopIteration:
            return False

    def read_line(self):
        while True:
            line = self.f.readline().strip()
            if not line:
                break
            yield line
            self.current_line += 1
        return False

    def read_ints(self):
        try:
            line = self.get_next()
            if not line:
                return False
            data = line.split(' ')
            return [int(v) for v in data]
        except Exception as e:
            raise Exception("Error %s on line %d" % (str(e), self.current_line))

    def read_strings(self):
        try:
            line = self.get_next()
            if not line:
                return False
            data = line.split(' ')
            return [str(v) for v in data]
        except Exception as e:
            raise Exception("Error %s on line %d" % (str(e), self.current_line))

    def get_current_line(self):
        return self.current_line

    def close(self):
        self.f.close()
