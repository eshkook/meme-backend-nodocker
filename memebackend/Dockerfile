# instructions on how to run the app

# the chosen base image
FROM python:3.8-slim-buster 

# sets the working directory in the container
WORKDIR /app

# copying the requirements file of this django app into the container app 
COPY requirements.txt requirements.txt 

# installing Python dependencies in the container
RUN pip3 install -r requirements.txt

# copying the entire folder of this django app into the container app (why did we copied earlier the requirements separately)
COPY . .

# the running command. the is meant to make the machine able to access the container
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]