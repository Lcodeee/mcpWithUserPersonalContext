FROM python:3.12-slim

ARG PORT=8050
WORKDIR /app

# Install uv
RUN pip install uv

# Copy only dependency files first (so install step can be cached)
COPY pyproject.toml poetry.lock* requirements.txt* ./

# Set up virtual environment
RUN python -m venv .venv

# Install dependencies
RUN uv pip install -e .

# Now copy the rest of the code (which may change often)
COPY . .

EXPOSE ${PORT}

CMD ["uv", "run", "src/main.py"]









# FROM python:3.12-slim

# ARG PORT=8050

# WORKDIR /app

# # Install uv
# RUN pip install uv

# # Copy the MCP server files
# COPY . .


# # Install packages
# RUN python -m venv .venv
# RUN uv pip install -e .


# EXPOSE ${PORT}

# # Command to run the MCP server
# CMD ["uv", "run", "src/main.py"]