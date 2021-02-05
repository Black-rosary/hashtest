import input
import validation
from pprint import pprint

processed_books = {}
processed_libraries = {}
bad_libraries = {}


def check_library(world, library_id):
    if library_id in processed_libraries:
        return False
    if library_id in bad_libraries:
        return False
    total = 0
    for book_id in world.Libraries[library_id].books:
        if book_id in processed_books:
            continue
        total += 1
    if total < 1:
        bad_libraries[library_id] = True
        return False
    return True


def get_summary_score(world, library_id):
    library_score = 0
    for book_id in world.Libraries[library_id].books:
        if book_id in processed_books:
            continue
        library_score += world.Books[book_id].score
    return library_score


def get_highest_score_library(world):
    max_score = 0
    best_library_id = -1
    for library_id in world.Libraries:
        if not check_library(world, library_id):
            continue
        library_score = get_summary_score(world, library_id)

        if library_score > max_score:
            max_score = library_score
            best_library_id = library_id

    if best_library_id >= 0:
        print("Fined best library %d with score %d" % (best_library_id, max_score))
        print(world.Libraries[best_library_id])
    return best_library_id


def get_highest_efficiency_library(world):
    max_efficiency = 99999999
    best_library_id = -1
    for library_id in world.Libraries:
        if not check_library(world, library_id):
            continue
        total_book = 0
        for book_id in world.Libraries[library_id].books:
            if book_id in processed_books:
                continue
            total_book += 1

        if (total_book / world.Libraries[library_id].speed) < max_efficiency and (
                total_book / world.Libraries[library_id].speed) > 1:
            max_efficiency = total_book / world.Libraries[library_id].speed
            best_library_id = library_id

    if best_library_id >= 0:
        print("Find eficiency library %d with efficiency %s" % (best_library_id, max_efficiency))
        print(world.Libraries[best_library_id])
    return best_library_id


def get_fastest_library(world):
    min_sign_time = 99999999
    best_library_id = -1
    for library_id in world.Libraries:
        if not check_library(world, library_id):
            continue
        if world.Libraries[library_id].sign_time < min_sign_time:
            min_sign_time = world.Libraries[library_id].sign_time
            best_library_id = library_id
        if world.Libraries[library_id].sign_time == min_sign_time:
            if get_summary_score(world, library_id) > get_summary_score(world, best_library_id):
                best_library_id = library_id

    if best_library_id >= 0:
        print("Find fastest library %d with score %s" % (best_library_id, min_sign_time))
        print(world.Libraries[best_library_id])
    return best_library_id


def score_speed(library):
    return float(library.score) / (float(library.sign_time) + (float(library.total_books) / float(library.speed)))

def book_rarity(library):
    return float(library.score) / (float(library.sign_time) + (float(library.total_books) / float(library.speed)))

def sort_libraries(libriaries):
    list = []
    for library_id in libriaries:
        list.append({
            "score": libriaries[library_id].score,
            "total_books": libriaries[library_id].total_books,
            "speed": libriaries[library_id].speed,
            "library_id": library_id,
            "score_speed": score_speed(libriaries[library_id]),
            "sign_time": libriaries[library_id].sign_time
        })
    list = sorted(list, key=lambda v: float(v["score_speed"]) / float(v["sign_time"]), reverse=True)
    return list


def get_best_speed_of_speed(libriaries, world):
    best_rarity = 0
    best_score_speed = 0
    best_library_id = None
    for library_id in libriaries:
        if libriaries[library_id].score_speed > best_score_speed:
            best_score_speed = libriaries[library_id].score_speed
            best_library_id = library_id
            best_rarity = 0
        elif libriaries[library_id].score_speed == best_score_speed and best_rarity < libriaries[library_id].get_rarity(world):
            best_rarity = libriaries[library_id].get_rarity(world)
            best_library_id = library_id

    return best_library_id

def speed_of_speed_sol(filename):
    processed_books = {}
    processed_libraries = {}
    input_file = filename
    world = input.read_input(input_file)
    libriaries = dict(world.Libraries)
    for library_id in libriaries:
        libriaries[library_id].recalculate()

    total_sign_time = 0
    while True:
        if len(libriaries) <= 0:
            break
        if total_sign_time > world.total_days:
            break
        best_id = get_best_speed_of_speed(libriaries, world)
        candidate = libriaries[best_id]
        print("(%d/%d) Find %s" % (total_sign_time, world.total_days, candidate))
        total_sign_time += libriaries[best_id].sign_time
        for book_id in libriaries[best_id].books:
            affected_libraries = world.BookIndex[book_id]
            book_score = world.Books[book_id].score
            for library_id in affected_libraries:
                if library_id != best_id and library_id in libriaries:
                    libriaries[library_id].score -= book_score
                    libriaries[library_id].total_books -= 1
                    del libriaries[library_id].books[book_id]
                    if libriaries[library_id].total_books <= 0:
                        del libriaries[library_id]
                    else:
                        libriaries[library_id].recalculate()
        del libriaries[best_id]
        processed_libraries[best_id] = []
        for book_id in world.Libraries[best_id].books:
            if book_id not in processed_books:
                processed_libraries[best_id].append(book_id)
            processed_books[book_id] = True

    output_to_file(filename + '.out', processed_libraries)
    return validation.validate(input_file, filename + '.out')


def output_to_file(filename, libraries):
    f = open(filename, "w+")

    f.write("%d\n" % len(libraries))
    for i in libraries:
        f.write("%d %d\n" % (i, len(libraries[i])))
        f.write("%s\n" % (' '.join([str(v) for v in libraries[i]])))
    f.close()


# Score: 5822900
def b_read_on_sol():
    input_file = 'data/b_read_on.txt'
    w = input.read_input(input_file)
    best_id = get_fastest_library(w)
    while best_id >= 0:
        processed_libraries[best_id] = []
        for book_id in w.Libraries[best_id].books:
            if book_id not in processed_books:
                processed_libraries[best_id].append(book_id)
            processed_books[book_id] = True
        best_id = get_fastest_library(w)

    output_to_file('data/b_read_on.out', processed_libraries)
    validation.validate(input_file, 'data/b_read_on.out')

#5643385
def c_incunabula_sol():
    input_file = 'data/c_incunabula.txt'
    w = input.read_input(input_file)
    best_id = get_fastest_library(w)
    while best_id >= 0:
        processed_libraries[best_id] = []
        for book_id in w.Libraries[best_id].books:
            if book_id not in processed_books:
                processed_libraries[best_id].append(book_id)
            processed_books[book_id] = True
        if (len(processed_libraries) < 8):
            best_id = get_fastest_library(w)
        else:
            best_id = get_highest_score_library(w)

    output_to_file('data/c_incunabula.out', processed_libraries)
    validation.validate(input_file, 'data/c_incunabula.out')


if __name__ == '__main__':
    total = 0
    total += speed_of_speed_sol('data/a_example.txt')
    total += speed_of_speed_sol('data/b_read_on.txt')
    total += speed_of_speed_sol('data/c_incunabula.txt')
    total += speed_of_speed_sol('data/d_tough_choices.txt')
    total += speed_of_speed_sol('data/e_so_many_books.txt')
    total += speed_of_speed_sol('data/f_libraries_of_the_world.txt')
    print(total)

