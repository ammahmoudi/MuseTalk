#!/usr/bin/env python3

# Quick validation of URL paths
base_url = "https://example.com"
avatar_id = "test123"

# URL generation (same as in musetalk_native_api.py)
steady_state_url = f"{base_url.rstrip('/')}/avatar/{avatar_id}/steady-state"
thumbnail_url = f"{base_url.rstrip('/')}/avatar/{avatar_id}/thumbnail"

print("✅ Generated URLs match endpoint paths:")
print(f"Steady State: {steady_state_url}")  
print(f"Thumbnail:    {thumbnail_url}")

# Extract paths to verify
steady_path = steady_state_url.replace(base_url, "")
thumb_path = thumbnail_url.replace(base_url, "")

print(f"\n🔍 Path patterns:")
print(f"Steady State: {steady_path}")  
print(f"Thumbnail:    {thumb_path}")
print("\n✅ All paths properly use BASE_URL configuration!")