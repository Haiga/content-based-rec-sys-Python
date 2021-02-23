import sys
from CB import CBCosineSimilarity
from utils import readFile, writePredict
from preprocessing import *

if __name__ == "__main__":
    content_file = sys.argv[1]
    ratings_file = sys.argv[2]
    targets_file = sys.argv[3]

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

    model = CBCosineSimilarity(content_file_name=content_file, used_infos=used_infos)
    model.fit(ratings_file)

    _, _, u_i_test, _ = readFile(targets_file, type_return="array", type="test")
    predictions = model.predict(u_i_test)

    writePredict("targets-results.csv", u_i_test, predictions, verbose=True)
