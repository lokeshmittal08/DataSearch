# Use official Python image
FROM python:3.11-bullseye as base

# update to sqlite 3.38
RUN wget https://www.sqlite.org/2022/sqlite-autoconf-3380500.tar.gz && \
    tar xvfz sqlite-autoconf-3380500.tar.gz && \
    cd sqlite-autoconf-3380500 && \
    export CFLAGS="-DSQLITE_ENABLE_FTS3 \
    -DSQLITE_ENABLE_FTS3_PARENTHESIS \
    -DSQLITE_ENABLE_FTS4 \
    -DSQLITE_ENABLE_FTS5 \
    -DSQLITE_ENABLE_JSON1 \
    -DSQLITE_ENABLE_LOAD_EXTENSION \
    -DSQLITE_ENABLE_RTREE \
    -DSQLITE_ENABLE_STAT4 \
    -DSQLITE_ENABLE_UPDATE_DELETE_LIMIT \
    -DSQLITE_SOUNDEX \
    -DSQLITE_TEMP_STORE=3 \
    -DSQLITE_USE_URI \
    -O2 \
    -fPIC" && \
    export PREFIX="/usr/local" && \
    LIBS="-lm" ./configure --disable-tcl --enable-shared --enable-tempstore=always --prefix="$PREFIX" && \
    make -j$(nproc) && \
    make install && \
    cp .libs/libsqlite3.so.0 /usr/lib/x86_64-linux-gnu/libsqlite3.so.0 && \
    rm -rf sqlite-autoconf-3380500 && \ 
    rm -rf sqlite-autoconf-3380500.tar.gz

FROM base

# Set work directory
WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    git \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python packages
# RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app files
COPY . .

RUN mkdir -p /app/data/faiss_index
RUN mkdir -p /app/data/uploads

RUN chmod +x /app/start.sh
RUN chmod +x /app/freeze.sh
ENV PYTHONPATH="/app"
# Expose FastAPI port
EXPOSE 8000

# Run the app
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["sleep", "infinity"]
