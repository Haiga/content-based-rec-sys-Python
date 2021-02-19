import re
import json
from utils import indexTwoSets, readFile, writePredict
import numpy as np

with open("content.csv", "r", encoding="utf8") as content_file:
    content = content_file.readlines()[1:]

first = True
items_infos = {}
# genres = {}
# years = {}
# releases = {}
# runtimes = {}
# languages = {}
# countries = {}
# imdb_ratings = {}
keys_infos_itens = {}
for line in content:
    pattern = re.compile('i([0-9]*),(.*)')
    groups = pattern.match(line).groups()
    item_id = groups[0]
    json_content = groups[1]
    dict_content = json.loads(json_content)
    if first:
        comp = sorted(dict_content.keys())
        print(dict_content.keys())
        first = False


    def add_to(any_dict, origin_dict, key, value, split=None):
        if key not in origin_dict:
            return
        if origin_dict[key] == "N/A":
            return
        if callable(split):
            new_key = split(origin_dict[key])
            if new_key == "N/A":
                return
            if new_key not in any_dict:
                any_dict.setdefault(new_key, [value])
            else:
                any_dict[new_key].append(value)
            return

        if split is None:
            new_key = key
            if new_key == "N/A":
                return
            if new_key not in any_dict:
                any_dict.setdefault(origin_dict[new_key], [value])
            else:
                any_dict[origin_dict[new_key]].append(value)
        else:
            sp = origin_dict[key].split(split)
            for s in sp:
                new_key = s.strip()
                if new_key == "N/A":
                    continue
                if new_key not in any_dict:
                    any_dict.setdefault(new_key, [value])
                else:
                    any_dict[new_key].append(value)


    item_id = int(item_id)
    items_infos[item_id] = dict_content


    def splitFim(my_str):
        return my_str.split(' ')[-1]

    def splitStart(my_str):
        return my_str.split(' ')[0]

    def intervalRuntime(my_str):
        execution_time = float(my_str.split(' ')[0])
        if execution_time < 20:
            return "less20"
        elif execution_time < 40:
            return "less40"
        elif execution_time < 60:
            return "less60"
        elif execution_time < 80:
            return "less80"
        elif execution_time < 100:
            return "less100"
        elif execution_time < 120:
            return "less120"
        else:
            return "larger"

    used_infos = {
        # 'Title': ' ',
        'Year': None,
        # 'Rated': None,
        'Released': splitFim,
        'Runtime': intervalRuntime,
        'Genre': ',',
        # 'Director': ',',
        # 'Writer': ',',
        # 'Actors': ',',
        # 'Plot': ' ',
        'Language': ',',
        'Country': ',',
        'imdbRating': None
    }
    # Writer tem informações esquisitas
    # Awards  Poster Metascore imdbVotes imdbID Type Response removi
    # split = [' ', None, None, None, None, ',', ',', ',', ',', ' ',
    #          ',', ',', None]
    for used_info in used_infos:
        if used_info in keys_infos_itens:
            add_to(keys_infos_itens[used_info], dict_content, used_info, item_id, split=used_infos[used_info])
        else:
            keys_infos_itens[used_info] = {}
            add_to(keys_infos_itens[used_info], dict_content, used_info, item_id, split=used_infos[used_info])

num_factors = 0
for keys_conj in keys_infos_itens:
    num_factors += len(keys_infos_itens[keys_conj])

print(num_factors)

items_ids, _ = indexTwoSets(items_infos, items_infos)
# print(len(items_ids))
# print(num_factors)

users_dict, items_dict, u_i, mean_ratings = readFile("ratings.csv")
# print(len(users_dict))
print(mean_ratings)
users_ids, _ = indexTwoSets(users_dict, users_dict)

items_vectors = np.zeros((len(items_ids), num_factors))
users_vectors = np.zeros((len(users_ids), num_factors))

# cont = 0
# for nconj in keys_infos_itens:
#     for conj in keys_infos_itens[nconj]:
#         keys_conj = keys_infos_itens[nconj][conj].keys()
#         for key in keys_conj:
#             for i in conj[key]:
#                 items_vectors[items_ids[i]][cont] = 1
#             cont += 1
cont = 0
for nconj in keys_infos_itens:
    for key in keys_infos_itens[nconj]:
        for i in keys_infos_itens[nconj][key]:
            items_vectors[items_ids[i]][cont] = 1
        cont += 1

for u in u_i:
    for i in u_i[u]:
        if i in items_ids:
            users_vectors[users_ids[u]] = users_vectors[users_ids[u]] + items_vectors[items_ids[i]] * u_i[u][i]

# Iremos varrer o conjunto de teste, se o usuário ou item não existir nos conjuntos
# setamos 8 para o rating deles,
# TODO calcular a media por usuário e a média global, quando não tiver utilizá-los

from numpy import dot
from numpy.linalg import norm

preds = []
users_test, items_test, u_i_test, _ = readFile("targets.csv", type_return="array", type="test")
preds2 = []
for u_i in u_i_test:
    u, i = u_i

    if u in users_ids and i in items_ids:
        a = users_vectors[users_ids[u]]
        b = items_vectors[items_ids[i]]
        norma_den = norm(a) * norm(b)
        if norma_den == 0:
            preds.append(users_dict[u]['sum']/users_dict[u]['cont'])
            # preds.append(0)
            preds2.append(1)
        else:
            cos_sim = dot(a, b) / (norma_den)
            preds.append(cos_sim * (users_dict[u]['sum']/users_dict[u]['cont']))
            # preds.append(cos_sim)
            preds2.append(0)
    else:
        if u in users_dict:
            preds.append(users_dict[u]['sum']/users_dict[u]['cont'])
        elif i in items_dict:
            preds.append(items_dict[i]['sum'] / items_dict[i]['cont'])
        else:
            preds.append(mean_ratings)
        # cos_sim = 8
        # # cos_sim = 0
        # preds.append(cos_sim)
        preds2.append(1)

# predsT = np.array(preds)[np.array(preds2) == 0]
# preds = preds + np.mean(predsT) * np.array(preds2)
# min_preds = np.min(preds)
# max_preds = np.max(preds)
#
# npred = (preds - min_preds)/(max_preds - min_preds)
# writePredict("results.csv", u_i_test, npred*10)


writePredict("iresults.csv", u_i_test, preds)
# 2.53 de RMSE
