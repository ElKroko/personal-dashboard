# Scripts Directory

This directory contains utility scripts for setup, data management, and maintenance of the Personal Finance Dashboard project.

## Structure

```
scripts/
├── README.md              # This file
├── setup/                 # Setup and configuration scripts
│   ├── add_default_categories.py
│   ├── migrate_database.py
│   ├── recreate_table.py
│   └── setup_dependencies.py
└── data/                  # Data management scripts
    ├── create_sample_data.py
    └── insert_sample_data.py
```

## Script Categories

### Setup Scripts (`setup/`)
- **setup_dependencies.py**: Install and configure project dependencies
- **add_default_categories.py**: Add default transaction categories to database
- **migrate_database.py**: Database migration utilities
- **recreate_table.py**: Recreate database tables (development use)

### Data Management Scripts (`data/`)
- **create_sample_data.py**: Generate sample transaction data for testing
- **insert_sample_data.py**: Insert sample data into the database

## Usage

### Initial Project Setup
```bash
# 1. Install dependencies
python scripts/setup/setup_dependencies.py

# 2. Setup database with default categories
python scripts/setup/add_default_categories.py

# 3. (Optional) Add sample data for testing
python scripts/data/create_sample_data.py
```

### Database Management
```bash
# Migrate database schema
python scripts/setup/migrate_database.py

# Recreate tables (WARNING: This will delete existing data)
python scripts/setup/recreate_table.py

# Insert sample data
python scripts/data/insert_sample_data.py
```

### Development Workflow
1. Run setup scripts when first cloning the project
2. Use data scripts to populate test data
3. Use migration scripts when database schema changes

## Important Notes

- **Data Loss Warning**: Scripts in `setup/` may modify or recreate database structures
- **Environment**: These scripts should be run from the project root directory
- **Dependencies**: Ensure virtual environment is activated before running scripts
- **Backup**: Always backup your database before running migration scripts

## Adding New Scripts

1. **Setup scripts**: Add to `scripts/setup/`
2. **Data scripts**: Add to `scripts/data/`
3. **Other utilities**: Add to appropriate subfolder or create new category

Follow the naming convention: `[action]_[target].py` (e.g., `migrate_database.py`, `create_sample_data.py`)
