# از ایمیج پایتون استفاده می‌کنیم
FROM python:3.10-slim

# جلوگیری از باگ با encoding
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# نصب وابستگی‌ها
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# مسیر کاری داخل کانتینر
WORKDIR /app

# کپی کردن فایل‌های مورد نیاز
COPY requirements.txt /app/

# نصب پکیج‌ها
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# کپی کل پروژه
COPY . /app/

# پورت
EXPOSE 8000

# دستور پیش‌فرض اجرا
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "project_name.wsgi:application"]
