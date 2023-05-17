import csv

from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db



# Flask 인스턴스 생성 #Flask instance 生成
app = Flask(__name__)
api = Api(app)



cred = credentials.Certificate("capstone-da813-firebase-adminsdk-sfdae-24fcf410e1.json")
obj = firebase_admin.initialize_app(cred,{
    'databaseURL' : 'https://capstone-da813-default-rtdb.firebaseio.com/'

})


# 제한과목 필터 func　#制限科目フィルター　func
def get_restricted(sentence):
    # major = "무역학부"
    # 1. firebase에서 "학과(부)" 가져오기!
    major = sentence

    with open('restricted_subjects.csv', newline='', encoding='UTF-8') as f2:
        reader = csv.reader(f2)
        data = list(reader)

    num = len(data)

    arr = [[0 for col in range(10)] for row in range(num)]

    for i in range(1, num):
        str2 = data[i][1]
        x = str2.split(",")
        for j in range(len(x)):
            arr[i].append(x[j])
    temp = ""
    for i in range(1, num):
        if major == data[i][0]:
            for j in range(0, len(arr[i])):
                if arr[i][j] != 0:
                    # print(arr[i][j])  # 제한과목 목록. 출력　#制限科目リスト、出力
                    temp+=arr[i][j]+","

    f2.close()

    return temp


#리스너 함수　#リスナー関数
def listener(event):

    """
     #데이터출력　#データ出力
    print(event.event_type)  # can be 'put' or 'patch'
    print(event.path)  # relative to the reference, it seems
    print(event.data)
    """
    with open('data.json', 'r', encoding='utf-8') as f1:
        json_data = json.load(f1)

    global str3


    CLASSES = json.dumps(json_data, ensure_ascii=False)
    jsob = json.loads(CLASSES)

    line = len(jsob)
    parser = reqparse.RequestParser()
    parser.add_argument('task')


    major = db.reference("majorName")


    restrict_class = get_restricted(major)

    class_arr = restrict_class.split(",")

    for i in range(0,len(class_arr)-1):
        print(class_arr[i])


    stt_text = str(event.data)

    df = pd.read_csv('class_all_FINAL.csv', encoding='utf-8')

    df.loc[(df['class'] == '검색'), 'keyword'] = stt_text

    tfidf_vectorizer = TfidfVectorizer()  # TF-IDF 객체선언　#TF-IDFオブジェクト宣言
    tfidf_matrix = tfidf_vectorizer.fit_transform(df['keyword'])

    cosine_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)

    class2id = {}
    for i, c in enumerate(df['class']): class2id[i] = c
    id2class = {}
    for i, c in class2id.items(): id2class[c] = i
    class_Num = {}
    for i, c in enumerate(df['class_num']): class_Num[i] = c

    idx = id2class['검색']
    # print(class2id)
    # print(id2class)
    # print(class_Num)
    sim_scores = [(i, c) for i, c in enumerate(cosine_matrix[idx]) if i != idx]  # 자기 자신을 제외한 과목들의 유사도 및 인덱스를 추출
                                                                                 # 科目たちの類似度、Index抽出
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)  # 유사도가 높은 순서대로 정렬
                                                                       # 類似度が高い順で整列

    sim_scores = [(class_Num[i], score) for i, score in sim_scores[0:10]]
    # print(sim_scores)
    res = []
    for i in range(10):
        if float(sim_scores[i][1]) > 0:
            res.append(sim_scores[i][0])

    m = dict(zip(range(1, len(res) + 1), res))  # 상위10개과목 제이슨으로 변환　# 上位10科目jsonに変換
    m = json.dumps(m, ensure_ascii=False)
    jsonObject = json.loads(m)

    # print(m)
    list = []

# sentence를 firebase로 부터 받아온다
# get_restricted(sentence)를 통해 문자열 temp를 받아 문자열을 ',' 로 split을 해서 각 과목명을 임시 list에 저장한다
# ex. 3개의 과목명이 있는 list_tmp[] 의 각 element와 추천과목의 과목명을 비교하여 filtering한다.
# filtering할 때 10개를 가져오면            1)10개 이하의 과목이 불러와져도 괜찮음. class로 넣는 것이기때문에 안드를 조금 수정해야함         2)10개를 가져옴. 대신 pycharm에서 counting이 필요함.

# sentenceをFirebaseから受け取ってくる
# get_restricted(sentence)を通じて文字列tempを受け取り、文字列を','とsplitして各科目名を臨時listに保存する
# ex. 3 つの科目名があるlist_tmp[] の各elementと推薦科目の科目名を比較してfilteringする。

    ref = db.reference('majorName')
    row = ref.get()
    sen = get_restricted(row)
    #print(sen)

    list_tmp = sen.split(',')
    # print("len:",len(list_tmp))

    cnt=0
    for i in range(1, 11):
        if cnt == 10 : break
        tmp = str(i)
        str2 = str(jsonObject.get(tmp)) # 학수번호　# 授業番号
        chk=True
        for i in range(0, line):
            if str2 == jsob[i].get("학수번호"):  # 비교해서 같을 경우　# 比較して同じ場合

                for j in range(0,len(list_tmp)-1):
                    if jsob[i].get("교과목명") == list_tmp[j]:
                        chk=False

                if chk is not False:
                    str3 = jsob[i].get("교과목명"), jsob[i].get("담당교수"), jsob[i].get("학수번호"), \
                           jsob[i].get("대학(원)"), jsob[i].get("학과(부)"), jsob[i].get("이수구분"), \
                           jsob[i].get("학년"), jsob[i].get("학점"), jsob[i].get("수업방법관리"), jsob[i].get("시간표")
                    list.append(str3)
                    cnt+=1
                    # print(str3)



    # print(len(list))
    # 추출한 정보들을 json으로 변환.
    # 抽出した情報をjsonに変換。
    l = dict(zip(range(0, len(list) + 1), list))
    l = json.dumps(l, ensure_ascii=False, indent="\t")
    print(l)
    jsonObject2 = json.loads(l)
    # print(jsonObject2)

    dir = db.reference('Recommendedclass')
    check = db.reference('check')
    dir.delete()
    dir.set(jsonObject2)  # db에 업데이트.
    if dir.get() is None:
        check.set("null")
    else:
        check.set("exist")
    f1.close()

#리스너 실행　# リスナー実行
dir=db.reference('sttText', app= obj).listen(listener)

# 서버 실행 # サーバー実行
if __name__ == '__main__':
    app.run(debug=True)
