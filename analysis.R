setwd("C:/Users/konra/OneDrive/Projekty/2018_Jobczyk_Pecherz/Papier2/v12-2020/app/jobczyk2020-app")

library(tableone)

training_pfs = data.table::fread("Data/training_pfs_old.csv")
training_pfs$Set = "Discovery"
training_rfs = data.table::fread("Data/training_rfs_old.csv")
validation_pfs = data.table::fread("Data/validation_pfs_old.csv")
validation_pfs$Set = "Validation"
validation_rfs = data.table::fread("Data/validation_rfs_old.csv")

dane = rbind(training_pfs, validation_pfs)
dane$EventR = c(training_rfs$Event, validation_rfs$Event)


tab1 = CreateTableOne(data = dane, factorVars = c("Gender", "T", "CIS", "Grading", "No_tumors", "Diameter", "BCG", "Event", "EventR"), strata = "Set", smd = T)
tab1
tab1mat <- print(tab1)
write.csv(t, "valResults/Table1.csv")


# #
# devtools::install_github('davidgohel/ReporteRsjars')
# devtools::install_github('davidgohel/ReporteRs')
# 
# # Load the packages
# library(officer)
# library(flextable)
# library(magrittr)
# # The script
# docx( ) %>% 
#   addFlexTable(tab1 %>%
#                  FlexTable(header.cell.props = cellProperties( background.color = "#003366"),
#                            header.text.props = textBold( color = "white" ),
#                            add.rownames = TRUE ) %>%
#                  setZebraStyle( odd = "#DDDDDD", even = "#FFFFFF" ) ) %>%
# writeDoc(file = "valResults/table1.docx")

mmc = data.table::fread("Data/shariatMMC.csv")
dane2 = plyr::rbind.fill(dane, mmc)
dane2$Set[is.na(dane2$Set)] = "MMC-treated"
dane2$Event[is.na(dane2$Event)] = mmc$`PFS_event [0 - censored, 1 - P]`
dane2$EventR[is.na(dane2$EventR)] = mmc$`RFS_event [0 - censored, 1 - R]`

tab2 = CreateTableOne(data = dane2, factorVars = c("Gender", "T", "CIS", "Grading", "No_tumors", "Diameter", "BCG", "Event", "EventR"), strata = "Set", smd = T)
tab2
tab2mat <- print(tab2)
write.csv(tab2mat, "valResults/SupplTab4.csv")
