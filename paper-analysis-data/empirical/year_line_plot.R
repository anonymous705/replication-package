cat("\014") 
options(max.print=1000000)
t1 <- Sys.time()
library(ggplot2)

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/GHUB_YEAR_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 25
# THE_DS_NAME <- "GITHUB"
# OUT_FIL     <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/writing/iac-categ-draft-jul20/plots/fig-freq-ghub.pdf"

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/MOZI_YEAR_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 9
# THE_DS_NAME <- "MOZILLA"
# OUT_FIL     <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/writing/iac-categ-draft-jul20/plots/fig-freq-mozi.pdf"

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/OSTK_YEAR_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 9
# THE_DS_NAME <- "OPENSTACK"
# OUT_FIL     <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/writing/iac-categ-draft-jul20/plots/fig-freq-ostk.pdf"

# THE_FILE    <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/output/WIKI_YEAR_TEMPORAL_FINAL.csv"
# THE_LIMIT   <- 9
# THE_DS_NAME <- "WIKIMEDIA"
# OUT_FIL     <- "/Users/akond/Documents/AkondOneDrive/OneDrive/IaC-Defect-Categ-Project/IaC_Defect_Categ_Revamp/writing/iac-categ-draft-jul20/plots/fig-freq-wiki.pdf"

### ======================================================================================== ###

# REPLICATIONDOCFIX
# company1CRITERIADOCFIX
# COMPANY2CRITERIADOCFIX

THE_FILE    <- "/home/aluno/ACID-dataset/ARTIFACT/IaC_Defect_Categ_Revamp/output/COMPANY2CRITERIADOCFIX_YEAR_TEMPORAL_FINAL.csv"
THE_LIMIT   <- 9
THE_DS_NAME <- "company2"
OUT_FIL     <- "/home/aluno/ACID-dataset/ARTIFACT/IaC_Defect_Categ_Revamp/src_categ_revamp/empirical/company2-2y-docfix-fig-freq.pdf"

Y_LABEL     <- "Defect/Year(%)"

# LINE_DATA <- read.csv(THE_FILE)
# LINE_DATA$YEAR <- as.factor(LINE_DATA$YEAR)
# print(head(LINE_DATA))


# pdf(OUT_FIL, width=8, height=1.6)

# the_plot  <- ggplot(data=LINE_DATA, aes(x=YEAR, y=CATEG_PERC, group=1)) + 
#   geom_point(size=0.1) +  scale_x_discrete(breaks = LINE_DATA$YEAR[seq(1, length(LINE_DATA$YEAR), by = THE_LIMIT)]) + 
#   geom_smooth(size=0.5, aes(color=CATEG), method='loess') +   
#   facet_grid( . ~ CATEG) +
#   labs(x='Year', y=Y_LABEL) +
#   theme(text = element_text(size=9), axis.text.x = element_text(angle=45, hjust=1, size=9), axis.text.y = element_text(size=9), axis.title=element_text(size=9, face="bold")) +
#   #ggtitle(THE_DS_NAME) + theme(plot.title = element_text(hjust = 0.5)) + 
#   theme(legend.position="none")   

LINE_DATA <- read.csv(THE_FILE)
LINE_DATA$YEAR <- substr(as.character(LINE_DATA$YEAR), 3, 4)
LINE_DATA$YEAR <- as.factor(LINE_DATA$YEAR)
print(head(LINE_DATA))

all_years <- sort(unique(as.character(LINE_DATA$YEAR)))
year_labels <- ifelse(seq_along(all_years) %% 2 == 1, all_years, "")

pdf(OUT_FIL, width=8, height=1.6)

the_plot  <- ggplot(data=LINE_DATA, aes(x=YEAR, y=CATEG_PERC, group=1)) + 
  geom_point(size=0.1) +
  scale_x_discrete(breaks = all_years, labels = year_labels) +
  geom_smooth(size=0.5, aes(color=CATEG), method='loess') +   
  facet_grid( . ~ CATEG) +
  labs(x='Year', y=Y_LABEL) +
  theme(text = element_text(size=9), 
        axis.text.x = element_text(angle=45, hjust=1, size=9), 
        axis.text.y = element_text(size=9), 
        axis.title=element_text(size=9, face="bold"),
        legend.position="none")

the_plot

dev.off()

t2 <- Sys.time()
print(t2 - t1)  
rm(list = setdiff(ls(), lsf.str()))