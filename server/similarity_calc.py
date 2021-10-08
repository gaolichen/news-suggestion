import spacy
#import zh_core_web_trf

class SimilarityCalc(object):
    def __init__(self):
        self.nlp = spacy.load("zh_core_web_sm")
        #self.nlp = zh_core_web_trf.load()
    
    def _process_text(self, text):
        doc = self.nlp(text)
        result = []
        for token in doc:
            if token.text in self.nlp.Defaults.stop_words:
                continue
            if token.is_punct:
                continue
            if token.lemma_ == '-PRON-':
                continue
            result.append(str(token))

        return "".join(result)
    
    def compute(self, target_texts, ref_texts, topk = 10):
        #targets = [self.nlp(self._process_text(target)) for target in target_texts]
        #refs = [self.nlp(self._process_text(ref)) for ref in ref_texts]
        targets = [self.nlp(target) for target in target_texts]
        refs = [self.nlp(ref) for ref in ref_texts]

        res = []
        for target in targets:
            scores = [target.similarity(ref) for ref in refs]
            scores.sort(reverse=True)
            scores = scores[:topk]
            res.append(sum(scores)/len(scores))
        
        return res

if __name__ == '__main__':
    from local_storage import LocalStorage
    import random
    storage = LocalStorage('news.db', 'news_record')
    visited = storage.retrieve(visited = True)
    unvisited = storage.retrieve(visited = False)
    #random.shuffle(visited)
    
    targets = visited[-10:]
    visited = visited[:-10]
    unvisited = unvisited[-10:]
    targets.extend(unvisited)
    print(targets)

    target_texts = [target[1] for target in targets]
    ref_texts = [ref[1] for ref in visited[-100:]]

    calc = SimilarityCalc()
    print(calc.compute(target_texts, ref_texts))