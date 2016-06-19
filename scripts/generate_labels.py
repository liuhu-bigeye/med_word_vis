# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os, pdb, pickle, json, sys
from scipy import spatial
from sklearn.manifold import TSNE
import pdb
import random
from sklearn.neighbors import KNeighborsClassifier

random_state = 1235
cor_thre = 0.90
#疾病, 表型, 用药
colors = ['', '', '#00ff00', '#000000', '#660099']

if __name__=='__main__':
    #concat origin annotations
    csv_names = ['lh.csv', 'mc.csv', 'qc.csv']
    df = []
    for cn in csv_names:
        if os.path.exists('../annot/%s'%cn):
            df.append(pd.read_csv('../annot/%s'%cn))

    df = pd.concat(tuple(df), ignore_index=True).drop('note',1)

    #0不确定, 1无关, 2疾病,3表型,4用药
    #df = df[df['tag']>1]
    #print df
    data = pd.read_table('../data/model1.txt', sep=' ', header=False)
    data_mini = pd.merge(df, data, on='name')
    features = data_mini.values[:,2:]

    tag = data_mini['tag'].values
    tag[tag<=1] = 1

    neigh = KNeighborsClassifier(n_neighbors=3)
    neigh.fit(features, tag)

    features_all = pd.read_table('../data/result-vector.txt', sep=' ', header=False).values[:,:-1]
    names = pd.read_table('../data/result.txt', header=False)
    pred = neigh.predict(features_all)
    print names[pred==2]
