# Step 1: Install yfinance if not already installed
# You can run this in your terminal
# pip install yfinance

# Step 2: Import yfinance
import yfinance as yf

# Step 3: Download ESZ24.CME data
ticker = 'ESZ24.CME'
data = yf.download(ticker)

# Print the data
print(data)
