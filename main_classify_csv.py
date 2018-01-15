# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 11:39:35 2018

@author: cisdi
"""

####读csv

#### 预处理数据
#### dt分类，获得labells
#### 找单位行
#### 检查与修正
#### 数据插入labells
#### 保存新csv
#### 


from sklearn import tree
import numpy as np
from sklearn.externals import joblib
from collections import Counter
import pandas as pd 
import csv
from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
import random
import os 
import sys
from time import time

#sys.path.append(r'C:\Users\cisdi\PycharmProjects\functionAPI\APIs\resources')
#from single_table_csv_labelling.csv_class import csv_one_table
#from single_table_csv_labelling.otherfunctions import *
##############api修改######################修改import以及model loading
from csv_class import csv_one_table
from otherfunctions import *
#from .csv_class import csv_one_table
#from .otherfunctions import *
#


#absolute_path = 'C:\\Users\\cisdi\\Desktop\\test_absolute_path\\' #loacl test
absolute_path = '' # none eq current folder 
#absolute_path = '/file_and_log/'

def labelling_csv_by_decision_tree(file_path):
    '''
    输入为文件路径
    输出为插入label的文件路径
    '''
###################api修改######################

    print('start laoding the trained model')
    clf = joblib.load('model2.m') #读取训练好的model
#    clf = joblib.load('./resources/single_table_csv_labelling/model1.m') 路径需要更改
    print('laoding model done')
    
    # try:
    csv_table = csv_one_table(file_path) #new一个csv_table
    # except:
        # print('ERROR , cannot create one_table_class' + '  input file_path is:   ' + file_path )
    
    try:
        features = csv_table.get_all_features() #获取每一行的特征
    except Exception as e:
        print('cannot get the features')
        print('Error, reason is:' ,e)
    
    try:
        results = clf.predict(features) #预测
    except Exception as e:
        print('cannot predict')
        print('Error, reason is:' ,e)
    
    print('predicting done, start labelling')
    return (results,csv_table.table_data)
    return labelling_and_output_to_csv(results,csv_table.table_data,file_path) #查找单位行，打上标签，检查单表，输出csv并返回路径


def labelling_and_output_to_csv(predict_results,csv_data,file_name):
    '''
    输入labels: array   csv_data:ndarray
    在确定只有一张表的情况下，给每一行加上标签，
    并且输出保存为csv
    返回csv
    '''     
    row_label_list_float = predict_results.tolist()
    row_label_list = list(map(int,row_label_list_float))
    last = 0
    exception_pos = len(row_label_list)
    for i in range(len(row_label_list)):
        if row_label_list[i] < last: # 被识别成了两张或多张表
            exception_pos = i ####找到从第多少行开始识别错误
            break
        last = row_label_list[i]
        
    for i in range(exception_pos,len(row_label_list)):
        row_label_list[i] = last 
    
    ###读取csv文件
    raw_data = csv_data
    
    ##########检查单位行################ 写文件的时候操作
    try:
        labels_with_units = find_label_the_units_line(raw_data,row_label_list)
    except:
        labels_with_units = row_label_list
    
    output_csv_name = file_name.replace('.csv', '') + '_' + 'one_table_only_output' + '.csv'
    
    try:
        print('start saving the labelled data')
        with open(output_csv_name, "w", encoding='utf-8', newline='') as outputcsv:
            writer = csv.writer(outputcsv)
            counter = 0
            for label in labels_with_units:
                data1 = list(raw_data[counter])
                data1 = [label] + data1
                writer.writerow(data1)
                counter += 1
    except:
        print('ERROR, cannot saving the labelled data into csvfile')
            
    return output_csv_name    #暂存的路径可能是个坑


def access_to_mongodb():
    '''
    逃学
    login 返回一个db
    '''
#    client = MongoClient('139.196.174.131',28017) ##### public IP
    client = MongoClient('10.26.205.75',28017)   ##### private IP
    client.refiner.authenticate('dancer', 'wecandance666', mechanism='SCRAM-SHA-1')
    db  = client.refiner
    return (db,client)
    

def upload_csv_files_to_mongodb (output_csv_name,db):
    '''
    把暂存在本地刚刚生成的csv文件上传到mongodb中
    '''
    fs = gridfs.GridFS(db)     #############创建了一个gridfs
    with open(output_csv_name,"r" ,encoding='utf-8') as outputcsv:   
        data = outputcsv.read()
        _id = fs.put(data,filename='first',encoding='utf-8')
        return(str(_id))

def download_csv_files_from_mongodb(_id,db):
    '''
    根据id下载mongodb中的csv文件 暂存到一个路径中
    '''
    fs = gridfs.GridFS(db)
    file = fs.find_one(_id)
    data = file.read()
    r = random.randint(0,6666666) ##以防出错
    file_name = str(_id) + str(r) + '.csv' #保证同步处理时不会重复即可
    file_name = absolute_path + file_name ############### change the current folder location to an absolute_path
    out = open(file_name,'wb')
    out.write(data)
    out.close()
    file.close()
    return file_name

def delete_all_tem_csv_files(files):
    '''
    输入为一个list,包含了所有要删除的'临时'csv文件
    '''
    try:
        for file in files:
            os.remove(file)
        print( 'deleted all tem csv files')
    except:
        print(  'cannot delete the tem csv files')
        

def upload_the_labelled_csv_file_downloaded_from_mongodb_to_mongodb(_id):
    '''
    根据逃学ID,从mongodb中获取数据文件,分类打标签后生成一个暂存的csv文件,再根据此文件上传到mongodb,最后返回上传过后的ID
    '''
    time0 = time()
    outputs = {'success': False , 'message': '' , 'data': ''}
    try: # 尝试吧输入的id字符串解析为ObjectId,如果传入非法字符串,则报错并返回错误信息
        _id = ObjectId(_id)
        outputs ['message']  += 'the input ID is valid;'
    except Exception as e:
        outputs ['message']  += 'the input ID is invalid'
        print('Error, reason is:' ,e)
        return outputs
    
    try:
        db , client_mongodb = access_to_mongodb()
        outputs ['message']  += ' can access to MongoDb;'
    except Exception as e:
        outputs ['message'] += ' cannot access to MongoDb / Auth failed;'
        print('Error, reason is:' ,e)
        return outputs
    
    try:
        csv_file = download_csv_files_from_mongodb(_id,db)   #根据db以及给定的ID获取csv数据文件 //需要删除
        print('all files are downloaded from database, start labelling')
        labelled_file = labelling_csv_by_decision_tree(csv_file) #生成标记后复制csv，创建了一个新的带有标记的csv文件 上传后需要删除
        print('labelling done')
    except Exception as e:
        outputs['message'] += ' cannot label the csv file; '
        print('Error, reason is:' ,e)
    
    try:
        mongodb_id = upload_csv_files_to_mongodb(labelled_file,db)
        outputs['success'] = True
        outputs['data'] = mongodb_id
        m = delete_all_tem_csv_files ( [csv_file,labelled_file] )
        time1 = time()
        outputs['message'] += ' all good, time cost:'  + str(time1 - time0) + '   '
        client_mongodb.close()
        outputs['message'] += 'Database is closed'
        return outputs
    except Exception as e:
        client_mongodb.close()
        outputs['message'] += 'Database is closed'
        print('Error, reason is:' ,e)
        return outputs
        
    
if __name__ == '__main__':
    
#    test = ('test_data/11test.csv')
#    output_path = labelling_csv_by_decision_tree(test)
#    db = access_to_mongodb()
#    mongodb_id = upload_csv_files_to_mongodb(output_path,db)
#    test_download_csv_file_path = download_csv_files_from_mongodb(mongodb_id,db)
    
    
#    test = ('test_data/11test.csv')
#    db,clinet = access_to_mongodb()
#    _id = upload_csv_files_to_mongodb(test,db)
##    _id = '5a547d459a2d921098c2da6m'
#    outputs = upload_the_labelled_csv_file_downloaded_from_mongodb_to_mongodb(_id)
#    print(outputs)
    
    test = ('test_data/333.csv')
    results,value = labelling_csv_by_decision_tree(test)
    
    
    
    
    
    
    
    
