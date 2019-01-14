
# coding: utf-8

# In[16]:


# -*- coding: utf-8 -*-
"""
Created on Mon Dec 24 21:03:52 2018

@author: liyufang
"""
########################################################################################################################################################
############################################################数据预处理####################################################################################
import pandas as pd
import numpy as np
import sys
import datetime
#参数初始化
inputPath = sys.argv[1]
outputPath = sys.argv[2]
gameId = sys.argv[3]

today = datetime.date.today()
formatted_today = today.strftime('%Y%m%d')


inputfile = inputPath+'/kmeans.xls' 
outputfile_147 = outputPath+'/eco_{}_kresult_{}.csv'.format(gameId,formatted_today) #保存结果的文件名
##异常值处理函数以及数据标准化
data = pd.read_excel(inputfile)
data = data.set_index(['game_id','op_id','server_id','server_name','op_name'])
#data = data.reset_index(drop=False,inplace=True)
data = data.dropna()
#print(data)
def Dealt_Outlier(dataframe, threshold=3.5):
    d = dataframe['paymoney_server_cost_ratio']
    zscore = (d - d.mean())/d.std()
    dataframe['isAnomaly'] = zscore.abs() > threshold
    return dataframe
Dealt_Outlier(data)
data=data[data['isAnomaly']==False]
#print(data)
data=data.drop('isAnomaly',axis=1)
#print(data)
data_zs = 1.0*(data - data.mean())/data.std() 
#print(data_zs)



########################################################################################################################################################
####################################################################147游戏聚类模型#######################################################################
#147游戏聚类
#147女神联盟
data_147=data_zs.loc[int(gameId)]
k = 4 
iteration = 500
print('data_147_previous-----------------------------------')
print(data_147)
from sklearn.cluster import KMeans
from sklearn import svm

# fit the model
clf = svm.OneClassSVM(nu=0.1, kernel="rbf", gamma=0.1)
clf.fit(data_147)
data_147_outlier = clf.predict(data_147)
print('data_147 outlier ---------------------------------------------')

n_error_train = data_147_outlier[data_147_outlier == -1].size
print('n_error_train---------------------------------------------')
print(n_error_train)

data_147_new = pd.concat([data_147, pd.Series(data_147_outlier, index = data_147.index)], axis = 1)
data_147_new.columns = list(data_147.columns) + ['cluster'] #重命名表头
#print(data_147_new.columns)
data_147 =data_147_new[data_147_new['cluster']==1]
#print(data_147_new)
model = KMeans(n_clusters = k, n_jobs = 4, max_iter = iteration) #分为k类，并发数4
model.fit(data_147.loc[:, ['avg_pcu','paymoney_server_cost_ratio']]) #开始聚类
#简单打印结果
r1 = pd.Series(model.labels_).value_counts() #统计各个类别的数目
r2 = pd.DataFrame(model.cluster_centers_) #找出聚类中心
r = pd.concat([r2, r1], axis = 1) #横向连接（0是纵向），得到聚类中心对应的类别下的数目
r.columns = list(['avg_pcu','paymoney_server_cost_ratio']) + [u'类别数目'] #重命名表头
print('类别数目-----------------------------------')
print(r)
#详细输出原始数据及其类别
r = pd.concat([data_147, pd.Series(model.labels_, index = data_147.index)], axis = 1)  #详细输出每个样本对应的类别
r.columns = list(data_147.columns) + [u'聚类类别'] #重命名表头

print(r)

#根据分组数据求均值
gp_col = u'聚类类别'
cols = [col for col in r.columns ]
r_mean = r.groupby(gp_col)[cols].mean()
print('r_mean-----------------------------------')
print(r_mean)
#对r_mean数据框中的两个特征按照paymoney_server_cost_ratio，pcu进行排序，区分出健康、亚健康不健康的类
r_mean = r_mean.sort_index(by=['paymoney_server_cost_ratio', 'avg_pcu'])   #这个代码按照升序进行排序
print(r_mean)
#求出排在第一个的索引
#r_mean.index[0]
#r_mean.index[1]
#r_mean.index[2]
#在r数据表中新增加一列health_status,当聚类类别==r_mean.index[0]，将health_status判断为不健康；
#当聚类类别==r_mean.index[1]，将health_status判断为亚健康；当聚类类别==r_mean.index[2]，将health_status判断为健康
#不健康的服务器
unhealth=r[r[u'聚类类别']==r_mean.index[0]]
unhealth['health_status']='不健康'
#print(unhealth)
#亚健康的服务器
sub_health=r[r[u'聚类类别']==r_mean.index[1]]
sub_health['health_status']='亚健康'
#print(sub_health)
#健康的服务器
ssub_health=r[r[u'聚类类别']==r_mean.index[2]]
ssub_health['health_status']='较健康'

#健康的服务器
health=r[r[u'聚类类别']==r_mean.index[3]]
health['health_status']='健康'
#print(health)
#将结果存入本地
unhealth_path = outputPath+'/unhealth.xlsx' #保存结果的文件名
sub_health_path = outputPath+'/sub_health.xlsx'
ssub_health_path = outputPath+'/ssub_health.xlsx' 
health_path = outputPath+'/health.xlsx'
unhealth.to_excel(unhealth_path) 
sub_health.to_excel(sub_health_path)
ssub_health.to_excel(ssub_health_path)
health.to_excel(health_path)
#把三个结果合并为一个一个结果并且将结果对应到最原始的数据上
frames=[health,sub_health,ssub_health,unhealth]
merge_result=pd.concat(frames)
final_merge_result = pd.merge(merge_result,data,how='left', on=['op_id','server_id','server_name','op_name'])
final_merge_result.reset_index(drop=False,inplace=True)
#final_merge_result.to_excel(outputfile_147,index=False) #保存结果
final_merge_result.op_id=final_merge_result.op_id.astype(str)
final_merge_result.op_id=final_merge_result.op_id.map(lambda row: row.replace(",","|"))
print(final_merge_result.head())
final_merge_result.drop('cluster',inplace=True,axis=1) 
final_merge_result.to_csv(outputfile_147,index=False,header=0,encoding='utf-8')   #保存結果
#print(final_merge_result)

# In[7]:




