FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the package files
COPY . .

# Install build dependencies and build the package
RUN pip install --no-cache-dir build hatchling && \
    python -m build && \
    pip install --no-cache-dir dist/*.whl

# Expose the port your app runs on
EXPOSE 8000

# Command to run when starting the container
CMD ["uvicorn", "cognition.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]