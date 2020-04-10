import numpy as np
import os
import pandas as pd
from myProject import app,db
from flask import render_template, redirect, request, url_for, flash,abort,jsonify
from sqlalchemy import create_engine
from flask_login import login_user,login_required,logout_user
from myProject.forms import LoginForm, RegistrationForm
from myProject.extraction import GetData
from myProject.process import Process
from werkzeug.security import generate_password_hash, check_password_hash
import time
import random
from sqlalchemy import *

import json
from werkzeug import secure_filename


# the database of match-app in yoni's heroku account
engine = create_engine('postgresql+psycopg2://iqzwkgpqdohsws:73f4aed745090d609fa70717fe474d506c667f15e941df5c6b8f8605314272f1@ec2-18-210-214-86.compute-1.amazonaws.com:5432/dev57ds8h0mm5k', echo = False)




listTypes = []
global_cols = []
global_listNumeric = []
global_listDates = []
global_query = []
global_tableName = []
global_filename = []
global_select = []
global_downloadquery = []


@app.route('/', methods=['GET'])
def home():
    # create a new table to store transcodification
    #query0 = "CREATE TABLE TransCod(trans_id CHAR(15),company_id CHAR(50),line_id CHAR(50),cont_id CHAR(50),cont_initial_contact_date CHAR(50),cont_status CHAR(50),cont_segment CHAR(50),cont_civility CHAR(50),cont_firstname CHAR(50),cont_lastname CHAR(50),cont_title CHAR(50),cont_email CHAR(50),cont_cellphone CHAR(50),cont_comment CHAR(50),cont_residency_state CHAR(50),cont_residency_street CHAR(50),cont_residency_street_compl01 CHAR(50),cont_residency_city CHAR(50),cont_residency_zip CHAR(50),cont_company_name CHAR(50),cont_company_state CHAR(50),cont_company_street CHAR(50),cont_company_city CHAR(50),cont_company_zip CHAR(50),transaction_id CHAR(50),transaction_date CHAR(50),transaction_amount_tax CHAR(50),transaction_amount_net CHAR(50),payment_date CHAR(50),delivery_date CHAR(50),prod_id CHAR(50),prod_price_tax CHAR(50),prod_price_net CHAR(50),prod_family CHAR(50),prod_subfamily CHAR(50),prod_category CHAR(50),prod_name CHAR(50),prod_style CHAR(50),prod_collection CHAR(50),prod_fabric CHAR(50),prod_color CHAR(50),sales_id CHAR(50),sales_firstname CHAR(50),sales_lastname CHAR(50),sales_title CHAR(50),sales_email CHAR(50),store_id CHAR(50),store_name CHAR(50),store_manager_flag CHAR(50),store_address CHAR(50),store_phone CHAR(50),store_city CHAR(50),store_state CHAR(50),date_of_record CHAR(50),state_of_stock_01 CHAR(50),state_of_stock_02 CHAR(50),other01 CHAR(50),other02 CHAR(50),other03 CHAR(50),other04 CHAR(50),other05 CHAR(50),other06 CHAR(50),other07 CHAR(50),other08 CHAR(50),other09 CHAR(50),other10 CHAR(50),PRIMARY KEY(Trans_ID))"
    #engine.execute(query0)
    #query1 = "CREATE TABLE Queries(Query text,TableName text,timestamp varchar(40) DEFAULT (now()),PRIMARY KEY(TableName))"

    #query1 = "CREATE TABLE TimeTest(id integer,datetime varchar(40) DEFAULT (now()),PRIMARY KEY(id))"
    #query2 = "insert into TimeTest(id) values(1)";
    #engine.execute(query1)
    #engine.execute(query2)

    return render_template('home.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global global_filename
    global_filename.clear()
    # get the uploaded file
    file = request.files['file']
    # get the filename
    filename = secure_filename(file.filename)
    global_filename.append(filename)
    # save it to static folder
    file.save("myProject/static/file/client.csv")
    # jump to matching page
    return redirect(url_for('clean'))

'''

@app.route('/matchCol',methods=['GET','POST'])
def matchCol():

    dfMaster = pd.read_csv("myProject/static/file/master.csv")
    dfClient = pd.read_csv("myProject/static/file/client.csv")
    # get columns in client table
    data = []
    vals = dfClient.values
    # split on delimitator '|'
    for row in vals:
        strs = row[0].split('|')
        data.append(strs)
        # generate a new dataframe
    cols = dfClient.columns.values[0].split('|')
    dfClient = pd.DataFrame(data, columns=cols)
    dfClient.to_csv("part.csv")
    client_label = cols
    # get columns in master table
    data = []
    vals = dfMaster.values
    for row in vals:
        strs = row[0].split('|')
        data.append(strs)
    cols = dfMaster.columns.values[0].split('|')
    dfMaster = pd.DataFrame(data, columns=cols)
    master_label = list(dfMaster['master_label'])
    p = Process()
    # get the possible master columns where each client column could map to, using matching algorithm
    mapping_dict = p.buildDict(master_label)
    mapping_res = p.match(client_label,master_label)
    # render the matching page and show the file we are working on
    return render_template('match.html',length=len(client_label),mapping_res=mapping_res,master_label=master_label,client_label=client_label,name=global_filename[0])


@app.route('/merge',methods=['POST'])
def merge():
    #select = request.form.get('method_cipher')
    dfMaster = pd.read_csv("myProject/static/file/master.csv")
    dfClient = pd.read_csv("myProject/static/file/client.csv")
    # get columns in client table
    data = []
    vals = dfClient.values
    for row in vals:
        strs = row[0].split('|')
        data.append(strs)
    client_label = dfClient.columns.values[0].split('|')
    dfClient = pd.DataFrame(data, columns=client_label)
    #the original columns in client table
    oldCols = list(dfClient.columns)
    # get columns in master table
    data = []
    vals = dfMaster.values
    for row in vals:
        strs = row[0].split('|')
        data.append(strs)
    cols = dfMaster.columns.values[0].split('|')
    dfMaster = pd.DataFrame(data, columns=cols)
    master_label = list(dfMaster['master_label'])
    # get data from front-end
    keys = list(request.form.keys())
    # get matched columns
    newCols = []
    for key in keys:
        if key!='submit':
            #res_dict[key] = request.form.get(key)
            newCols.append(request.form.get(key))
    # create the matched table and save it to static folder
    dfMerge = dfClient.copy()
    dfMerge.columns = newCols
    dfMerge.to_csv("myProject/static/file/matched.csv",index = False)
    #get random Trans_ID
    timeStamp = int(time.time())
    randNum = random.randint(0,9999)+10000
    trans_id = str(timeStamp)+str(randNum)
    # create a dataframe to store the transcodification and save it to static folder
    data = []
    oldCols.insert(0,'SampleID')
    oldCols.insert(0,trans_id)
    data.append(oldCols)
    newCols.insert(0,'company_id')
    newCols.insert(0,'trans_id')
    dfMatch = pd.DataFrame(data,columns = newCols)
    dfMatch.to_csv("myProject/static/file/CurTransCod.csv")
    # save this record to database
    query = "INSERT INTO TransCod ("
    for i in range(len(newCols)):
        query += newCols[i]
        if(i<len(newCols)-1):
            query += ","
    query += ") VALUES ("
    for i in range(len(oldCols)):
        query = query + "'" + oldCols[i] + "'"
        if(i<len(newCols)-1):
            query += ","
    query += ")"
    #print("______________query: "+query)
    #engine.execute(query)
    # continue to clean data
    return redirect((url_for('clean')))

'''

@app.route("/clean",methods=['POST',"GET"])
def clean():
    global global_cols
    global global_listNumeric
    global global_listDates

    global_cols.clear()
    global_listNumeric.clear()
    global_listDates.clear()

    dfMaster = pd.read_csv("myProject/static/file/master.csv")
    dfMerged = pd.read_csv('myProject/static/file/matched.csv',dtype='str')
    # get the cleaned file
    p = Process()
    dfCleaned = p.clean(dfMaster,dfMerged)
    # get the filename
    tableSQL = global_filename[0].split('.', 1)[0]
    # save the dataframe to database, not efficient method but enough for now
    dfCleaned.to_sql(name = tableSQL, con = engine,chunksize=1000, if_exists = 'replace', index = False)
    dfCleaned.to_csv("myProject/static/file/cleaned.csv")
    columns = dfCleaned.columns
    cols_helper = set()
    # get all columns
    for item in columns:
        cols_helper.add(item)
    for item in cols_helper:
        global_cols.append(item)
    # get numeric columns
    listNumeric = dfCleaned.select_dtypes(include=[np.number,int]).columns.tolist()
    for x in listNumeric:
        global_listNumeric.append(x)
    # get Date columns
    listDates = dfCleaned.select_dtypes(include=np.datetime64).columns.tolist()
    for y in listDates:
        global_listDates.append(y)
    # print to check
    print(global_listNumeric)
    print(global_listDates)
    # jump to filter page
    return redirect((url_for('filter')))


@app.route("/filter",methods=['POST',"GET"])
def filter(listNumeric = global_listNumeric, cols = global_cols, listDates = global_listDates):
    list_dicts = []
    for i in range(0, len(cols)):
        if cols[i] in listNumeric:
            dictionary = {
                        "id": cols[i],
                        "label" : cols[i],
                        "type": 'double',
                        "operators": ['between', 'not between', 'not equal', 'less or equal to', 'greater', 'greater or equal','equal', 'not_equal', 'in', 'not_in', 'is_null', 'is_not_null']
            }
            list_dicts.append(dictionary)
        elif cols[i] in listDates:
            dictionary = {
                        "id": cols[i],
                        "label" : cols[i] ,
                        "type": 'date',
                        "validation": {
                        "format": 'YYYY/MM/DD'
                        },
                        "plugin": 'datepicker',
                        "plugin_config": {
                        "format": 'yyyy/mm/dd',
                        "todayBtn": 'linked',
                        "todayHighlight": "true",
                        "autoclose": "true"
                        },
                        "operators": ['between', 'not between', 'not equal', 'less or equal to', 'greater', 'greater or equal','equal', 'not_equal', 'in', 'not_in', 'is_null', 'is_not_null']
            }
            list_dicts.append(dictionary)
        else:
            dictionary = {
                        "id": cols[i],
                        "label" : cols[i] ,
                        "type": 'string',
                        "operators": ['equal', 'not_equal', 'in', 'not_in', 'begins with', 'contains','not_contains', 'ends with' , 'is empty' 'is not empty', 'is_null', 'is_not_null']
            }
            list_dicts.append(dictionary)

    #print(list_dicts)
    #convert the dictionary to json data
    json_filters = json.dumps(list_dicts)
    # get possible values for each column
    tableSQL = global_filename[0].split('.', 1)[0]
    pre = "SELECT * FROM "
    query = pre + tableSQL
    dfCleaned = pd.read_sql(query,engine)
    cols = list(dfCleaned.columns)
    allPossibleV = {}
    for i,c in enumerate(cols):
        if c in listDates:
            dfCleaned[c] = dfCleaned[c].dt.date
        v = dfCleaned.iloc[:,i].unique()
        v.sort()
        allPossibleV[c] = v
    #print(allPossibleV)
    # render the filter page
    return render_template('filter.html',json_filters = json_filters,cols=cols,length=len(cols),allPossibleV=allPossibleV,name=global_filename[0])


@app.route('/tableResults', methods=['GET','POST'])
def tableResults(filename = global_filename, cols = global_cols):
    #print("____________/tableResults____________________")
    global global_query
    global global_tableName
    global_tableName.clear()

    json_data = request.get_json()
    # get rule
    name = json_data["data"]
    # get table name
    tableName = json_data["tableName"]
    global_query.append(name)
    global_tableName.append(tableName)
    #print(global_query)
    where = " WHERE "
    pre = "SELECT * FROM "
    tableSQL = global_filename[0].split('.', 1)[0]
    query = pre + tableSQL  + where + name
    #print("**************************query1: "+query)
    #query2 = "INSERT INTO FacebookAds.Queries (Query, TableName) VALUES ("  + '"' + name + '"' + " , " + '"' + tableName + '"' + ")"
    #print("query2"+query2)
    #engine.execute(query2)
    # do query and convert to dataFrame
    query1 = text(query)
    df = pd.read_sql(query1, engine)
    # save the result to database
    df.to_sql(name = tableName, con = engine, chunksize=1000, if_exists = 'replace', index = False)
    #save the result to static folder
    df.to_csv("myProject/static/file/filtered.csv")
    name = name.replace("'", "''");
    query2 = "INSERT INTO Queries (Query, TableName) VALUES (" + "'" + name + "','"+tableName + "')"

    print("**************************query2: "+query2)
    query2 = text(query2)
    engine.execute(query2)
    return jsonify(query = query)


@app.route('/pastFilter', methods=['GET','POST'])
def pastFilter():

    queries = "SELECT * FROM Queries"
    query_df = pd.read_sql(queries, engine)
    query_df.to_csv("history.csv")
    query_json = query_df.to_json(date_format = 'iso', orient='records')
    #print(type(query_json))
    query = "SELECT COUNT(*) FROM "
    linesCount = []
    for item in json.loads(query_json):
        queryString = query + item["tablename"]
        lines = engine.execute(queryString)
        linesCount.append(lines.fetchone()[0])
    #print(linesCount)
    print("query_json:  "+query_json)
    return render_template('history.html', linesCount = linesCount, final_result = query_json)


@app.route('/delete', methods=['GET','POST'])
def delete():
    #takes in query and deletes the table
    json_data = request.get_json()
    findvar=json_data["findvar"]
    query1 = "DROP TABLE "
    query2 = "DELETE FROM Queries WHERE TableName = " + "'" + findvar + "'"
    query1 += findvar
    engine.execute(query1)
    engine.execute(query2)
    return jsonify(findvar = findvar)


@app.route('/fetch', methods=['GET','POST'])
def fetch():
    #print("____________/fetch____________________")
    #takes in query and populates the results
    query = "SELECT * FROM "

    json_data = request.get_json()
    findvar=json_data["findvar"]
    print(findvar)
    query += findvar
    print(query)
    engine.execute(query)

    # Convert to DataFrame
    df = pd.read_sql(query, engine)
    print(df.shape[0])
    pandas_dataframe_sample = df.to_html()
    return jsonify(pandas_dataframe_sample = pandas_dataframe_sample)
    #return render_template('results.html', pandas_dataframe_sample  = pandas_dataframe_sample )

@app.route('/display/<item_id>', methods=['GET','POST'])
def display(item_id):
    #print("____________/display____________________")
    query = "SELECT * FROM "
    query += item_id
    engine.execute(query)
    print(query)
    # Convert to DataFrame
    df = pd.read_sql(query, engine)
    df.to_csv("myProject/static/file/query.csv",index = False)
    pandas_dataframe_sample = df.to_html(classes='mystyle',formatters={'Name': lambda x: '<b>' + x + '</b>'})

    return render_template('results.html', pandas_dataframe_sample  = pandas_dataframe_sample )

@app.route("/downloadQuery",methods=['POST'])
def downloadQuery():
    df = pd.read_csv("myProject/static/file/query.csv")
    return GetData(df)()


@app.route("/seg",methods=['GET','POST'])
def seg():
    return render_template('seg.html',filename = global_filename[0]);

@app.route("/seg/cus_seg",methods=['GET','POST'])
def cus_seg():
    dfMerged = pd.read_csv('myProject/static/file/filtered.csv')
    p = Process()
    cols = p.getCusCols(dfMerged)
    return render_template('cus_seg.html',cols=cols,length = len(cols),filename = global_filename[0]);


@app.route("/seg/cus_seg_res",methods=['GET','POST'])
def cus_seg_res():
    dfMerged = pd.read_csv('myProject/static/file/filtered.csv',dtype='str')
    dfMaster = pd.read_csv("myProject/static/file/master.csv")
    picked = request.form.getlist('attributes')
    num = int(request.form.getlist('number')[0])

    p = Process()
    res = p.cus_seg(dfMaster,dfMerged,picked,num)
    cols = p.getCusCols(dfMerged)
    count = res[0]
    resDF = res[1]
    resDF.to_csv("myProject/static/file/cusRes1.csv",index = True)
    index = list(reversed(resDF.index.tolist()))
    clusters = list(resDF.columns)
    data = res[4]
    data.to_csv("myProject/static/file/cusRes2.csv",index = True)
    data = []
    max = 0.0
    for i in range(0, len(resDF)):
        for x,c in enumerate(clusters):
            data.append([x,len(resDF)-i-1,resDF.iloc[i][c]])
            if resDF.iloc[i][c]>max:
                max = resDF.iloc[i][c]
    print(data)
    return render_template('cus_seg_res.html',filename = global_filename[0],cols=cols,length = len(cols),k=res[3],values = count,clusters=clusters,attributes=picked,
    T = [resDF.to_html(classes='mystyle',formatters={'Name': lambda x: '<b>' + x + '</b>'})],index = index,data=data,maxValue = max);

@app.route("/downloadCus1",methods=['POST'])
def downloadCus1():
    df = pd.read_csv("myProject/static/file/cusRes1.csv")
    return GetData(df)()
@app.route("/downloadCus2",methods=['POST'])
def downloadCus2():
    df = pd.read_csv("myProject/static/file/cusRes2.csv")
    return GetData(df)()

@app.route("/seg/com_seg",methods=['GET','POST'])
def com_seg():
    dfMaster = pd.read_csv("myProject/static/file/master.csv")
    dfClient = pd.read_csv("myProject/static/file/client.csv", sep='\t')
    dfMerged = pd.read_csv('myProject/static/file/filtered.csv',dtype='str')
    p = Process()
    res = p.com_seg(dfMaster,dfMerged)

    count = res[1]
    cent = res[3]
    numOfC = len(count)
    cols = []
    for i in range(numOfC):
        cols.append("S "+str(i))
    clustroidsT = pd.DataFrame(cent.T,index=["transaction_sum","transaction_amount_sum"],columns=cols)
    resDF = clustroidsT
    resDF.to_csv("myProject/static/file/comRes1.csv",index = True)
    data = res[2]
    data.to_csv("myProject/static/file/comRes2.csv",index = True)
    clusters = []
    for i in range(len(count)):
        clusters.append('S'+str(i))
    return render_template('com_seg.html',k=res[0],values=count,clusters = clusters,filename = global_filename[0],
    T = [clustroidsT.to_html(classes='mystyle',formatters={'Name': lambda x: '<b>' + x + '</b>'})],index = clustroidsT.index.tolist());

@app.route("/downloadCom1",methods=['POST'])
def downloadCom1():
    df = pd.read_csv("myProject/static/file/comRes1.csv")
    return GetData(df)()

@app.route("/downloadCom2",methods=['POST'])
def downloadCom2():
    df = pd.read_csv("myProject/static/file/comRes2.csv")
    return GetData(df)()

@app.route("/seg/auto_seg",methods=['GET','POST'])
def auto_seg():
    return render_template('auto_seg.html')

@app.route("/downloadAuto",methods=['POST'])
def downloadAuto():
    df = pd.read_csv("myProject/static/file/autoRes.csv")
    return GetData(df)()

@app.route('/test')
def test():
    #index = [0,1,2]
    label = ["cont_id","prod_name","prod_family"]
    return render_template('test.html',label = label)


@app.route("/downloadCSV",methods=['POST'])
def downloadCSV():
    dfMaster = pd.read_csv("myProject/static/file/master.csv")
    dfClient = pd.read_csv("myProject/static/file/upload/client.csv", sep='\t')
    # get columns in client table
    data = []
    vals = dfClient.values
    for row in vals:
        strs = row[0].split('|')
        data.append(strs)
    client_label = dfClient.columns.values[0].split('|')
    dfClient = pd.DataFrame(data, columns=client_label)
    # get columns in master table
    data = []
    vals = dfMaster.values
    for row in vals:
        strs = row[0].split('|')
        data.append(strs)
    cols = dfMaster.columns.values[0].split('|')
    dfMaster = pd.DataFrame(data, columns=cols)
    keys = list(request.form.keys())
    res_dict = {}
    newCols = []
    for key in keys:
        if key!='submit':
            res_dict[key] = request.form.get(key)
            newCols.append(request.form.get(key))
    dfMerge = dfClient.copy()
    dfMerge.columns = newCols

    dfMerge.to_csv("myProject/static/file/matched.csv",index = False)
    return GetData(dfMerge)()



if __name__ == '__main__':
    app.run(debug=True)
