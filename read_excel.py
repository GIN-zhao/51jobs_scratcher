import pandas as pd 
data = pd.read_excel('./final_analyzed_results.xlsx')

#count classes of data
print(data["学科"].value_counts())