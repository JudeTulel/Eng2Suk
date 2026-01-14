# Use the official Python 3.10 image.
# https://hub.docker.com/_/python
FROM python:3.10-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the local code to the container image.
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run the web service on container startup.
# Streamlit listens on port 8501 by default, so we configure it to 8080
CMD ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]
