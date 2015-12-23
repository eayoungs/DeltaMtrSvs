# __author__ = "Eric Allen Youngson"
# __email__ = "eric@scneco.com"
# __copyright__ = "Copyright Dec. 2015, Succession Ecological Services"
# __license__ = "GNU Affero (GPLv3)"
# 
# This file contains functions for working with the results of API queries from
# DeltaMeterServices.com

install.packages("lubridate")
library("lubridate")


DmsAuditFormat <- function(fname){
  # Reformats date-time strings to R date type objects: removing empty time
  # values, then reorders dataframe rows by absolute month (without year).
  #
  # Args:
  #   fname: File name to be processed by function
  # 
  # Returns:
  #   a dataframe containing the original file content reordered by absolute
  #   month (regardless of year)
  audit.data = read.csv(fname, header = TRUE, stringsAsFactors = FALSE)
  
  audit.data$Per..Start = as.Date(audit.data$Per..Start)
  audit.data$Per..End = as.Date(audit.data$Per..End)
  audit.data$Per..Start.1 = as.Date(audit.data$Per..Start.1)
  audit.data$Per..End.1 = as.Date(audit.data$Per..End.1)

  audit.data = audit.data[order(month(audit.data$Per..Start)),]

  print(mnths)
  write.csv(audit.data, paste("out-", fname))
  return(audit.data)
}
