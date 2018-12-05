import re
import string
from collections import namedtuple

import numpy as np
import pandas as pd

from gensim.models import Word2Vec
from gensim.models.phrases import Phraser
from gensim import utils, matutils
import spacy


class Themes:
    def __init__(self):
        pass

    def add_theme(self):
        pass

    def remove_theme(self):
        pass


class Theme:
    def __init__(self, name, initial_seeds, model, topn):
        self.name = name
        self.initial_seeds = initial_seeds
        self.model = model
        if topn > 0:
            self.seeds = self.create_seeds(initial_seeds, topn)
        else:
            self.seeds = initial_seeds

    def remove_seed(self, seed):
        try:
            self.seeds.remove(seed)
        except ValueError:
            pass

    def create_seeds(self, seed_list, top_n=10):
        seeds = set()
        for seed in seed_list:
            seeds.add(seed)
            seeds.update([word for word, _ in self.model.most_similar(seed, topn=top_n)])
        return seeds


class ThemeClassifier:
    Sentence = namedtuple('Sentence', 'text, words')

    def __init__(self, w2v_model_file, phraser_file, dictionary_file, seed_expansion=0, lang='en_core_web_sm',
                 average_seed_vectors=True):

        self.model = Word2Vec.load(w2v_model_file)
        self.phrase_transformer = Phraser.load(phraser_file)
        self._dictionary_file = dictionary_file
        self._expand_dictionary_n = seed_expansion
        self.themes = self._read_dictionary(self._dictionary_file)
        self.nlp = spacy.load(lang)
        self._stop_words = spacy.lang.en.STOP_WORDS
        if average_seed_vectors:
            self.get_themes = self._themes_average_seeds
        else:
            self.get_themes = self._themes_individual_seeds

    def _read_dictionary(self, dictionary_file):
        dictionary = pd.read_excel(dictionary_file, sheet_name="Unique List", header=0)

        themes = {column: Theme(column, self._parse_column(dictionary[column]), self.model, self._expand_dictionary_n)
                  for column in dictionary}

        return themes

    def _parse_column(self, column):
        words = [row.lower() for row in column if not pd.isnull(row)]
        words = filter(lambda x: x in self.model.wv.vocab, words)  # filter out the words not in the dictionary
        return list(set(words))

    @staticmethod
    def _normalize_text(text):
        # Lower case
        norm_text = text.lower()

        # Pad '-', '/' and '\' as they are common word separators
        norm_text = re.sub("\\\\", ' ', norm_text)
        norm_text = re.sub("/", ' ', norm_text)
        norm_text = re.sub("-", ' ', norm_text)

        # Remove successive blanks
        norm_text = re.sub('\s+', ' ', norm_text)  # replace sequence of spaces by one space

        # Remove punctuation
        table = str.maketrans({key: None for key in string.punctuation})
        norm_text = norm_text.translate(table)

        # Remove numbers
        norm_text = re.sub("\d+", 'NUM', norm_text)

        # Translate to unicode and split into tokens
        norm_text = utils.to_unicode(norm_text).split()
        return norm_text

    def _get_sentences(self, text):
        doc = self.nlp(text)
        sentences = []

        for sentence in doc.sents:
            words = self._normalize_text(str(sentence))
            words = self.phrase_transformer[words]
            sentences.append(self.Sentence(str(sentence), words))

        return sentences

    def _themes_individual_seeds(self, tokens, top_n=3, threshold=0.37):
        words = self._remove_stops_and_punct(tokens)
        words = [word for word in words if word in self.model.wv.vocab]
        doc_vec = self._mean_vector(words)
        matches = []
        for name, theme in self.themes.items():
            scores = [(seed, self._cosine_similarity(self.model.wv[seed], doc_vec)) for seed in theme.seeds]
            matches.append((name, sorted(scores, key=lambda tup: tup[1], reverse=True)[0][1]))
        matches = [match for match in matches if match[1] >= threshold]
        matches = sorted(matches, key=lambda tup: tup[1], reverse=True)
        matches = matches[:top_n]
        return matches

    def _themes_average_seeds(self, tokens, top_n=3, threshold=0.44):
        words = self._remove_stops_and_punct(tokens)
        words = [word for word in words if word in self.model.wv.vocab]
        doc_vec = self._mean_vector(words)
        matches = [(theme, self._cosine_similarity(self._mean_vector(self.themes[theme].seeds), doc_vec))
                   for theme in self.themes]
        matches = [match for match in matches if match[1] >= threshold]
        matches = sorted(matches, key=lambda tup: tup[1], reverse=True)
        matches = matches[:top_n]
        return matches

    def _mean_vector(self, tokens):
        doc = [token for token in tokens if token in self.model.wv.vocab]
        return np.mean(self.model.wv[doc], axis=0)

    @staticmethod
    def _cosine_similarity(vec1, vec2):
        return np.dot(matutils.unitvec(vec1), matutils.unitvec(vec2))

    def _remove_stops_and_punct(self, tokens):
        punctuation = (',', '.', '-', ':', ';', ')', '(')
        return [w for w in tokens if w not in self._stop_words and w not in punctuation]

    def predict(self, text):
        sentences = self._get_sentences(text)

        result = []

        for sentence in sentences:
            themes = self.get_themes(tokens=sentence.words)
            result.append({'sentence': sentence.text,
                           'themes': themes})

        return result

    def train(self):
        # train phraser
        # train word2vec
        pass

    def load_model(self):
        pass

    def save_model(self):
        pass


if __name__ == '__main__':
    MODEL = '../data/lbg_culture_prop_w2v_cg,d300,n5,w10,mc2,s0.001,t4'
    PHRASER = '../data/culture_prop_phraser_bigram-npmi'
    THEME_XLS = '../data/LBG Culture - Sample Dictionary - Semantic v4.1.xlsx'

    text = 'Culture is really shit in here. I am not sure how my manager can handle the pressure'

    classifier = ThemeClassifier(MODEL, PHRASER, THEME_XLS)

    print(classifier.predict(text))
    pass
