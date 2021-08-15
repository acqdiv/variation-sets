# To long format for Nick
# Steven Moran <steven.moran@uzh.ch>

# Target format:
# session_id total_utterances match_type window_size num_match match vs_percentage corpus age_in_days unique_speaker_id
# 1 175 fuzzy 2 1 44 0.251428571428571 Chintang 1059 11

library(dplyr)
library(tidyr)

df <- read.csv('English_Adults/results/02_06_2020_12_51_counts.csv', header=T, stringsAsFactors = F)
head(df)

## Calculate what percentage of utterances are variation sets
df.long <- df %>% gather(type, match, 3:ncol(df))
df.long.split <- df.long %>% separate(type, c("match_type", "window_size", "num_match"), "_")
df.long.split <- df.long.split %>% mutate(vs_percentage = match/total_utterances)
head(df.long.split)

results <- df.long.split

# Bug in the output for strict matching, rename
# results$match_type <- "strict"
table(results$match_type)

save(results, file="English_Adults/results/english_results-w1-w10-m1-m4-v-strict.Rdata")
