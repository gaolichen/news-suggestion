import spacy

class SimilarityCalc(object):
    def __init__(self, ref_texts, topk = 10):
        self.nlp = spacy.load("zh_core_web_sm")
        self.topk = topk
        #self.refs = [self.nlp(self._process_text(ref)) for ref in ref_texts]
        self.refs = [self.nlp(ref) for ref in ref_texts]
    
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
    
    def compute(self, target_texts):
        #targets = [self.nlp(self._process_text(target)) for target in target_texts]
        targets = [self.nlp(target) for target in target_texts]
        res = []
        for target in targets:
            scores = [target.similarity(ref) for ref in self.refs]
            scores.sort(reverse=True)
            scores = scores[:self.topk]
            res.append(sum(scores)/len(scores))
        
        return res
    
    def topk_similar(self, target, texts, topk = 10):
        nlp1 = self.nlp(self._process_text(target))
        refs = [self.nlp(self._process_text(text)) for text in texts]
        #nlp1 = self.nlp(target)
        #refs = [self.nlp(text) for text in texts]

        scores = [(ref, nlp1.similarity(ref)) for ref in refs]
        scores.sort(key = lambda x : -x[1])

        return scores[:topk]

if __name__ == '__main__':
    from local_storage import LocalStorage
    import random
    storage = LocalStorage('news.db', 'news_record')
    visited = storage.retrieve(visited = True, topk = 1000)
    unvisited = storage.get_unvisited(site = 'backchina', topk = 10)

    target_texts = [target['title'] for target in unvisited]
    ref_texts = [ref['title'] for ref in visited]

    calc = SimilarityCalc(ref_texts, topk = 10)
#    print(calc.sentence_vector(ref_texts[1:10]))
    text = target_texts[1]
    print(text)
    print(calc.compute([text]))
    res = calc.topk_similar(text, ref_texts, topk = 10)
    print(res)