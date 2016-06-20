# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os, pdb, pickle, json, sys
from scipy import spatial
from sklearn.manifold import TSNE
import pdb
import random

random_state = 1235
link_thre = 200
#疾病, 表型, 用药
colors = ['', '', '#00ff00', '#000000', '#660099']

def generate():
    #concat origin annotations
    csv_names = ['lh.csv', 'mc.csv', 'qc.csv']
    df = []
    for cn in csv_names:
        if os.path.exists('../annot/%s'%cn):
            df.append(pd.read_csv('../annot/%s'%cn))

    df = pd.concat(tuple(df)).drop('note',1)
    df = df[df['tag']>1]
    #print df

    #merge and filter, only those tag in [2,3,4] left
    data = pd.read_table('../data/model1.txt', sep=' ')
    data = pd.merge(df, data, on='name')

    data = data[data.tag>1]

    print data.shape
    #pdb.set_trace()
    #data = data.loc[random.sample(range(data.shape[0]), 20)]
    data = data.reset_index(drop=True)
    print data.shape

    features = data.values[:,5:]

    num, dim = features.shape
    cosr = np.zeros((num, num))
    for i in range(num):
        #print i
        cosr[i, i] = 1
        for j in range(i + 1, num):
            cosr[i, j] = abs(1-spatial.distance.cosine(features[i], features[j]))
    cosr += cosr.T
    #print data.name

    # no inner connections
    cosr_outer = cosr.copy()
    for i in range(num):
        for j in range(num):
            if data.tag[i]==data.tag[j]:
                cosr_outer[i][j]=0
    cosr_outer = np.abs(cosr_outer)

    thre = 0.8
    best_indexs, best_score = [], 0
    for i in range(10):
        indexs = random.sample(range(num), 20)
        score = np.sum(cosr_outer[np.meshgrid(indexs, indexs)])

        if score>best_score:
            best_indexs = [ind for ind in indexs if np.max(cosr_outer[ind, indexs])>thre]
            best_score = score
            print score

    selected_nodes = best_indexs

    with open('../tools/d3/experiment/force.json') as f:
        nodes = json.load(f)
    #pdb.set_trace()
    selected_nodes = [data.name.values.tolist().index(n['name'].encode('utf-8')) for n in nodes['nodes']]

    miserables = {'nodes':[], 'links':[]}
    miserables_all = {'nodes':[], 'links':[]}

    for index_i, i in enumerate(selected_nodes):
        node = {'name':data.name[i], 'group':int(data.tag[i])}
        #pdb.set_trace()
        links = [{'source':index_i, 'target':index_j, 'value':abs(cosr[i, j])} for index_j,j in enumerate(selected_nodes) if index_i!=index_j and abs(cosr[i, j])>thre]
        links_all = [{'source':index_i, 'target':index_j, 'value':abs(cosr[i, j])} for index_j,j in enumerate(selected_nodes) if index_i!=index_j and abs(cosr[i, j])>0]

        miserables['nodes'].append(node)
        miserables['links'].extend(links)

        miserables_all['nodes'].append(node)
        miserables_all['links'].extend(links_all)

    print num, len(miserables['nodes']), len(miserables['links'])

    with open('../tools/d3/experiment/_force.json', 'wb') as f:
        json.dump(miserables, f)
    with open('../tools/d3/experiment/_force_all.json', 'wb') as f:
        json.dump(miserables_all, f)
    #pdb.set_trace()

if __name__=='__main__':
    generate()

    #with open('../data/cos_dis.json', 'wb') as f:
    #    df = {'names':df.values[:,0].tolist(), 'cosr':cosr.tolist(), 'tags':df.values[:,1].tolist()}
    #    json.dump(df, f)





    ##dimention reduce
    #model = TSNE(n_components=2, random_state=random_state)
    #features_reduced = model.fit_transform(features)
    #fmin, fmax = np.min(features_reduced), np.max(features_reduced)
    #features_reduced = (features_reduced - fmin)/(fmax - fmin)

    ## cosine distance
    #num, dim = features.shape
    #if os.path.exists('../data/reduced_cos_dis.pkl'):
    #    with open('../data/reduced_cos_dis.pkl') as f:
    #        cosr = pickle.load(f)
    #else:
    #    cosr = np.zeros((num, num))
    #    for i in range(num):
    #        print i
    #        for j in range(i + 1, num):
    #            cosr[i, j] = abs(1-spatial.distance.cosine(features[i], features[j]))
    #    cosr += cosr.T
    #    print data.name

    #g = {'nodes':[], 'edges':[]}
    #count = np.zeros(num)
    #for i in range(num):
    #    for j in range(i + 1, num):
    #        if cosr[i, j] > cor_thre and data['tag'][i]!=data['tag'][j]:
    #            edge = {'id': 'e_%d_%d'%(i, j), 'source': 'n_%d'%i, 'target': 'n_%d'%j, 'size': 0.1+(cosr[i, j]-cor_thre)/(1-cor_thre)*0.9, 'color': '#666666'}
    #            g['edges'].append(edge)
    #            count[i]+=1
    #            count[j]+=1

    #for i in range(num):
    #    if count[i]>0:
    #        node = {'id': 'n_%d'%i, 'label':data['name'][i], 'x':features_reduced[i, 0], 'y':features_reduced[i, 1],
    #                    'size': np.sum(cosr[i]), 'color': colors[int(data['tag'][i])]}
    #        g['nodes'].append(node)

    #print np.sum(count), num, np.sum(count!=0), np.sum(count)/1.0/np.sum(count!=0)

    #with open('../data/med_data.json', 'wb') as f:
    #    json.dump(g, f)

    ## data['reduced_0'] = features_reduced[:,0]
    ## data['reduced_1'] = features_reduced[:,1]
    ##
    ## print features_reduced
    ##
    ##dump to file
    #data.to_csv('../data/reduced_features.csv')
    #with open('../data/reduced_cos_dis.pkl', 'wb') as f:
    #    pickle.dump(cosr, f)
