import re
import sys
import json
from utils import indexTwoSets, readFile, writePredict
import numpy as np
from numpy import dot
from numpy.linalg import norm


def readContent(content_file_name, ignore_header=True):
    with open(content_file_name, "r", encoding="utf8") as content_file:
        if ignore_header:
            return content_file.readlines()[1:]
        else:
            return content_file.readlines()


def processItemInformation(used_infos, raw_content):
    informations_items = {}
    all_items = set()

    def add_to(any_dict, origin_dict, key, value, split=None):
        if key not in origin_dict:
            return
        if origin_dict[key] == "N/A":
            return

        def add_some_key_to_any_dict(some_key):
            if some_key == "N/A":
                return
            if some_key not in any_dict:
                any_dict.setdefault(some_key, [value])
            else:
                any_dict[some_key].append(value)

        if callable(split):
            new_key = split(origin_dict[key])

            if isinstance(new_key, list):
                for i_new_key in new_key:
                    add_some_key_to_any_dict(i_new_key)
                return

            add_some_key_to_any_dict(new_key)
            return

        if split is None:
            add_some_key_to_any_dict(origin_dict[key])
        else:
            sp = origin_dict[key].split(split)
            for s in sp:
                new_key = s.strip()
                add_some_key_to_any_dict(new_key)

    for line in raw_content:
        pattern = re.compile('i([0-9]*),(.*)')
        groups = pattern.match(line).groups()
        item_id = groups[0]
        json_content = groups[1]
        dict_content = json.loads(json_content)

        item_id = int(item_id)
        all_items.add(item_id)

        for used_info in used_infos:
            if used_info in informations_items:
                add_to(informations_items[used_info], dict_content, used_info,
                       item_id,
                       split=used_infos[used_info])
            else:
                informations_items[used_info] = {}
                add_to(informations_items[used_info], dict_content, used_info,
                       item_id,
                       split=used_infos[used_info])
    return informations_items, all_items


def splitFim(my_str):
    return my_str.split(' ')[-1]


def splitStart(my_str):
    return my_str.split(' ')[0]


def splitLarge(my_str):
    return my_str.replace(',', '')


def splitCommaUnigram(my_str):
    unigrams = my_str.split(",")
    return unigrams

def splitCommaFirst(my_str):
    unigrams = my_str.split(",")
    return unigrams[0]

def splitCommaBigram(my_str):
    unigrams = my_str.split(",")
    bigrams = []
    for word in unigrams:
        bigrams.append(word)
        for other_word in unigrams:
            bigrams.append(word + "-" + other_word)
    return bigrams


def intervalRuntime(my_str, step_runtime=20, maximum_runtime=1000):
    runtime = float(my_str.split(' ')[0])
    for i in range(0, maximum_runtime, step_runtime):
        if runtime <= i:
            return "less" + str(i)
    return "larger"


def intervalYear(my_str, step_year=30, maximum_year=2100):
    year = int(my_str)
    for i in range(1890, maximum_year, step_year):
        if year <= i:
            return "less" + str(i)
    return "larger"


def intervalRating(my_str, step_rating=2, maximum_ratings=11):
    rating = float(my_str)
    for i in range(0, maximum_ratings, step_rating):
        if rating <= i:
            return "less" + str(i)
    return "larger"


def intervalImdbVotes(my_str, step_votes=20000, maximum_votes=1600000):
    n_votes = float(my_str.replace(",", ""))
    for i in range(0, maximum_votes, step_votes):
        if n_votes <= i:
            return "less" + str(i)
    return "larger"


def doNothing(my_str):
    return "N/A"


def createItemRepresentations(informations_items, all_items):
    num_factors = 0
    for keys_infos in informations_items:
        num_factors += len(informations_items[keys_infos])

    items_ids, _ = indexTwoSets(all_items, all_items)

    items_vectors = np.zeros((len(items_ids), num_factors))

    cont = 0
    for keys_infos in informations_items:
        for key in informations_items[keys_infos]:
            for i in informations_items[keys_infos][key]:
                items_vectors[items_ids[i]][cont] = 1
            cont += 1

    return items_vectors, items_ids


def createUserRepresentations(ratings_users_items, items_vectors, items_ids, users_ids):
    assert isinstance(items_vectors, np.ndarray) == True
    users_vectors = np.zeros((len(users_ids), items_vectors.shape[1]))

    for u in ratings_users_items:
        for i in ratings_users_items[u]:
            if i in items_ids:
                users_vectors[users_ids[u]] = users_vectors[users_ids[u]] + \
                                              items_vectors[items_ids[i]] * \
                                              ratings_users_items[u][i]
    return users_vectors


def computePredictions(u_i_to_predict, users_vectors, items_vectors, ids_users_vector, ids_items_vector,
                       users_dict_train, items_dict_train, type=1, mean_ratings=0):
    predictions = []
    predictions_mask = []

    for u, i in u_i_to_predict:
        if u in ids_users_vector and i in ids_items_vector:
            user_u_vector = users_vectors[ids_users_vector[u]]
            item_i_vector = items_vectors[ids_items_vector[i]]
            norma_denominator = norm(user_u_vector) * norm(item_i_vector)
            if norma_denominator == 0:
                if type == 1:
                    predictions.append(users_dict_train[u]['sum'] / users_dict_train[u]['cont'])
                elif type == 2 or type == 3:
                    predictions.append(0)
                predictions_mask.append(1)
            else:
                cos_sim = dot(user_u_vector, item_i_vector) / norma_denominator
                if type == 1:
                    predictions.append(cos_sim)
                elif type == 2 or type == 3:
                    predictions.append(cos_sim)
                predictions_mask.append(0)

        else:
            if type == 1:
                if u in users_dict_train:
                    predictions.append(users_dict_train[u]['sum'] / users_dict_train[u]['cont'])
                elif i in items_dict_train:
                    predictions.append(
                        items_dict_train[i]['sum'] / items_dict_train[i]['cont'])
                else:
                    predictions.append(mean_ratings)
            elif type == 2 or type == 3:
                predictions.append(0)
            predictions_mask.append(1)

    predictions = np.array(predictions)
    if type == 1:
        predsT = np.multiply(predictions, np.array(predictions_mask) == 0)
        predictions = predictions + 10 * (predsT / np.max(predsT))

    if type == 8:
        predsT = np.array(predictions)[np.array(predictions_mask) == 0]
        predictions = predictions + np.mean(predsT) * np.array(predictions_mask)
        min_preds = np.min(predictions)
        max_preds = np.max(predictions)

        npred = (predictions - min_preds) / (max_preds - min_preds)
        npred = npred * 10
        predictions = npred

    if type == 3:
        predsT = np.array(predictions)[np.array(predictions_mask) == 0]
        predictions = predictions + np.mean(predsT) * np.array(predictions_mask)

        npred = predictions * 10
        predictions = npred

    return predictions


if __name__ == "__main__":
    content_file = sys.argv[1]
    ratings_file = sys.argv[2]
    targets_file = sys.argv[3]

    content = readContent(content_file)

    used_infos = {
        'Title': doNothing,
        'Year': intervalYear,
        'Rated': None,
        'Released': doNothing,
        'Runtime': intervalRuntime,
        'Genre': splitCommaUnigram,
        'Director': doNothing,
        'Writer': doNothing,
        'Actors': splitCommaFirst,
        'Plot': doNothing,
        'Language': splitCommaUnigram,
        'Country': splitCommaUnigram,
        'imdbRating': intervalRating,
        'imdbVotes': doNothing
    }

    informations_items, all_items = processItemInformation(used_infos=used_infos, raw_content=content)
    items_vectors, ids_items_vector = createItemRepresentations(informations_items, all_items)

    users_dict_train, items_dict_train, ratings_train, mean_ratings = readFile(ratings_file)
    ids_users_vector, _ = indexTwoSets(users_dict_train, users_dict_train)

    users_vectors = createUserRepresentations(ratings_train, items_vectors, ids_items_vector, ids_users_vector)

    _, _, u_i_test, _ = readFile(targets_file, type_return="array", type="test")

    predictions = computePredictions(u_i_test, users_vectors, items_vectors, ids_users_vector, ids_items_vector,
                                     users_dict_train,
                                     items_dict_train, mean_ratings=mean_ratings)

    writePredict("targets-results.csv", u_i_test, predictions, verbose=True)
