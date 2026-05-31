import sqlite3
import pandas as pd

# Part 1: Data Management

DB_NAME = "immune_data.db"
CSV_NAME = "cell-count.csv"

def main():
    df = pd.read_csv(CSV_NAME)

    # connect to sqlite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # handles reruns: "table samples already exists"
    cursor.execute("DROP TABLE IF EXISTS cell_populations")
    cursor.execute("DROP TABLE IF EXISTS samples")

    # init database with the schema
    cursor.execute("""
    CREATE TABLE samples (
        sample TEXT PRIMARY KEY,
        project TEXT,
        subject TEXT,
        condition TEXT,
        age INTEGER,
        sex TEXT,
        treatment TEXT,
        response TEXT,
        sample_type TEXT,
        time_from_treatment_start INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE cell_populations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sample TEXT,
        population TEXT,
        count INTEGER,
        FOREIGN KEY(sample) REFERENCES samples(sample)
    )
    """)

    # populate sample table
    sample_cols = [
        "sample",
        "project",
        "subject",
        "condition",
        "age",
        "sex",
        "treatment",
        "response",
        "sample_type",
        "time_from_treatment_start"]

    samples_df = df[sample_cols]

    samples_df.to_sql(
        "samples",
        conn,
        if_exists="append",
        index=False
    )

    # populate cell_populations table
    pop_cols = [
        "b_cell",
        "cd8_t_cell",
        "cd4_t_cell",
        "nk_cell",
        "monocyte"
    ]

    # conv. to long format
    # ex row: sample: sample00000, population: b_cell, count: 4000
    pop_df = df.melt(
        id_vars=["sample"],
        value_vars=pop_cols, # measured var
        var_name="population",
        value_name="count"
    )

    pop_df.to_sql(
        "cell_populations",
        conn,
        if_exists="append",
        index=False
    )

    conn.commit()
    conn.close()

    print(f"Part 1: created database '{DB_NAME}'.")

if __name__ == "__main__":
    main()