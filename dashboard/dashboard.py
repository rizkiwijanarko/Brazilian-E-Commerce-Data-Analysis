import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import matplotlib.ticker as mtick
import os

sns.set(style='dark')


# Helper functions
def create_review_df(df):
    review_df = df.groupby('review_score').agg({
        'review_id': 'count'
    })

    review_df = review_df.reset_index()

    review_df.rename(columns={
        'review_score': 'review_score',
        'review_id': 'number_of_reviews'
    }, inplace=True)

    return review_df


def create_sales_df(df):
    sales_df = df.groupby('product_category_name_english').agg({
        'order_id': 'count'
    })

    sales_df = sales_df.reset_index()

    sales_df.rename(columns={
        'product_category_name_english': 'product_category',
        'order_id': 'number_of_orders'
    }, inplace=True)

    return sales_df


def create_revenue_df(df):
    revenue_df = df.groupby('product_category_name_english').agg({
        'payment_value': 'sum'
    })

    revenue_df = revenue_df.reset_index()

    revenue_df.rename(columns={
        'product_category_name_english': 'product_category',
        'payment_value': 'total_revenue'
    }, inplace=True)

    return revenue_df


def create_rfm_df(df):
    rfm_df = df.groupby(by='customer_id', as_index=False).agg({
        "order_purchase_timestamp": "max",
        "order_id": "count",
        "payment_value": "sum"
    })

    rfm_df.columns = ['customer_id', 'last_purchase', 'frequency', 'monetary']

    # Extract the date from the 'last_purchase' column
    rfm_df['last_purchase'] = rfm_df['last_purchase'].dt.date

    # Use the last purchase date to calculate recency
    recent_date = rfm_df['last_purchase'].max()
    rfm_df['recency'] = rfm_df['last_purchase'].apply(lambda x: (recent_date - x).days)

    rfm_df.drop('last_purchase', axis=1, inplace=True)

    return rfm_df


# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create the full path to the file
file_path = os.path.join(current_dir, 'main_data.csv')

# Load dataset
all_df = pd.read_csv(file_path)


# Memastikan kolom-kolom yang bertipe datetime sudah dalam format yang benar
datetime_columns = ['order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date',
                    'order_delivered_customer_date', 'order_estimated_delivery_date']

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

# Membuat Komponen Filter
min_date = all_df['order_purchase_timestamp'].min()
max_date = all_df['order_purchase_timestamp'].max()

# Sidebar
with st.sidebar:
    st.title('Filter')
    st.subheader('Rentang Waktu')
    start_date = st.date_input('Tanggal Dimulai', min_date)
    end_date = st.date_input('End Date', max_date)

    if st.button('Terapkan Filter'):
        # Convert start_date and end_date to datetime64[ns] type
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)

        # Filter data
        main_df = all_df[(all_df['order_purchase_timestamp'] >= start_date) & (all_df['order_purchase_timestamp'] <= end_date)]
    else:
        main_df = all_df.copy()

# Memanggil Fungsi Helper
review_df = create_review_df(main_df)
sales_df = create_sales_df(main_df)
revenue_df = create_revenue_df(main_df)
rfm_df = create_rfm_df(main_df)

# Main
st.header('Dashboard Penjualan E-commerce di Brazil')

# Review Score Distribution
st.subheader('Persentase Tingkat Kepuasan Pelanggan Selama Berbelanja')

# Plotting Pie Chart
plt.figure(figsize=(15, 8))
plt.pie(review_df['number_of_reviews'], labels=review_df['review_score'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel', 5))
plt.title('Distribusi Tingkat Kepuasan Pelanggan')
st.pyplot(fig=plt)

# Penjualan Berdasarkan Kategori Produk
st.subheader('Penjualan Berdasarkan Kategori Produk')
# Plotting Bar Chart
fig, ax = plt.subplots(1, 2, figsize=(20, 10))
colors_ = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Jumlah Penjualan Paling Banyak
sns.barplot(x='number_of_orders', y='product_category', data=sales_df.sort_values(by='number_of_orders', ascending=False).head(10), ax=ax[0], palette=colors_)
ax[0].set_title('10 Kategori dengan Penjualan Paling Banyak', loc='center')
ax[0].set_xlabel('Total Penjualan')
ax[0].set_ylabel(None)

# Jumlah Penjualan Paling Sedikit
sns.barplot(x='number_of_orders', y='product_category', data=sales_df.sort_values(by='number_of_orders', ascending=True).head(10), ax=ax[1], palette=colors_)
ax[1].set_title('10 Kategori Produk dengan Penjualan Paling Sedikit', loc='center')
ax[1].set_xlabel('Total Penjualan')
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
plt.suptitle("Penjualan Terbanyak dan Terendah Berdasarkan Kategori Produk")
st.pyplot(fig)

# Total Revenue Berdasarkan Kategori Produk
st.subheader('Total Revenue Berdasarkan Kategori Produk')
# Plotting Bar Chart
fig, ax = plt.subplots(1, 2, figsize=(45, 20))

# Total Revenue Paling Banyak
sns.barplot(x='total_revenue', y='product_category', data=revenue_df.sort_values(by='total_revenue', ascending=False).head(10), ax=ax[0], palette=colors_)
ax[0].set_title('10 Kategori Produk dengan Total Revenue Paling Banyak', fontsize=25)
ax[0].set_xlabel('Total Revenue')
ax[0].set_ylabel('Kategori Produk')
# Format sumbu-x ke skala normal
fmt = '{x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
ax[0].xaxis.set_major_formatter(tick)
ax[0].tick_params(axis='x', labelsize=20)
ax[0].tick_params(axis='y', labelsize=30)

# Total Revenue Paling Sedikit
sns.barplot(x='total_revenue', y='product_category', data=revenue_df.sort_values(by='total_revenue', ascending=True).head(10), ax=ax[1], palette=colors_)
ax[1].set_title('10 Kategori Produk dengan Total Revenue Paling Sedikit', fontsize=25)
ax[1].set_xlabel('Total Penjualan')
ax[1].set_ylabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].tick_params(axis='x', labelsize=20)
ax[1].tick_params(axis='y', labelsize=30)
plt.suptitle("Total Revenue Terbanyak dan Terendah Berdasarkan Kategori Produk", fontsize=35)
st.pyplot(fig)

# RFM Analysis
st.subheader('Pelanggan Terbaik Berdasarkan RFM Analysis')
col1, col2, col3 = st.columns(3)

# Recency Average
with col1:
    avg_recency = round(rfm_df['recency'].mean(),1)
    st.metric(label='Rata-rata Recency (hari)', value=avg_recency, delta=0, delta_color='normal')

# Frequency Average
with col2:
    avg_frequency = round(rfm_df['frequency'].mean(),1)
    st.metric(label='Rata-rata Frequency', value=avg_frequency, delta=0, delta_color='normal')

# Monetary Average
with col3:
    avg_monetary = format_currency(rfm_df['monetary'].mean(), 'BRL', locale='pt_BR')
    st.metric(label='Rata-rata Monetary', value=avg_monetary, delta=0, delta_color='normal')

# Plotting Bar Chart
fig, ax = plt.subplots(1, 3, figsize=(35, 15))

colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]

# Recency
sns.barplot(y='recency', x='customer_id', data=rfm_df.sort_values(by='recency', ascending=True).head(5), ax=ax[0], palette=colors)
ax[0].set_ylabel(None)
ax[0].set_xlabel('customer_id', fontsize=30)
ax[0].set_title('Recency (hari)', loc='center', fontsize=50)
ax[0].tick_params(axis='y', labelsize=30)
ax[0].tick_params(axis='x', rotation=10)
# Atur batas bawah sumbu-y ke 0
ax[0].set_ylim(0, 10)


# Frequency
sns.barplot(y='frequency', x='customer_id', data=rfm_df.sort_values(by='frequency', ascending=False).head(5), ax=ax[1], palette=colors)
ax[1].set_ylabel(None)
ax[1].set_xlabel('customer_id', fontsize=30)
ax[1].set_title('Frequency', loc='center', fontsize=50)
ax[1].tick_params(axis='y', labelsize=30)
ax[1].tick_params(axis='x', rotation=10)

#Monetary
sns.barplot(y='monetary', x='customer_id', data=rfm_df.sort_values(by='monetary', ascending=False).head(5), ax=ax[2], palette=colors)
ax[2].set_ylabel(None)
ax[2].set_xlabel('customer_id', fontsize=30)
ax[2].set_title('Monetary', loc='center', fontsize=50)
ax[2].tick_params(axis='y', labelsize=30)
ax[2].tick_params(axis='x', rotation=10)

st.pyplot(fig)

st.caption('Made by Kharisma Rizki Wijanarko')