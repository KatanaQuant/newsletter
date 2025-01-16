# Use the official R image
FROM r-base:latest

# Install dependencies
RUN apt-get update && apt-get install -y \
    libcurl4-openssl-dev \
    libfontconfig1-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev \
    libpq-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install packages
RUN R -e "install.packages('crypto2')"
RUN R -e "install.packages('RPostgres')"
RUN R -e "install.packages('dplyr')"

# Copy the R script into the container
COPY fetch_data.r /usr/local/bin/fetch_data.r

# Set the working directory
WORKDIR /usr/local/bin

# Run the script
CMD ["Rscript", "fetch_data.r"]