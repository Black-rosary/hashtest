from pprint import pprint
import json
import utils

filename = "test.txt"


class Book:
    book_id = 0
    score = 0

    def __init__(self, index, score):
        self.book_id = index
        self.score = score

    def __repr__(self):
        return "  book id:%s, score :%s" % (self.book_id, self.score)


class Library:
    library_id = 0
    total_books = 0
    books = {}
    sign_time = 0
    speed = 0
    score = 0
    score_speed = 0
    speed_of_speed = 0
    rarity = None
    processed_books = {}

    def del_book(self, book_id):
        del self.books[book_id]
        self.rarity = None

    def get_rarity(self, w):
        if self.rarity is None:
            libs = {}
            self.rarity = 0
            for book_id in self.books:
                for lid in w.BookIndex[book_id]:
                    if lid not in libs:
                        libs[lid] = lid
            self.rarity = len(libs)
        return self.rarity

    def recalculate(self):
        self.score_speed = float(self.score) / (float(self.sign_time) + (float(self.total_books) / float(self.speed)))
        self.speed_of_speed = float(self.score_speed) / float(self.sign_time)


    def __repr__(self):
        return "Library id:%s, total_books :%s sign_time: %s speed: %s score_speed %s, speed_of_speed: %s (rarity: %s)" % (
            self.library_id,
            self.total_books,
            self.sign_time,
            self.speed,
            self.score_speed,
            self.speed_of_speed,
            self.rarity
        )

class World(object):
    current_day = 0
    total_books = 0
    total_libraries = 0
    total_days = 0
    BookIndex = {}
    Libraries = {}
    Books = {}

    def print(self):
        print(self.__dict__)
        pprint(self.BookIndex)
        pprint(self.Books)
        pprint(self.Libraries)


def read_input(filename):
    f = open(filename, 'r')

    w = World()

    w.BookIndex = {}
    w.Libraries = {}
    w.Books = {}

    data = utils.read_ints(f)
    w.total_books = int(data[0])
    w.total_libraries = int(data[1])
    w.total_days = int(data[2])

    data = utils.read_ints(f)
    bindex = 0
    for score in data:
        w.Books[bindex] = Book(bindex, int(score))
        bindex += 1

    lindex = 0
    while True:
        data = utils.read_ints(f)
        if not data:
            break
        L = Library()
        L.library_id = lindex
        L.total_books = data[0]
        L.sign_time = data[1]
        L.speed = data[2]

        data = utils.read_ints(f)
        books = {}
        for book_id in data:
            if book_id not in books:
                books[book_id] = w.Books[book_id].score
            L.score += w.Books[book_id].score
            if book_id not in w.BookIndex:
                w.BookIndex[book_id] = []
            if L.library_id not in w.BookIndex[book_id]:
                w.BookIndex[book_id].append(L.library_id)
            L.books = books

        w.Libraries[lindex] = L
        lindex += 1
    return w
