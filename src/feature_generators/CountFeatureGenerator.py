from FeatureGenerator import *
import ngram
import pickle
import pandas as pd
from time import time
from nltk.tokenize import sent_tokenize
from helpers import *
import hashlib


class CountFeatureGenerator(FeatureGenerator):
    """
    This module takes the uni-grams, bi-grams and tri-grams and
    creates various counts and ratios which could potentially
    signify how a body text is related to a headline. Specifically,
    it counts how many times a gram appears in the headline, how
    many unique grams there are in the headline, and the ratio 
    between the two. The same statistics are computed for the body 
    text, too. It then calculates how many grams in the headline 
    also appear in the body text, and a normalized version of this 
    overlapping count by the number of grams in the headline. The 
    results are saved in the pickle file which will be read back 
    in by the classifier.
    """

    def __init__(self, name='countFeatureGenerator'):
        super(CountFeatureGenerator, self).__init__(name)


    def process(self, df):
        t0 = time()
        print("\n---Generating Counting Features:---\n")

        grams = ["unigram", "bigram", "trigram"]
        feat_names = ["Headline", "articleBody"]

        for feat_name in feat_names:
            for gram in grams:
                df["count_of_%s_%s" % (feat_name, gram)] = \
                    list(df.apply(lambda x: len(x[feat_name + "_" + gram]), axis=1))
                df["count_of_unique_%s_%s" % (feat_name, gram)] = \
		            list(df.apply(lambda x: len(set(x[feat_name + "_" + gram])), axis=1))
                df["ratio_of_unique_%s_%s" % (feat_name, gram)] = \
                    list(map(try_divide, df["count_of_unique_%s_%s"%(feat_name,gram)], df["count_of_%s_%s"%(feat_name,gram)]))

        # overlapping n-grams count
        for gram in grams:
            df["count_of_Headline_%s_in_articleBody" % gram] = \
                list(df.apply(lambda x: sum([1. for w in x["Headline_" + gram] if w in set(x["articleBody_" + gram])]), axis=1))
            df["ratio_of_Headline_%s_in_articleBody" % gram] = \
                list(map(try_divide, df["count_of_Headline_%s_in_articleBody" % gram], df["count_of_Headline_%s" % gram]))
        
        # number of sentences in headline and body
        for feat_name in feat_names:
            df['len_sent_%s' % feat_name] = df[feat_name].astype(str).apply(lambda x: len(sent_tokenize(x)))

        # dump the basic counting features into a file
        feat_names = [ n for n in df.columns \
                if "count" in n \
                or "ratio" in n \
                or "len_sent" in n]
        
        # binary refuting features
        _refuting_words = [
            'fake',
            'fraud',
            'hoax',
            'false',
            'deny', 'denies',
            # 'refute',
            'not',
            'despite',
            'nope',
            'doubt', 'doubts',
            'bogus',
            'debunk',
            'pranks',
            'retract'
        ]

        _hedging_seed_words = [
            'alleged', 'allegedly',
            'apparently',
            'appear', 'appears',
            'claim', 'claims',
            'could',
            'evidently',
            'largely',
            'likely',
            'mainly',
            'may', 'maybe', 'might',
            'mostly',
            'perhaps',
            'presumably',
            'probably',
            'purported', 'purportedly',
            'reported', 'reportedly',
            'rumor', 'rumour', 'rumors', 'rumours', 'rumored', 'rumoured',
            'says',
            'seem',
            'somewhat',
            # 'supposedly',
            'unconfirmed'
        ]
        

        check_words = _refuting_words
        for rf in check_words:
            fname = '%s_exist' % rf
            feat_names.append(fname)
            df[fname] = df['Headline'].astype(str).map(lambda x: 1 if rf in x else 0)
	    

        xBasicCounts = df[feat_names].values
        print ('xBasicCounts.shape:', xBasicCounts.shape)
        outfilename_bcf = "basic.pkl"
        with open("../saved_data/kaggle/" + outfilename_bcf, "wb") as outfile:
            pickle.dump(feat_names, outfile, -1)
            pickle.dump(xBasicCounts, outfile, -1)
        print ('basic counting features saved in %s' % outfilename_bcf)

        print ('\n---Counting Features is complete---')
        print("Time taken {} seconds\n".format(time() - t0))
        return 1


    def read(self):

        filename_bcf = "basic.pkl"
        with open("../saved_data/new/" + filename_bcf, "rb") as infile:
            _ = pickle.load(infile)
            xBasicCounts = pickle.load(infile)
        
        print ('xBasicCounts.shape: ', xBasicCounts.shape)
        return [xBasicCounts]

