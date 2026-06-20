# metafor parity runner for B1: pool one contrast under DL and REML.
# Usage: Rscript parity.R "<yi csv>" "<sei csv>"
# Output (stdout): one line per method -> "<METHOD> <estimate> <se>"
args <- commandArgs(trailingOnly = TRUE)
yi  <- as.numeric(strsplit(args[1], ",")[[1]])
sei <- as.numeric(strsplit(args[2], ",")[[1]])
suppressMessages(library(metafor))
for (m in c("DL", "REML")) {
  fit <- rma(yi = yi, sei = sei, method = m)
  cat(m, coef(fit), fit$se, "\n")
}
