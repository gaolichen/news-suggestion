import numpy as np
from bert4keras.backend import keras, K
from bert4keras.models import build_transformer_model
from bert4keras.tokenizers import Tokenizer
from bert4keras.snippets import sequence_padding

maxlen = 32
config_path = 'E:/deeplearning-data/simbert/chinese_simbert_L-4_H-312_A-12/bert_config.json'
checkpoint_path = 'E:/deeplearning-data/simbert/chinese_simbert_L-4_H-312_A-12/bert_model.ckpt'
dict_path = 'E:/deeplearning-data/simbert/chinese_simbert_L-4_H-312_A-12/vocab.txt'

class SimilarityCalc(object):
    def __init__(self, ref_texts, topk = 10):
        self.ref_texts = ref_texts
        self.topk = topk
        self.tokenizer = Tokenizer(dict_path, do_lower_case=True) 

        bert = build_transformer_model(
            config_path,
            checkpoint_path,
            with_pool='linear',
            application='unilm',
            return_keras_model=False,
        )

        self.encoder = keras.models.Model(bert.model.inputs, bert.model.outputs[0])
        self.ref_vec = np.transpose(self.sentence_vector(ref_texts))
    
    def sentence_vector(self, texts):
        token_ids = []
        for text in texts:
            ids, _ = self.tokenizer.encode(text, maxlen=maxlen)
            token_ids.append(ids)

        token_ids = sequence_padding(token_ids)
        segment_ids = [[0] * len(tok) for tok in token_ids]
        
        inputs = [np.array(token_ids), np.array(segment_ids)]
        vec = self.encoder(inputs)
        vec_n = np.linalg.norm(vec, axis = 1, keepdims = True)
        return np.divide(vec, vec_n)
    
    def compute(self, target_texts):
        target_vec = self.sentence_vector(target_texts)

        scores = np.matmul(target_vec, self.ref_vec)
        scores = np.sort(scores, axis = -1)[:,:self.topk]
        scores = np.mean(scores, axis = -1)
        return scores.tolist()

    def topk_similar(self, target, topk = 10):
        vec = self.sentence_vector([target])

        scores = np.matmul(vec, self.ref_vec)[0]
        text_scores = [(text, score) for text, score in zip(self.ref_texts, scores)]
        text_scores.sort(key = lambda x : -x[1])
        return text_scores[:topk]

if __name__ == '__main__':
    from local_storage import LocalStorage
    import random
    storage = LocalStorage('news.db', 'news_record')
    visited = storage.retrieve(visited = True, topk = 2000)
    unvisited = storage.get_unvisited(site = 'backchina', topk = 10)

    target_texts = [target['title'] for target in unvisited]
    ref_texts = [ref['title'] for ref in visited]

    calc = SimilarityCalc(ref_texts, topk = 10)
#    print(calc.sentence_vector(ref_texts[1:10]))
    text = target_texts[1]
    print(calc.compute([text]))
    print(text)
    res = calc.topk_similar(text, topk = 10)
    print(res)