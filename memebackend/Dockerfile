# Base image
FROM python:3.8-slim-buster
# FROM python:3.8 # for non-binary psycopg2

# Set environment variables for Python and ensure output is sent straight to the terminal
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /django

# Install system dependencies for psycopg2 and any other necessary packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt requirements.txt
# RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --verbose --no-cache-dir -r requirements.txt

# for psycopg2 (non-binary):
# Optionally, remove unnecessary build packages to keep the image smaller
# This will remove the gcc compiler and libpq-dev, which are not required after psycopg2 is built
# RUN apt-get purge -y \
#     libpq-dev \
#     gcc && \
#     apt-get autoremove -y && \
#     apt-get clean

# Copy the rest of the application code into the container
COPY . .

# Remaining Dockerfile commands, like the CMD or ENTRYPOINT to start your application, can be added here
# For example, if you use gunicorn as a WSGI server, you can have:
CMD ["gunicorn", "memebackend.wsgi:application", "--bind", "0.0.0.0:8000"]
