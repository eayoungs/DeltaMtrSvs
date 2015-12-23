dms.adt.vis <- function(fname){
  library("lubridate")
  
  adt.data = read.csv(fname, header = TRUE, stringsAsFactors = FALSE)
  
  mnths = data.frame()
  for(i in 1:length(adt.data$Per..Start)){
    mnths = rbind(data.frame(month(adt.data$Per..Start[i])), mnths)
  }
  
  print(mnths)
}
