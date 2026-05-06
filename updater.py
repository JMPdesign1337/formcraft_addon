"""
Update checker and installer for FormCraft.
Supports GitHub releases and local ZIP updates.
"""

import bpy
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


def get_addon_path():
    prefs = bpy.context.preferences
    for path in prefs.filepaths.script_directories:
        addon_path = os.path.join(path.directory, "addons", "formcraft_addon")
        if os.path.isdir(addon_path):
            return addon_path
    return None


def get_current_version():
    from . import bl_info
    return bl_info["version"]


def version_tuple_to_str(v):
    return ".".join(str(x) for x in v)


def version_str_to_tuple(s):
    try:
        return tuple(int(x) for x in s.lstrip("v").split("."))
    except (ValueError, AttributeError):
        return (0, 0, 0)


def check_github_updates(repo, use_prereleases=False):
    if not repo:
        return None, "No GitHub repository configured"

    api_url = f"https://api.github.com/repos/{repo}/releases"
    if not use_prereleases:
        api_url += "?per_page=1"

    try:
        req = urllib.request.Request(api_url)
        req.add_header("User-Agent", "FormCraft-Blender-Addon")
        req.add_header("Accept", "application/vnd.github.v3+json")

        with urllib.request.urlopen(req, timeout=10) as response:
            releases = json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return None, f"HTTP error: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return None, f"Network error: {e.reason}"
    except Exception as e:
        return None, f"Error: {str(e)}"

    if not use_prereleases and releases:
        releases = releases[:1]

    if use_prereleases:
        releases = [r for r in releases if r.get("prerelease") is False or use_prereleases]

    if not releases:
        return None, "No releases found"

    current = get_current_version()
    best_release = None
    best_version = current

    for release in releases:
        tag = release.get("tag_name", "").lstrip("v")
        version = version_str_to_tuple(tag)
        if version > best_version:
            best_version = version
            best_release = release

    if best_release is None:
        return None, "Already on the latest version"

    assets = best_release.get("assets", [])
    download_url = None
    for asset in assets:
        if asset.get("name", "").endswith(".zip"):
            download_url = asset.get("browser_download_url")
            break

    if not download_url:
        download_url = best_release.get("html_url", "")

    release_notes = best_release.get("body", "No release notes available.")

    return best_version, download_url, release_notes


def download_and_install(download_url):
    addon_dir = get_addon_path()
    if addon_dir is None:
        scripts_path = bpy.utils.user_resource("SCRIPTS")
        addon_dir = os.path.join(scripts_path, "addons", "formcraft_addon")

    temp_dir = tempfile.mkdtemp(prefix="formcraft_update_")
    zip_path = os.path.join(temp_dir, "update.zip")

    try:
        with urllib.request.urlopen(download_url, timeout=30) as response:
            with open(zip_path, "wb") as f:
                f.write(response.read())

        extract_dir = os.path.join(temp_dir, "extracted")

        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        extracted_items = os.listdir(extract_dir)

        if len(extracted_items) == 1:
            source_dir = os.path.join(extract_dir, extracted_items[0])
            if os.path.isdir(source_dir) and "__init__.py" in os.listdir(source_dir):
                pass
            else:
                source_dir = extract_dir
        else:
            source_dir = extract_dir

        if os.path.exists(addon_dir):
            shutil.rmtree(addon_dir)

        shutil.copytree(source_dir, addon_dir)

        return True, f"Installed to: {addon_dir}"

    except Exception as e:
        return False, f"Install failed: {str(e)}"

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def install_local_zip(zip_path):
    addon_dir = get_addon_path()
    if addon_dir is None:
        scripts_path = bpy.utils.user_resource("SCRIPTS")
        addon_dir = os.path.join(scripts_path, "addons", "formcraft_addon")

    if not os.path.isfile(zip_path):
        return False, f"File not found: {zip_path}"

    temp_dir = tempfile.mkdtemp(prefix="formcraft_local_")
    extract_dir = os.path.join(temp_dir, "extracted")

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        extracted_items = os.listdir(extract_dir)

        if len(extracted_items) == 1:
            source_dir = os.path.join(extract_dir, extracted_items[0])
            if os.path.isdir(source_dir) and "__init__.py" in os.listdir(source_dir):
                pass
            else:
                source_dir = extract_dir
        else:
            source_dir = extract_dir

        if os.path.exists(addon_dir):
            shutil.rmtree(addon_dir)

        shutil.copytree(source_dir, addon_dir)

        return True, f"Installed from: {zip_path}"

    except Exception as e:
        return False, f"Install failed: {str(e)}"

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
