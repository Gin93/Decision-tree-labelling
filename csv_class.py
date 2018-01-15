# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 15:13:00 2018

@author: cisdi
"""

'''
定义一个只含有单表的csv类,主要用于保存与提取特征
'''

import pandas as pd 

import numpy as np
import collections

#from .otherfunctions import *
from otherfunctions import *


class csv_one_table:
    def __init__(self, file_path):
        
        df = pd.read_csv(file_path, header=None, encoding="utf-8")  # 读取csv文件
        df = df.replace(np.nan,'')
        self.table_data = np.array(df)
        self.rows = self.table_data.shape[0]
               
    def get_features_for_row_data(self,row_data):
        '''
        输入：(list) ： 一行数据
        输入: （list）：由特征组成的list
        '''
        
        def numbers_ratio (row_data_without_null,total):
            '''
            各类型占比
            '''
            _int = _num = _float = _str = 0
            
            for i in row_data:
                if isinstance(i, int):
                    _int += 1
                elif isinstance(i, float):
                    _float += 1  
                elif isinstance(i, str):
                    if i.isdigit(): # 是整数但不可能是浮点数
                        _int += 1     
                    else:
                        try:
                            float(i)
                            _float += 1
                        except:
                            _str += 1
            _num = _float + _int ### 数字包含了浮点数以及整数
            
            return (_num/total , _int/total, _str/total )
    		
        def merged_ratio(row_data_without_null,total):
            '''
            合并单元格占比 
            注意换行符问题
            '''
            ### 会有小量误差
            list_elements_stats = collections.Counter(row_data_without_null) # 统计词频
            
            return ( ( total - len(list_elements_stats)) / total) #返回合并单元格的比值
        
        def spaces_ratio(row_data,total):
            '''
            空值占比
            '''
            count = 0
            for i in row_data:
                if i == '':
                    count += 1	# count 为空值的数量
            return count / total 
        
        def var (row_data,total): ##为了效率需要手动设置一个阈值
            '''
            离散程度
            '''        
            def get_lens(data):
                try:
                    float(data)
                    return 1
                except:
                    return len(data)
                
            list_elements_stats = collections.Counter(row_data_without_null)
            l = total - len(list_elements_stats)
            for i in range(l):
                row_data.append('')
            l = row_data
            N = len(l)     
            lens_for_each_elements = [get_lens(l[i]) for i in range(N)] 
            narray=np.array(lens_for_each_elements)
            sum1=narray.sum()
            narray2=narray*narray
            sum2=narray2.sum()
            mean=sum1/N
            var=sum2/N-mean**2
            
            return (mean,var)		
            
        row_data_without_null = [ a for a in row_data if a is not '' ]
        lens_for_clean_rowdata = len(row_data_without_null)
        lens_for_rowdata = len(row_data)
        
#        data_without_merged = list(set(row_data)) #把合并填充过的都替换为''，会有小误差
#        if '' in data_without_merged:
#            data_without_merged.remove('')
#        for i in range(lens_for_rowdata - len(data_without_merged)):
#            data_without_merged.append('')
        
        output = []
        output.append(numbers_ratio(row_data_without_null,lens_for_clean_rowdata)[0])
        output.append(merged_ratio(row_data_without_null,lens_for_clean_rowdata))
        output.append(spaces_ratio(row_data,lens_for_rowdata))
        output.append(var(row_data_without_null,lens_for_clean_rowdata)[0])
        output.append(var(row_data_without_null,lens_for_clean_rowdata)[1])
        return(output)        
        
    def get_all_features(self):
        '''
        获取每行的特征
        '''
#        return [self.get_features_for_row_data(i) for i in self.table_data ]
        threshold = 7
        all_features = []
        for row, row_data in enumerate (self.table_data):
            top_feature = bottom_feature = 0
            if row < threshold:
                top_feature =  (threshold - row) / threshold
            if row >= self.rows - threshold:
                bottom_feature = (row - self.rows + threshold + 1) / threshold 
            features = self.get_features_for_row_data(row_data)
            features.append(top_feature)
            features.append(bottom_feature)
            all_features = all_features +  [features]
        return np.array(all_features)
                
#        top_feature = [ (threshold - x) / threshold for x in  ]
        
    def get_training_data(self):
        '''
        对于训练数据，要解析第一列的label，用于制作训练数据集
        '''
        all_features = []
        threshold = 7
        for row, row_data in enumerate (self.table_data):
            label = labelling(row_data[0])
            if label != 'trash':
#                row_data.pop(0) 
                row_data = np.delete(row_data, 0)# 删除掉label（abcd），只保留数据
                if not empty(row_data):
                    top_feature = bottom_feature = 0
                    if row < threshold:
                        top_feature =  (threshold - row) / threshold
                    if row >= self.rows - threshold:
                        bottom_feature = (row - self.rows + threshold + 1) / threshold 
                    features = self.get_features_for_row_data(row_data) #top bot 特征后面手动添加，因为空行问题
                    features.append(top_feature)
                    features.append(bottom_feature)
                    features.append(label)
                    all_features = all_features +  [features]
                    
        return all_features #features_with_label
                    

    
if __name__ == '__main__':
    x = ('all_data/0Co5c8iJpcvnp5ktpRAzKqlR.csv')
    a = csv_one_table(x)
    data = a.table_data
    xx = a.get_all_features()
    xxx = a.get_training_data()
    features_with_label = a.get_training_data()
    
    


	
	
		
