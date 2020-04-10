import numpy as np
import pandas as pd
from difflib import SequenceMatcher
from sklearn.cluster import KMeans
from sklearn import metrics

class Process:
    def __init__(self):
        pass


    def similarity(self,a, b):
        # use library difflib to get similarity
        return SequenceMatcher(None, a, b).ratio()

    def mapping(self,mapping_dict,all_columns,column):
        # return auto-mapping result for all columns
        column = column.lower()
        # 1. find all possible matched columns in master table for the specific column in client table
        syn = {"postal_code":"zip",
                "code_postal":'zip',
                "first_name":"firstname",
                "last_name":"lastname"
        }
        candidates = set()
        res = []
        for key in mapping_dict:
            if column.find(key)!= -1:
                for w in mapping_dict[key]:
                    candidates.add(w)
            if column in syn.keys():
                if syn[column].find(key)!=-1:
                    for w in mapping_dict[key]:
                        candidates.add(w)
        # if we didn't find important substrings, then add all possible "other" columns
        if len(candidates)==0:
            for w in all_columns:
                res.append(w)
            return res
        # 2. rank the possible candidates
        res = list(candidates)
        res= sorted(candidates,key=lambda x: self.similarity(x,column),reverse=True)
        # if the similiarity between the most possible candidate and the column is 1, then we can match the column to it
        if self.similarity(res[0],column)==1:
            return [res[0]]
        return res

    def buildDict(self,labels):
        # build a dictionary to store important substrings for each label
        # split each label name on "_" to get all important substrings
        mapping_dict = {}
        for l in labels:
            substrs = l.split("_")
            for s in substrs:
                if not s in mapping_dict:
                    mapping_dict[s] = []
                mapping_dict[s].append(l)
        return mapping_dict

    def match(self,client_label,master_label):
        mapping_dict = self.buildDict(master_label)
        matchingRes = {}
        for c in client_label:
            if len(c) == 0: continue
            matchingRes[c] = self.mapping(mapping_dict,master_label,c)
        return matchingRes

    def getMasterCols(self,dfMaster):
        # return master columns
        data = []
        vals = dfMaster.values
        for row in vals:
            strs = row[0].split('|')
            data.append(strs)
        cols = dfMaster.columns.values[0].split('|')
        dfMaster = pd.DataFrame(data, columns=cols)
        master_label = list(dfMaster['master_label'])
        return master_label

    def clean(self,dfMaster,dfMerged):
        # return cleaned dataset
        master_label = self.getMasterCols(dfMaster)
        allCols = list(dfMerged.columns)
        idCols = {'line_id', 'cont_id','sales_id','transaction_id','prod_id','store_id'}
        zipCols = {'cont_residency_zip','cont_company_zip'}
        phoneCols = {'store_phone','cont_cellphone'}
        # only allow strings made up of numbers
        dateCols = {'cont_initial_contact_date','transaction_date','payment_date','delivery_date','date_of_record'}
        # only allow strings made up of numbers and '-'
        otherCols = {'other01', 'other02', 'other03', 'other04', 'other05', 'other06', 'other07', 'other08', 'other09', 'other10'}
        numCols = {'transaction_amount_tax', 'transaction_amount_net','prod_price_tax', 'prod_price_net'}
        # only allow strings made up of numbers and '.'
        strCols = set(master_label)-idCols-zipCols-phoneCols-dateCols-numCols-otherCols
        # doesn't allow strings made up of only numbers
        dfCleaned = dfMerged.copy()
        for col in allCols:
            if col=='cont_id':
                dfCleaned[col] = dfCleaned[col].astype(str)
                dfCleaned=dfCleaned[(dfCleaned[col].str.isdigit())]
            elif col=='prod_family':
                dfCleaned[col] = dfCleaned[col].astype(str)
                dfCleaned=dfCleaned[(dfCleaned[col].isin(['nan']) | ~(dfCleaned[col].str.isdigit()))]
                #dfCleaned = dfCleaned[~(dfCleaned[col].isin(['SERVICE','SERVICE NO MARGIN']))]
            elif col in idCols or col in zipCols:
                dfCleaned[col] = dfCleaned[col].astype(str)
                dfCleaned=dfCleaned[(dfCleaned[col].isin(['nan']) | dfCleaned[col].str.isdigit())]

                try:
                    dfCleaned[col] = dfCleaned[col].astype(int)
                except ValueError:
                    pass

            elif col in dateCols:
                dfCleaned[col] = dfCleaned[col].astype(str)
                dfCleaned=dfCleaned[(dfCleaned[col].isin(['nan']) | dfCleaned[col].str.find('-')!=-1)]
                try:
                    dfCleaned[col] = pd.to_datetime(dfCleaned[col])
                except ValueError:
                    pass
            elif col in numCols:
                dfCleaned[col] = dfCleaned[col].astype(str)
                dfCleaned=dfCleaned[(dfCleaned[col].isin(['nan']) | ~(dfCleaned[col].str.isalpha()))]
                try:
                    dfCleaned[col] = dfCleaned[col].astype(float)
                except ValueError:
                    pass
            elif col in strCols:
                dfCleaned[col] = dfCleaned[col].astype(str)
                dfCleaned = dfCleaned[(dfCleaned[col].isin(['nan']) | ((dfCleaned[col].str.len()>=2) & ~(dfCleaned[col].str.isdigit())))]


        return dfCleaned

    def getCusCols(self,dfMerged):
        # return columns for users to choose from in custom seg
        allowed = ['cont_id','transaction_id','store_name','prod_family','prod_subfamily','prod_style','prod_price_net']
        allCols = list(dfMerged.columns)
        #print(allCols)
        res = []
        for i in allowed:
            if i in allCols:
                res.append(i)
        # replace 'transaction_id' with 'transaction_sum'
        if 'transaction_id' in res:
            res.remove('transaction_id')
            res.append('transaction_sum')
        if 'prod_price_net' in res:
            res.remove('prod_price_net')
            res.append('transaction_amount')
        # remove 'cont_id' since it's a necessary one
        res.remove('cont_id')
        return res

    def cus_seg(self,dfMaster,dfMerged,pickedCols,num=0):
        # append 'cont_id' to pickedCols
        pickedCols.append('cont_id')
        if 'transaction_sum' in pickedCols:
            pickedCols.remove('transaction_sum')
            pickedCols.append('transaction_id')
        if 'transaction_amount' in pickedCols:
            pickedCols.remove('transaction_amount')
            pickedCols.append('prod_price_net')
        master_label = self.getMasterCols(dfMaster)
        cateFeatures = {'store_name','prod_family','prod_subfamily','prod_style'}
        numFeatures = {'transaction_amount_tax', 'transaction_amount_net','prod_price_tax', 'prod_price_net'}
        dfCleaned = dfMerged.copy()
        pickedCate = []
        pickedNum = []
        dummCols = []
        for i in pickedCols:
            if i in cateFeatures:
                pickedCate.append(i)
            elif i in numFeatures:
                pickedNum.append(i)
        cateDF = pd.DataFrame(dfCleaned,columns=pickedCate)
        # do one-hot encoding for all categorical features
        if len(pickedCate)>0:
            cateDF = pd.get_dummies(cateDF)
            for i in list(cateDF.columns):
                if i.find('_nan')==-1:
                    dummCols.append(i)
        dataDF = pd.DataFrame(dfCleaned,columns=pickedCols)
        dataDF=dataDF.drop(columns=pickedCate)
        # join the df after one-hot encoding with the numerical columns
        dataDF = dataDF.join(cateDF)
        # convert data type to float
        for i in list(dataDF.columns):
            if i in numFeatures:
                dataDF[i] = dataDF[i].astype(float)
        # group records by cont_id
        g1 = dataDF[dummCols].groupby(dataDF['cont_id']).sum()
        # get the transaction_sum for each customer
        if 'transaction_id' in pickedCols:
            g2 = dataDF.groupby('cont_id')['transaction_id'].nunique().to_frame()
            g1 = pd.merge(g1,g2,on='cont_id',how='inner')
        # group records by cont_id and get the sum
        for i in pickedNum:
            g2 = dataDF.groupby('cont_id')[i].sum().to_frame()
            g1 = pd.merge(g1,g2,on='cont_id',how='inner')
        dataDF = g1.copy()
        # auto-select
        # pick the optimal k
        if num==0:
            SSE=self.elbow(dataDF)
            k_best = -1

            alpha = 2
            while k_best==-1:
                for i in range(1,len(SSE)-1):
                    if SSE[i-1]-SSE[i]>=alpha*(SSE[i]-SSE[i+1]):
                        k_best = i

                alpha = alpha*0.9
            num = k_best+2
        # train model
        print("**********model start*********")
        model1 =KMeans(n_clusters=num, max_iter=300, n_init=10)
        model1.fit(dataDF)
        y_pre = model1.predict(dataDF)

        print("**********model end***********")
        # collect results
        clusterIdx = []
        for i in range(num):
            clusterIdx.append('S'+str(i))

        count = []
        for i in range(num):
            count.append(len(np.where(y_pre == i)[0]))

        centroids = model1.cluster_centers_.round(2)
        res = pd.DataFrame(centroids.T,index=list(dataDF.columns),columns=clusterIdx)
        dataDF['cluster'] = y_pre

        return [count,res,pickedCols,num,dataDF]

    def com_seg(self,dfMaster,dfMrged):
        data = []
        vals = dfMaster.values
        for row in vals:
            strs = row[0].split('|')
            data.append(strs)
        cols = dfMaster.columns.values[0].split('|')
        dfMaster = pd.DataFrame(data, columns=cols)
        master_label = list(dfMaster['master_label'])
        dateFeatures = {'cont_initial_contact_date','transaction_date','payment_date','delivery_date','date_of_record'}
        numFeatures = {'transaction_amount_tax', 'transaction_amount_net','prod_price_tax', 'prod_price_net'}
        otherFeatures = {'other01', 'other02', 'other03', 'other04', 'other05', 'other06', 'other07', 'other08', 'other09', 'other10'}
        cateFeatures = set(master_label)-numFeatures-otherFeatures


        dfMrged=dfMrged[~(dfMrged['cont_id'].isin(['nan']))]

        curCols = list(dfMrged.columns.values)
        for col in curCols:
            if col in dateFeatures:
                dfMrged.loc[:,col]=pd.to_datetime(dfMrged.loc[:,col],errors='coerce')
                dfMrged[col] = dfMrged[col].dt.day_name()
            elif col in cateFeatures:
                dfMrged[col] = dfMrged[col].astype(str)
            elif col in numFeatures:
                dfMrged[col] = dfMrged[col].astype(float)
        filter1 = dfMrged.groupby('cont_id')['transaction_id'].nunique().to_frame()
        filter1 = filter1[(filter1['transaction_id']>=0)]
        filter2 = dfMrged.groupby('cont_id')['prod_price_net'].sum().to_frame()
        filter2 = filter2[(filter2['prod_price_net']>=0)]
        data = pd.merge(filter1,filter2,on='cont_id',how='inner')
        data.columns = ['transaction_sum','transaction_amount_sum']
        # pick the optimal k
        SSE=self.elbow(data)
        k_best = -1
        alpha = 2
        while k_best==-1:
            for i in range(1,len(SSE)-1):
                if SSE[i-1]-SSE[i]>=alpha*(SSE[i]-SSE[i+1]):
                    k_best = i
            alpha = alpha*0.8
        model = KMeans(n_clusters=k_best+2,max_iter=1000, n_init=10)
        model.fit(data)
        centroids = model.cluster_centers_
        y_pre = model.predict(data)
        data['cluster'] = y_pre
        count = []
        for i in range(k_best+2):
            count.append(len(np.where(y_pre == i)[0]))
        return [k_best+2,count,data,centroids]

    def elbow(self,data):
        SSE=[]
        k_vals=[2,3,4,5,6,7,8,9,10,11]
        for k in k_vals:
            model=KMeans(n_clusters=k,max_iter=500, n_init=10)
            model.fit(data)
            SSE.append(model.inertia_)
        return SSE
