# __author__ = "Eric Allen Youngson"
# __email__ = "eric@scneco.com"
# __copyright__ = "Copyright Dec. 2015, Succession Ecological Services"
# __license__ = "GNU Affero (GPLv3)"
# 
# This file contains functions for working with the results of API queries from
# DeltaMeterServices.com

# install.packages("lubridate") ## Comment out after first call to source()
library("lubridate")
# install.packages("ggplot2") ## Comment out after first call to source()
library("ggplot2")
# install.packages("Rmisc") ## Comment out after first call to source()
library("Rmisc")


DmsFmatAudit <- function(f.names){
  # Reformats date-time strings to R date type objects: removing empty time
  # values, then reorders dataframe rows by absolute month (without year).
  #
  # Args:
  #   f.names: File names, as a list, to be processed by function
  # 
  # Returns:
  #   A dataframe containing the original file content reordered by absolute
  #   month (regardless of year), and contents of each dataframe to a seperate
  #   file.
  
  # f.names = c(read.table(fname_list, sep="\n", stringsAsFactors = FALSE))
  audit.data.lst = list()
  for(i in 1:length(f.names)){
    audit.data = read.csv(f.names[i], header = TRUE, stringsAsFactors = FALSE)
    
    audit.data$Per..Start = as.Date(audit.data$Per..Start)
    audit.data$Per..End = as.Date(audit.data$Per..End)
    audit.data$Per..Start.1 = as.Date(audit.data$Per..Start.1)
    audit.data$Per..End.1 = as.Date(audit.data$Per..End.1)

    audit.data = audit.data[order(month(audit.data$Per..Start.1)),]
    audit.data.lst[[i]] <- audit.data
    # write.csv(audit.data, paste("out-", f.names[i]))
  audit.data = data.frame(audit.data.lst[1])
  }
  return(audit.data)
}

DmsPlotUsePer <- function(df.name){
  # Plots a data-frame containing *audit* data from the DeltaMeterServices.com
  # website; power = f(reading length)
  #
  # Args:
  #   df.name: 
  # Returns:
  #   pwr.tmp.mplot: 
  audit.data = read.csv(df.name, header = TRUE, stringsAsFactors = FALSE)
  pwr.tmp.gas = qplot(audit.data[,"Hrs..in.Per."], audit.data[,"X.W.SF."], 
                      colour = df.name, main = "Gas", xlab = "Hrs. In Period",
                      ylab = "[W/SF]", xlim = c(0,1000))
  pwr.tmp.elec = qplot(audit.data[,"Hrs..in.Per..1"], audit.data[,"X.W.SF..1"],
                       colour = df.name, main = "Elec.",
                       xlab = "Hrs. In Period",
                       ylab = "[W/SF]", xlim = c(0,1000))
  pwr.tmp.mplot = multiplot(pwr.tmp.elec, pwr.tmp.gas) #, title = "234")

  return(pwr.tmp.mplot)
}

DmsGetUseRange <- function(df.name){
  # Takes a data-frame of 'audit' data from DeltaMeterServices.com as argument,
  # returns the start & end dates for both (Electric & Gas) common fuel types.
  #
  # Args:
  #   df.name: Data-frame containing utility billing history from
  #   DeltaMeterServices.com
  # Returns:
  #   use.range: Data-frame containing the start & end dates for both (Electric
  #   & Gas)common fuel type
  gas.start = min(df.name$Per..Start, na.rm=TRUE)
  gas.end = max(df.name$Per..End, na.rm=TRUE)
  elec.start = min(df.name$Per..Start.1, na.rm=TRUE)
  elec.end = max(df.name$Per..End.1, na.rm=TRUE)

  col.names = c("Gas Start", "Gas End", "Elec. Start", "Elec. End")
  vals = c(gas.start, gas.end, elec.start, elec.end)

  use.range = data.frame(vals, row.names = col.names)
  return(use.range)
}
