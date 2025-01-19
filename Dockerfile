# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV DATABASE_URL=postgresql://users_owner:oIUjKy23DAcq@ep-holy-mouse-a12tmgtt.ap-southeast-1.aws.neon.tech/users?sslmode=require
ENV GEMINI_API_KEY=AIzaSyCQTi02_eguYtdpMwTU7qyU3Ix9UFWFtXQ
ENV APP_SECRET_KEY=random_secret_key

# Run app.py when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "600", "app:app"]