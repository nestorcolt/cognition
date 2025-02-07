FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Copy the package files
COPY . .

# Install build dependencies and build the package
RUN pip install --no-cache-dir build hatchling && \
    python -m build && \
    pip install --no-cache-dir dist/*.whl

# Set default environment variables
ENV ANTHROPIC_API_KEY=""
ENV HUGGINGFACE_API_TOKEN=""
ENV PORTKEY_API_KEY="your-default-portkey"
ENV PORTKEY_VIRTUAL_KEY=""
ENV LONG_TERM_DB_PASSWORD=""
ENV APP_LOG_LEVEL="DEBUG"
ENV CHROMA_PASSWORD=""

# Expose the port your app runs on
EXPOSE 8000

# Command to run when starting the container
CMD ["uvicorn", "cognition.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]