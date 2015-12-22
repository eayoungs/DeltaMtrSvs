dms.adt.vis <- function(fname){
  library("lubridate")
  
  adt.data = read.csv(fname, header = TRUE, stringsAsFactors = FALSE)
  
  for(i in 1:length(adt.data$Per..Start)){
    mnths = month(adt.data$Per..Start[i])
  }
  
  print(mnths)
}
