# Use an official Python runtime as a parent image
FROM python:3.12-alpine

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install PostgreSQL dependencies
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project code
COPY . /code/

# Expose the port the app runs on
EXPOSE 8000

RUN chmod +x /code/pmpy
ENV PATH="/code:$PATH"

# Define the command to run the app using Gunicorn (or Django's runserver for development)
# For production, you'd typically use Gunicorn:
# CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]
# For development:
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 