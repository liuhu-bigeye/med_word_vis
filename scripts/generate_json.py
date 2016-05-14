import pandas as pd
import numpy as np
import os, pdb, pickle, json
from scipy import spatial
from sklearn.manifold import TSNE

random_state = 1235
cor_thre = 0.1
colors = ['', '', '#666', '#777', '#888']

if __name__=='__main__':

	#concat origin annotations
	csv_names = ['lh.csv', 'mc.csv', 'qc.csv']
	df = []
	for cn in csv_names:
		if os.path.exists('../annot/%s'%cn):
			df.append(pd.read_csv('../annot/%s'%cn))

	df = pd.concat(tuple(df)).drop('note',1)
	df = df[df['tag']>1]
	print df

	#merge and filter, only those tag in [2,3,4] left
	data = pd.read_table('../data/model1.txt', sep=' ')
	data = pd.merge(df, data, on='name')

	features = data.values[:,2:]

	#dimention reduce
	model = TSNE(n_components=2, random_state=random_state)
	features_reduced = model.fit_transform(features)
	fmin, fmax = np.min(features_reduced), np.max(features_reduced)
	features_reduced = (features_reduced - fmin)/(fmax - fmin)

	# cosine distance
	num, dim = features.shape
	cosr = np.zeros((num, num))
	for i in range(num):
		print i
		for j in range(i + 1, num):
			cosr[i, j] = spatial.distance.cosine(features[i], features[j])
	cosr += cosr.T
	print data.name

	g = {'nodes':[], 'edges':[]}
	count = 0
	for i in range(num):
		node = {'id': 'n_'+i, 'label':data['name'][i], 'x':features_reduced[i, 0], 'y':features_reduced[i, 1],
						'size': np.sum(cosr[i]), 'color': colors[data['tag'][i]]}
		g['nodes'].append(node)
		for j in range(i + 1, num):
			if cosr[i, j] > cor_thre:
				edge = {'id': 'e_%d_%d'%(i, j), 'source': 'n_'+i, 'target': 'n_'+j, 'size': cosr[i, j], 'color': '#ccc'}
				g['edges'].append(edge)
				count += 1

	print count, num

	with open('../data/med_data.json', 'wb') as f:
		json.dump(g, f)

	# data['reduced_0'] = features_reduced[:,0]
	# data['reduced_1'] = features_reduced[:,1]
	#
	# print features_reduced
	#
	# #dump to file
	# data.to_csv('../data/reduced_features.csv')
	# with open('../data/reduced_cos_dis.pkl', 'wb') as f:
	# 	pickle.dump(cosr, f)