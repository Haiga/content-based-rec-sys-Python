import numpy as np
from numpy import dot
from numpy.linalg import norm
import re
import json

from utils import indexTwoSets, readFile, readContent


class CBCosineSimilarity:
    def __init__(self, content_file_name, used_infos):
        """
            Parameters
            ----------
            content_file_name: str Nome do arquivo que será lido em utf-8
            used_infos: dict Contém a chave para as informações que serão processadas segundo o conteúdo da chave
            e que irão compor o dicionário de retorno, podem ser funções para definir intervalos ou processar strings
            raw_content: array É um array com a representação de cada item, onde cada linha tem  formato  itemId:JsonContent
            Returns
            -------
        """
        content = readContent(content_file_name)
        self.informations_items, self.all_items = self.processItemInformation(used_infos=used_infos,
                                                                              raw_content=content)
        self.items_vectors, self.ids_items_vector = self.createItemRepresentations(self.informations_items,
                                                                                   self.all_items)

    def fit(self, ratings_file):
        """
        Cria os seguintes atributos utilizados para calcular predições
        users_vectors : np.ndarray com formato len(users_ids) x  items_vectors.shape[1]
            Esse vetor é a representação vetorial dos usuários que possuem ratings
        items_vectors : np.ndarray com formato len(items_ids) x número de features
            O 1 nesse vetor em uma posisão i,j significa que o item i possui o atributo j
            O 0 nesse vetor em uma posisão i,j significa que o item i não possui o atributo j
        ids_items_vector: Dict
            É um dicionário mapeando o identificador do item a sua posição na matriz item_vectors
            O item 'i0005' está na linha items_ids['i0005'] de items_vectors
        ids_users_vector: Dict
            É um dicionário mapeando o identificador do usuário a sua posição na matriz users_vectors
            O usuário 'u0999' estará na linha users_ids['u0999'] de users_vectors
        users_dict_train: Dict informações relativas ao usuários, ex.: número de ratings do usuário, média dos ratings
            do usuário. É mapeado pelo UserID
        items_dict_train: Dict informações relativas ao itens, ex.: número de ratings do item, média dos ratings
            do item. É mapeado pelo ItemID

        Parameters
            ratings_file: str O nome do arquivo a ser lido, contém os ratings para os pares de usuário id
        """
        self.users_dict_train, self.items_dict_train, self.ratings_train, self.mean_ratings = readFile(ratings_file)
        self.ids_users_vector, _ = indexTwoSets(self.users_dict_train, self.users_dict_train)

        self.users_vectors = self.createUserRepresentations(self.ratings_train, self.items_vectors,
                                                            self.ids_items_vector, self.ids_users_vector)

    def processItemInformation(self, used_infos, raw_content):
        """
            Parameters
            ----------
            used_infos: dict Contém a chave para as informações que serão processadas segundo o conteúdo da chave
            e que irão compor o dicionário de retorno, podem ser funções para definir intervalos ou processar strings
            raw_content: array É um array com a representação de cada item, onde cada linha tem  formato  itemId:JsonContent
            Returns
            -------
            informations_items : Dict
                É um dicionário que mapeia as chaves de used_infos aos subniveis possiveis dessas chaves, e que por fim mapeia
                    os itens que possuem essas características
                    Ex.: {'Actor':{'Scarlet': [1, 2, 8, 10]}, 'Year':{'before1990': [5, 6]}}
                    Os itens 1, 2, 8 e 10 possuem 'Scarlet' como atriz
                    Os itens 5 e 6 foram lançados 'before1990'
            all_items : Dict
                É um set com os ids dos itens presentes no raw_content
        """
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

    def createItemRepresentations(self, informations_items, all_items):
        """
            Parameters
            ----------
            informations_items: Dict Dicionário no formato 'Chave-Classe-Pai': {'Chave-Classe-Filha': [array_of_itens]}
            all_items: set Conjunto de itens para os quais serão computadas as representações
            Returns
            -------
            items_vectors : np.ndarray com formato len(items_ids) x número de features
                Onde o número de features é a quantidade de chaves do tipo 'Chave-Classe-Filha'
                O 1 nesse vetor em uma posisão i,j significa que o item i possui o atributo j
                O 0 nesse vetor em uma posisão i,j significa que o item i não possui o atributo j
            items_ids: Dict
                É um dicionário mapeando o identificador do item a sua posição na matriz item_vectors
                O item 'i0005' está na linha all_items['i0005'] de items_vectors
        """
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

    def createUserRepresentations(self, ratings_users_items, items_vectors, items_ids, users_ids):
        """
            Parameters
            ----------
            ratings_users_items: Dict Dicionário no formato 'UserID': {'ItemID': rating]}
            items_vectors : np.ndarray com formato len(items_ids) x número de features
                O 1 nesse vetor em uma posisão i,j significa que o item i possui a feature j
                O 0 nesse vetor em uma posisão i,j significa que o item i não possui a feature j
            items_ids: Dict
                É um dicionário mapeando o identificador do item a sua posição na matriz item_vectors
                O item 'i0005' está na linha items_ids['i0005'] de items_vectors
            users_ids: Dict
                É um dicionário mapeando o identificador do usuário a sua posição na matriz users_vectors
                O usuário 'u0999' estará na linha users_ids['u0999'] de users_vectors
            Returns
            -------
            users_vectors : np.ndarray com formato len(users_ids) x  items_vectors.shape[1]
                Esse vetor é calculado somando-se o produto escalar de todos os ratings do usuário u para os itens que avaliou
                com a representação vetorial de cada item respectivamente

        """
        assert isinstance(items_vectors, np.ndarray) == True
        users_vectors = np.zeros((len(users_ids), items_vectors.shape[1]))

        for u in ratings_users_items:
            for i in ratings_users_items[u]:
                if i in items_ids:
                    users_vectors[users_ids[u]] = users_vectors[users_ids[u]] + \
                                                  items_vectors[items_ids[i]] * \
                                                  ratings_users_items[u][i]
        return users_vectors

    def predict(self, u_i_to_predict, type=1, fator_multiply=10):
        """
            Parameters
            ----------
            u_i_to_predict: array of (u, i) para ser computado o rating do user u para o item i
            type: int Para type==1 utiliza a média dos ratings de treino quandoo usuário não avaliou nenhum item
                Para type==2 é feita uma normalização entre 0 e 1 dos valorespreditos antes de multiplicar por fator_multiply
                Para type==3 o valor de similaridade é multiplicado por fator_multiply após atribuir para os usuários que não
                avaliaram nenhum item a média das similaridades do teste
            mean_ratings: float Caso não exista informação relativa ao usuário ou para o item em u_i_to_predict, esse valor
                é retornado
            fator_multiply: float Após computar a similaridade esse valor é utilizado para normalizar o rating predito
            Returns
            -------
            predictions: array
                Retorna um array com a predição do rating para cada U_I em u_i_to_predict
        """

        predictions = []
        predictions_mask = []

        for u, i in u_i_to_predict:
            if u in self.ids_users_vector and i in self.ids_items_vector:
                user_u_vector = self.users_vectors[self.ids_users_vector[u]]
                item_i_vector = self.items_vectors[self.ids_items_vector[i]]
                norma_denominator = norm(user_u_vector) * norm(item_i_vector)
                if norma_denominator == 0:
                    if type == 1:
                        predictions.append(self.users_dict_train[u]['sum'] / self.users_dict_train[u]['cont'])
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
                    if u in self.users_dict_train:
                        predictions.append(self.users_dict_train[u]['sum'] / self.users_dict_train[u]['cont'])
                    elif i in self.items_dict_train:
                        predictions.append(
                            self.items_dict_train[i]['sum'] / self.items_dict_train[i]['cont'])
                    else:
                        predictions.append(self.mean_ratings)
                elif type == 2 or type == 3:
                    predictions.append(0)
                predictions_mask.append(1)

        predictions = np.array(predictions)
        if type == 1:
            predsT = np.multiply(predictions, np.array(predictions_mask) == 0)
            predictions = predictions + fator_multiply * (predsT / np.max(predsT))

        if type == 2:
            predsT = np.array(predictions)[np.array(predictions_mask) == 0]
            predictions = predictions + np.mean(predsT) * np.array(predictions_mask)
            min_preds = np.min(predictions)
            max_preds = np.max(predictions)

            npred = (predictions - min_preds) / (max_preds - min_preds)
            npred = npred * fator_multiply
            predictions = npred

        if type == 3:
            predsT = np.array(predictions)[np.array(predictions_mask) == 0]
            predictions = predictions + np.mean(predsT) * np.array(predictions_mask)

            npred = predictions * fator_multiply
            predictions = npred

        return predictions
