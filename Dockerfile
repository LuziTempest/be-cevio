# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set environment variables
# Mencegah Python menulis file .pyc ke disk
ENV PYTHONDONTWRITEBYTECODE 1
# Mencegah Python menyangga stdout dan stderr
ENV PYTHONUNBUFFERED 1

# Set working directory di dalam container
WORKDIR /app

# Instal dependensi sistem yang dibutuhkan oleh psycopg2 (PostgreSQL adapter)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Salin requirements dan instal dependensi Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode proyek
COPY . .

# Buat folder static/uploads jika belum ada
RUN mkdir -p app/static/uploads

# Expose port yang digunakan Flask
EXPOSE 8080

# Jalankan aplikasi
CMD ["python", "main.py"]
