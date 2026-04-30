# Fetch!
<img src="resources/Fetch_Full_Panle_Header.png" alt="App Icon" width="100%300">

**Your loyal companion for fetching workspaces and user parameters in Fusion.**

**Version:** 1.0.0

**Author:** Ed Johnson (Making With An EdJ)

## Introduction: The "Why" and "What"

Do you find that frequently hunting down and reopening the same set of project files, or manually recreating the same user parameters across new designs, is tedious and breaks your creative flow? 

**Fetch!** is a simple utility Add-in for Fusion designed to automate the repetitive parts of your workflow by saving your digital setups and fetching them exactly when you need them.

* **Workspaces:** Save all of your currently open documents into a named "Workspace" and reopen them all at once with a single click.
* **User Parameters:** Save your carefully crafted user parameters into distinct sets (e.g., "Standard Nut Clearances", "Laser Cut Boxes") and instantly inject them into any active design.
* **Granular Control:** Use the interactive HTML checklists to selectively save or fetch only the specific files or parameters you need for the task at hand.

---
## ✨ What's New in v1.0.0

* **Initial Release:**
* **Workspace Management:** Save and Fetch groups of documents seamlessly, complete with a progress bar.
* **Parameter Management:** Save and Fetch specific User Parameter sets. Updates existing parameters or creates new ones from scratch.
* **Beautiful UI:** Custom HTML/CSS interfaces with automatic dark-mode support and interactive checkboxes.

*For older release notes, please see the **CHANGELOG**.*

## Installation

### Manual Installation Options

This add-in requires a quick manual installation. You can choose to install it in Fusion's default scripts directory or a custom folder of your choice.

#### Option 1: Install in the Default Fusion Directory
1. **Download:** Download the source code as a ZIP file and extract the `Fetch` folder.
2. **Move the Folder:** Move the entire `Fetch` folder into your native Fusion Scripts directory:
   * **Windows:** `%appdata%\Autodesk\Autodesk Fusion\API\Addins`
   * **Mac:** `~/Library/Application Support/Autodesk/Autodesk Fusion/API/Addins`
3. **Open Fusion:** Press `Shift + S` to open the **Scripts and Add-Ins** dialog.
4. **Run the Add-in:** Make sure the **Add-ins** filter checkbox is checked. You should see **Fetch** in the list of add-ins. You may want to check the 'Run on startup' option so it automatically runs when Fusion starts. Click the **Run** icon to execute the add-in.

#### Option 2: Install in a Custom Directory
1. **Download:** Download the source code as a ZIP file and extract the `Fetch` folder.
2. **Organize:** Create a dedicated folder on your computer for your Fusion tools (e.g., `Documents\Fusion_Tools`) and move the `Fetch` folder inside it.
3. **Open Fusion:** Press `Shift + S` to open the **Scripts and Add-Ins** dialog.
4. **Add the Add-in:** Click the grey **"+"** icon next to the search box at the top of the dialog and select **Script or add-in from device**.
5. **Locate:** Navigate to your custom folder, select the `Fetch` folder, and click **Select Folder**.
6. **Run the Add-in:** Make sure the **Add-ins** filter checkbox is checked. You should now see **Fetch** listed. You may want to check the 'Run on startup' option so it automatically runs when Fusion starts. Click the **Run** icon to execute the add-in.

## Using Fetch!

Once installed, you'll find the **Fetch!** commands in the **Design** workspace under the **Utilities** tab. 

The "Fetch Workspace!" and "Fetch Parameters" commands will be promoted directly to your toolbar for easy access. The "Save" commands can be found inside the expanded Scripts and Add-ins panel. All commands can be pinned to the toolbar or added to your 'S' key Design Shortcuts for even faster access.

### Workspace Management
Manage the documents you currently have open.

* **Save Workspace:** Opens a dialog to save your currently open files as a new or existing workspace. Use the checkboxes to selectively exclude any files you don't want to save.
* **Fetch Workspace!:** Select a saved workspace from the dropdown. Use the checkboxes to pick exactly which designs to open, and Fetch will handle the rest.
* **Delete Workspace:** Click the red trash can icon next to the workspace dropdown to remove a saved workspace from your local data file. (This does *not* delete your actual Fusion design files).

### Parameter Management
Manage the User Parameters for your designs.

* **Save Parameters:** Extracts User Parameters from your active document and saves them to a named set. Check or uncheck parameters to save only what you need.
* **Fetch Parameters:** Injects a saved set of parameters into your currently active document. If a parameter already exists, it intelligently updates the expression and comment. If it doesn't, it creates it from scratch!
* **Delete Parameter Set:** Click the red trash can icon next to the parameter set dropdown to remove a saved set from your local data file. (This does *not* delete any parameters from your active Fusion design).

## Tech Stack

For the fellow coders and makers out there, here is how Fetch! was built:

* **Language:** Python (Fusion API)
* **Interface:** Custom HTML/CSS/JavaScript rendered natively in Fusion via `BrowserCommandInput` and `HTMLEventHandler`.
* **Data Storage:** Data is serialized and saved locally to `workspaces.json` and `parameters.json` inside the Add-in's root directory.

## Acknowledgements & Credits

* **Developer:** Ed Johnson ([Making With An EdJ](https://www.youtube.com/@makingwithanedj))
* **AI Assistance:** Developed with coding assistance from Google's Gemini 3.1 Pro model.
* **Lucy (The Cavachon Puppy):**
***Chief Wellness Officer & Director of Mandatory Breaks***
    * Thank you for ensuring I maintained healthy circulation by interrupting my deep coding sessions with urgent requests for play.
* **License:** Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

---

## ❤️ Support the Maker (and Lucy!)

I develop these tools to improve my own workflows and love sharing them with the community. If you find Fetch! useful and want to say thanks, feel free to **buy Lucy a dog treat on Ko-fi**!

***

*Happy Making!*
*— EdJ*