# Use official Python image
#FROM python:3.11-slim

# Set working directory
#WORKDIR /app

# Copy backend and frontend into container
#COPY backend /app/backend
#COPY frontend /app/frontend
#
# Install dependencies directly (no requirements.txt)
#RUN pip install --no-cache-dir -r requirements.txt


# Expose Flask port
#EXPOSE 5001

# Run Flask app
#CMD ["python", "/app/backend/app.py"]




# movie-review-app/backend/Dockerfile
FROM python:3.11-slim

# Create app dir
WORKDIR /app

# --- Copy backend files ---
COPY ./backend/requirements.txt /app/requirements.txt
COPY ./backend/app.py /app/app.py
COPY ./backend/scripts /app/scripts

# --- Copy frontend assets where Flask expects them ---
COPY ./frontend /app/frontend

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt
RUN pip install prometheus_client
## Expose Flask port
EXPOSE 5001

# Start the app (dev server)
CMD ["python", "/app/app.py"]
# (Prod recommendation)

