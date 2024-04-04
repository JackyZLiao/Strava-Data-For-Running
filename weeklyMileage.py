import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# put csv data into dataframe
df = pd.read_csv('runData.csv')
runs = df[['distance', 'moving_time', 'start_date_local']]

runs['start_date_local'] = pd.to_datetime(runs['start_date_local'])

# print(runs)

runs['distance'] = round(runs['distance'] / 1000, 2)
runs['minutes'] = runs['moving_time'] // 60 
runs['seconds'] = runs['moving_time'] % 60
runs['pace_minutes'] = runs['moving_time'] / runs['distance'] // 60
runs['pace_seconds'] = round(runs['moving_time'] / runs['distance'] / 60 % 1 * 60)
runs['start_week'] = runs['start_date_local'].dt.to_period('W')

print(runs)


# print(runs)
weeklyMileage = runs.groupby('start_week')['distance'].sum()

# print(weeklyMileage)
# weeklyMileage.plot()
# plt.show()


# Get the current year 
currentYear = datetime.today().year
startOfYear = datetime(currentYear, 1, 1)
today = datetime.today()
dateRange = pd.date_range(start=startOfYear, end=today, freq='W')

#convert the dates to periods
weeklyPeriods = dateRange.to_period('W')

# prints out weekly mileage since the start of the year
# for period in weeklyPeriods:
#     if period in weeklyMileage.index:
#         print(f"{period}: {weeklyMileage[period]} km")
#     else:
#         print(f"{period}: 0km")

# prints each week's runs 
# for week, group in runs.groupby('start_week'):
#     print(f"Week: {week}")
#     print(group)
#     print()