import  datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x : '%.2f' %x)
#pd.set_option('display.max_rows', 200)

df_ = pd.read_excel(r'C:\Users\ap\Desktop\miuul\CRM\online_retail_II.xlsx', sheet_name="Year 2010-2011")
df = df_.copy()
df.head()
df.describe().T
df.isnull().sum()
df.dropna(inplace=True)
df["StockCode"].nunique()
df["StockCode"].value_counts()
df.groupby("Description").agg({"Quantity": "sum"})
df.groupby("Description").agg({"Quantity": "sum"}).sort_values("Quantity", ascending=False).head()
df = df[~df["Invoice"].str.contains("C", na=False)]
df["TotalPrice"] = df["Quantity"] * df["Price"]

df["InvoiceDate"].max()
today_date = dt.datetime(2011, 12, 11)

rfm = df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate: (today_date - InvoiceDate.min()),
                                     "Invoice": lambda Invoice: Invoice.nunique(),
                                     "TotalPrice": lambda  TotalPrice: TotalPrice.sum()})
rfm.columns = ["Recency", "Frequency", "Monetary"]

rfm["recency_score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1])
rfm["frequency_score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
rfm["monetary_score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5])
rfm["RF_SCORE"] = rfm["recency_score"].astype(str) + rfm["frequency_score"].astype(str)
rfm.head()

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customer',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}
rfm["segment"] = rfm["RF_SCORE"].replace(seg_map, regex=True)
rfm["segment"].value_counts()
rfm.groupby("segment").agg({"Frequency": "mean",
                            "Recency": "mean",
                            "Monetary": "mean"})

# cant_loose segmentindeki müşteriler, monetary değeri en yüksek olan müşterilerdir.
# Bu müşterileri kaybetmemek ve geri kazanmak için özel teklifler ve kampanyalar sunulabilir.

# potantial_loyalist segmentindeki müşterileri champions segmentine dahil edebilmek adına,
# kişisel kampanyalar sunabiliriz, alışverişlerinde ekstra ödüllendirme programları hazırlayarak
# bu müşterilerimizi sadık müşterimiz yapabiliriz.

# Düşük recency ve frekanslara sahip olan yeni müşterilerimiz(new_customer segmenti) için,
# hoşgeldiniz kampanyaları sunulabilir, yaptıkları alışverişlere göre onlara kişiselleştirilmiş
# önerilerde bulunulabilir, uzun vadede kazançlı çıkacakları çeşitli müşteri sadakat kampanyalarına
# dahil edilebilirler ve bu sayede bağlılıkları artırılabilir.

rfm.reset_index()
loyal_cust_ids = pd.DataFrame()
loyal_cust_ids = loyal_cust_ids.reset_index()
loyal_cust_ids = loyal_cust_ids["Customer ID"]
loyal_cust_ids.to_excel("loyal_customers.xlsx")