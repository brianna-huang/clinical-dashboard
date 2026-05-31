import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind, mannwhitneyu

# Part 3: Statistical Analysis

DB_NAME = "immune_data.db"

def main():
    conn = sqlite3.connect(DB_NAME)

    # filter for melanoma patients receiving miraclib & pbmc samples
    # join with frequencies on sample id
    query = """
        SELECT s.sample, s.response, f.population, f.percentage
        FROM samples s JOIN frequencies f ON s.sample = f.sample
        WHERE s.condition="melanoma" AND s.treatment="miraclib" AND s.sample_type="PBMC"
        """

    # each sample now has cell pop, freq, AND yes/no response
    filtered_df = pd.read_sql_query(query, conn)
    conn.close()

    # create boxplot
    plt.figure()
    sns.boxplot(
        data=filtered_df,
        x="population",
        y="percentage",
        hue="response"
    )
    plt.title("Immune cell population relative frequencies– Melanoma PBMC samples treated with Miraclib")
    plt.tight_layout()
    plt.savefig("outputs/boxplot.png")
    print("Part 3: boxplot saved to boxplot.png.")

    # run t-test and mann whitney u test on merged data to compare responsive & non-responsive
    pop_cols = [
        "b_cell",
        "cd8_t_cell",
        "cd4_t_cell",
        "nk_cell",
        "monocyte"
    ]
    res = []
    for pop in pop_cols:
        yes = filtered_df[
            (filtered_df["population"] == pop)
            & (filtered_df["response"] == "yes")
        ]["percentage"]

        no = filtered_df[
            (filtered_df["population"] == pop)
            & (filtered_df["response"] == "no")
        ]["percentage"]

        t_statistic, t_pvalue = ttest_ind(yes, no, equal_var=False)
        u_statistic, u_pvalue = mannwhitneyu(yes, no, alternative="two-sided")

        res.append({
            "population": pop,
            "t_statistic": t_statistic,
            "t_p_value": t_pvalue,
            "u_statistic": u_statistic,
            "u_p_value": u_pvalue
        })

    stats_df = pd.DataFrame(res)

    # significance flags
    stats_df["t_significant"] = stats_df["t_p_value"] < 0.05
    stats_df["u_significant"] = stats_df["u_p_value"] < 0.05

    stats_df.to_csv("outputs/statistical_results.csv", index=False)

    print("Part 3: statistical results saved to statistical_results.csv.")


if __name__ == "__main__":
    main()