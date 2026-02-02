#!/bin/bash

# Initialize database on Codespace startup
# Creates tables and restores from backup if available

set -e

echo "🚀 Initializing SCISLiSA Backend..."

# Navigate to backend directory
cd /workspaces/SCISLiSA/src/backend

# Activate virtual environment
source .venv/bin/activate

echo "📦 Creating database tables..."
python << EOF
from config.db_config import Base, engine
from models.db_models import Author, Publication, Collaboration, DataSource, Venue

Base.metadata.create_all(bind=engine)
print("✅ Tables created successfully")
EOF

echo "✅ Backend initialization complete!"
