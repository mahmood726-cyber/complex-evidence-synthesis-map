# RoBMA cross-check runner for the publication-bias axis.
# Usage: Rscript robma.R "<yi csv>" "<sei csv>"
# Output: "ROBMA <mean> <ci_low> <ci_high>" or "ROBMA_UNAVAILABLE <reason>".
# Requires JAGS >= 4.3.1 (external) + RoBMA; degrades cleanly if absent.
args <- commandArgs(trailingOnly = TRUE)
yi  <- as.numeric(strsplit(args[1], ",")[[1]])
sei <- as.numeric(strsplit(args[2], ",")[[1]])
ok <- requireNamespace("RoBMA", quietly = TRUE)
if (!ok) { cat("ROBMA_UNAVAILABLE package-not-installed\n"); quit(status = 0) }
fit <- tryCatch(
  RoBMA::RoBMA(d = yi, se = sei, chains = 2, sample = 1000, burnin = 500,
               parallel = FALSE, seed = 1),
  error = function(e) paste("ERR", conditionMessage(e)))
if (is.character(fit)) {
  cat("ROBMA_UNAVAILABLE", gsub("\\s+", "_", fit), "\n")
} else {
  s <- summary(fit)$estimates
  mu <- s["mu", "Mean"]; lo <- s["mu", "0.025"]; hi <- s["mu", "0.975"]
  cat("ROBMA", mu, lo, hi, "\n")
}
