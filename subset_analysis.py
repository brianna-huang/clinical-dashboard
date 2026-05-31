import sqlite3
import pandas as pd

# Part 4 Data Subset Analysis

DB_NAME = "immune_data.db"

def main():
    conn = sqlite3.connect(DB_NAME)

    # filter samples for melanoma pbmc samples at baseline treated w/ miraclib
    query = """
        SELECT sample, project, subject, sex, response
        FROM samples
        WHERE condition="melanoma" 
            AND treatment="miraclib" 
            AND sample_type="PBMC" 
            AND time_from_treatment_start=0
        """

    melanoma_pbmc_baseline_df = pd.read_sql_query(query, conn)
    melanoma_pbmc_baseline_df.to_csv("outputs/melanoma_pbmc_baseline_df.csv", index=False)
    print("Part 4: all PBMC samples of melanoma patients receiving miraclib @ baseline saved to melanoma_pbmc_baseline_df.csv.")

    # persist this cohort to DB for later use
    melanoma_pbmc_baseline_df.to_sql(
        "melanoma_pbmc_baseline",
        conn,
        if_exists="replace",
        index=False
    )

    # query for # samples per project
    project_counts = pd.read_sql_query(
        """
        SELECT project, COUNT(*) AS num_samples
        FROM melanoma_pbmc_baseline
        GROUP BY project
        """,
        conn
    )

    # query for # subjects that were responsive vs non-responsive
    response_counts = pd.read_sql_query(
        """
        SELECT response, COUNT(DISTINCT subject) AS num_subjects
        FROM melanoma_pbmc_baseline
        GROUP BY response
        """,
        conn
    )

    # query for # subjects that are male vs female
    sex_counts = pd.read_sql_query(
        """
        SELECT sex, COUNT(DISTINCT subject) AS num_subjects
        FROM melanoma_pbmc_baseline
        GROUP BY sex
        """,
        conn
    )

    conn.close()
    project_counts.to_csv("outputs/project_counts.csv", index=False)
    response_counts.to_csv("outputs/response_counts.csv", index=False)
    sex_counts.to_csv("outputs/sex_counts.csv", index=False)
    print("Part 4: additional queries saved to project_counts.csv, response_counts.csv, and sex_counts.csv.")

if __name__ == "__main__":
    main()