import math
from pprint import pprint
from time import time

from common import get_world, output_to_file

LIMIT = 5000


def get_candidates(photos, index, slide_id, slide_tags, index_key='index', limit=LIMIT):
    candidates = {}
    slide_tags_count = len(slide_tags)

    for tag in slide_tags:
        if tag not in index:
            continue
        for candidate_id in list(index[tag][index_key])[0:limit]:
            if candidate_id not in photos:
                continue
            if candidate_id not in slide_id:
                if candidate_id not in candidates:
                    candidates[candidate_id] = {
                        'common': 1,
                        'type': photos[candidate_id]['type'],
                        'tags_count': photos[candidate_id]['tags_count'],
                        'score': min(1, photos[candidate_id]['tags_count'] - 1),
                    }
                else:
                    candidates[candidate_id]['common'] += 1
                    candidates[candidate_id]['score'] = min(
                        candidates[candidate_id]['common'],
                        slide_tags_count - candidates[candidate_id]['common'],
                        candidates[candidate_id]['tags_count'] - candidates[candidate_id]['common']
                    )
    return candidates


def get_vertical_candidates(verticals, vertical_index, candidate_id, candidate, slide_id, slide_tags):
    slide_id = list(slide_id)
    slide_id.append(candidate_id)
    slide_tags_count = len(slide_tags)
    max_score = slide_tags_count // 2
    vertical_tags = verticals[candidate_id]['tags']

    additional_tags = list(set(slide_tags) - set(vertical_tags))
    candidates = get_candidates(verticals, vertical_index, slide_id, additional_tags)
    candidates = {k: v for k, v in
                  sorted(candidates.items(),
                         key=lambda item: abs(item[1]['common'] - max_score),
                         reverse=False)}

    return candidates


def get_tags(photos, slide_id):
    tags = []
    for photo_id in slide_id:
        tags += photos[photo_id]['tags']
    return list(set(tags))


def get_max_score(photos, slide_id):
    tags = get_tags(photos, slide_id)
    return len(tags) // 2


def filter_vertical_candidates(candidates):
    vertical_candidates = {}
    for candidate_id, candidate in candidates.items():
        if candidate['type'] == 'V':
            vertical_candidates[candidate_id] = candidate
    return vertical_candidates


def get_next_slide(photos):
    res = []
    for photo_id, photo in photos.items():
        if photo['type'] == 'V':
            res.append(photo_id)
            if len(res) == 2:
                return res
        else:
            return [photo_id]
    return None


def sol7(input_file):
    w = get_world(input_file, make_bit_mask=False)
    gallery = []

    photos = {}
    tags = dict(w['tags'])

    for photo_id, photo in w['images'].items():
        photos[photo_id] = photo
        photos[photo_id]['max_score'] = get_max_score(photos, [photo_id])

    photos = {k: v for k, v in sorted(photos.items(), key=lambda item: item[1]['max_score'], reverse=True)}\

    for tag in tags:
        tags[tag]['index'] = {k: v for k, v in sorted(tags[tag]['index'].items(), key=lambda item: photos[item[0]]['max_score'], reverse=True)}

    vertical = {}
    vertical_tags = {}

    c = 0
    for photo_id, photo in photos.items():
        print("Build vertical index %d/%d..." % (c, len(photos)), end="\r")
        c += 1
        if photo['type'] == 'V':
            vertical[photo_id] = photo
            for tag in photo['tags']:
                if tag not in vertical_tags:
                    vertical_tags[tag] = {'index': {}}
                vertical_tags[tag]['index'][photo_id] = photo_id\

    for tag in vertical_tags:
        vertical_tags[tag]['index'] = {k: v for k, v in
                              sorted(vertical_tags[tag]['index'].items(), key=lambda item: photos[item[0]]['max_score'], reverse=True)}

    vertical = {k: v for k, v in sorted(vertical.items(), key=lambda item: item[1]['max_score'], reverse=True)}

    total_photos = len(photos)
    total_score = 0

    last_slide_id = get_next_slide(photos)

    while last_slide_id is not None:
        checked_candidates = 0
        start = time()
        gallery.append(last_slide_id)
        slide_tags = get_tags(w['images'], last_slide_id)
        slide_tags_count = len(slide_tags)
        max_score = get_max_score(photos, last_slide_id)

        best_slide_id = []
        best_score = -1

        candidates = get_candidates(photos, tags, last_slide_id, slide_tags)
        candidates = {k: v for k, v in
                      sorted(candidates.items(),
                             key=lambda item: (item[1]['score'] * 10000 + item[1]['tags_count']),
                             reverse=True)}

        for candidate_id, candidate in candidates.items():
            checked_candidates += 1
            if best_score == max_score or candidate['score'] < best_score:
                break
            if candidate['type'] == 'V':
                vertical_candidates = get_vertical_candidates(vertical, vertical_tags, candidate_id, candidate, last_slide_id, slide_tags)
                for vertical_candidate_id, vertical_candidate in vertical_candidates.items():
                    vertical_common = len(set(slide_tags) & set(photos[candidate_id]['tags'] + photos[vertical_candidate_id]['tags']))
                    vertical_count = photos[candidate_id]['tags_count'] + photos[vertical_candidate_id]['tags_count'] - vertical_common
                    score = min(vertical_common, slide_tags_count - vertical_common, vertical_count - vertical_common)
                    if score > best_score:
                        best_score = score
                        best_slide_id = [candidate_id, vertical_candidate_id]
            else:
                score = candidate['score']
                if score > best_score:
                    best_score = score
                    best_slide_id = [candidate_id]
                if best_score == max_score:
                    break

        for photo_id in last_slide_id:
            for tag in photos[photo_id]['tags']:
                tags[tag]['index'] = list(filter(lambda item: item != photo_id, tags[tag]['index']))
            if photo_id in vertical:
                for tag in vertical[photo_id]['tags']:
                    vertical_tags[tag]['index'] = list(
                        filter(lambda item: item != photo_id, vertical_tags[tag]['index'])
                    )

        print("[%d/%d] : Find score %s/%d best candidate %s for %s checked(%s/%s) %3.6f" % (
            len(photos), total_photos, best_score, get_max_score(photos, last_slide_id), best_slide_id, last_slide_id,
            checked_candidates, len(candidates), time() - start
        ))

        for photo_id in last_slide_id:
            del photos[photo_id]
            if photo_id in vertical:
                del vertical[photo_id]


        if len(best_slide_id) > 0:
            last_slide_id = best_slide_id
            total_score += best_score
        else:
            last_slide_id = get_next_slide(photos)

        if last_slide_id is None:
            break

    print(total_score)
    output_file_name = input_file + '.out'
    output_to_file(output_file_name, gallery)
    return output_file_name
