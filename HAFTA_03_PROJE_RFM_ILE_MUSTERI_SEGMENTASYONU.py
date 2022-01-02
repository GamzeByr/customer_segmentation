
import pandas as pd
import datetime as dt

pd.set_option('display.max_columns', None)
pd.set_option('display.width', 500)
pd.set_option('display.float_format', lambda x: '%.4f' % x)

def data_preparing(df):
        pd.set_option('display.max_columns', None)
        print(df.head())
        print(df.info())
        print(df.shape)
        # 3. are there any null values?
        print(f"Count of null values: {df.isnull().sum()}")
        # 4. drop null values
        df.dropna(inplace=True)
        # 5. How many unique items are there ?
        print(f"Unique items: {df.nunique()}")
        # 6. How many of each product are there?
        df["Description"].value_counts().head()
        # 7. Sort 5 most ordered products from most to least.
        df["Description"].value_counts().sort_values(ascending=False).head(5)
        # 8. The 'C' in the invoices shows the canceled transactions. Remove the canceled transactions from the dataset.
        df[~df["InvoiceNo"].str.contains("C", na=False)].head()
        #select values greater than 0(zero)
        df=df[(df["Quantity"]>0)]
        df=df[(df["UnitPrice"]>0)]

def RFM_Metrics_Calculation():
        # 9. Create a variable named 'TotalPrice' that represents the total earnings per invoice
        df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]
        #get today date
        today_date = dt.datetime(2011, 12, 11)
        #calculate RFM metrics
        rfm = df.groupby('CustomerID').agg(
                {'InvoiceDate': lambda x: (today_date - x.max()).days,
                 'InvoiceNo': lambda x: x.nunique(),
                 'TotalPrice': lambda x: x.sum()})
        rfm.columns = ['Recency', 'Frequency', 'Monetary']
        rfm.head()
        rfm = rfm[(rfm["Monetary"] > 0)]

        #RFM Scores
        rfm["Recency_score"] = pd.qcut(rfm["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1])
        rfm["Frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        rfm["Monetary_score"] = pd.qcut(rfm["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
        rfm["RFM_SCORE"] = rfm["Recency_score"].astype(str) + rfm["Frequency_score"].astype(str)

        #create segments
        seg_map = {
                r'[1-2][1-2]': 'hibernating',
                r'[1-2][3-4]': 'at_risk',
                r'[1-2]5': 'cant_loose',
                r'3[1-2]': 'about_to_sleep',
                r'33': 'need_attention',
                r'[3-4][4-5]': 'loyal_customers',
                r'41': 'promising',
                r'51': 'new_customers',
                r'[4-5][2-3]': 'potential_loyalists',
                r'5[4-5]': 'champions'
        }
        #apply segments
        rfm["segment"] = rfm["RFM_SCORE"].replace(seg_map, regex=True)
        return(rfm)

def segment_investigate(rfm,segment_1,segment_2,segment_3):
        rfm_1 = rfm.loc[rfm["segment"] == segment_1]
        rfm_2 = rfm.loc[rfm["segment"] == segment_2]
        rfm_3 = rfm.loc[rfm["segment"] == segment_3]
        return(rfm_1,rfm_2,rfm_3)

def to_excel(rfm,level):
        #export only "loyal_customers"
        rfm2 = rfm.loc[rfm["segment"] == level]
        rfm2.to_excel('RFM.xlsx')
        print(rfm2.head())


#import excel file
df_=pd.read_excel("OnlineRetail.xlsx")
df=df_.copy()
df.head()

data_preparing(df)
#calculate RFM metrics
rfm=RFM_Metrics_Calculation()
rfm.reset_index(inplace=True)

#Export to excel file
to_excel(rfm,"loyal_customers")

#investigate 3 segments
segment_investigate(rfm,'champions','cant_loose','new_customer')













