import re
import json
from utils import indexTwoSets, readFile, writePredict
import numpy as np

with open("content.csv", "r", encoding="utf8") as content_file:
    content = content_file.readlines()[1:]

first = True
items_infos = {}
genres = {}
titles = {}
# years = {}
# releases = {}
# runtimes = {}
languages = {}
countries = {}
# imdb_ratings = {}

for line in content:
    pattern = re.compile('i([0-9]*),(.*)')
    groups = pattern.match(line).groups()
    item_id = groups[0]
    json_content = groups[1]
    dict_content = json.loads(json_content)
    if first:
        comp = sorted(dict_content.keys())
        # print(dict_content.keys())
        first = False


    def add_to(any_dict, origin_dict, key, value, split=None):
        if key not in origin_dict:
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
                if len(new_key) <= 3 and split == " ":
                    continue
                if new_key not in any_dict:
                    any_dict.setdefault(new_key, [value])
                else:
                    any_dict[new_key].append(value)


    item_id = int(item_id)
    items_infos[item_id] = dict_content
    add_to(genres, dict_content, 'Genre', item_id, split=",")
    add_to(titles, dict_content, 'Title', item_id, split=" ")
    # add_to(years, dict_content, 'Year', item_id)
    # add_to(releases, dict_content, 'Released', item_id)
    # add_to(runtimes, dict_content, 'Runtime', item_id)
    add_to(languages, dict_content, 'Language', item_id, split=",")
    add_to(countries, dict_content, 'Country', item_id, split=",")
    # add_to(imdb_ratings, dict_content, 'imdbRating', item_id)

# print(genres)
# print(years)
# print(releases)
# print(runtimes)
# print(languages)
# print(countries)
# print(imdb_ratings)

keys_genres = genres.keys()
keys_titles = titles.keys()
# keys_years = years.keys()
# keys_releases = releases.keys()
# keys_runtimes = runtimes.keys()
keys_languages = languages.keys()
keys_countries = countries.keys()
# keys_imdb_ratings = imdb_ratings.keys()

num_factors = 0
# for keys_conj in [keys_genres, keys_years, keys_releases, keys_runtimes, keys_languages, keys_countries,
#                   keys_imdb_ratings]:
for keys_conj in [keys_genres, keys_titles, keys_languages, keys_countries]:
    num_factors += len(keys_conj)

items_ids, _ = indexTwoSets(items_infos, items_infos)
# print(len(items_ids))
# print(num_factors)

users_dict, items_dict, u_i = readFile("ratings.csv")
# print(len(users_dict))
users_ids, _ = indexTwoSets(users_dict, users_dict)

items_vectors = np.zeros((len(items_ids), num_factors))
users_vectors = np.zeros((len(users_ids), num_factors))

cont = 0
for conj in [genres, titles, languages, countries]:
    keys_conj = conj.keys()
    for key in keys_conj:
        for i in conj[key]:
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
users_test, items_test, u_i_test = readFile("targets.csv", type_return="array", type="test")
preds2 = []
for u_i in u_i_test:
    u, i = u_i

    if u in users_ids and i in items_ids:
        a = users_vectors[users_ids[u]]
        b = items_vectors[items_ids[i]]
        norma_den = norm(a) * norm(b)
        if norma_den == 0:
            preds.append(8)
            # preds.append(0)
            preds2.append(1)
        else:
            cos_sim = dot(a, b) / (norma_den)
            preds.append(cos_sim * 10)
            # preds.append(cos_sim)
            preds2.append(0)
    else:
        cos_sim = 8
        # cos_sim = 0
        preds.append(cos_sim)
        preds2.append(1)

# predsT = np.array(preds)[np.array(preds2) == 0]
# preds = preds + np.mean(predsT) * np.array(preds2)
# min_preds = np.min(preds)
# max_preds = np.max(preds)
#
# npred = (preds - min_preds)/(max_preds - min_preds)
# writePredict("results.csv", u_i_test, npred*10)


writePredict("results.csv", u_i_test, preds)
#2.77 de RMSE