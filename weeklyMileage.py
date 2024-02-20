import pandas as pd
from datetime import datetime

df = pd.read_csv('runData.csv')
runs = df[['distance', 'start_date_local']]

runs['start_date_local'] = pd.to_datetime(runs['start_date_local'])

runs['start_week'] = runs['start_date_local'].dt.to_period('W')

weeklyMileage = runs.groupby('start_week')['distance'].sum()

print(weeklyMileage)

# Get the current year 
currentYear = datetime.today().year
startOfYear = datetime(currentYear, 1, 1)
today = datetime.today()
dateRange = pd.date_range(start=startOfYear, end=today, freq='W')

#convert the dates to periods
weeklyPeriods = dateRange.to_period('W')

for period in weeklyPeriods:
    if period in weeklyMileage.index:
        print(f"{period}: {weeklyMileage[period]} km")
    else:
        print(f"{period}: 0km")