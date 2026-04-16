from django.db.models import Count
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

import pandas as pd
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
# Create your views here.
from Remote_User.models import ClientRegister_Model,identity_theft_detection,detection_ratio,detection_accuracy

def login(request):


    if request.method == "POST" and 'submit1' in request.POST:

        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            enter = ClientRegister_Model.objects.get(username=username,password=password)
            request.session["userid"] = enter.id

            return redirect('ViewYourProfile')
        except:
            pass

    return render(request,'RUser/login.html')

def index(request):
    return render(request, 'RUser/index.html')

def Add_DataSet_Details(request):

    return render(request, 'RUser/Add_DataSet_Details.html', {"excel_data": ''})


def Register1(request):

    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phoneno = request.POST.get('phoneno')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        gender = request.POST.get('gender')
        ClientRegister_Model.objects.create(username=username, email=email, password=password, phoneno=phoneno,
                                            country=country, state=state, city=city,address=address,gender=gender)

        obj = "Registered Successfully"
        return render(request, 'RUser/Register1.html',{'object':obj})
    else:
        return render(request,'RUser/Register1.html')

def ViewYourProfile(request):
    userid = request.session['userid']
    obj = ClientRegister_Model.objects.get(id= userid)
    return render(request,'RUser/ViewYourProfile.html',{'object':obj})


def Predict_Theft_Status(request):
    if request.method == "POST":
        Account_Id=request.POST.get('Account_Id')
        Trans_Id=request.POST.get('Trans_Id')
        Age=request.POST.get('Age')
        Followers=request.POST.get('Followers')
        NAME_CONTRACT_TYPE=request.POST.get('NAME_CONTRACT_TYPE')
        GENDER=request.POST.get('GENDER')
        AMT_INCOME_TOTAL=request.POST.get('AMT_INCOME_TOTAL')
        AMT_CREDIT=request.POST.get('AMT_CREDIT')
        AMT_ANNUITY=request.POST.get('AMT_ANNUITY')
        AMT_GOODS_PRICE=request.POST.get('AMT_GOODS_PRICE')
        NAME_INCOME_TYPE=request.POST.get('NAME_INCOME_TYPE')
        NAME_FAMILY_STATUS=request.POST.get('NAME_FAMILY_STATUS')

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

        best_model = None
        best_score = 0.0
        for name, model in models:
            model.fit(X_train, y_train)
            score = accuracy_score(y_test, model.predict(X_test))
            if score > best_score:
                best_score = score
                best_model = model

        if best_model is None:
            best_model = models[0][1]

        model_name = [name for name, model in models if model is best_model][0]
        print(f"Best model: {model_name} accuracy={best_score*100:.2f}%")

        input_data = {
            'Age': float(Age or 0),
            'Followers': float(Followers or 0),
            'NAME_CONTRACT_TYPE': NAME_CONTRACT_TYPE or '',
            'GENDER': GENDER or '',
            'AMT_INCOME_TOTAL': float(AMT_INCOME_TOTAL or 0),
            'AMT_CREDIT': float(AMT_CREDIT or 0),
            'AMT_ANNUITY': float(AMT_ANNUITY or 0),
            'AMT_GOODS_PRICE': float(AMT_GOODS_PRICE or 0),
            'NAME_INCOME_TYPE': NAME_INCOME_TYPE or '',
            'NAME_FAMILY_STATUS': NAME_FAMILY_STATUS or ''
        }
        input_df = pd.DataFrame([input_data])
        predict_text = best_model.predict(input_df)

        prediction = int(predict_text[0])

        if (prediction == 0):
            val = 'No Theft or Fraud Found'
        elif (prediction == 1):
            val = 'Theft or Fraud Found'

        print(val)

        identity_theft_detection.objects.create(
        Account_Id=Account_Id,
        Trans_Id=Trans_Id,
        Age=Age,
        Followers=Followers,
        NAME_CONTRACT_TYPE=NAME_CONTRACT_TYPE,
        GENDER=GENDER,
        AMT_INCOME_TOTAL=AMT_INCOME_TOTAL,
        AMT_CREDIT=AMT_CREDIT,
        AMT_ANNUITY=AMT_ANNUITY,
        AMT_GOODS_PRICE=AMT_GOODS_PRICE,
        NAME_INCOME_TYPE=NAME_INCOME_TYPE,
        NAME_FAMILY_STATUS=NAME_FAMILY_STATUS,
        Prediction=val)

        return render(request, 'RUser/Predict_Theft_Status.html',{'objs': val})
    return render(request, 'RUser/Predict_Theft_Status.html')



