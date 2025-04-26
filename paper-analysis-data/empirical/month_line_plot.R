cat("\014") 
options(max.print=1000000)
t1 <- Sys.time()
library(ggplot2)

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_MONTH_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 250
# THE_DS_NAME <- "GITHUB"
# OUT_FIL     <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/writing/iac-categ-draft/plots/fig-freq-ghub-month.pdf"

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_MONTH_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 200
# THE_DS_NAME <- "MOZILLA"
# OUT_FIL     <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/writing/iac-categ-draft/plots/fig-freq-mozi-month.pdf"

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_MONTH_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 200
# THE_DS_NAME <- "OPENSTACK"
# OUT_FIL     <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/writing/iac-categ-draft/plots/fig-freq-ostk-month.pdf"

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_MONTH_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 200
# THE_DS_NAME <- "WIKIMEDIA"
# OUT_FIL     <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/writing/iac-categ-draft/plots/fig-freq-wiki-month.pdf"

### ======================================================================================== ###

THE_FILE    <- "/home/aluno/ACID-dataset/ARTIFACT/IaC_Defect_Categ_Revamp/output/REPLICATION_MONTH_TEMPORAL_FINAL.csv"
# THE_FILE    <- "/home/aluno/ACID-dataset/ARTIFACT/IaC_Defect_Categ_Revamp/output/PULUMI_MONTH_TEMPORAL_FINAL.csv"
THE_LIMIT   <- 250
THE_DS_NAME <- "PIPR-REPLICATION-TOTAL"
OUT_FIL     <- "/home/aluno/ACID-dataset/ARTIFACT/IaC_Defect_Categ_Revamp/src_categ_revamp/empirical/replication-fig-freq-month-total.pdf"

Y_LABEL     <- "Defect/Month"

LINE_DATA <- read.csv(THE_FILE)
LINE_DATA$MONTH <- as.factor(LINE_DATA$MONTH)
print(head(LINE_DATA))


pdf(OUT_FIL, width=8, height=1.6)

the_plot  <- ggplot(data=LINE_DATA, aes(x=MONTH, y=CATEG_PERC, group=1)) + 
  geom_point(size=0.1) + scale_x_discrete(breaks = LINE_DATA$MONTH[seq(1, length(LINE_DATA$MONTH), by = THE_LIMIT)]) + 
  geom_smooth(size=0.5, aes(color=CATEG), method='loess') +   
  facet_grid( . ~ CATEG) +
  labs(x='Month', y=Y_LABEL) +
  theme(legend.position="none") +
  theme(text = element_text(size=9), axis.text.x = element_text(angle=45, hjust=1, size=9), axis.text.y = element_text(size=9), axis.title=element_text(size=9, face="bold"))  

the_plot

dev.off()

t2 <- Sys.time()
print(t2 - t1)  
rm(list = setdiff(ls(), lsf.str()))