
from django.db.models import  Count, Avg
from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models import Q
import datetime
import xlwt
from django.http import HttpResponse


import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.ensemble import ExtraTreesClassifier, RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Create your views here.
from Remote_User.models import ClientRegister_Model,identity_theft_detection,detection_ratio,detection_accuracy


def serviceproviderlogin(request):
    if request.method  == "POST":
        admin = request.POST.get('username')
        password = request.POST.get('password')
        if admin == "Admin" and password =="Admin":
            detection_accuracy.objects.all().delete()
            return redirect('View_Remote_Users')

    return render(request,'SProvider/serviceproviderlogin.html')

def View_Theft_Status_Ratio(request):
    detection_ratio.objects.all().delete()
    ratio = ""
    kword = 'No Theft or Fraud Found'
    print(kword)
    obj = identity_theft_detection.objects.all().filter(Q(Prediction=kword))
    obj1 = identity_theft_detection.objects.all()
    count = obj.count()
    count1 = obj1.count()
    if count1 > 0:
        ratio = (count / count1) * 100
        if ratio != 0:
            detection_ratio.objects.create(names=kword, ratio=ratio)

    ratio12 = ""
    kword12 = 'Theft or Fraud Found'
    print(kword12)
    obj12 = identity_theft_detection.objects.all().filter(Q(Prediction=kword12))
    obj112 = identity_theft_detection.objects.all()
    count12 = obj12.count()
    count112 = obj112.count()
    if count112 > 0:
        ratio12 = (count12 / count112) * 100
        if ratio12 != 0:
            detection_ratio.objects.create(names=kword12, ratio=ratio12)


    obj = detection_ratio.objects.all()
    return render(request, 'SProvider/View_Theft_Status_Ratio.html', {'objs': obj})

def View_Remote_Users(request):
    obj=ClientRegister_Model.objects.all()
    return render(request,'SProvider/View_Remote_Users.html',{'objects':obj})

def charts(request,chart_type):
    chart1 = detection_ratio.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts.html", {'form':chart1, 'chart_type':chart_type})

def charts1(request,chart_type):
    chart1 = detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/charts1.html", {'form':chart1, 'chart_type':chart_type})

def View_Prediction_Of_Theft_Status(request):
    obj =identity_theft_detection.objects.all()
    return render(request, 'SProvider/View_Prediction_Of_Theft_Status.html', {'list_objects': obj})

def likeschart(request,like_chart):
    charts =detection_accuracy.objects.values('names').annotate(dcount=Avg('ratio'))
    return render(request,"SProvider/likeschart.html", {'form':charts, 'like_chart':like_chart})


def Download_Predicted_DataSets(request):

    response = HttpResponse(content_type='application/ms-excel')
    # decide file name
    response['Content-Disposition'] = 'attachment; filename="Predicted_Datasets.xls"'
    # creating workbook
    wb = xlwt.Workbook(encoding='utf-8')
    # adding sheet
    ws = wb.add_sheet("sheet1")
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    # headers are bold
    font_style.font.bold = True
    # writer = csv.writer(response)
    obj = identity_theft_detection.objects.all()
    data = obj  # dummy method to fetch data.
    for my_row in data:

        row_num = row_num + 1

        ws.write(row_num, 0, my_row.Account_Id, font_style)
        ws.write(row_num, 1, my_row.Trans_Id, font_style)
        ws.write(row_num, 2, my_row.Age, font_style)
        ws.write(row_num, 3, my_row.Followers, font_style)
        ws.write(row_num, 4, my_row.NAME_CONTRACT_TYPE, font_style)
        ws.write(row_num, 5, my_row.GENDER, font_style)
        ws.write(row_num, 6, my_row.AMT_INCOME_TOTAL, font_style)
        ws.write(row_num, 7, my_row.AMT_CREDIT, font_style)
        ws.write(row_num, 8, my_row.AMT_ANNUITY, font_style)
        ws.write(row_num, 9, my_row.AMT_GOODS_PRICE, font_style)
        ws.write(row_num, 10, my_row.NAME_INCOME_TYPE, font_style)
        ws.write(row_num, 11, my_row.NAME_FAMILY_STATUS, font_style)
        ws.write(row_num, 12, my_row.Prediction, font_style)

    wb.save(response)
    return response

def train_model(request):
    detection_accuracy.objects.all().delete()

    df = pd.read_csv('Datasets.csv')
    df['results'] = df['Label'].astype(int)

    feature_cols = [
        'Age', 'Followers', 'NAME_CONTRACT_TYPE', 'GENDER',
        'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE',
        'NAME_INCOME_TYPE', 'NAME_FAMILY_STATUS'
    ]
    categorical_cols = ['NAME_CONTRACT_TYPE', 'GENDER', 'NAME_INCOME_TYPE', 'NAME_FAMILY_STATUS']
    numeric_cols = ['Age', 'Followers', 'AMT_INCOME_TOTAL', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE']

    X = df[feature_cols]
    y = df['results']

    numeric_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    categorical_transformer = Pipeline([
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', drop='first')),
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_cols),
            ('cat', categorical_transformer, categorical_cols),
        ],
        remainder='drop'
    )

    models = [
        ('extra_tree', Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', ExtraTreesClassifier(class_weight='balanced', random_state=42))
        ])),
        ('random_forest', Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42))
        ])),
        ('gradient_boosting', Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', GradientBoostingClassifier(n_estimators=150, learning_rate=0.1, max_depth=3, random_state=42))
        ])),
        ('logistic', Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42))
        ])),
    ]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=42
    )

    for name, model in models:
        model.fit(X_train, y_train)
        score = accuracy_score(y_test, model.predict(X_test)) * 100
        print(name)
        print("ACCURACY")
        print(score)
        print("CLASSIFICATION REPORT")
        print(classification_report(y_test, model.predict(X_test)))
        print("CONFUSION MATRIX")
        print(confusion_matrix(y_test, model.predict(X_test)))
        detection_accuracy.objects.create(names=name.replace('_', ' ').title(), ratio=score)



    csv_format = 'Results.csv'
    df.to_csv(csv_format, index=False)
    df.to_markdown

    obj = detection_accuracy.objects.all()
    return render(request,'SProvider/train_model.html', {'objs': obj})