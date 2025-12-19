FROM python:3.11-slim

WORKDIR /app

# 1. Instal dependencies sebagai root (agar masuk ke PATH global)
COPY requirement.txt .
RUN pip install --no-cache-dir -r requirement.txt

# 2. Buat user (Bab 10: Security)
RUN adduser --disabled-password appuser

# 3. Copy semua kode
COPY . .

# 4. Ubah kepemilikan folder ke appuser
RUN chown -R appuser:appuser /app

# 5. Switch ke user tersebut
USER appuser

# 6. Gunakan 'python -m uvicorn' untuk menghindari error PATH
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]