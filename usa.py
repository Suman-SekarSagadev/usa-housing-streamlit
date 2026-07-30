import pandas as pd
import streamlit as st
%pip install plotly
import plotly.express as px

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="USA Housing Analytics",
    page_icon="🏠",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("USA Project/USA Housing Dataset.csv")

    # Convert date
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Convert price
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    return df


df = load_data()

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🏠 USA Housing Analytics Dashboard")

st.write(
    "Interactive analysis of housing prices, property characteristics, "
    "and city-level trends."
)

st.divider()

# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("🔍 Filters")

# Date Filter
min_date = df["date"].min()
max_date = df["date"].max()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# City Filter
cities = sorted(
    df["city"].dropna().unique()
)

selected_city = st.sidebar.multiselect(
    "Select City",
    options=cities,
    default=[]
)
# --------------------------------------------------
# APPLY FILTERS
# --------------------------------------------------

filtered_df = df.copy()

# Date filter
if len(date_range) == 2:

    start_date = pd.to_datetime(date_range[0])
    end_date = pd.to_datetime(date_range[1])

    filtered_df = filtered_df[
        (filtered_df["date"] >= start_date) &
        (filtered_df["date"] <= end_date)
    ]

# City filter
if selected_city:

    filtered_df = filtered_df[
        filtered_df["city"].isin(selected_city)
    ]

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------

total_properties = len(filtered_df)

average_price = filtered_df["price"].mean()

median_price = filtered_df["price"].median()

average_living_area = filtered_df["sqft_living"].mean()

# --------------------------------------------------
# KPI CARDS
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:

    st.metric(
        "🏠 Total Properties",
        f"{total_properties:,}"
    )

with col2:

    st.metric(
        "💰 Average Price",
        f"${average_price:,.0f}"
        if pd.notna(average_price)
        else "$0"
    )

with col3:

    st.metric(
        "💵 Median Price",
        f"${median_price:,.0f}"
        if pd.notna(median_price)
        else "$0"
    )

with col4:

    st.metric(
        "📐 Avg Living Area",
        f"{average_living_area:,.0f} sqft"
        if pd.notna(average_living_area)
        else "0 sqft"
    )

st.divider()

# --------------------------------------------------
# ROW 1
# --------------------------------------------------

col1, col2 = st.columns(2)

# --------------------------------------------------
# PRICE TREND
# --------------------------------------------------

with col1:

    st.subheader("📈 Housing Price Trend")

    price_trend = (
        filtered_df
        .groupby("date", as_index=False)["price"]
        .mean()
    )

    fig_price = px.line(
        price_trend,
        x="date",
        y="price",
        title="Average Housing Price Over Time",
        labels={
            "date": "Date",
            "price": "Average Price"
        }
    )

    fig_price.update_layout(
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_price,
        use_container_width=True
    )

# --------------------------------------------------
# CITY PRICE
# --------------------------------------------------

with col2:

    st.subheader("🏙️ City-wise Average Price")

    city_price = (
        filtered_df
        .groupby("city", as_index=False)["price"]
        .mean()
        .sort_values(
            "price",
            ascending=False
        )
        .head(15)
    )

    fig_city = px.bar(
        city_price,
        x="price",
        y="city",
        orientation="h",
        title="Top 15 Cities by Average House Price",
        labels={
            "price": "Average Price",
            "city": "City"
        }
    )

    st.plotly_chart(
        fig_city,
        use_container_width=True
    )

# --------------------------------------------------
# ROW 2
# --------------------------------------------------

col1, col2 = st.columns(2)

# --------------------------------------------------
# BEDROOM DISTRIBUTION
# --------------------------------------------------

with col1:

    st.subheader("🛏️ Bedroom Distribution")

    bedroom_data = (
        filtered_df["bedrooms"]
        .value_counts()
        .reset_index()
    )

    bedroom_data.columns = [
        "bedrooms",
        "count"
    ]

    fig_bedrooms = px.bar(
        bedroom_data,
        x="bedrooms",
        y="count",
        title="Number of Properties by Bedrooms",
        labels={
            "bedrooms": "Bedrooms",
            "count": "Properties"
        }
    )

    st.plotly_chart(
        fig_bedrooms,
        use_container_width=True
    )

# --------------------------------------------------
# PRICE VS LIVING AREA
# --------------------------------------------------

with col2:

    st.subheader("💰 Price vs Living Area")

    scatter_df = filtered_df.dropna(
        subset=[
            "price",
            "sqft_living"
        ]
    )

    fig_scatter = px.scatter(
        scatter_df,
        x="sqft_living",
        y="price",
        title="House Price vs Living Area",
        labels={
            "sqft_living": "Living Area (sqft)",
            "price": "Price"
        },
        opacity=0.6
    )

    st.plotly_chart(
        fig_scatter,
        use_container_width=True
    )

# --------------------------------------------------
# ROW 3
# --------------------------------------------------

col1, col2 = st.columns(2)

# --------------------------------------------------
# CONDITION DISTRIBUTION
# --------------------------------------------------

with col1:

    st.subheader("🏠 Property Condition")

    condition_data = (
        filtered_df["condition"]
        .value_counts()
        .reset_index()
    )

    condition_data.columns = [
        "condition",
        "count"
    ]

    fig_condition = px.pie(
        condition_data,
        names="condition",
        values="count",
        title="Properties by Condition"
    )

    st.plotly_chart(
        fig_condition,
        use_container_width=True
    )

# --------------------------------------------------
# WATERFRONT ANALYSIS
# --------------------------------------------------

with col2:

    st.subheader("🌊 Waterfront Properties")

    waterfront_data = (
        filtered_df["waterfront"]
        .value_counts()
        .reset_index()
    )

    waterfront_data.columns = [
        "waterfront",
        "count"
    ]

    waterfront_data["waterfront"] = (
        waterfront_data["waterfront"]
        .map({
            0: "No Waterfront",
            1: "Waterfront"
        })
    )

    fig_waterfront = px.pie(
        waterfront_data,
        names="waterfront",
        values="count",
        title="Waterfront vs Non-Waterfront"
    )

    st.plotly_chart(
        fig_waterfront,
        use_container_width=True
    )

# --------------------------------------------------
# FILTERED DATA
# --------------------------------------------------

st.divider()

st.subheader("📋 Filtered Property Data")

st.write(
    f"Showing {len(filtered_df):,} properties"
)

st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True
)