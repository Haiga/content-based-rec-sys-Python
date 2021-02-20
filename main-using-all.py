import re
import json
from utils import indexTwoSets, readFile, writePredict
import numpy as np
from numpy import dot
from numpy.linalg import norm

with open("content.csv", "r", encoding="utf8") as content_file:
    content = content_file.readlines()[1:]


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
    for opt in options:
        try:
            items_infos = {}
            keys_infos_itens = {}

            used_infos = {
                'Title': ' ',
                'Year': None,
                'Rated': None,
                'Released': splitFim,
                'Runtime': intervalRuntime,
                'Genre': ',',
                'Director': ',',
                'Writer': ',',
                'Actors': ',',
                'Plot': ' ',
                'Language': ',',
                'Country': ',',
                'imdbRating': None
            }

            for not_used_opt in options:
                if opt != not_used_opt:
                    _ = used_infos.pop(not_used_opt, None)

            print(used_infos)

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

                for used_info in used_infos:
                    if used_info in keys_infos_itens:
                        add_to(keys_infos_itens[used_info], dict_content, used_info, item_id, split=used_infos[used_info])
                    else:
                        keys_infos_itens[used_info] = {}
                        add_to(keys_infos_itens[used_info], dict_content, used_info, item_id, split=used_infos[used_info])

            num_factors = 0
            for keys_conj in keys_infos_itens:
                num_factors += len(keys_infos_itens[keys_conj])

            print(f"Type Execution: {type}")
            print(f"Nº fatores: {num_factors}")

            items_ids, _ = indexTwoSets(items_infos, items_infos)

            users_dict, items_dict, u_i, mean_ratings = readFile("ratings.csv")
            a_users_dict, a_items_dict, a_u_i, a_mean_ratings = readFile("ratings.csv", type_return="array")

            users_ids, _ = indexTwoSets(users_dict, users_dict)

            items_vectors = np.zeros((len(items_ids), num_factors))
            users_vectors = np.zeros((len(users_ids), num_factors))

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

            preds = []
            users_test, items_test, u_i_test, _ = readFile("ratings.csv", type_return="array", type="train")
            preds_mask = []

            for u_i in u_i_test:
                u, i, r = u_i

                if u in users_ids and i in items_ids:
                    a = users_vectors[users_ids[u]]
                    b = items_vectors[items_ids[i]]
                    norma_den = norm(a) * norm(b)
                    if norma_den == 0:
                        if type == 1:
                            preds.append(users_dict[u]['sum'] / users_dict[u]['cont'])
                        elif type == 2 or type == 3:
                            preds.append(0)

                        preds_mask.append(1)
                    else:
                        cos_sim = dot(a, b) / (norma_den)
                        if type == 1:
                            preds.append(cos_sim * (users_dict[u]['sum'] / users_dict[u]['cont']))
                        elif type == 2 or type == 3:
                            preds.append(cos_sim)
                        preds_mask.append(0)
                else:
                    if type == 1:
                        if u in users_dict:
                            preds.append(users_dict[u]['sum'] / users_dict[u]['cont'])
                        elif i in items_dict:
                            preds.append(items_dict[i]['sum'] / items_dict[i]['cont'])
                        else:
                            preds.append(mean_ratings)
                    elif type == 2 or type == 3:
                        preds.append(0)

                    preds_mask.append(1)

            preds = np.array(preds)
            if type == 2:
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

            result = rmse(preds, np.array(a_u_i)[:, 2])
            if result < best:
                best = result
                conj_best = [type, opt]
                print("New Best")
            print(result)
            print("---------------")
        except:
            print("Execução com erro")
            print("---------------")

print("---------------\n\n")
print(f"Best RMSE: {best}")
print(conj_best)

