# 🔄 Project Reorganization - Import & Path Updates

This document tracks all the import and path updates made after reorganizing the project structure.

## Summary of Changes

### 1. Docker Compose Configuration Updates

**File:** `docker/docker-compose.yml`

All relative paths updated to work from the docker folder:
- Build context changed from `.` to `..`
- Volume paths changed from `./` to `../`
- Updated paths:
  - `./models` → `../models`
  - `./data` → `../data`
  - `./test_assets` → `../test_assets`
  - `./nginx` → `../nginx`

### 2. Script Path Updates

**File:** `scripts/install_dependencies.sh`

Updated to find `download_weights.sh` in the same directory:
```bash
# Before
if [ -f "download_weights.sh" ]; then
    ./download_weights.sh

# After
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/download_weights.sh" ]; then
    "$SCRIPT_DIR/download_weights.sh"
```

### 3. Documentation Path Updates

**File:** `README.md`

Updated script references in main documentation:
```bash
# Before
sh ./download_weights.sh
download_weights.bat

# After
sh ./scripts/download_weights.sh
scripts\download_weights.bat
```

### 4. Folder Reorganization

**Moved:** `docker/entrypoints/` → `scripts/entrypoints/`

**Reason:** Entrypoint scripts are application logic, not Docker configuration

**Updated files:**
- `docker/README.md` - Added note about entrypoints location
- `scripts/README.md` - Added entrypoints section
- `scripts/entrypoints/README.md` - Updated COPY command examples
- `README.md` - Updated project structure diagram

### 5. README Structure Updates

**Files Updated:**
- `docker/README.md` - Removed entrypoints directory section, added reference to scripts
- `scripts/README.md` - Added entrypoints directory documentation
- `README.md` - Updated project structure tree
- `docs/PROJECT_ORGANIZATION.md` - Updated to reflect entrypoints move

## Files Modified

1. ✅ `docker/docker-compose.yml` - Build context and volume paths
2. ✅ `scripts/install_dependencies.sh` - Script path resolution
3. ✅ `README.md` - Script command examples
4. ✅ `docker/README.md` - Entrypoints reference
5. ✅ `scripts/README.md` - Entrypoints documentation
6. ✅ `scripts/entrypoints/README.md` - Docker COPY command example

## Import Verification

### Python Imports
✅ No Python import changes needed - all imports use relative or package imports

### Shell Scripts
✅ Updated to use directory-aware paths with `$SCRIPT_DIR`

### Docker
✅ Updated relative paths in docker-compose.yml to work from docker/ folder

## Testing Checklist

After these changes, verify:

- [ ] Docker compose works from docker folder: `cd docker && docker-compose up`
- [ ] Docker compose works with full path: `docker-compose -f docker/docker-compose.yml up`
- [ ] Scripts work from root: `./scripts/install_dependencies.sh`
- [ ] Scripts work from scripts folder: `cd scripts && ./install_dependencies.sh`
- [ ] APIs import correctly: `cd api && uv run python main.py`
- [ ] Documentation links are correct

## Breaking Changes

### For Users

⚠️ **Docker Compose Usage Changed:**

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

### For Developers

⚠️ **Entrypoint Scripts Moved:**

If you have custom Dockerfiles that copy entrypoint scripts:

**Before:**
```dockerfile
COPY docker/entrypoints/musetalk-mock-dev.sh /app/entrypoint.sh
```

**After:**
```dockerfile
COPY scripts/entrypoints/musetalk-mock-dev.sh /app/entrypoint.sh
```

## Benefits of These Changes

1. ✅ **Clearer Organization** - Docker config in docker/, scripts in scripts/
2. ✅ **Better Separation** - Application logic (entrypoints) separate from infra (docker-compose)
3. ✅ **Easier Maintenance** - Related scripts grouped together
4. ✅ **More Intuitive** - Entrypoints are scripts, so they're in scripts/
5. ✅ **Consistent Structure** - All executable scripts in one place

## Migration Guide

### If You Have Custom Scripts

1. Update any scripts that reference old paths
2. Change `./download_weights.sh` to `./scripts/download_weights.sh`
3. Change `./install_dependencies.sh` to `./scripts/install_dependencies.sh`

### If You Use Docker

1. Navigate to docker folder before running compose: `cd docker`
2. Or use full path: `docker-compose -f docker/docker-compose.yml up`
3. Update any custom Dockerfiles to reference `scripts/entrypoints/`

### If You Have CI/CD Pipelines

1. Update paths in build scripts
2. Update docker-compose commands
3. Update any script execution paths

## Validation Results

✅ **APIs Tested:**
- Real API imports: `cd api && uv run python main.py` ✓
- Mock API imports: `cd api && uv run python mock_api.py` ✓

✅ **Structure Verified:**
- Entrypoints in scripts/entrypoints/ ✓
- Docker config in docker/ ✓
- All docs in docs/ ✓
- All scripts in scripts/ ✓

## Related Documentation

- [Project Organization](docs/PROJECT_ORGANIZATION.md) - Full reorganization details
- [Quick Start](QUICKSTART.md) - Updated commands and paths
- [Organization Summary](ORGANIZATION_SUMMARY.md) - Complete file inventory

---

**Last Updated:** January 2025
**Changes:** Path updates and entrypoints reorganization
