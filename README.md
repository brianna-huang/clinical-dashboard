# Immune Cell Population Analysis Pipeline & Dashboard

## How to run

### 1. Setup environment and install all required dependencies

```make setup```

### 2. Run data analysis pipeline

```make pipeline```

### 3. Run dashboard locally

```make dashboard```


## Database schema design
To model the data in cell-count.csv, I designed the relational database schema in SQLite as follows:

```samples``` table:
- sample (primary key)
- project
- subject
- condition
- age
- sex
- treatment
- response
- sample_type
- time_from_treatment_start

```cell_populations``` table:
- id (primary key)
- sample (foreign key references samples.sample)
- population
- count

### Rationale:
In the orignal data provided, cell population measurements are stored as columns per sample row which causes a few issues in terms of both normalization and scalability. This structure does not scale well if additional cell populations are introduced in the future and makes aggregation and calculations across subjects/projects more difficult. For example, if we wanted to get the total population for a given sample, we would've needed to manually select the cell population names, instead of simply using one SUM() aggregation with my schema.

To normalize the data, I separated the sample metadata and cell population measurements into two tables. The ```samples``` table stores one row per sample, while the ```cell_populations``` table stores one row per population measurement. This long format design removes repeating groups, reduces redundancy, supports analytical queries, and allows potentially new immune populations to be added without requiring alterations to the schema itself. Thus, the resulting structure would scale a lot better to thousands of samples and additional immune cell populations or other measurements.

In a large prod system, I would actually normalize the schema further to 3NF so that we have separate subjects and projects tables as well, but for now, I chose the design above for simplicity.

## Code Structure

Part 1: Data ingestion & management (```load_data.py```)
- Initializes the SQLite database with the table schemas from above, and loads the tables with data from ```cell-count.csv```
- I used pandas ```df.melt()``` to convert the cell population columns into long format.

Part 2: Initial Analysis - Data Overview (```init_analysis.py```)
- Queries the DB for the relative frequency of each cell type for each sample. I first calculate the total number of cells for each sample by by summing counts across all cell populations, then join that with the original ```cell_poplations``` table to get the relative frequency of each population as a percentage of the total cell count for that sample.
- The resulting frequency table is saved to ```outputs/frequency_table.csv``` as well as persisted to the DB, since we need it for later analysis.

Part 3: Statistical Analysis (```statistical_analysis.py```)
- Queries the DB to filter for requested clinical cohort (PBMC samples of melanoma patients receiving miraclib), and join with frequency table from Part 2 to get a resulting table with both response metadata AND relative cell population frequency
- Creates a boxplot using Seaborn and matplotlib, saved to ```outputs/boxplot.png```
- For statistical analysis, I ran both the T-test and Mann-Whitney U test to help indicate which cell populations have a significant difference in relative frequencies between responders and non-responders. I ran the Mann-Whitney to account for the fact that the cell populations may not be perfectly normally distributed. Results table including T-test and U-test p-values and an indication of whether each population is significant or not is saved to ```outputs/statistical_results.csv```.

Part 4 Data Subset Analysis (```subset_analysis.py```)
- Queries DB to filter for clinical cohort (PBMC samples of melanoma patients receiving miraclib, at baseline). The resulting samples are saved to ```outputs/melanoma_pbmc_baseline_df.csv``` and persisted to the DB for later use.
- Queries cohort table from above to calculate the number of samples per project (saved in ```outputs/project_counts.csv```), number of responders vs non-responders (saved in ```outputs/response_counts.csv```), and number of male and female subjects (saved in ```outputs/sex_counts.csv```).

Dashboard (```dashboard.py```)
- Interactive dashboard using Streamlit to display the results from above.
