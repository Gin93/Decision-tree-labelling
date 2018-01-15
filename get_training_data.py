# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 08:42:47 2018

@author: cisdi
"""
from csv_class import csv_one_table
from sklearn.datasets import load_iris
from sklearn import tree
import numpy as np
from sklearn.externals import joblib
from otherfunctions import *


train_data_path = 'train_data/'
all_files = dirlist(train_data_path,[])#获取文件夹下所有文件的路径


all_train_features = []
for files in all_files: #读取逐个文件  
    csvdata = csv_one_table(files) ##############操作训练数据 把多表的删除掉
    train_features = csvdata.get_training_data()
    all_train_features += (train_features)


train_data = np.array(all_train_features)
num_features = len(all_train_features[0]) - 1  #以防features的数量会改变

clf = tree.DecisionTreeClassifier()
clf = clf.fit(train_data[:,:num_features],train_data[:,num_features])
joblib.dump(clf, 'model2.m') #保存训练好的model
 
## export the tree in Graphviz format using the export_graphviz exporter
#with open("iris.dot", 'w') as f:
#    f = tree.export_graphviz(clf, out_file=f)
# 
## predict the class of samples
results = clf.predict(train_data[:,:num_features])
## the probability of each class
#y = clf.predict_proba(iris.data[:1, :])

l = len (results)
for i in range(l):
    if results[i] != train_data[i,num_features]:
        print('wrong')