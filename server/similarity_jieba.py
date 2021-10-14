import jieba
import jieba.analyse

class SimilarityCalc(object):
    def __init__(self, texts, topk = 100):
        content = '\n'.join(texts)
        self.tags = jieba.analyse.extract_tags(content, topK = topk, withWeight = True)
    
    def compute(self, target_texts):
        scores = []
        for text in target_texts:
            parts = jieba.lcut(text, cut_all=True)
            score = 0
            for tag in self.tags:
                if tag[0] in parts:
                    score += tag[1]
            
            scores.append(score)

        return scores

if __name__ == '__main__':
    from local_storage import LocalStorage
    storage = LocalStorage('news.db', 'news_record')
    visited = storage.retrieve(visited = True, topk = 1000)
    entries = [entry['title'] for entry in visited]
    calc = SimilarityCalc(entries)

    unvisited = storage.get_unvisited(site = 'backchina', topk = 10)
    target_texts = [target['title'] for target in unvisited]

    scores = calc.compute(target_texts)
    for text, score in zip(target_texts, scores):
        print(text, ':\t', score)