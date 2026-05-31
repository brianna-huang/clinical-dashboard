import sqlite3
import pandas as pd

# Part 2: Initial Analysis - Data Overview

DB_NAME = "immune_data.db"

def main():
    conn = sqlite3.connect(DB_NAME)

    # 1. get total # of cells by summing counts across all 5 cell pops for each sample
    # 2. get relative freq of each pop as a % of the total cell count for that sample
    query = """
        SELECT
            p.sample AS sample,
            t.total_count,
            p.population,
            p.count,
            ROUND((p.count * 100.0/ t.total_count),2) AS percentage
        FROM cell_populations p
        JOIN (SELECT sample, SUM(count) AS total_count
            FROM cell_populations
            GROUP BY sample) t
        ON p.sample = t.sample
        """

    freq_df = pd.read_sql_query(query, conn)

    # persist frequency table for later use
    freq_df.to_sql(
        "frequencies",
        conn,
        if_exists="replace",
        index=False
    )

    conn.close()

    freq_df.to_csv("outputs/frequency_table.csv", index=False)

    print("Part 2: frequency table saved to DB and frequency_table.csv.")

if __name__ == "__main__":
    main()