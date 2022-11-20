import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random
import os

root = "/home/sethbw/Documents/brian_flow_code/Data/spectralFiles/figures/rr/experiment"

random.seed(0)

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
#for numPostYears in range(numPreYears):

dataDict = {"sample_no":[], "year_post_fire":[],"mean_percent_effect":[], "trial_no":[]}


df = pd.read_csv("runoff_ratio_timeseries_burn_only.csv")
print(df)
#quit()
numPreYears = 5
numPostYears = 8


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
for index, row in df.iterrows():
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
print(outDf)
outDf = outDf.merge(charDf, on="catchment")
outDf = outDf.merge(burnDf, on="catchment")
print(outDf)
#outDf = outDf[outDf["percent_burned"] > 10]
outDf.to_csv("runoff_ratio_real_burn_effects_catchments.csv")

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


cdf = pd.read_csv("runoffRatio_simulated_burn_effects.csv")
cdf =cdf[cdf["percentEffect"] < 5]
cdf =cdf[cdf["percentEffect"] > -5]

statDict = {"year":[],"effect":[],"pvalue":[]}

# open the distances to nearest catchments dataframe
for year in range(1,numPostYears + 1):
    ldf = outDf[outDf["postYear"] == str(year)]
    lcdf = cdf[cdf["yearPostFire"] == year]
    print(lcdf)
    print(np.mean(ldf["postMinusPrePercent"]))
    print("p value")
    statDict["year"].append(year)
    statDict["pvalue"].append(getPValue(list(lcdf["percentEffect"]), np.mean(ldf["postMinusPrePercent"])))
    statDict["effect"].append(np.mean(ldf["postMinusPrePercent"]))
    print(getPValue(list(lcdf["percentEffect"]), np.mean(ldf["postMinusPrePercent"])))
    plt.hist(lcdf["percentEffect"], bins=500)

    if year == 1:
        dist = -900
        title = "Simulated Burn Effects - " + str(year) + " Year Post Fire - RR Approach"
    elif year == 2:
        dist = -900
        title = "Simulated Burn Effects - " + str(year) + " Years Post Fire - RR Approach"
    else:
        dist = -900
        title = "Simulated Burn Effects - " + str(year) + " Years Post Fire - RR Approach"

    plt.scatter([np.mean(ldf["postMinusPrePercent"])], [dist], c="orange", s=100, marker="|", label="real mean burn effect,\narea burned > 10%,\nn=28 catchments")
    plt.scatter([np.mean(lcdf["percentEffect"])], [dist], c="k", s=100, marker="|", label="distribution mean")
    plt.legend()
    plt.title(title)
    plt.ylabel("count")
    plt.xlabel("mean effect (% different from 5 year mean prior to burn)")
    plt.savefig(os.path.join(root, "rr_experiment_yr" + str(year) + ".png"))
    plt.show()
    print(lcdf)

    print(year)
    print(len(ldf["postMinusPrePercent"]))

statDf = pd.DataFrame.from_dict(statDict)
statDf.to_csv(os.path.join(root, "stats_dict"), index=False)

size = list(outDf["percent_burned"])
alpha = 1
size = [alpha * x for x in size]
plt.scatter(outDf["postYear"], outDf["postMinusPrePercent"], s=size,c="orange", alpha=0.3, label="1 catchment (size ~ percent burned)")
plt.ylabel("burn effect (% change from 5 year mean prior to burn)")
plt.xlabel("years post wildfire")
plt.title("Runoff Ratio Measured Burn Effects Through Time")
plt.legend()
plt.savefig(os.path.join(root, "rr_experiment_summary.png"))
plt.show()

