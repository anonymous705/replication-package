cat("\014") 
options(max.print=1000000)
t1 <- Sys.time()
library(ggplot2)

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 101
# THE_DS_NAME <- "MOZILLA"

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 101
# THE_DS_NAME <- "OPENSTACK"

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 101
# THE_DS_NAME <- "WIKIMEDIA"

### ======================================================================================== ###

THE_FILE    <- "/home/aluno/ACID-dataset/ARTIFACT/IaC_Defect_Categ_Revamp/output/REPLICATION_MONTH_TEMPORAL_FINAL.csv"
THE_LIMIT   <- 101
THE_DS_NAME <- "PIPR-REPLICATION"

Y_LABEL     <- "Defect-related Commit (%)"

LINE_DATA <- read.csv(THE_FILE)
print(head(LINE_DATA))


the_plot  <- ggplot(data=LINE_DATA, aes(x=MONTH, y=CATEG_PERC, group=1)) + 
  geom_point(size=0.1) + scale_x_discrete(breaks = LINE_DATA$MONTH[seq(1, length(LINE_DATA$MONTH), by = THE_LIMIT)]) + 
  geom_smooth(size=0.5, aes(color=CATEG), method='loess') +   
  facet_grid( . ~ CATEG) +
  labs(x='Month', y=Y_LABEL) +
  theme(legend.position="none") +
  ggtitle(THE_DS_NAME) + theme(plot.title = element_text(hjust = 0.5)) +
  theme(text = element_text(size=11), axis.text.x = element_text(angle=45, hjust=1, size=11), axis.text.y = element_text(size=12.5), axis.title=element_text(size=11, face="bold"))  

the_plot

t2 <- Sys.time()
print(t2 - t1)  
rm(list = setdiff(ls(), lsf.str()))