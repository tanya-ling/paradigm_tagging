Tr <- read.csv("for_r2t.csv", # url
              sep = "\t", # тип разделителя
              header = FALSE)
Nr <- read.csv("for_r2n.csv", # url
              sep = "\t", # тип разделителя
              header = FALSE)
par(mfrow = c(1, 2)) # строит два графика в одном
hist(log(Nr$V1*1000), main = "RNC", ylab = NA, las = 1)
hist(log(Tr$V1*1000), main = "TOROT", ylab = NA, las = 1)
hist(Nr$V1, main = "RNC", ylab = NA, las = 1)
hist(Tr$V1, main = "TOROT", ylab = NA, las = 1)