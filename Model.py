import pickle as pk
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from sklearn.ensemble import GradientBoostingClassifier
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class FitModel(object):

    def __init__(self):
        self.df=None
        self.X=None

    def _event_to_pd(self,event):
        """
        Takes in a python dictionary object
        Returns None
        """
        df=pd.DataFrame({"delivery_method2":[1,0,3,1,0,3,1,0,3,0],
        "payout_type2":["",'CHECK','ACH',"",'CHECK','ACH',"",'CHECK','ACH','ACH'],
        "user_type2":[1,3,4,5,103,2,3,1,4,1],"cluster":[0,1,2,3,4,5,6,7,8,9]})
        df=pd.DataFrame([event])
        return df

    def feature_selection(self,event):
        df=self._event_to_pd(event)
        df=self.clean_description(df)
        df=self.clean_delivery(df)
        df=self.clean_payouttype(df)
        self.build_features(df)
        #df=clean_tickettype(df)
        x_df=df[['delivery_method_0.0',
           'delivery_method_1.0', 'delivery_method_3.0','payout_type_',
           'payout_type_ACH', 'payout_type_CHECK','has_analytics','fb_published',
           'has_logo','user_age','diff_domicile','diff_payee_compmany',
           'has_multiple_payees','user_type_1','user_type_2','user_type_3',
           'user_type_4','user_type_5','user_type_103','diff_email_domain',
           'cluster_0', 'cluster_1', 'cluster_2','cluster_3', 'cluster_4',
           'cluster_5', 'cluster_6', 'cluster_7','cluster_8', 'cluster_9']]
        X=x_df.as_matrix()
        return X

    def predict(self,event):
        """
        Takes in feature matrix
        Return predicted probability
        """
        X=self.feature_selection(event)
        with open("gbcModel.pkl",'rb') as f_un:
            gbcmodel= pk.load(f_un)
        predictions=gbcmodel.predict_proba(X)
        return list(predictions[:,1])[0]


    def clean_description(self,df):
        '''cleans the descriptions, creating text.
            Puts into nlp to get a sparse matrix.
            Takes sparse matrix and clustered to get categories of 10 types'''
        descriptions = df.description
        text_descriptions = descriptions.apply(self.remove_html)
        with open('vec.pkl', 'rb') as f:
            vec = pk.load(f)
        nlp_transform=vec.transform(text_descriptions)

        with open('kmeans.pkl','rb') as f:
            kmeans = pk.load(f)
        clusters=kmeans.predict(nlp_transform)
        df['cluster'] = clusters
        df['cluster_0'] = df['cluster'].apply(lambda x: 1 if x == 0 else 0)
        df['cluster_1'] = df['cluster'].apply(lambda x: 1 if x == 1 else 0)
        df['cluster_2'] = df['cluster'].apply(lambda x: 1 if x == 2 else 0)
        df['cluster_3'] = df['cluster'].apply(lambda x: 1 if x == 3 else 0)
        df['cluster_4'] = df['cluster'].apply(lambda x: 1 if x == 4 else 0)
        df['cluster_5'] = df['cluster'].apply(lambda x: 1 if x == 5 else 0)
        df['cluster_6'] = df['cluster'].apply(lambda x: 1 if x == 6 else 0)
        df['cluster_7'] = df['cluster'].apply(lambda x: 1 if x == 7 else 0)
        df['cluster_8'] = df['cluster'].apply(lambda x: 1 if x == 8 else 0)
        df['cluster_9'] = df['cluster'].apply(lambda x: 1 if x == 9 else 0)

        return df


    def remove_html(self,html):
        soup = BeautifulSoup(html, 'html.parser')
        return(soup.text)


    def clean_delivery(self,df):
        #df=pd.get_dummies(df, prefix=['delivery_method'], columns=['delivery_method'])
        #return df

        df['delivery_method_1.0'] = df['delivery_method'].apply(lambda x: 1 if x == 1.0 else 0)
        df['delivery_method_0.0'] = df['delivery_method'].apply(lambda x: 1 if x == 0.0 else 0)
        df['delivery_method_3.0'] = df['delivery_method'].apply(lambda x: 1 if x == 3.0 else 0)
        return df

    def clean_payouttype(self,df):
        df['payout_type_CHECK'] = df['payout_type'].apply(lambda x: 1 if x == "CHECK" else 0)
        df['payout_type_ACH'] = df['payout_type'].apply(lambda x: 1 if x == "ACH" else 0)
        df['payout_type_'] = df['payout_type'].apply(lambda x: 1 if x == "" else 0)
        return df


    def build_features(self,df):

        # Is the domicile of the company the same as the venue?
        df['diff_domicile'] = (df['country']!=df['venue_country']).astype(int)

        # Is the payee name the same as the company ?
        df['diff_payee_compmany'] = (df['org_name']!=df['payee_name']).astype(int)

        #Is the payee always the same?
        df['has_multiple_payees'] = df['previous_payouts'].apply(self.check_same_payee)

        #payout type is check

        #df['payout_type'] = (df['payout_type']=='CHECK').astype(int)

        # creates dummy columns
        df['user_type_1'] = (df['user_type']==1).astype(int)
        df['user_type_2'] = (df['user_type']==2).astype(int)
        df['user_type_3'] = (df['user_type']==3).astype(int)
        df['user_type_4'] = (df['user_type']==4).astype(int)
        df['user_type_5'] = (df['user_type']==5).astype(int)
        df['user_type_103'] = (df['user_type']==103).astype(int)

        #creates a column with the domain:
        df['email_domain'] = df['email_domain'].apply(self.check_email_domain)

        #creates a column with words from company name:
        df['split_name'] = df['org_name'].apply(self.split_name)

        # creates a field indicating diff domain name

        df['diff_email_domain'] = ''
        for i in range(len(df)):
            df.loc[i, 'diff_email_domain'] = int(df.loc[i, 'email_domain'] not in df.loc[i,'split_name'])


    def check_same_payee(self,data):
        values = [i.get('name') for i in data]
        values = set(values)
        return int(len(values) <=1)


    def check_email_domain(self,data):
        return data.split('.')[0]

    def split_name(self,data):
        output = [word.lower() for word in data.split()]
        return set(output)
    ### Add in other defs to construct feature matrix and self.X = X
