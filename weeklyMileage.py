import pandas as pd

df = pd.read_csv('runData.csv')
runs = df[['distance', 'start_date_local']]

runs['start_date_local'] = pd.to_datetime(runs['start_date_local'])

runs['start_week'] = runs['start_date_local'].dt.to_period('W')

weeklyMileage = runs.groupby('start_week')['distance'].sum()

print(weeklyMileage)

