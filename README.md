# NVDA Translation Helper

A simple tool to help NVDA translators use `l10nUtil.exe` for downloading and uploading translation files without needing to use the command line.

---

## Features

* Provides a user-friendly graphical interface for common translation tasks.
* **One-Time API Token Setup:** The first time you need it, the app will securely prompt for your Crowdin API token and save it for future use.
* **Automatic Tool Discovery:** Automatically locates `l10nUtil.exe` from the default NVDA installation folder or from the same folder this program is in.
* Download translation files (`.po`, `.xliff`) from the NVDA Crowdin project.
* Upload your translated files back to Crowdin.
* Convert `.xliff` documentation files to `.html` to preview your changes.

---

## Installation and Usage

You can either run the pre-built application directly or run it from the source code if you have Python installed.

### Option 1: For End-Users (Recommended)

This is the easiest way to get started.

1. Go to the **[Releases](https://github.com/audioses/NVDA-translation-helper/releases)** page of this project.
2. Download the `NVDA Translation Helper.exe` file from the latest release.
3. Place the `.exe` file anywhere on your computer (e.g., your Desktop or Documents folder) and double-click it to run.
4. The first time you try to download or upload, the application will prompt you to enter your Crowdin API Token (see "First-Time Setup" below).

### Option 2: For Developers (Running from Source)

If you have Python and want to run the script directly or modify it:

1. **Prerequisites:** Make sure you have Python 3 installed.
2. **Clone the Repository:**
    ```sh
    git clone https://github.com/audioses/NVDA-translation-helper.git
    cd NVDA-translation-helper
    ```
3. **Install Dependencies:** Open a command prompt or terminal in the project folder and run:
    ```sh
    pip install -r requirements.txt
    ```
4. **Run the Application:**
    ```sh
    python main.py
    ```

---

## Requirements

If you're running from source, the only required Python package is:

* `wxPython`

---

## How to Build the .exe with PyInstaller

If you've made changes to the code, you can easily package it into a single `.exe` file yourself.

1. **Install PyInstaller:**
    ```sh
    pip install pyinstaller
    ```
2. **Build the Executable:** In your terminal, run the following command from the project directory:
    ```sh
    pyinstaller build.spec
    ```
3. The final `NVDA Translation Helper.exe` file will be located in the `dist` folder that PyInstaller creates.

---

## First-Time Setup: Getting your Crowdin Token

The first time you try to download or upload, the application will ask for your Crowdin Personal Access Token. This is a one-time setup.

1. Log in to your Crowdin account.
2. Go to your **Account Settings** and then your profile.
3. Go to the **API** tab.
4. Click **"New Token"**.
5. Give the token a name (e.g., "NVDA Translation").
6. **Crucially, you must check the box for the `translations` scope.**
7. Click **Create**.
8. Copy the generated token (`crowdin-token-xxxxxxxx`) and paste it into the dialog box in the NVDA Translation Helper.

All done!

---

## Thanks

I built this tool because I found it tiring to go through the command line all the time. I prefer using guis, and I hope this app is useful for you too!