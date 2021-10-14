import os
import sys
import unicodedata
from dataclasses import dataclass

from flask import Flask, request
from flask_cors import CORS
from flask_restful import abort, Api, Resource
from local_storage import LocalStorage

similarity_algorithm = 'jieba'
#similarity_algorithm = 'simbert'
#similarity_algorithm = 'spacy'

if similarity_algorithm == 'simbert':
    from similarity_simbert import SimilarityCalc
elif similarity_algorithm == 'jieba':
    from similarity_jieba import SimilarityCalc
else:
    from similarity_spacy import SimilarityCalc

@dataclass
class Settings(object):
    db_name: str = 'news.db'
    table_name: str = 'news_record'

settings = Settings()

storage = LocalStorage(settings.db_name, settings.table_name)
storage.init_db()
storage.import_from_browser_history()

def create_similarity_calc(storage):
    visited = storage.retrieve(visited = True, topk = 2000)
    ref_texts = [ref['title'] for ref in visited]
    return SimilarityCalc(ref_texts)

similarity_calc = create_similarity_calc(storage)

def normalize(contents):
    for content in contents:
        if 'title' in content:
            content['title'] = unicodedata.normalize('NFKC', content['title'])
        else:
            print('content=', content)

class SaveToDatabase(Resource):
    def __init__(self):
        super(SaveToDatabase, self).__init__()

    def put(self):
        data = request.get_json()
        content = data['content']
        site = data['site']
        ignore_if_exists = data.get('ignore_if_exists', 0)

        if len(content) > 0:
            normalize(content)
            storage.save(content, ignore_if_exists)

            visited, unvisited = storage.count_pages()
            print(f'no. of visited news: {visited}')
            print(f'no. of unvisited news: {unvisited}')

        ret = []

        # ignore_if_exists == 1 means the request is from news index page
        # and we need to return which news to highlight
        if ignore_if_exists == 1:
            unvisited = storage.get_unvisited(site, topk = 100)
            unvisited_text = [news['title'] for news in unvisited]

            print('computing similarity...')
            scores = similarity_calc.compute(unvisited_text)
            print('finished computing similarity')

            entries = [(news['href'], score) for news, score in zip(unvisited, scores)]
            entries.sort(key = lambda x: -x[1])
            ret = [{'href': entry[0], 'score': entry[1]} for entry in entries]

        return ret, 200


def start_app(debug = False):
    app = Flask(__name__)
    CORS(app)
    api = Api(app)
    
    ##
    ## Actually setup the Api resource routing here
    ##
    api.add_resource(SaveToDatabase, '/savenews')
    app.run(debug = debug)

if __name__ == '__main__':    
    start_app(debug=True)