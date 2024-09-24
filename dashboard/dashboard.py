import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set_theme(style='dark')

# Helper function yang dibutuhkan untuk menyiapkan berbagai dataframe
def fix_data_type(df):
    df['holiday'] = df['holiday'].astype(bool)
    df['workingday'] = df['workingday'].astype(bool)
    df['dteday'] = pd.to_datetime(df['dteday'])
    return df
    

def create_descriptive_df(df):
    season_map = {
        "1": "Spring",
        "2": "Summer",
        "3": "Fall",
        "4": "Winter",
    }
    weathersit_map = {
        "1": "Clear",
        "2": "Cloudy",
        "3": "Light Rain",
        "4": "Heavy Rain",
    }
    
    descriptive_df = df.copy()
    list_of_cols = ['season', 'weathersit']
    
    for col in list_of_cols:
        # mengubah tipe data dari int ke str
        descriptive_df[col] = descriptive_df[col].astype(str)
        # ubah semua data dengan map
        if col == 'season':
            descriptive_df[col] = descriptive_df[col].map(season_map)
        else:
            descriptive_df[col] = descriptive_df[col].map(weathersit_map)
            
    # data cleaning/fixing
    descriptive_df['holiday'] = descriptive_df['holiday'].astype(bool)
    descriptive_df['workingday'] = descriptive_df['workingday'].astype(bool)
    descriptive_df['dteday'] = pd.to_datetime(descriptive_df['dteday'])
    
    year_map = {
        0: 2011,
        1: 2012,
    }
    descriptive_df['yr'] = descriptive_df['yr'].map(year_map)
    
    return descriptive_df

# Load cleaned data
day_df = fix_data_type(pd.read_csv("data/day.csv"))
hour_df = fix_data_type(pd.read_csv("data/hour.csv"))

day_df_alt = create_descriptive_df(day_df)
hour_df_alt = create_descriptive_df(hour_df)

# Filter data
min_date = day_df_alt["dteday"].min()
max_date = day_df_alt["dteday"].max()

with st.sidebar:
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
# UI START
st.title("Data Analysis Project")
st.subheader("(Dataset Bike Sharing System)")

# memberikan datafram berdasarkan input dari sidebar
main_df = day_df_alt[(day_df_alt["dteday"] >= str(start_date)) & 
                (day_df_alt["dteday"] <= str(end_date))]
st.subheader("Data Berdasarkan Date dari sidebar")
st.dataframe(main_df, hide_index=True)

workday_df = main_df.groupby(by="workingday", observed=False).agg({
  "cnt": ["max", "min", "mean"]
})
# Flatten the MultiIndex columns  
workday_df.columns = [col[1] + " user count" for col in workday_df.columns.values]  

# Reset index if needed  
workday_df.reset_index(inplace=True)

# workday_df.columns = ["working day?", "Average User Count", "Max User Count", "Min User Count"]
st.subheader("Perbandingan total pengguna berdasarkan hari libur (sabtu, minggu) vs hari kerja")
st.dataframe(workday_df, hide_index=True)

# DATA VISUALIZATION

st.subheader("Pertumbuhan total pengguna tiap bulannya")

# menjumlahkan total / cnt dari dataset day_df dan menjadikan total pengguna perbulannya
month_data = day_df_alt.groupby(["mnth", "yr"])["cnt"].sum().reset_index().sort_values(by=["yr", "mnth"])

# mengubah format date menjadi YYYY-MM
month_data["date"] = pd.to_datetime(month_data["yr"].astype(str) + "-" + month_data["mnth"].astype(str) + "-01")

# set datetime index
month_data.set_index("date", inplace=True)
month_data.index = month_data.index.strftime("%Y-%m")

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(x="date", y="cnt", data=month_data, ax=ax)
# rotate date agar lebih terbaca
ax.set_xticks(range(len(month_data)))
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=14)
# banyak label yg muncul (24 bulan)
ax.xaxis.set_major_locator(plt.MaxNLocator(24))

# labels dan text format
ax.set_xlabel('Date', fontsize=18)
ax.set_ylabel('Total Users', fontsize=18)
ax.set_title('Monthly Total Users', fontsize=24)
ax.tick_params(axis='y', labelsize=16)
ax.tick_params(axis='x', labelsize=16)
ax.grid(True)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{x / 1000:,.0f}k"))

st.pyplot(fig)

st.subheader("Total pengguna berdasarkan musim (Season)")

seasonal_data = day_df_alt.groupby(["mnth", "season"])["cnt"].sum().reset_index().sort_values(by="mnth")
pivot_table = seasonal_data.pivot_table(index="mnth", columns="season", values="cnt")

fig, ax = plt.subplots(figsize=(12, 6))
pivot_table.plot(kind="bar", stacked=True, ax=ax)

# labels dan title
ax.set_xlabel("Month (combined)")
ax.set_ylabel("Total Users (combined)")
ax.set_title("Total Pengguna berdasarkan musim (Season)")
ax.set_xticklabels(pivot_table.index, rotation=0, ha="right")

# format ribuan menjadi "k"
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f"{x / 1000:,.0f}k"))  # Comma separator for thousands

st.pyplot(fig)

st.subheader("Rata-rata total pengguna per-Jam")

hourly_data = hour_df_alt.groupby("hr")["cnt"].mean().reset_index()
pivot_table = hourly_data.pivot(columns="hr", values="cnt")

fig, ax = plt.subplots(figsize=(12, 6))
sns.lineplot(x=hourly_data.index, y=hourly_data["cnt"], marker="o", color="tab:blue", label="Total Users", ax=ax)

# labels dan title
ax.set_xlabel("Jam", fontsize=14)
ax.set_ylabel("Rata-rata pengguna", fontsize=14)
ax.set_title("Rata-rata total pengguna per Jam nya", fontsize=16)

# Format x-axis hanya melihatkan jam
ax.set_xticks(range(24))
ax.set_xticklabels([f"{i:02d}" for i in range(24)])
ax.grid(linestyle='--', alpha=0.7)

# peak hour annotation
peak_hour = hourly_data["cnt"].idxmax()
ax.annotate('Peak Hour', xy=(peak_hour, hourly_data["cnt"].max()), xytext=(peak_hour, hourly_data["cnt"].max() + 5),
            arrowprops=dict(facecolor='black', shrink=0.05))

# Display the plot in Streamlit
st.pyplot(fig)

# MANUAL GROUPING KOLOM JAM

# membuat kolom baru pada dataset hour_df untuk memberi label keterangan waktu yang lebih deskriptif
# Morning = jam 5-12
# Afternoon = jam 12-16
# Evening = jam 17-21
# Night = jam 22-04
hour_df_alt['hour_group'] = pd.cut(hour_df_alt['hr'], bins=[4, 11, 16, 20, 24], labels=['Morning', 'Afternoon', 'Evening', 'Night'])

# inlcude jam 21-23 dan 0-4 sebagai Night
hour_df_alt.loc[(hour_df_alt['hr'] > 21) | (hour_df_alt['hr'] < 5), 'hour_group'] = 'Night'

hour_segment_df = hour_df_alt.groupby(by="hour_group", observed=False).agg({
  "cnt": "mean",
}).reset_index()
hour_segment_df.columns = ['hour_group', 'average_user_count']

fig, ax = plt.subplots(figsize=(10, 5))
colors_ = ["#D3D3D3", "#D3D3D3", "#72BCD4", "#72BCD4"]

sns.barplot(
    x="average_user_count", 
    y="hour_group",
    data=hour_segment_df.sort_values(by="hour_group", ascending=False),
    palette=colors_,
    hue="average_user_count",
    dodge=False,
    ax=ax
)

# Title and labels
ax.set_title("Average Total User by Hour Group", loc="center", fontsize=15)
ax.set_ylabel(None)
ax.set_xlabel("Average Total User")
ax.tick_params(axis='y', labelsize=12)

# Remove legend
ax.get_legend().remove()

st.pyplot(fig)

st.caption('Copyright © RikiSanjaya 2024')