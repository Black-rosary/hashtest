from reader import Reader
from utils import read_ints, read_strings


def get_world(filename, make_bit_mask=False):
    reader = Reader(filename)
    data = reader.read_ints()

    world = {'total_photos': data[0], 'images': {}, 'tags': {},
             'vertical_photos': {}, 'horizontal_photos': {}, 'counts' : {}}

    photo_index = 0
    tag_index = 0
    while True:
        data = reader.read_strings()
        if not data:
            break
        world['images'][photo_index] = {
            'type': data[0],
            'id': [photo_index],
            'tags_count': int(data[1]),
        }
        if data[0] == 'V':
            world['vertical_photos'][photo_index] = photo_index
        else:
            world['horizontal_photos'][photo_index] = photo_index

        tags = data[2:]
        world['images'][photo_index]['tags'] = tags
        for tag in tags:
            if tag not in world['tags']:
                tag_index += 1
                world['tags'][tag] = {'bit': tag_index, 'index': {}}
            world['tags'][tag]['index'][photo_index] = photo_index
        photo_index += 1

    if make_bit_mask:
        for pid in world['images']:
            world['images'][pid]['bit_mask'] = 0
            for tag in world['images'][pid]['tags']:
                bit = world['tags'][tag]['bit']
                world['images'][pid]['bit_mask'] |= 1 << bit
    world['total_tags'] = len(world['tags'])

    counts = {}
    for t in world['tags']:
        l = len(world['tags'][t]['index'])
        if l not in counts:
            counts[l] = 1
        else:
            counts[l] += 1
    world['counts'] = counts
    reader.close()
    return world


def score(tags_1, tags_2):
    diff_1 = set(tags_1) - set(tags_2)
    diff_2 = set(tags_2) - set(tags_1)
    common = set(tags_2) & set(tags_1)

    return min(len(diff_1), len(diff_2), len(common))


def validation(input_file, output_file, debug_level=0):
    total_score = 0
    w = get_world(input_file)

    reader = Reader(output_file)

    data = reader.read_ints()
    if len(data) > 1:
        raise Exception("Bad format: on line %s. Only one value expected" % reader.get_current_line())
    v = {'total': data[0]}

    prev_tags = []
    while True:
        data = reader.read_ints()
        if not data:
            break
        tags = []
        if len(data) > 2:
            raise Exception("Bad format: on line %s. Find more than two photos in line" % reader.get_current_line())
        if len(data) == 2:
            photo1 = w['images'][data[0]]
            if photo1['type'] != 'V':
                raise Exception("Bad format: on line %s. Photo is not vertical" % reader.get_current_line())
            photo2 = w['images'][data[1]]
            if photo2['type'] != 'V':
                raise Exception("Bad format: on line %s. Photo is not vertical" % reader.get_current_line())
            tags = list(set(photo2['tags'] + photo1['tags']))
            #print("get two vertical photos %s, %s with tags (%s) and (%s) summary tags are (%s)" % (
            #     data[0], data[1], ','.join(photo1['tags']), ','.join(photo2['tags']), ','.join(tags)))
        if len(data) == 1:
            photo1 = w['images'][data[0]]
            if photo1['type'] != 'H':
                raise Exception("Bad format: on line %s. Photo is not horiznotal" % reader.get_current_line())
            tags = photo1['tags']
            #print("get one horizontal photo %s with tags (%s) " % (data[0], ','.join(photo1['tags'])))

        scr = score(prev_tags, tags)
        print("Validation: get slide with (%s) score (%s) " % (data, scr))

       # print("score with prev %s" % scr)
        total_score += scr
        prev_tags = tags

    print(total_score)
    reader.close()
    return total_score



def str_tags(photo):
    return ','.join(photo['tags'])


def output_to_file(filename, images):
    f = open(filename, "w+")
    f.write("%d\n" % len(images))
    for i in images:
        f.write("%s\n" % (' '.join([str(v) for v in i])))
    f.close()
