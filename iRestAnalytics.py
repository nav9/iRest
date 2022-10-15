#Note: This is an old program that may need to be modified
import matplotlib.pyplot as plt

logFile = "irest.log"
resultsFile = "irest.results"

hours = []
days = []
counter = 1
toMinutes = 3600
with open(resultsFile) as f:
    lines = [line.rstrip() for line in f]
    
    for line in lines:
        hours.append(float(line.split(',')[1]) / toMinutes)
        days.append(counter)
        counter = counter + 1
    
    print('The hours worked')
    print(hours)
    print('Note: This is only for laptop use. The mobile phone would have been used for an equivalent number of hours per day')
    print('Start date: ', lines[0].split(',')[0])
    print('End date: ', lines[-1].split(',')[0])    
    print('Average hours: ', sum(hours)/(counter-1))
    print('Total days: ', counter-1)    
    daysGreaterThan6 = sum([1 for x in hours if x > 6])    
    daysGreaterThan5 = sum([1 for x in hours if x > 5])
    daysGreaterThan4 = sum([1 for x in hours if x > 4])
    daysGreaterThan3 = sum([1 for x in hours if x > 3])    
    print('Num days > 5hr: ', daysGreaterThan5)
    print('% of days worked > 6hr: ', daysGreaterThan6*100 / (counter-1), '%')    
    print('% of days worked > 5hr: ', daysGreaterThan5*100 / (counter-1), '%')
    print('% of days worked > 4hr: ', daysGreaterThan4*100 / (counter-1), '%')
    print('% of days worked > 3hr: ', daysGreaterThan3*100 / (counter-1), '%')    
    
    bars = plt.bar(days, hours)
    for i in range(counter-1):
        if hours[i] > 5:
            bars[i].set_color('r')


    plt.xlabel('day')
    plt.ylabel('hours per day')
    plt.title('Computer use in hours for ')
    
    plt.show()
    
    
