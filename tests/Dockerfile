FROM python:3.11-slim

WORKDIR /app

# Instal dependensi testing
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy file test ke dalam image
COPY . .

# Secara default, container ini akan menunggu perintah 'pytest'
# Namun kita set entrypoint agar tetap aktif atau langsung menjalankan test
CMD ["pytest", "integration_test.py", "-v"]