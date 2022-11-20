import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

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


mbdf = pd.read_csv("master_burn_data.csv")
newCats = []
for cat in mbdf["STAID"]:
    cat =str(int(cat))
    if len(cat) == 7:
        cat = "0" + cat
    cat = "X" + cat
    newCats.append(cat)
mbdf["catchment"] = newCats


# keep only catchments with 5 years before 5 years after
#for numPostYears in range(numPreYears):

dataDict = {"sample_no":[], "year_post_fire":[],"mean_percent_effect":[], "trial_no":[]}


for trialNo in range(40):

    df = pd.read_csv("ml_errors_aligned_control_" + str(trialNo) + ".csv")
    mdf = pd.read_csv("ml_measured_aligned_control_" + str(trialNo) + ".csv")

    numPreYears = 5
    numPostYears = 4

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
    
    # remove catchments that are > 200 km away from a burned catchment
    newCats = []
    for cat in outDf["catchment"]:
        newCats.append(cat.split("_")[0])
    outDf["catchment2"] = outDf["catchment"]
    outDf["catchment"] = newCats

    outDf = outDf.merge(mbdf, on="catchment")
    outDf = outDf[outDf["distance_to_nearest_burn"] < 200]
    outDf = outDf.drop(mbdf.columns, axis=1)
    outDf["catchment"] = outDf["catchment2"]
    outDf = outDf.drop("catchment2", axis=1)

    outDf.to_csv("ml_burnEffects_control_" + str(trialNo) + ".csv")

    catchments = list(outDf["catchment"])
    #outDf = outDf.merge(burnDf, on="catchment")
    for sampleNo in range(5000):
        sampleCats = random.sample(catchments, k=28)
        sdf = outDf[outDf["catchment"].isin(sampleCats)]
        #print(list(set(outDf["postYear"])))
        for year in range(1, numPostYears + 1):
            ldf = sdf[sdf["postYear"] == str(year)]
            #print(year)
            #print(np.mean(ldf["postMinusPrePercent"]))
            dataDict["sample_no"].append(sampleNo)
            dataDict["trial_no"].append(trialNo)
            dataDict["year_post_fire"].append(year)
            dataDict["mean_percent_effect"].append(np.mean(ldf["postMinusPrePercent"]))
        if sampleNo % 1000 == 0:
            print(sampleNo)
    dataDf = pd.DataFrame.from_dict(dataDict)
    dataDf.to_csv("ml_simulated_burn_effects.csv", index=False)
    print(dataDf)

