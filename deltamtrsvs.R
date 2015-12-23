# __author__ = "Eric Allen Youngson"
# __email__ = "eric@scneco.com"
# __copyright__ = "Copyright Dec. 2015, Succession Ecological Services"
# __license__ = "GNU Affero (GPLv3)"
# 
# This file contains functions for working with the results of API queries from
# DeltaMeterServices.com

# install.packages("lubridate") ## Uncomment on first execution (source)
# library("lubridate")          ## Uncomment on first execution (source)


DmsAuditFormat <- function(fname){
  # Reorders audit data from DeltaMeterServices.com for review, based on
  # requirements of the America Saves\! project
  #
  # Args:
  #   fname: File name to be processed by function
  # 
  # Returns:
  #   a dataframe containing the original file content reordered by absolute
  #   month (regardless of year)
  adt.data = read.csv(fname, header = TRUE, stringsAsFactors = FALSE)
  
  mnths = data.frame()
  for(i in 1:length(adt.data$Per..Start)){
    mnths = rbind(data.frame(month(adt.data$Per..Start[i])), mnths)
  }
  
  print(mnths)
}
