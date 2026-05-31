import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

DB_NAME = "immune_data.db"

st.set_page_config(page_title="Loblaw Bio Clinical Trial Dashboard", layout="wide")
conn = sqlite3.connect(DB_NAME)

st.title("Immune Cell Population Analysis")
st.markdown("Understanding how drug candidates affect immune cell populations.")

# ------- data overview -------
samples = pd.read_sql_query("SELECT COUNT(*) AS n FROM samples", conn).iloc[0]["n"]
subjects = pd.read_sql_query("SELECT COUNT(DISTINCT subject) AS n FROM samples", conn).iloc[0]["n"]
projects = pd.read_sql_query("SELECT COUNT(DISTINCT project) AS n FROM samples", conn).iloc[0]["n"]

col1, col2, col3 = st.columns(3)
col1.metric("Samples:", samples)
col2.metric("Subjects:", subjects)
col3.metric("Projects:", projects)

# ------- Part 2: frequency table -------

st.header("Part 2: Cell Population Relative Frequencies")

freq_df = pd.read_sql_query("SELECT * FROM frequencies", conn)

# allow filtering by population
all_pops = list(freq_df["population"].unique())
all_pops.append("All")
population = st.selectbox("Filter by population", all_pops)
filtered = freq_df
if population != "All":
    filtered = filtered[filtered["population"] == population]
st.dataframe(filtered)

# ------- Part 3: statistical analysis -------

st.header("Part 3: Melanoma PBMC samples treated with Miraclib")

subset_freq_df = pd.read_sql_query(
    """
    SELECT s.response, f.population, f.percentage
    FROM samples s JOIN frequencies f ON s.sample = f.sample
    WHERE s.condition='melanoma' AND s.treatment='miraclib' AND s.sample_type='PBMC'
    """,
    conn
)

# recreate boxplot so it's interactive on the dashboard
fig = px.box(
    subset_freq_df,
    x="population",
    y="percentage",
    color="response",
    title="Immune cell population relative frequencies"
)
st.plotly_chart(fig, use_container_width=True)

# display stats
st.subheader("Statistical Results")
st.write("Results of T-test and Mann-Whitney U-test statistical analyses")
stats_df = pd.read_csv("outputs/statistical_results.csv")
st.dataframe(stats_df)

# ------- Part 4: subset analysis -------

st.header("Part 4: Baseline Melanoma PBMC Cohort")

cohort = pd.read_sql_query("SELECT * FROM melanoma_pbmc_baseline", conn)
st.write("All baseline melanoma PBMC cohort samples:")
st.dataframe(cohort)

project_counts = pd.read_csv("outputs/project_counts.csv")
st.write("Number of samples per project")
st.dataframe(project_counts)

response_counts = pd.read_csv("outputs/response_counts.csv")
fig = px.pie(response_counts, names="response", values="num_subjects", title="Number of responders vs. non-responders")
fig.update_traces(textposition="inside", textinfo="label+value+percent")
st.plotly_chart(fig)

sex_counts = pd.read_csv("outputs/sex_counts.csv")
fig = px.pie(sex_counts, names="sex", values="num_subjects", title="Number of males vs. females")
fig.update_traces(textposition="inside", textinfo="label+value+percent")
st.plotly_chart(fig)

conn.close()