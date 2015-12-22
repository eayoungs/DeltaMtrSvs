dms.adt.vis <- function(fname){
  
  adt.data = read.csv(fname, header = TRUE, stringsAsFactors = FALSE)
  
  print(adt.data)
}
