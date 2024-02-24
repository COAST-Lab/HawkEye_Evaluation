import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import stats

# Load the data
df = pd.read_excel('/Users/mitchtork/HawkEye_Evaluation/data/acrobat/050523/transects/processed_transects/satsitu.xlsx')

# Data cleaning: Remove rows with missing values in relevant columns
df.dropna(subset=['in_situ_chl', 'hawkeye_chl', 'modisa_chl', 's3a_chl', 's3b_chl'], inplace=True)

# Save descriptive statistics to a CSV file
desc_stats = df.describe()
desc_stats.to_csv('descriptive_statistics.csv')
print("Descriptive Statistics saved to descriptive_statistics.csv")

# Visualize distributions with displot and save figures
plt.figure(figsize=(10, 6))
for column in ['hawkeye_chl', 'modisa_chl', 's3a_chl', 's3b_chl']:
    sns.displot(df[column], kind="kde", label=column)
    plt.legend()
    plt.title(f'Distribution of {column}')
    plt.savefig(f'distribution_{column}.png')
    plt.close()

sns.displot(df['in_situ_chl'], kind="kde", color='k', label='in_situ_chl')
plt.legend()
plt.title('Distribution of in_situ_chl')
plt.savefig('distribution_in_situ_chl.png')
plt.close()

# Correlation Analysis and save results
correlations = df.corr()
correlations.to_csv('correlation_analysis.csv')
print("Correlation analysis saved to correlation_analysis.csv")

# Regression Analysis and Bland-Altman Plot
for satellite in ['hawkeye_chl', 'modisa_chl', 's3a_chl', 's3b_chl']:
    # Regression Analysis
    plt.figure(figsize=(8, 6))
    sns.lmplot(x='in_situ_chl', y=satellite, data=df)
    plt.title(f'Regression: in_situ_chl vs {satellite}')
    plt.xlabel('In Situ Chlorophyll')
    plt.ylabel(f'{satellite} Chlorophyll')
    plt.savefig(f'regression_in_situ_vs_{satellite}.png')
    plt.close()

    # Bland-Altman Plot
    df['average'] = df[['in_situ_chl', satellite]].mean(axis=1)
    df['difference'] = df['in_situ_chl'] - df[satellite]
    plt.figure(figsize=(8, 6))
    sns.scatterplot(x='average', y='difference', data=df)
    plt.axhline(df['difference'].mean(), color='red', linestyle='--', label='Mean difference')
    plt.axhline(df['difference'].mean() + 1.96*df['difference'].std(), color='blue', linestyle='--', label='Upper limit of agreement')
    plt.axhline(df['difference'].mean() - 1.96*df['difference'].std(), color='blue', linestyle='--', label='Lower limit of agreement')
    plt.title(f'Bland-Altman Plot: in_situ_chl vs {satellite}')
    plt.xlabel('Average Chlorophyll Concentration')
    plt.ylabel('Difference in Chlorophyll Concentration')
    plt.legend()
    plt.savefig(f'bland_altman_in_situ_vs_{satellite}.png')
    plt.close()

# Paired Statistical Tests
paired_tests_results = {'Satellite': [], 'T-statistic': [], 'P-value': []}
for satellite in ['hawkeye_chl', 'modisa_chl', 's3a_chl', 's3b_chl']:
    t_stat, p_value = stats.ttest_rel(df['in_situ_chl'], df[satellite])
    paired_tests_results['Satellite'].append(satellite)
    paired_tests_results['T-statistic'].append(t_stat)
    paired_tests_results['P-value'].append(p_value)
    print(f"Paired T-test for in_situ_chl vs {satellite}: T-statistic = {t_stat:.4f}, P-value = {p_value:.4g}")

# Convert paired test results to DataFrame and save
paired_tests_df = pd.DataFrame(paired_tests_results)
paired_tests_df.to_csv('paired_tests_results.csv', index=False)
print("Paired T-test results saved to paired_tests_results.csv")
