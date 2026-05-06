# FormCraft - GitHub Upload & Setup Guide

## Trin 1: Opret et GitHub konto (hvis du ikke har et)
1. Gå til [github.com](https://github.com)
2. Klik **Sign up**
3. Udfyld email, password og vælg et brugernavn
4. Verificér din email

## Trin 2: Opret et nyt repository
1. Log ind på GitHub
2. Klik det grønne **New** (eller **+** ikonet øverst til højre > **New repository**)
3. Udfyld:
   - **Repository name**: `formcraft_addon`
   - **Description**: `Blender addon for generating slip-casting plaster molds`
   - **Visibility**: Vælg **Public** (gratis, alle kan se det) eller **Private** (kun du)
4. Lad alt andet være tomt (ikke check README eller .gitignore her - vi har allerede vores egne)
5. Klik **Create repository**

## Trin 3: Clone repoet med GitHub Desktop
1. Åbn **GitHub Desktop**
2. Log ind med din GitHub-konto
3. Klik **File > Clone repository**
4. Gå til **URL** fanen
5. Kopiér URL'en fra GitHub (den ser sådan ud: `https://github.com/DIT_BRUGERNAVN/formcraft_addon.git`)
6. **Local path**: Vælg f.eks. `C:\Users\Jacob\Documents\GitHub\formcraft_addon`
7. Klik **Clone**

## Trin 4: Kopier FormCraft filerne ind i repoet
1. Åbn den mappe du cloned i Trin 3
2. Kopiér **alle filerne** fra `formcraft_addon` mappen på dit Desktop:
   - `__init__.py`
   - `geometry.py`
   - `operators.py`
   - `properties.py`
   - `ui.py`
   - `updater.py`
   - `README.md`
   - `.gitignore`
3. Indsæt dem i den clonedede mappe

## Trin 5: Commit og push
1. I **GitHub Desktop** vil du nu se alle filerne under "Changes"
2. Skriv en **Summary** (f.eks. `Initial release - FormCraft v0.1.0`)
3. Klik **Commit to main**
4. Klik **Push origin** (blå knap øverst)

## Trin 6: Lav din første release (kræves for at update-systemet virker)
1. Gå til dit repo på github.com
2. Klik **Releases** (til højre, under "About")
3. Klik **Create a new release**
4. Udfyld:
   - **Tag**: `v0.1.0`
   - **Title**: `FormCraft v0.1.0 - Initial Release`
   - **Beskrivelse**: Skriv hvad der er med i denne version
5. Klik **Attach binaries** og upload `formcraft_addon.zip` fra dit Desktop
6. Klik **Publish release**

## Trin 7: Konfigurér opdatering i Blender
1. Åbn Blender
2. **Edit > Preferences > Add-ons > FormCraft**
3. Sæt **GitHub Repository** til: `DIT_BRUGERNAVN/formcraft_addon`
4. Luk preferences

Nu virker **Check for Updates** og **Install Update** knapperne i N-panelet!
