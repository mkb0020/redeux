FROM python:3.11-slim

#INSTALL FFMPEG
RUN apt-get update && apt-get install -y ffmpeg

# SET WORKING DIRECTORY
WORKDIR /app

# COPY APP FILES
COPY . .

# INSTALL PYTHON DEPENDENCIES 
RUN pip install --no-cache-dir -r requirements.txt

# RUN THE APP
CMD ["python", "app.py"]
