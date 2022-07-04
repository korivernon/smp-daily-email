import os

CWD = os.getcwd()

path = os.path.join(CWD)
directories = []

#create the individual directories

files = []
walk_dir = os.walk(CWD)
for root,dirs,file in walk_dir:
    files = file
for file in files:
    if file.endswith("historical.csv"):
        directories.append(file)

print("the directories:", directories)
def parse_dir(dirs):
    counter = 0
    prev_day = 0
    prediction_next_day = []
    correct_pred = []
    comp = []

    for filename in dirs:

        # open file
        file_obj = open( os.path.join(CWD, filename), "r")
        file_obj.readline()
        print("opening filename", filename)
        for line in file_obj:
            print(line)
            line = line.strip('\n').split(',')
            if counter == 0:
                prev_day = float(line[8])
                counter+=1
                continue
            # Date,Open,High,Low,Close,Adj Close,Volume,Percent_Change,Volume_Change
            _open , _close = float(line[1]), float(line[4])
            perc_change =  (1-(_open/_close))*100
            if prev_day != 0:
                curr_day = line[8]

                if prev_day > 0.0:
                    # positive growth
                    if perc_change > 0.0:
                        # positive change
                        prediction_next_day.append(True)
                    elif perc_change < 0.0:
                        # negative change
                        prediction_next_day.append(False)
                else:
                    if perc_change > 0.0:
                        # positive change
                        prediction_next_day.append(True)
                    elif perc_change < 0.0:
                        # negative change
                        prediction_next_day.append(False)
                direction = perc_change > 0.0
                # compare to the previous day
                try:
                    if prediction_next_day[-2] != direction:
                        correct_pred.append(True)
                        print(filename,"Prediction", True)
                    else:
                        correct_pred.append(False)
                        print(filename,"Prediction", False)
                except:
                    continue

        acc = correct_pred.count(True)/len(correct_pred)
        result_tup = (filename, acc)
        comp.append(result_tup)
    return comp

def main():
    print(parse_dir(directories))
main()
