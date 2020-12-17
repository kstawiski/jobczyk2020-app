setwd("C:/Users/konra/Downloads/data/data")

library(data.table)
library(plyr)

shariat = fread("shariatMMC.csv")
shariat$MMC = 1
training_pfs = fread("training_pfs_old.csv")
training_rfs = fread("training_rfs_old.csv")
validation_pfs = fread("validation_pfs_old.csv")
validation_rfs = fread("validation_rfs_old.csv")

training_pfs$MMC = 0
training_rfs$MMC = 0
validation_pfs$MMC = 0
validation_rfs$MMC = 0

features = colnames(training_pfs)
features = features[-which(features == "Time")]
features = features[-which(features == "Event")]
new_training_pfs = dplyr::select(training_pfs, all_of(features))
new_training_rfs = dplyr::select(training_rfs, all_of(features))
new_validation_pfs = dplyr::select(validation_pfs, all_of(features))
new_validation_rfs = dplyr::select(validation_rfs, all_of(features))

new_validation_pfs$Time = validation_pfs$Time
new_validation_rfs$Time = validation_rfs$Time
new_validation_pfs$Event = validation_pfs$Event
new_validation_rfs$Event = validation_rfs$Event

shariat_x = dplyr::select(shariat, all_of(features))

new_training_pfs = rbind(new_training_pfs, shariat_x)
new_training_rfs = rbind(new_training_rfs, shariat_x)

new_training_pfs$Time = c(training_pfs$Time, shariat$`PFS_time [years]`)
new_training_rfs$Time = c(training_rfs$Time, shariat$`RFS_time [years]`)

new_training_pfs$Event = c(training_pfs$Event, shariat$`PFS_event [0 - censored, 1 - P]`)
new_training_rfs$Event = c(training_rfs$Event, shariat$`RFS_event [0 - censored, 1 - R]`)

fwrite(new_training_pfs, "training_pfs.csv")
fwrite(new_training_rfs, "training_rfs.csv")

fwrite(new_validation_pfs, "validation_pfs.csv")
fwrite(new_validation_rfs, "validation_rfs.csv")
