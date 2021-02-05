
import input
import utils
from pprint import pprint


def validate(input_file, output_file):

    w = input.read_input(input_file)
    f = open(output_file, 'r')

    processing = {
        'total': 0,
        'libraries': {}
    }

    data = utils.read_ints(f)
    processing['total'] = data[0]

    while True:
        data = utils.read_ints(f)
        if not data:
            break
        if data[0] in processing['libraries']:
            raise Exception('Library %s already in list' % data[0])

        library_id = data[0]
        total = data[1]
        processing['libraries'][library_id] = {
            'library_id': data[0],
            'total': total,
            'speed': w.Libraries[library_id].speed,
            'sign_time': w.Libraries[library_id].sign_time,
        }

        data = utils.read_ints(f)
        if not data:
            break
        if len(data) > processing['libraries'][library_id]['total']:
            raise Exception("Library %s have not a total %s book. It has %d" % (library_id, total, len(data)))

        processing['libraries'][library_id]['books'] = data

    processed_books = {}
    end = {}
    day = 0
    while day <= w.total_days:
        in_sign = False
        for library_id in processing['libraries']:
            library = processing['libraries'][library_id]
            if library['sign_time'] > 0 and not in_sign:
                print("Validation: Day:%d/%d Library %d in sign process %d days left" % (day, w.total_days, library_id, library['sign_time']))
                library['sign_time'] -= 1
                in_sign = True
            elif library['sign_time'] == 0 and len(library['books']) > 0:
                speed = library['speed']
                taken_books = library['books'][:speed]
                print("Validation: Day:%d/%d Library %d has %d books, %d will be processed" % (day, w.total_days, library_id, len(library['books']), len(taken_books)))
                library['books'] = library['books'][speed:]
                for b in taken_books:
                    if b in processed_books:
                        print(' book %s already processed', b)
                    processed_books[b] = w.Books[b].score
            elif library['sign_time'] == 0 and len(library['books']) == 0 and library_id not in end:
                print("Validation: Day %d/%d Library %d processed" % (day, w.total_days, library_id))
                end[library_id] = True
        day += 1

    total_score = 0
    for b in processed_books:
        total_score += processed_books[b]

    print("Score %d" % total_score)
    return total_score


if __name__ == '__main__':
    validate('data/example.in', 'data/example.out')
