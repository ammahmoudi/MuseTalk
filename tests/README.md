# Tests Directory

This directory contains test files for the MuseTalk integration system.

## Test Files

### API Tests

- **`test_mock_api.py`** - Tests mock API functionality
- **`test_streaming_api.py`** - Tests streaming API features
- **`test_client.py`** - Tests client API interactions
- **`test_url_generation.py`** - Tests URL generation and routing

### System Tests

- **`test_ffmpeg.py`** - Tests FFmpeg functionality  
- **`test_persistence.py`** - Tests data persistence features
- **`test_avatar_prep.py`** - Tests avatar preparation processes
- **`test_upload_forms.py`** - Tests file upload functionality

### Utility Tests

- **`test_fixed_urls.py`** - Tests URL fix utilities

## Running Tests

Make sure the MuseTalk API server is running, then:

```bash
# Run individual test files
python tests/test_mock_api.py
python tests/test_streaming_api.py

# Or run all tests with pytest if configured
pytest tests/
```

## Configuration

- **API Base URL**: `http://localhost:8000` (production) or `http://localhost:8001` (mock)
- **Test Assets**: Located in `../test_assets/` directory
- **Audio Files**: Located in `../data/audio/` directory

## Requirements

- MuseTalk API server running
- Test assets available in the project
- Python dependencies: `requests`, `aiohttp`, `pathlib`