# Tests Directory

This directory contains all test files and testing utilities for the Personal Finance Dashboard project.

## Structure

```
tests/
├── README.md              # This file
├── backend/               # Backend-specific tests
│   ├── test_categorization.py
│   ├── test_database_direct.py
│   ├── test_frontend_api.py
│   └── test_update_db.py
├── utils/                 # Testing utilities and analysis scripts
│   ├── analyze_tef_data.py
│   ├── check_uncategorized.py
│   └── quick_check.py
├── test_cartola_b25.py    # Bank statement integration tests
├── test_cartola_integration.py
├── test_date_parsing.py   # Date parsing tests
├── test_debug_errors.py   # Error debugging tests
├── test_endpoint_fix.py   # API endpoint tests
├── test_endpoints.py
├── test_final_verification.py
├── test_real_tef_files.py # Real TEF file processing tests
├── test_tef_integration.py
└── test_tef_processing.py
```

## Test Categories

### Backend Tests (`backend/`)
- **test_categorization.py**: Tests for transaction categorization logic
- **test_database_direct.py**: Direct database operation tests
- **test_frontend_api.py**: API endpoint functionality tests
- **test_update_db.py**: Database update operation tests

### Integration Tests (root level)
- **test_cartola_*.py**: Bank statement (cartola) file processing tests
- **test_tef_*.py**: TEF (Transferencia Electrónica de Fondos) file processing tests
- **test_endpoints.py**: API endpoint integration tests

### Utility Tests
- **test_date_parsing.py**: Date parsing and formatting tests
- **test_debug_errors.py**: Error handling and debugging tests
- **test_final_verification.py**: Final system verification tests

### Testing Utilities (`utils/`)
- **analyze_tef_data.py**: Utility to analyze TEF data files
- **check_uncategorized.py**: Utility to check for uncategorized transactions
- **quick_check.py**: Quick system health check utility

## Running Tests

### Backend Tests
```bash
# From the backend directory
cd backend
python -m pytest ../tests/backend/

# Run specific test
python ../tests/backend/test_categorization.py
```

### Integration Tests
```bash
# From the project root
python tests/test_endpoints.py
python tests/test_cartola_integration.py
```

### Utilities
```bash
# Run analysis utilities
python tests/utils/quick_check.py
python tests/utils/check_uncategorized.py
```

## Test Data

Test files may use sample data located in:
- `backend/data/load_excels/` - Sample Excel files for testing
- `backend/data/finanzas.db` - Test database (not committed to git)

## Adding New Tests

1. **Backend tests**: Add to `tests/backend/`
2. **Integration tests**: Add to `tests/` root
3. **Utilities**: Add to `tests/utils/`

Follow the naming convention: `test_[feature_name].py`
