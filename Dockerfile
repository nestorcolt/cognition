FROM python:3.12-slim
WORKDIR /app

# Copy the package files
COPY . .

# Install build dependencies and build the package
RUN pip install --no-cache-dir build hatchling && \
    python -m build && \
    pip install --no-cache-dir dist/*.whl

# Command to run when starting the container
CMD ["python", "-m", "cognition"] 