from time import time

from common import get_world, validation, score, output_to_file, str_tags
from solution1 import sol7



def get_candidates_by_bit_mask(photos, index, slide_id, slide_tags):

    candidates = {}

    bit_mask = 0
    for tag in slide_tags:
        bit_mask |= 1 << index[tag]['bit']

    for photo_id, photo in photos.items():
        common = list(set(slide_tags + photos[photo_id]['tags']))
        if len(common):
            candidates[photo_id] = {
                'photo_id': photo_id,
                'common': len(common),
                'type': photos[photo_id]['type'],
                'tags_count': photos[photo_id]['tags_count'],
                'common_tags': common,
                'tags': photos[photo_id]['tags'],
                'max_score': get_max_score(photos, [photo_id])
            }
    candidates = {k: v for k, v in sorted(candidates.items(), key=lambda item: item[1]['max_score'], reverse=True)}
    return candidates


def sol1(input_file):
    w = get_world(input_file)
    gallery = []

    prev_id = 0

    while True:
        prev_image = w['images'][prev_id]
        del w['images'][prev_id]

        best_score = -1
        best_candidate = -1
        for id in w['images']:
            s = score(prev_image['tags'], w['images'][id]['tags'])
            #s = score_on_bit_mask(prev_image, w['images'][id])
            if s > best_score:
                best_candidate = id
                best_score = s
            if best_score >= 3:
                break
        if best_candidate > 0:
            print("[%d/ %d] : Find best candidate for %s (%s) - %s (%s) with score %s" % (
                len(w['images']), w['total_photos'], prev_id, prev_image['tags'], best_candidate,
                w['images'][best_candidate]['tags'], best_score
            ))

            gallery.append([best_candidate])
            prev_id = best_candidate
        else:
            break


    output_file_name = input_file + '.out'
    output_to_file(output_file_name, gallery)
    return output_file_name


def score_on_bit_mask(photo1, photo2):
    common = bin(photo1['bit_mask'] & photo2['bit_mask']).count('1')
    diff_1 = bin(photo1['bit_mask'] & ~photo2['bit_mask']).count('1')
    diff_2 = bin(photo2['bit_mask'] & ~photo1['bit_mask']).count('1')
    return min(common, diff_1, diff_2)

def sol3(input_file):
    w = get_world(input_file)
    gallery = []
    print('create world with %d vertical' % len(w['vertical_photos']))
    w['vertical_idxs'] = {}
    vertical = dict(w['vertical_photos'])
    for vid1 in w['vertical_photos']:
        print("process %s" % vid1)
        del vertical[vid1]
        for vid2 in vertical:
            new_id = "%s_%s" % (vid1, vid2)
            w['images'][new_id] = {
                'id': [vid1, vid2],
                'type': 'V',
                'bit_mask': w['images'][vid1]['bit_mask'] | w['images'][vid2]['bit_mask'],
                'tags': w['images'][vid1]['tags'] + w['images'][vid2]['tags'],
                'tags_count': w['images'][vid1]['tags_count'] + w['images'][vid2]['tags_count'],
            }
            if not vid1 in w['vertical_idxs']:
                w['vertical_idxs'][vid1] = []
            w['vertical_idxs'][vid1].append(new_id)
        del w['images'][vid1]
    print( w['vertical_idxs'])
    total = len(w['images'])
    prev_id = 100
    while True:
        prev_image = w['images'][prev_id]
        if prev_image['type'] == 'V':
            for phid in w['vertical_idxs'][prev_image['id'][0]]:
                if phid in w['images']:
                    del w['images'][phid]
            if prev_image['id'][1] in w['vertical_idxs']:
                for phid in w['vertical_idxs'][prev_image['id'][1]]:
                    if phid in w['images']:
                        del w['images'][phid]
        else:
            del w['images'][prev_id]

        best_score = -1
        best_candidate = -1
        for photo_id in w['images']:

            #s = score_on_bit_mask(prev_image, w['images'][photo_id])
            s = score(prev_image['tags'], w['images'][photo_id]['tags'])
            if s >= best_score:
                best_candidate = photo_id
                best_score = s
        if best_candidate != -1:
            print("[%d/ %d] : Find best candidate for %s (%s %s) - %s (%s %s) with score %s" % (
                len(w['images']), total, prev_id, prev_image['id'], prev_image['tags'], best_candidate,
                w['images'][best_candidate]['id'], w['images'][best_candidate]['tags'], best_score
            ))

            gallery.append(w['images'][best_candidate]['id'])
            prev_id = best_candidate
        else:
            break


    output_file_name = input_file + '.out'
    output_to_file(output_file_name, gallery)
    return output_file_name

def sol2(input_file):
    w = get_world(input_file)
    gallery = []

    prev_photo_ids = [0]

    while True:

        prev_image = w['images'][prev_photo_ids[0]]

        if prev_image['type'] == 'V':
            del w['vertical_photos'][prev_photo_ids[0]]
        else:
            del w['horizontal_photos'][prev_photo_ids[0]]
        del w['images'][prev_photo_ids[0]]

        if 1 in prev_photo_ids:
            prev_image['bit_mask'] |= w['images'][prev_photo_ids[1]]['bit_mask']
            prev_image['tags'] += w['images'][prev_photo_ids[1]]['tags']
            prev_image['total_tags'] += w['images'][prev_photo_ids[1]]['total_tags']
            if prev_image['type'] == 'V':
                del w['vertical_photos'][prev_photo_ids[1]]
            else:
                del w['horizontal_photos'][prev_photo_ids[1]]
            del w['images'][prev_photo_ids[1]]

        best_score = -1
        best_candidate = []
        for photo_id in w['images']:
            if w['images'][photo_id]['type'] == 'V':
                for id2 in w['vertical_photos']:
                    if w['images'][id2]['type'] == 'V':
                        surrogate = {'bit_mask':  w['images'][photo_id]['bit_mask'] | w['images'][id2]['bit_mask']}
                        s_pair = score_on_bit_mask(prev_image, surrogate)
                        if s_pair > best_score:
                            best_candidate = [photo_id, id2]
            else:
                s = score_on_bit_mask(prev_image, w['images'][photo_id])
                if s > best_score:
                    best_candidate = [photo_id]
                    best_score = s
        if len(best_candidate) > 0:
            if len(best_candidate) == 1:
                print("[%d/ %d] : Find best candidate for %s (%s) - %s (%s) with score %s" % (
                    len(w['images']), w['total_photos'], prev_photo_ids, prev_image['tags'], best_candidate[0],
                    w['images'][best_candidate[0]]['tags'], best_score
                ))
            else:
                print("[%d/ %d] : Find best candidates for %s (%s) - %s (%s) and %s (%s) with score %s" % (
                    len(w['images']), w['total_photos'], prev_photo_ids, prev_image['tags'],
                    best_candidate[0],  w['images'][best_candidate[0]]['tags'],
                    best_candidate[1], w['images'][best_candidate[1]]['tags'],
                    best_score
                ))

            gallery.append(best_candidate)
            prev_photo_ids = best_candidate
        else:
            break

    output_file_name = input_file + '.out'
    output_to_file(output_file_name, gallery)
    return output_file_name


def get_all_possible_vertical_candidates(w):
    print('create world with %d vertical' % len(w['vertical_photos']))
    result = {'vertical_photos': {}, 'tags': {}, 'pair_idx': {}}
    vertical = dict(w['vertical_photos'])
    for vid1 in w['vertical_photos']:
        del vertical[vid1]
        print(vid1)
        result['pair_idx'][vid1] = []
        for vid2 in vertical:
            new_id = "%s_%s" % (vid1, vid2)
            surrogate = {
                'id': [vid1, vid2],
                'type': 'V',
                'tags': list(set(w['images'][vid1]['tags'] + w['images'][vid2]['tags'])),
                'tags_count': w['images'][vid1]['tags_count'] + w['images'][vid2]['tags_count'],
            }
            for tag in surrogate['tags']:
                if tag not in result['tags']:
                    result['tags'][tag] = {}
                result['tags'][tag][new_id] = new_id
            result['pair_idx'][vid1].append(new_id)
            result['vertical_photos'][new_id] = surrogate

    return result


def get_candidates(photos, index, photo_id, id2 = None):
    candidates = {}
    for tag in photos[photo_id]['tags']:
        for candidate_id in index[tag]['index']:
            if candidate_id in photos:
                candidates[candidate_id] = candidate_id
    if id2:
        for tag in photos[id2]['tags']:
            for candidate_id in index[tag]['index']:
                if candidate_id in photos:
                    candidates[candidate_id] = candidate_id
    return candidates



def sol4(input_file):
    w = get_world(input_file)
    vertical = get_all_possible_vertical_candidates(w)
    pair_idx = vertical['pair_idx']

    photos = {}
    for photo_id in w['horizontal_photos']:
        photos[photo_id] = w['images'][photo_id]
        prev_photo_id = photo_id
    photos = dict(photos, **vertical['vertical_photos'])
    index = w['tags']
    for tag in vertical['tags']:
        if tag not in index:
            index[tag] = []
        index[tag]['index'] = dict(index[tag]['index'], **vertical['tags'][tag])

    gallery = []
    total_photos = len(photos)


    while True:
        prev_photo = photos[prev_photo_id]

        candidates = get_candidates(photos, index, prev_photo_id)
        print("Check %s find %d candidates" % (prev_photo_id, len(candidates)))

        if prev_photo['type'] == 'V':
            for vertical_photo_id in prev_photo['id']:
                for pair_id in pair_idx[vertical_photo_id]:
                    if pair_id in photos:
                        del photos[pair_id]
        else:
            del photos[prev_photo_id]

        best_score = -1
        best_candidate_id = False
        for candidate_id in candidates:
            if candidate_id in photos:
                s = score(prev_photo['tags'], photos[candidate_id]['tags'])
                if s >= best_score:
                    best_score = s
                    best_candidate_id = candidate_id

        if not best_candidate_id:
            break

        print("[%d/ %d] : Find best candidate for %s (%s) - %s (%s) with score %s" % (
            len(photos), total_photos, prev_photo_id, prev_photo['tags'], best_candidate_id,
            photos[best_candidate_id]['tags'], best_score
        ))

        gallery.append(photos[best_candidate_id]['id'])
        prev_photo_id = best_candidate_id

    output_file_name = input_file + '.out'
    output_to_file(output_file_name, gallery)
    return output_file_name


def get_max_score(photo):
    return len(photo['tags']) // 2

def sol5(input_file):
    w = get_world(input_file)

    prev_photo_id = 0
    best_vertical_pair_id = 0
    vertical_photos = {k: v for k, v in sorted(w['vertical_photos'].items(), key=lambda item: get_max_score(w['images'][item[1]]))}
    photos = w['images']
    index = w['tags']

    gallery = []
    total_photos = len(photos)

    while True:
        prev_photo = photos[prev_photo_id]

        candidates = get_candidates(photos, index, prev_photo_id)
        if best_vertical_pair_id:
            candidates = get_candidates(photos, index, prev_photo_id, best_vertical_pair_id)
            #print("Check %s_%s find %d candidates" % (prev_photo_id, best_vertical_pair_id, len(candidates)))
        else:
            candidates = get_candidates(photos, index, prev_photo_id)
            #print("Check %s find %d candidates" % (prev_photo_id, len(candidates)))

        del photos[prev_photo_id]
        if best_vertical_pair_id:
            del photos[best_vertical_pair_id]
            del vertical_photos[best_vertical_pair_id]

        best_score = -1
        best_candidate_id = False
        for candidate_id in candidates:
            if candidate_id in photos:
                if photos[candidate_id]['type'] == 'V':
                    cnt = 0
                    for vertical_id in vertical_photos:
                        if cnt > 10000:
                            break
                        cnt += 1
                        if vertical_id not in photos:
                            continue
                        if vertical_photos[vertical_id] < best_score:
                            break
                        tags_2 = photos[vertical_id]['tags'] + photos[candidate_id]['tags']
                        common = set(tags_2) & set(prev_photo['tags'])
                        if len(common) < best_score:
                            continue
                        diff_1 = set(prev_photo['tags']) - set(tags_2)
                        if len(diff_1) < best_score:
                            continue
                        diff_2 = set(tags_2) - set(prev_photo['tags'])
                        if len(diff_2) < best_score:
                            continue
                        s = min(len(diff_1), len(diff_2), len(common))
                        #s = score(prev_photo['tags'], photos[vertical_id]['tags'] + photos[candidate_id]['tags'])
                        if s >= best_score:
                            best_score = s
                            best_candidate_id = candidate_id
                            best_vertical_pair_id = vertical_id
                else:
                    s = score(prev_photo['tags'], photos[candidate_id]['tags'])
                    if s >= best_score:
                        best_score = s
                        best_candidate_id = candidate_id
                        best_vertical_pair_id = False
            if best_score >= (len(prev_photo['tags']) // 2):
                break
        if not best_candidate_id:
            break

        print("[%d/ %d] : Find best candidate for %s (%s) - %s_%s (%s) with score %s" % (
            len(photos), total_photos, prev_photo_id, prev_photo['tags'], best_candidate_id,
            best_vertical_pair_id, photos[best_candidate_id]['tags'], best_score
        ))

        if best_vertical_pair_id:
            gallery.append([best_candidate_id, best_vertical_pair_id])
        else:
            gallery.append([best_candidate_id])
        prev_photo_id = best_candidate_id

    output_file_name = input_file + '.out'
    output_to_file(output_file_name, gallery)
    return output_file_name


def index_tree(photos):
    idx = {k: set() for k in range(0, 100)}
    other_photos = dict(photos)
    for photo_id in photos:
        print("%s / %s \r" % (photo_id, len(photos)))
        del other_photos[photo_id]
        for other_photo_id in other_photos:
            common = bin(other_photos[other_photo_id]['bit_mask'] & photos[photo_id]['bit_mask']).count('1')
            idx[common].add(photo_id)
            idx[common].add(other_photo_id)
            #common = set(other_photos[other_photo_id]['tags']) & set(photos[photo_id]['tags'])
            #idx[len(common)].add(photo_id)
            #idx[len(common)].add(other_photo_id)
    return idx


def sol6(input_file):
    w = get_world(input_file, make_bit_mask=True)

    photos = w['images']
    tags = w['tags']
    index = {}
    candidates = {}

    index = index_tree(photos)
    print(index)

if __name__ == '__main__':

   # w = get_world('data/a_example.txt')
   # print(len(w['tags']))
   # print(len(w['images']))
   #w = get_world('data/b_lovely_landscapes.txt')
   # print(counts)
   # print(len(w['images']))
   # w = get_world('data/c_memorable_moments.txt')
   # print(len(w['tags']))
   # print(len(w['images']))
   # w = get_world('data/d_pet_pictures.txt')
   # print(len(w['tags']))
   # print(len(w['images']))
   # w = get_world('data/e_shiny_selfies.txt')
   # print(len(w['tags']))
   # print(len(w['images']))
   #

   total_score = 0
   start = time()

   output_filename = sol7('data/a_example.txt')
   total_score+= validation('data/a_example.txt', output_filename)

   output_filename = sol7('data/b_lovely_landscapes.txt')
   total_score += validation('data/b_lovely_landscapes.txt', output_filename)

   output_filename = sol7('data/c_memorable_moments.txt')
   total_score += validation('data/c_memorable_moments.txt', output_filename)

   output_filename = sol7('data/d_pet_pictures.txt')
   total_score += validation('data/d_pet_pictures.txt', output_filename)

   output_filename = sol7('data/e_shiny_selfies.txt')
   total_score += validation('data/e_shiny_selfies.txt', output_filename)

   # Total
   # 1023212, Time: 2451.4303073883057
   print("Total %s, Time: %s" % (total_score, time() - start))

