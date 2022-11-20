import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

root = "/home/sethbw/Documents/brian_flow_code/Data/spectralFiles/figures/ml/experiment"

burnDf = pd.read_csv("/home/sethbw/Documents/brian_flow_code/Data/metadata/catchments_for_Q_analysis.csv")
newCats = []
for cat in burnDf["GAGE_ID"]:
    cat = str(int(cat))
    if len(cat) == 7:
        cat = "0" + cat
    cat = "X" + cat
    newCats.append(cat)

burnDf["catchment"] = newCats

catsThatAppearTwice = []
alreadyAppeared = []
for index, row in burnDf.iterrows():
    if row["catchment"] in alreadyAppeared:
        catsThatAppearTwice.append(row["catchment"])
    alreadyAppeared.append(row["catchment"])

print(burnDf)
burnDf = burnDf[~burnDf["catchment"].isin(catsThatAppearTwice)] # remove catchments that burned multiple times
burnDf = burnDf[["percent_burned", "catchment"]]
print(burnDf)

charDf = pd.read_csv("/home/sethbw/Documents/brian_flow_code/Data/metadata/corrected_catchment_characteristics.csv")
newCats = []
for cat in charDf["STAID"]:
    cat = str(cat)
    if len(cat) == 7:
        cat = "0" + cat
    cat = "X" + cat
    newCats.append(cat)

charDf["catchment"] = newCats
print(charDf)

# keep only catchments with 5 years before 5 years after
df = pd.read_csv("ml_errors_aligned.csv")
mdf = pd.read_csv("ml_measured_aligned.csv")
print(df)
print(df.columns)


numPreYears = 5
numPostYears = 4

#for numPostYears in range(numPreYears):
if True:
    #preYears = list(range(1,numPreYears))

    preYears = list(range(1, numPreYears + 1))
    preYears = [-1 * x for x in preYears]
    preYears = [str(x) for x in preYears]

    postYears = list(range(1, numPostYears + 1)) 
    postYears = [str(x) for x in postYears] 

    yearsToKeep = preYears + postYears
    yearsToKeep = [str(x) for x in yearsToKeep]

    for yr in yearsToKeep:
        mask1 = np.asarray(~df[yr].isna())
        if yr == yearsToKeep[0]:
            mask = mask1
        else:
            mask = np.logical_and(mask, mask1)

    df = df[mask]
    df = df[yearsToKeep + ["catchment"]]

    mdf = mdf[mask]
    mdf = mdf[yearsToKeep + ["catchment"]]

    print(preYears) 
    print(postYears)

    outDict = {
            "catchment":[],
            "numPreYears":[],
            "postYear":[],
            #"numPostYears":[],
            "preMean":[],
            "postMean":[],
            "postMinusPre":[],
            "postMinusPrePercent":[]

    }

    catToMean = {}
    for index, row in mdf.iterrows():
        catToMean[row["catchment"]] = np.mean(row[preYears])

    print(df)

    for index, row in df.iterrows():

        cat = row["catchment"]
        for postYear in postYears:
            print(postYear)
        #if True:
            preMean = np.mean(row[preYears])
            postMean = row[postYear]
            #postMean = np.mean(row[postYears])

            residual = postMean - preMean
        
            outDict["catchment"].append(cat)
            outDict["numPreYears"].append(numPreYears)
            outDict["postYear"].append(postYear)
            #outDict["numPostYears"].append(len(postYears))
            outDict["preMean"].append(preMean)
            outDict["postMean"].append(postMean)
            outDict["postMinusPre"].append(residual)
            outDict["postMinusPrePercent"].append(residual / catToMean[cat])


    outDf = pd.DataFrame.from_dict(outDict)
    outDf.to_csv("ml_burnEffects_real.csv")

    outDf = outDf.merge(charDf, on="catchment")
    outDf = outDf.merge(burnDf, on="catchment")

    outDf = outDf[outDf["postMinusPrePercent"] > -5]
    outDf = outDf[outDf["postMinusPrePercent"] < 5]

    print(np.mean(outDf["postMinusPrePercent"]))

    #outDf = outDf[outDf["percent_burned"] > 5]
    #print(np.mean(outDf["postMinusPrePercent"]))

outDf = outDf[outDf["percent_burned"] > 10]
    #print(np.mean(outDf["postMinusPrePercent"]))

    #outDf = outDf[outDf["percent_burned"] > 20]
    #print(np.mean(outDf["postMinusPrePercent"]))

#    for year in postYears:
#        ldf = outDf[outDf["postYear"] == year]


#        print(str(year) + " " + str(np.mean(ldf["postMinusPrePercent"])))

simDf = pd.read_csv("ml_simulated_burn_effects.csv")
simDf = simDf[simDf["mean_percent_effect"] < 10]
simDf = simDf[simDf["mean_percent_effect"] > -10]

print(list(set(outDf["postYear"])))

def getPValue(array, value):
    arrayMean = np.mean(array)
    keepers = []
    if value < arrayMean:
        for val in array:
            if val < arrayMean:
                keepers.append(val)
        numDiff = np.sum(keepers < value)
    if value >= arrayMean:
        for val in array:
            if val >= arrayMean:
                keepers.append(val)
        numDiff = np.sum(keepers >= value)
    pValue = numDiff / len(keepers)
    return pValue


def getConfidneceInterval(array):
    arrayMean = np.mean(array)
    
    array.sort()
    num = len(array)
    divisionLength = int(float(num) / 20.0)


for year in range(1, numPostYears + 1):
    ldf = outDf[outDf["postYear"] == str(year)]
    lsdf = simDf[simDf["year_post_fire"] == year]
    print(lsdf)
    print(np.mean(lsdf["mean_percent_effect"]))
    print(np.mean(ldf["postMinusPrePercent"]))
    pVal = getPValue(list(lsdf["mean_percent_effect"]), np.mean(ldf["postMinusPrePercent"]))
    print(pVal)
    plt.hist(lsdf["mean_percent_effect"], bins=500)
    if year == 1:
        dist = -300
        title = "Simulated Burn Effects - " + str(year) + " Year Post Fire - ML Approach"
    elif year == 2:
        dist = -250
        title = "Simulated Burn Effects - " + str(year) + " Years Post Fire - ML Approach"
    else:
        dist = -400
        title = "Simulated Burn Effects - " + str(year) + " Years Post Fire - ML Approach"

    plt.scatter([np.mean(ldf["postMinusPrePercent"])], [dist], c="orange", s=100, marker="|", label="real mean burn effect,\narea burned > 10%,\nn=28 catchments")
    plt.scatter([np.mean(lsdf["mean_percent_effect"])], [dist], c="k", s=100, marker="|", label="distribution mean")
    plt.legend()

    plt.title(title)
    plt.ylabel("count")
    plt.xlabel("mean effect (% different from 5 year mean prior to burn)")
    plt.savefig(os.path.join(root, "ml_experiment_masd_yr" + str(year) + ".png"))
    plt.show()

    #print(year)
    #print(ldf)
print(outDf)
print("num catchments")
print(len(list(set(outDf["catchment"]))))
size = list(outDf["percent_burned"])
alpha = 1
size = [alpha * x for x in size]
plt.scatter(outDf["postYear"], outDf["postMinusPrePercent"], s=size,c="orange", alpha=0.3, label="1 catchment (size ~ percent burned)")
plt.ylabel("burn effect (% change from 5 year mean prior to burn)")
plt.xlabel("years post wildfire")
plt.title("Machine Learning Measured Burn Effects Through Time")
plt.legend()
plt.savefig(os.path.join(root, "ml_experiment_summary.png"))
plt.show()

