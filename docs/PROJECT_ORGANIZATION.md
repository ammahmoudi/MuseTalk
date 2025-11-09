# 📁 Project Organization Summary

This document summarizes the recent reorganization of the MuseTalk project structure for better maintainability and clarity.

## What Changed?

All documentation, Docker files, and scripts have been reorganized into dedicated folders:

### 📚 Documentation (`docs/`)
**Moved files:**
- `API_STREAMING_GUIDE.md`
- `AVATAR_MEDIA_GUIDE.md`
- `DOCKER_INTEGRATION_GUIDE.md`
- `DOCKER_QUICKSTART.md`
- `INSTALLATION.md`
- `MOCK_API_GUIDE.md`
- `MUSETALK_INTEGRATION.md`
- `ONLINE_INSTANCE_SETUP.md`
- `PERSISTENCE_SUMMARY.md`

All documentation is now centralized in the `docs/` folder for easy access.

### 🐳 Docker (`docker/`)
**Moved files:**
- `docker-compose.yml`
- `docker-compose.dev.yml`
- `docker-compose.prod.yml`
- `docker-setup.sh`
- `docker-setup.bat`
- `entrypoint.sh`

All Docker-related configuration and setup files are now in the `docker/` folder.

**Important:** When using docker-compose, you now need to run it from the docker directory:
```bash
cd docker
docker-compose up
```

Or reference the files explicitly:
```bash
docker-compose -f docker/docker-compose.yml up
```

### 🛠️ Scripts (`scripts/`)
**Moved files:**
- `download_weights.sh`
- `download_weights.bat`
- `install_dependencies.sh`
- `install_dependencies.bat`
- `install_dependencies.py`
- `inference.sh`
- `setup_online_instance.sh`
- `train.sh`
- `start_mock_api.bat`
- `sync_requirements.py`

**Note:** The following files remain in `scripts/` but existed there already:
- `inference.py`
- `realtime_inference.py`
- `preprocess.py`
- `__init__.py`

All utility and setup scripts are now organized in the `scripts/` folder.

### 🧪 Tests (`tests/`)
**Moved files:**
- `debug_avatar_endpoints.py`
- `simple_debug.py`
- `test_real_api.py`
- `validate_paths.py`

All test and debug scripts are now in the `tests/` folder.

## New Structure

```
MuseTalk/
├── 📚 docs/              # All documentation
├── 🐳 docker/            # Docker configuration
├── 🛠️ scripts/          # Setup and utility scripts
├── 🧪 tests/            # Test scripts
├── 🎭 api/              # API implementation
├── 🧠 musetalk/         # Core modules
├── 🎨 assets/           # Demo assets
├── ⚙️ configs/          # Config files
├── 📦 models/           # Model weights
├── 📄 app.py            # Gradio app
├── 📄 main.py           # Main entry point
├── 📄 train.py          # Training script
└── 📄 README.md         # Main readme
```

## Benefits

1. **🔍 Better Organization** - Related files are grouped together
2. **📖 Easier Navigation** - Clear separation of concerns
3. **🧹 Cleaner Root** - Less clutter in the project root
4. **🎯 Clear Purpose** - Each folder has a specific role
5. **🚀 Better Maintainability** - Easier to find and update files

## Usage Updates

### Running Scripts

**Before:**
```bash
./download_weights.sh
./install_dependencies.sh
```

**After:**
```bash
./scripts/download_weights.sh
./scripts/install_dependencies.sh
```

Or run from the scripts directory:
```bash
cd scripts
./download_weights.sh
./install_dependencies.sh
```

### Using Docker

**Before:**
```bash
docker-compose up
```

**After (Option 1):**
```bash
cd docker
docker-compose up
```

**After (Option 2):**
```bash
docker-compose -f docker/docker-compose.yml up
```

### Accessing Documentation

All guides are now in `docs/`:
- Installation guide: `docs/INSTALLATION.md`
- Docker guide: `docs/DOCKER_QUICKSTART.md`
- API guide: `docs/API_STREAMING_GUIDE.md`

## README Files

Each folder now includes a `README.md` explaining its contents:
- `docs/README.md` - Documentation index
- `docker/README.md` - Docker setup guide
- `scripts/README.md` - Scripts usage guide

## Backward Compatibility

⚠️ **Important:** If you have scripts or tools that reference the old file locations, you'll need to update them to use the new paths.

Common updates needed:
- Update paths in CI/CD pipelines
- Update Docker build contexts if needed
- Update script references in documentation
- Update symlinks or shortcuts

## Next Steps

1. ✅ Test all Docker compose configurations
2. ✅ Verify all scripts work from new locations
3. ✅ Update any external references
4. ✅ Update IDE/editor project configurations
5. ✅ Test API startup with new structure

## Questions?

If you encounter any issues with the new structure, please:
1. Check this document for path updates
2. Look at the README in each folder
3. Open an issue on GitHub

---

*Last updated: January 2025*
