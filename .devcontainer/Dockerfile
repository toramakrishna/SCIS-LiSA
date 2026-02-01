FROM mcr.microsoft.com/devcontainers/base:ubuntu

# Install system dependencies
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential \
    curl \
    git \
    postgresql-client \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Install Python dependencies will be done in postCreateCommand
# Install Node dependencies will be done in postCreateCommand
