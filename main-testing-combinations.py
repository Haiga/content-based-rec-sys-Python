import re
import json
from utils import indexTwoSets, readFile, writePredict
import numpy as np
from numpy import dot
from numpy.linalg import norm
import time

mylogoutput = open('resultado2.log.txt', 'w')

with open("content.csv", "r", encoding="utf8") as content_file:
    content = content_file.readlines()[1:]

users_dict, items_dict, u_i_train, mean_ratings = readFile("train.csv")
a_users_dict, a_items_dict, a_u_i, a_mean_ratings = readFile("train.csv",
                                                             type_return="array")
users_ids, _ = indexTwoSets(users_dict, users_dict)
users_test, items_test, u_i_test, _ = readFile("test.csv",
                                               type_return="array",
                                               type="train")

step_runtime = 20
step_year = 10
step_rating = 2
# step_votes = 1000
step_votes = 20000

maximum_votes = 1600000
maximum_ratings = 11
maximum_year = 2100
maximum_runtime = 1000


def splitFim(my_str):
    return my_str.split(' ')[-1]


def splitStart(my_str):
    return my_str.split(' ')[0]


def splitLarge(my_str):
    return my_str.replace(',', '')


def splitCommaUnigram(my_str):
    unigrams = my_str.split(",")
    return unigrams


def splitCommaBigram(my_str):
    unigrams = my_str.split(",")
    bigrams = []
    for word in unigrams:
        bigrams.append(word)
        for other_word in unigrams:
            bigrams.append(word + "-" + other_word)
    return bigrams


def intervalRuntime(my_str):
    runtime = float(my_str.split(' ')[0])
    for i in range(0, maximum_runtime, step_runtime):
        if runtime <= i:
            return "less" + str(i)
    return "larger"


def intervalYear(my_str):
    year = int(my_str)
    for i in range(1890, maximum_year, step_year):
        if year <= i:
            return "less" + str(i)
    return "larger"


def intervalRating(my_str):
    rating = float(my_str)
    for i in range(0, maximum_ratings, step_rating):
        if rating <= i:
            return "less" + str(i)
    return "larger"


def intervalImdbVotes(my_str):
    n_votes = float(my_str.replace(",", ""))
    for i in range(0, maximum_votes, step_votes):
        if n_votes <= i:
            return "less" + str(i)
    return "larger"


def doNothing(my_str):
    return "N/A"


def rmse(y, yhat):
    y = np.array(y)
    yhat = np.array(yhat)
    return np.sqrt(np.mean((y - yhat) ** 2))


options = ['Title',
           'Year',
           'Rated',
           'Released',
           'Runtime',
           'Genre',
           'Director',
           'Writer',
           'Actors',
           'Plot',
           'Language',
           'Country',
           'imdbRating']

best = 10000
conj_best = []

for type in [1, 2, 3]:
    t3 = time.time()
    for year_param in [doNothing, None, intervalYear]:
        for rated_param in [doNothing, None]:
            for runtime_param in [doNothing, splitStart, intervalRuntime]:
                t1 = time.time()
                for genre_param in [doNothing, ',', splitCommaBigram]:
                    for language_param in [doNothing, ',']:
                        for country_param in [doNothing, ',']:
                            for imdb_param in [doNothing, None, intervalRating]:
                                for imbdvotes_param in [doNothing, None, intervalImdbVotes]:
                                    for opt2 in ['']:
                                        # for type in [1]:
                                        # for opt in options:
                                        for opt in ['']:
                                            try:
                                            # for inf in [1]:
                                                items_infos = {}
                                                keys_infos_itens = {}

                                                used_infos = {
                                                    # 'Title': ' ',
                                                    'Year': year_param,
                                                    'Rated': rated_param,
                                                    # 'Released': splitFim,
                                                    'Runtime': runtime_param,
                                                    'Genre': genre_param,
                                                    # 'Director': ',',
                                                    # 'Writer': ',',
                                                    # 'Actors': splitActor,
                                                    # 'Plot': ' ',
                                                    'Language': language_param,
                                                    'Country': country_param,
                                                    'imdbRating': imdb_param,
                                                    'imdbVotes': imbdvotes_param
                                                }

                                                print(used_infos)
                                                mylogoutput.write(str(used_infos) + "\n")

                                                for line in content:
                                                    pattern = re.compile('i([0-9]*),(.*)')
                                                    groups = pattern.match(line).groups()
                                                    item_id = groups[0]
                                                    json_content = groups[1]
                                                    dict_content = json.loads(json_content)


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


                                                    item_id = int(item_id)
                                                    items_infos[item_id] = dict_content

                                                    for used_info in used_infos:
                                                        if used_info in keys_infos_itens:
                                                            add_to(keys_infos_itens[used_info], dict_content, used_info,
                                                                   item_id,
                                                                   split=used_infos[used_info])
                                                        else:
                                                            keys_infos_itens[used_info] = {}
                                                            add_to(keys_infos_itens[used_info], dict_content, used_info,
                                                                   item_id,
                                                                   split=used_infos[used_info])

                                                num_factors = 0
                                                for keys_conj in keys_infos_itens:
                                                    num_factors += len(keys_infos_itens[keys_conj])

                                                # print(sorted([float(x) for x in keys_infos_itens['imdbVotes'].keys()]))
                                                print(f"Type Execution: {type}")
                                                mylogoutput.write(f"Type Execution: {type}" + "\n")
                                                print(f"Nº fatores: {num_factors}")
                                                mylogoutput.write(f"Nº fatores: {num_factors}" + "\n")
                                                items_ids, _ = indexTwoSets(items_infos, items_infos)

                                                items_vectors = np.zeros((len(items_ids), num_factors))
                                                users_vectors = np.zeros((len(users_ids), num_factors))

                                                cont = 0
                                                for nconj in keys_infos_itens:
                                                    for key in keys_infos_itens[nconj]:
                                                        for i in keys_infos_itens[nconj][key]:
                                                            items_vectors[items_ids[i]][cont] = 1
                                                        cont += 1

                                                for u in u_i_train:
                                                    for i in u_i_train[u]:
                                                        if i in items_ids:
                                                            # if u_i[u][i] >= users_dict[u]['sum'] / users_dict[u]['cont']:
                                                            users_vectors[users_ids[u]] = users_vectors[users_ids[u]] + \
                                                                                          items_vectors[items_ids[i]] * \
                                                                                          u_i_train[u][i]

                                                preds = []

                                                preds_mask = []

                                                num_ratings_without = 0
                                                all_num_ratings = 0
                                                all_num_items_without = 0
                                                all_without_nothing = 0
                                                for u_i in u_i_test:
                                                    u, i, r = u_i
                                                    all_num_ratings += 1
                                                    if u in users_ids and i in items_ids:
                                                        a = users_vectors[users_ids[u]]
                                                        b = items_vectors[items_ids[i]]
                                                        norma_den = norm(a) * norm(b)
                                                        if norma_den == 0:
                                                            if type == 1:
                                                                preds.append(
                                                                    users_dict[u]['sum'] / users_dict[u]['cont'])
                                                            elif type == 2 or type == 3:
                                                                preds.append(0)

                                                            preds_mask.append(1)
                                                            num_ratings_without += 1
                                                        else:
                                                            cos_sim = dot(a, b) / (norma_den)
                                                            if type == 1:
                                                                preds.append(cos_sim)
                                                            elif type == 2 or type == 3:
                                                                preds.append(cos_sim)
                                                            preds_mask.append(0)

                                                    else:
                                                        if type == 1:
                                                            if u in users_dict:
                                                                preds.append(
                                                                    users_dict[u]['sum'] / users_dict[u]['cont'])
                                                            elif i in items_dict:
                                                                preds.append(
                                                                    items_dict[i]['sum'] / items_dict[i]['cont'])
                                                                all_num_items_without += 1
                                                            else:
                                                                preds.append(mean_ratings)
                                                                all_without_nothing += 1
                                                        elif type == 2 or type == 3:
                                                            preds.append(0)

                                                        preds_mask.append(1)
                                                        num_ratings_without += 1
                                                # print(num_ratings_without / all_num_ratings)  # approx 19%
                                                # print(num_ratings_without)  ###sem informação do usuário ou sem informação do item, ou ambos
                                                # print(all_num_ratings)
                                                # print(all_num_items_without)  ###sem informação do usuário, com informação do item
                                                # print(all_without_nothing)  ###sem informação do usuário, sem informação do item
                                                preds = np.array(preds)
                                                if type == 1:
                                                    predsT = np.multiply(preds, np.array(preds_mask) == 0)
                                                    preds = preds + 10 * (predsT / np.max(predsT))

                                                if type == 8:
                                                    predsT = np.array(preds)[np.array(preds_mask) == 0]
                                                    preds = preds + np.mean(predsT) * np.array(preds_mask)
                                                    min_preds = np.min(preds)
                                                    max_preds = np.max(preds)

                                                    npred = (preds - min_preds) / (max_preds - min_preds)
                                                    npred = npred * 10
                                                    preds = npred

                                                if type == 3:
                                                    predsT = np.array(preds)[np.array(preds_mask) == 0]
                                                    preds = preds + np.mean(predsT) * np.array(preds_mask)

                                                    npred = preds * 10
                                                    preds = npred

                                                result = rmse(preds, np.array(u_i_test)[:, 2])
                                                if result < best:
                                                    best = result
                                                    conj_best = used_infos
                                                    print("New Best")
                                                    mylogoutput.write("New Best" + "\n")
                                                print(result)
                                                mylogoutput.write(str(result) + "\n")
                                                print("---------------")
                                                mylogoutput.write("---------------" + "\n")
                                                # writePredict("results.csv", u_i_test, preds)

                                            except:
                                                print("Execução com erro")
                                                print("---------------")
                                                mylogoutput.write("Execução com erro" + "\n")
                                                mylogoutput.write("---------------" + "\n")
                t2 = time.time()
                print("Tempo: " + str(t2 - t1))
    t4 = time.time()
    print("tempo2: " + str(t4 - t3))

print("---------------\n\n")
print(f"Best RMSE: {best}")
print(conj_best)

mylogoutput.write("---------------\n\n" + "\n")
mylogoutput.write(f"Best RMSE: {best}" + "\n")
mylogoutput.write(str(conj_best) + "\n")

mylogoutput.close()
