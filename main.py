import re
import json

with open("content.csv", "r", encoding="utf8") as content_file:
    content = content_file.readlines()[1:]


def my_prepro(info_dict):
    info_dict['Genre'].split(",")


first = True
items_infos = {}
genres = set()
years = set()
releases = set()
runtimes = set()
languages = set()
countries = set()
imdb_ratings = set()
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
    # else:
    #     if sorted(dict_content.keys()) != comp:
    #         print(dict_content.keys())
    #         print(item_id)
    #         print("diff")
    # break
    items_infos[item_id] = dict_content
    if 'Genre' in dict_content:
        sp = dict_content['Genre'].split(",")
        for genre in sp:
            if genre.strip() != "N/A":
                genres.add(genre.strip())
    if 'Year' in dict_content:
        if dict_content['Year'] != "N/A":
            years.add(dict_content['Year'])
    if 'Released' in dict_content:
        if dict_content['Released'] != "N/A":
            releases.add(dict_content['Released'].split(" ")[-1])
    if 'Runtime' in dict_content:
        if dict_content['Runtime'] != "N/A":
            runtimes.add(dict_content['Runtime'].split(" ")[0])
    if 'Language' in dict_content:
        if dict_content['Language'] != "N/A":
            for lang in dict_content['Language'].split(","):
                languages.add(lang.strip())
    if 'Country' in dict_content:
        if dict_content['Country'] != "N/A":
            for count in dict_content['Country'].split(","):
                countries.add(count.strip())
    if 'imdbRating' in dict_content:
        if dict_content['imdbRating'] != "N/A":
            imdb_ratings.add(dict_content['imdbRating'])
# print(items_infos)
print(genres)
print(years)
print(releases)
print(runtimes)
print(languages)
print(countries)
print(imdb_ratings)
