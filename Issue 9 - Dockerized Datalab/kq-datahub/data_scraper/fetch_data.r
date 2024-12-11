library(crypto2)
library(RPostgres)
library(dplyr)

# https://github.com/sstoeckl/crypto2
# https://cran.r-project.org/web/packages/crypto2/crypto2.pdf

process_and_persist_ohlcv <- function(group, start_date, con, ohlcv_table_name, coins, interval) {
  print(paste("Fetching historical data for coins with start_date:", start_date))
  
  # Fetch historical data for the current group
  coin_hist <- crypto_history(group, start_date=start_date, end_date=today, finalWait=FALSE, interval=interval)
  coin_hist <- merge(coin_hist, coins[, c("id", "symbol")], by.x = "symbol", by.y = "symbol")
  
  # Convert timestamps to POSIXct format
  coin_hist$time_open <- as.POSIXct(coin_hist$time_open, format="%Y-%m-%dT%H:%M:%OS", tz="UTC")
  coin_hist$time_close <- as.POSIXct(coin_hist$time_close, format="%Y-%m-%dT%H:%M:%OS", tz="UTC")
  coin_hist$time_high <- as.POSIXct(coin_hist$time_high, format="%Y-%m-%dT%H:%M:%OS", tz="UTC")
  coin_hist$time_low <- as.POSIXct(coin_hist$time_low, format="%Y-%m-%dT%H:%M:%OS", tz="UTC")
  
  coin_hist$interval <- interval
  
  coin_hist <- coin_hist[, c("id.x", "interval", "time_open", "time_close", "time_high", "time_low", "open", "high", "low", "close", "volume", "market_cap")]
  names(coin_hist)[1] <- "coin_id"
  
  # Remove duplicate rows
  coin_hist <- unique(coin_hist)
  
  print(paste("Number of rows in coin_hist for start_date", start_date, ":", nrow(coin_hist)))
  
  # Fetch existing data from the database for the same time period
  existing_rows <- dbGetQuery(con, paste0("
    SELECT * FROM ", ohlcv_table_name, "
    WHERE coin_id IN (", paste(shQuote(coin_hist$coin_id), collapse = ","), ")
    AND time_open >= '", min(coin_hist$time_open), "'
    AND time_open <= '", max(coin_hist$time_open), "'
  "))
  
  # Filter out rows that are already present
  new_rows <- anti_join(coin_hist, existing_rows, by = c("coin_id", "time_open"))
  
  # Insert only the new rows into the database
  if (nrow(new_rows) > 0) {
    dbWriteTable(con, ohlcv_table_name, new_rows, append = TRUE, row.names = FALSE)
    print(paste("Inserted", nrow(new_rows), "new rows into the database"))
  } else {
    print("No new rows to insert")
  }
}

# Function to split a data frame into chunks
split_into_chunks <- function(df, chunk_size) {
  split(df, ceiling(seq_along(1:nrow(df)) / chunk_size))
}

# Retrieve environment variables
db_user <- Sys.getenv("DB_USER")
db_password <- Sys.getenv("DB_PW")
db_name <- Sys.getenv("DB_DB")
db_port <- as.integer(Sys.getenv("DB_PORT"))

# Establish a connection to the PostgreSQL database
con <- dbConnect(
  RPostgres::Postgres(),
  dbname = db_name,
  host = "db", # Use the service name of the database container
  port = db_port,
  user = db_user,
  password = db_password
)

# Fetch distinct coin_id, symbol (as slug), and the last timestamp for each coin
existing_data <- dbGetQuery(con, "
  SELECT ohlcv.coin_id, coins.symbol AS slug, MAX(ohlcv.time_open) as last_timestamp
  FROM ohlcv
  JOIN coins ON ohlcv.coin_id = coins.id
  GROUP BY ohlcv.coin_id, coins.symbol
")

# Fetch the list of coins
coins <- crypto_list(only_active=TRUE)

# Create a temporary table to hold the new data
dbWriteTable(con, "temp_coins", coins, overwrite = TRUE, row.names = FALSE)

# Insert new rows into the coins table, avoiding duplicates
dbExecute(con, "
  INSERT INTO coins (id, name, symbol, is_active, first_historical_data, last_historical_data)
  SELECT id, name, symbol, is_active, first_historical_data, last_historical_data
  FROM temp_coins
  ON CONFLICT (id) DO NOTHING
")

# Drop the temporary table
dbExecute(con, "DROP TABLE temp_coins")

today <- Sys.Date()
ohlcv_table_name <- "ohlcv"
interval <- "1d"

# look if we have existing ohlcv data for coins
existing_data <- dbGetQuery(con, "
  SELECT ohlcv.coin_id AS id, coins.symbol AS slug, MAX(ohlcv.time_open) as last_timestamp
  FROM ohlcv
  JOIN coins ON ohlcv.coin_id = coins.id
  GROUP BY ohlcv.coin_id, coins.symbol
")

default_start_date <- "2007-01-01"
existing_data$last_timestamp[is.na(existing_data$last_timestamp)] <- default_start_date

existing_groups <- split(existing_data, existing_data$last_timestamp)
for (group in existing_groups) {
  process_and_persist_ohlcv(group, group$last_timestamp[1], con, ohlcv_table_name, coins, interval)
}

no_existing_data <- coins[!coins$id %in% existing_data,]

# Split no_existing_data into chunks
chunk_size <- 10
no_existing_data_chunks <- split_into_chunks(no_existing_data, chunk_size)
for (chunk in no_existing_data_chunks) {
  process_and_persist_ohlcv(chunk, default_start_date, con, ohlcv_table_name, coins, interval)
}

dbDisconnect(con)