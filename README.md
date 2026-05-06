# FormCraft - Plaster Mold Generator for Blender

A Blender addon that generates slip-casting style plaster molds from 3D models.

## Features
- **Square/Rectangular mold boxes** with rounded corners
- **Automatic splitting** into two halves (Z, Y, or X axis)
- **Round registration keys** for precise alignment
- **Pouring hole** and **vent channels**
- **STL export** for 3D printing
- **Auto-updater** via GitHub releases

## Installation
1. Download the latest `formcraft_addon.zip` from [Releases](https://github.com/YOUR_USERNAME/formcraft_addon/releases)
2. In Blender: **Edit > Preferences > Add-ons**
3. Click **Install** and select the ZIP file (do not unzip)
4. Enable the addon

## Usage
1. Select a mesh object in the 3D viewport
2. Press **N** to open the sidebar
3. Go to the **FormCraft** tab
4. Adjust settings as needed
5. Click **Generate Mold**

## Settings
- **Square Box**: Makes the outer shape square using the largest dimension
- **Corner Radius**: Rounds the outer corners of the mold box
- **Wall Thickness**: Thickness of the plaster walls
- **Margin**: Clearance around the master object
- **Split Axis**: Z (Top/Bottom), Y (Front/Back), or X (Left/Right)
- **Registration Keys**: Number, radius, and depth of alignment keys
- **Pouring Hole**: Adds a hole in the top for pouring
- **Vent Channels**: Small channels for air escape

## Updating
### From GitHub
1. Go to **Edit > Preferences > Add-ons > FormCraft**
2. Enter the repository: `YOUR_USERNAME/formcraft_addon`
3. In the N-panel, click **Check for Updates** or **Install Update**

### From Local ZIP
- Click **Install from Local ZIP** in the N-panel and select a downloaded ZIP file.

## License
GPL-3.0
