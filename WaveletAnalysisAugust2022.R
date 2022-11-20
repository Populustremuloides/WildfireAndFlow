#install.packages("WaveletComp", repos='http://cran.us.r-project.org')
library("WaveletComp")

rootDir = "/home/sethbw/Documents/brian_flow_code/Data/all_flow_specific_discharge_corrected_for_units_august2022/FlowYearByYear"
outDir = "/home/sethbw/Documents/brian_flow_code/Data/spectralFiles/spectralAnalysisAugust2022"

for (fix in 1971:2022) {
    	postFix = toString(fix)

	dataFile = paste("waterYear_", postFix, sep="")
	dataFile = paste(dataFile, ".csv", sep="")
	dataFolder = paste(rootDir, dataFile, sep="/")
	print(dataFolder)
	data = read.csv(dataFolder, sep=",")
	#print(data)
	originalData = data.frame(data)

	sites = names(data)
	sites

	site = sites[[100]] # test site
	wvlt = analyze.wavelet(originalData, site,loess.span = 0,
                      dt = 1, dj = 1/100,lowerPeriod = 2,
                      upperPeriod = 512,make.pval = F, n.sim = 1)

	wt.image(wvlt, color.key = "quantile", 
        	n.levels = 100,legend.params = list(lab = "wavelet power levels", mar = 4.7))

	scale = wvlt$Scale
	power = data.frame(scale)
	pval = data.frame(scale)

	for (indx in 1:length(sites)) {
		currentSite = sites[indx]
		tryCatch ({
			wvlt = analyze.wavelet(originalData, currentSite,loess.span = 0,
	                      dt = 1, dj = 1/100,lowerPeriod = 2,
	                      upperPeriod = 512,make.pval = F, n.sim = 1)

			power[[currentSite]] = wvlt$Power.avg
			pval[[currentSite]] = wvlt$Power.avg.pval
	    	}, error=print)
	}

	outFile = paste("waterYear_", postFix, sep="")
	outFile = paste(outFile, "_FlowPeriodPowers.csv", sep="")
	write.csv(power,paste(outDir, outFile, sep="/"), row.names=FALSE)

}
