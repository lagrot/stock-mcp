# Use a lightweight Python base
FROM python:3.12-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Ensure the virtual environment created by uv is in the path
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

WORKDIR /app

# Install uv from the official source
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml uv.lock ./

# Use 'uv sync' to install everything defined in the project
# --frozen: ensures we use the exact versions in uv.lock
# --no-dev: don't install development dependencies
RUN uv sync --frozen --no-dev --no-cache

# Copy the rest of the application
COPY . .

# Run as a non-root user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Run the server
CMD ["python", "-m", "src.mcp.server", "--debug"]
