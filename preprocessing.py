def splitFim(my_str):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para extrair o ano de Release dos itens
        Ex.: "09 Jan 1894" -> "1984"
    """
    return my_str.split(' ')[-1]


def splitStart(my_str):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para extrair o tempo de Duração dos filmes
        Ex.: "125 min" -> "125"
    """
    return my_str.split(' ')[0]


def splitLarge(my_str):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para converter números longos para inteiros
        Ex.: "154,586,987,633" -> "154586987633"
    """
    return my_str.replace(',', '')


def splitCommaUnigram(my_str):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para separar os Gêneros dos filmes
        Ex.: "Ação, Romance" -> ["Ação", "Romance"]
    """
    unigrams = my_str.split(",")
    return unigrams


def splitCommaFirst(my_str):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para extrair o primeiro ator da lista de atores
        Ex.: "Scarlet, José" -> "Scarlet"
    """
    unigrams = my_str.split(",")
    return unigrams[0]


def splitCommaBigram(my_str):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para separar os Gêneros dos filmes e criar os bigramas
        Ex.: "Ação, Romance" -> ["Ação", "Romance", "Ação-Romance"]
    """
    unigrams = my_str.split(",")
    bigrams = []
    for word in unigrams:
        bigrams.append(word)
        for other_word in unigrams:
            bigrams.append(word + "-" + other_word)
    return bigrams


def intervalRuntime(my_str, step_runtime=20, maximum_runtime=1000):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para definir o intervalo ao qual pertence o tempo de duração
        Ex.: "120 min" -> "less150"
    """
    runtime = float(my_str.split(' ')[0])
    for i in range(0, maximum_runtime, step_runtime):
        if runtime <= i:
            return "less" + str(i)
    return "larger"


def intervalYear(my_str, step_year=30, maximum_year=2100):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para definir o intervalo ao qual pertence o ano de lançamento
        Ex.: "1950" -> "less2000"
    """
    year = int(my_str)
    for i in range(1890, maximum_year, step_year):
        if year <= i:
            return "less" + str(i)
    return "larger"


def intervalRating(my_str, step_rating=2, maximum_ratings=11):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para definir o intervalo ao qual pertence o rating
        Ex.: "9.8" -> "less10"
    """
    rating = float(my_str)
    for i in range(0, maximum_ratings, step_rating):
        if rating <= i:
            return "less" + str(i)
    return "larger"


def intervalImdbVotes(my_str, step_votes=20000, maximum_votes=1600000):
    """
        Funções simples para processar as features do conteúdo de itens,
            pode ser utilizada para definir o intervalo ao qual pertence o imdbVotes
        Ex.: "1200" -> "less3000"
    """
    n_votes = float(my_str.replace(",", ""))
    for i in range(0, maximum_votes, step_votes):
        if n_votes <= i:
            return "less" + str(i)
    return "larger"


def doNothing(my_str):
    """
        Funções simples para processar as features do conteúdo de itens
        Os métodos que retornam N/A não são utilizados para compor features das representações
    """
    return "N/A"