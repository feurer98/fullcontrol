# Node-Slicer Backend

FastAPI backend for Node-Slicer - Visual Node-Editor for 3D printing.

## Setup

```bash
# Install dependencies
pip install -e ".[dev]"

# Run development server
pnpm dev

# Or directly with uvicorn
uvicorn main:app --reload
```

## Project Structure

```
backend/
├── src/
│   ├── core/          # Core business logic
│   ├── api/           # API routes
│   ├── models/        # Data models
│   └── utils/         # Utility functions
├── tests/             # Test suite
├── main.py           # FastAPI application
└── pyproject.toml    # Python dependencies
```

## Development

- **Linting**: `pnpm lint` (runs ruff)
- **Formatting**: `pnpm format` (runs black + ruff fix)
- **Testing**: `pnpm test` (runs pytest)
