FROM python:3.10-slim

WORKDIR /app

# Copy the package files
COPY . .

# Install the package
RUN pip install --no-cache-dir .

# Command to run when starting the container
CMD ["python", "-m", "cognition"] 