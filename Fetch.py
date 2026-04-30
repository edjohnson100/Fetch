import adsk.core, adsk.fusion, traceback
import json
import os

app = None
ui  = None

# Global set of event handlers to keep them referenced in memory
handlers = []

current_save_state = {'mode': 'Create New', 'name': '', 'select': ''}
current_open_state = {'select': ''}
current_save_params_state = {'mode': 'Create New', 'name': '', 'select': ''}
current_open_params_state = {'select': ''}

def get_json_path():
    # This automatically saves the JSON file right next to Fetch.py
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'workspaces.json')

def load_workspaces():
    path = get_json_path()
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_workspaces(data):
    with open(get_json_path(), 'w') as f:
        json.dump(data, f, indent=4)

def get_params_json_path():
    # Saves a separate JSON file for your user parameters
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'parameters.json')

def load_parameters():
    path = get_params_json_path()
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_parameters(data):
    with open(get_params_json_path(), 'w') as f:
        json.dump(data, f, indent=4)

class FetchSaveCommandHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global current_save_state
            if args.action == 'ready':
                workspaces = load_workspaces()
                
                open_files = []
                for doc in app.documents:
                    if doc.dataFile:
                        open_files.append(doc.dataFile.name)
                    else:
                        open_files.append(doc.name)
                        
                info = {
                    'hasDocs': app.documents.count > 0,
                    'openFiles': open_files,
                    'workspaces': workspaces
                }
                args.browserCommandInput.sendInfoToHTML('init', json.dumps(info))
            elif args.action == 'update':
                current_save_state = json.loads(args.data)
        except:
            pass

class FetchSaveCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global app, ui
            docs = app.documents
            
            if docs.count == 0:
                return # User clicked OK on the warning screen, abort gracefully
            
            mode = current_save_state.get('mode', 'Create New')
            if mode == 'Update Existing':
                ws_name = current_save_state.get('select', '').strip()
            else:
                ws_name = current_save_state.get('name', '').strip()
            
            if not ws_name:
                ui.messageBox('Please provide a valid workspace name.')
                return

            ws_data = []
            
            if 'selectedFiles' in current_save_state:
                selected_files = current_save_state['selectedFiles']
            else:
                # Fallback if JS fails to send the list
                selected_files = [doc.dataFile.name for doc in docs if doc.dataFile]

            for doc in docs:
                df = doc.dataFile
                if df and df.name in selected_files:
                    # Traverse upwards to capture any nested subfolders
                    folders = []
                    folder = df.parentFolder
                    while folder and not folder.isRoot:
                        folders.insert(0, folder.name)
                        folder = folder.parentFolder
                    
                    ws_data.append({
                        "project": df.parentProject.name,
                        "folders": folders,
                        "file": df.name
                    })
            
            if not ws_data:
                ui.messageBox('No documents were selected to save.')
                return

            # Load existing setups, add the new one, and write back
            workspaces = load_workspaces()
            workspaces[ws_name] = ws_data
            save_workspaces(workspaces)
            
            ui.messageBox(f'Workspace "{ws_name}" saved successfully with {len(ws_data)} files!')
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FetchSaveCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global app, ui
            cmd = args.command
            inputs = cmd.commandInputs
            
            html_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'save.html').replace('\\', '/')
            inputs.addBrowserCommandInput('saveBrowser', ' ', html_path, 250, 750)
            
            onExecute = FetchSaveCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
            onHTML = FetchSaveCommandHTMLEventHandler()
            cmd.incomingFromHTML.add(onHTML)
            handlers.append(onHTML)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FetchOpenCommandHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global current_open_state, ui
            if args.action == 'ready':
                workspaces = load_workspaces()
                args.browserCommandInput.sendInfoToHTML('init', json.dumps(workspaces))
            elif args.action == 'update':
                current_open_state = json.loads(args.data)
            elif args.action == 'delete':
                data = json.loads(args.data)
                ws_name = data.get('select')
                if ws_name and ui:
                    result = ui.messageBox(f'Are you sure you want to delete the workspace "{ws_name}"?', 'Confirm Deletion', adsk.core.MessageBoxButtonTypes.YesNoButtonType, adsk.core.MessageBoxIconTypes.WarningIconType)
                    if result == adsk.core.DialogResults.DialogYes:
                        workspaces = load_workspaces()
                        if ws_name in workspaces:
                            del workspaces[ws_name]
                            save_workspaces(workspaces)
                            args.browserCommandInput.sendInfoToHTML('init', json.dumps(workspaces))
        except:
            pass

class FetchOpenCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global app, ui
            
            ws_name = current_open_state.get('select', '').strip()
            if not ws_name:
                return
                
            workspaces = load_workspaces()
            all_files_in_workspace = workspaces.get(ws_name, [])

            if 'selectedFiles' in current_open_state:
                selected_files = current_open_state['selectedFiles']
            else:
                selected_files = [f['file'] for f in all_files_in_workspace]

            files_to_open = [f for f in all_files_in_workspace if f['file'] in selected_files]

            total_files = len(files_to_open)
            if total_files == 0 and len(all_files_in_workspace) > 0:
                ui.messageBox('No files were selected to fetch.')
                return

            if total_files > 0:
                progress = ui.createProgressDialog()
                progress.isCancelButtonShown = False
                progress.isBackgroundDependent = False
                progress.show('Fetching Workspace', 'Working... Please wait.\nOpening design %v of %m', 0, total_files, 0)
                adsk.doEvents()
            
            opened_count = 0
            processed_count = 0
            for f_info in files_to_open:
                if total_files > 0:
                    progress.progressValue = processed_count
                    adsk.doEvents()
                processed_count += 1
                
                proj = None
                for p in app.data.dataProjects:
                    if p.name == f_info["project"]:
                        proj = p
                        break
                if not proj: continue
                
                # Drill down into the specific folder structure
                folder = proj.rootFolder
                valid_path = True
                for f_name in f_info.get("folders", []):
                    folder = folder.dataFolders.itemByName(f_name)
                    if not folder:
                        valid_path = False
                        break
                
                if not valid_path: continue
                
                # Open the file
                df = None
                for f in folder.dataFiles:
                    if f.name == f_info["file"]:
                        df = f
                        break
                
                if df:
                    app.documents.open(df)
                    opened_count += 1
            
            if total_files > 0:
                progress.hide()
            
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FetchOpenCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global ui
            cmd = args.command
            inputs = cmd.commandInputs
            
            html_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'open.html').replace('\\', '/')
            inputs.addBrowserCommandInput('openBrowser', ' ', html_path, 250,750)
            
            onExecute = FetchOpenCommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
            onHTML = FetchOpenCommandHTMLEventHandler()
            cmd.incomingFromHTML.add(onHTML)
            handlers.append(onHTML)
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FetchSaveParamsHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global current_save_params_state, app
            if args.action == 'ready':
                param_sets = load_parameters()
                
                design = adsk.fusion.Design.cast(app.activeProduct)
                open_params = []
                has_docs = False
                if design:
                    has_docs = design.userParameters.count > 0
                    for param in design.userParameters:
                        open_params.append({'name': param.name, 'expression': param.expression})
                        
                info = {
                    'hasDocs': has_docs,
                    'openParams': open_params,
                    'paramSets': param_sets
                }
                args.browserCommandInput.sendInfoToHTML('init', json.dumps(info))
            elif args.action == 'update':
                current_save_params_state = json.loads(args.data)
        except:
            pass

class FetchSaveParamsExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global app, ui
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design:
                return # Handled by HTML warning
            
            mode = current_save_params_state.get('mode', 'Create New')
            if mode == 'Update Existing':
                set_name = current_save_params_state.get('select', '').strip()
            else:
                set_name = current_save_params_state.get('name', '').strip()
            
            if not set_name:
                ui.messageBox('Please provide a valid parameter set name.')
                return

            params_data = []
            
            if 'selectedParams' in current_save_params_state:
                selected_params = current_save_params_state['selectedParams']
            else:
                selected_params = [p.name for p in design.userParameters]
                
            for param in design.userParameters:
                if param.name in selected_params:
                    params_data.append({
                        'name': param.name,
                        'expression': param.expression,
                        'unit': param.unit,
                        'comment': param.comment
                    })
            
            if not params_data:
                ui.messageBox('No user parameters selected to save.')
                return
                
            param_sets = load_parameters()
            param_sets[set_name] = params_data
            save_parameters(param_sets)
            ui.messageBox(f'Saved {len(params_data)} parameters to the "{set_name}" set!')
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FetchSaveParamsCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            
            html_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'saveParams.html').replace('\\', '/')
            inputs.addBrowserCommandInput('saveParamsBrowser', ' ', html_path, 250, 750)
            
            onExecute = FetchSaveParamsExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
            onHTML = FetchSaveParamsHTMLEventHandler()
            cmd.incomingFromHTML.add(onHTML)
            handlers.append(onHTML)
        except:
            pass

class FetchOpenParamsHTMLEventHandler(adsk.core.HTMLEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global current_open_params_state, ui
            if args.action == 'ready':
                param_sets = load_parameters()
                args.browserCommandInput.sendInfoToHTML('init', json.dumps(param_sets))
            elif args.action == 'update':
                current_open_params_state = json.loads(args.data)
            elif args.action == 'delete':
                data = json.loads(args.data)
                set_name = data.get('select')
                if set_name and ui:
                    result = ui.messageBox(f'Are you sure you want to delete the parameter set "{set_name}"?', 'Confirm Deletion', adsk.core.MessageBoxButtonTypes.YesNoButtonType, adsk.core.MessageBoxIconTypes.WarningIconType)
                    if result == adsk.core.DialogResults.DialogYes:
                        param_sets = load_parameters()
                        if set_name in param_sets:
                            del param_sets[set_name]
                            save_parameters(param_sets)
                            args.browserCommandInput.sendInfoToHTML('init', json.dumps(param_sets))
        except:
            pass

class FetchOpenParamsExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global app, ui
            design = adsk.fusion.Design.cast(app.activeProduct)
            if not design: return
                
            set_name = current_open_params_state.get('select', '').strip()
            if not set_name: return
            
            param_sets = load_parameters()
            params_data = param_sets.get(set_name, [])
            
            if 'selectedParams' in current_open_params_state:
                selected_params = current_open_params_state['selectedParams']
            else:
                selected_params = [p['name'] for p in params_data]
            
            added = 0
            updated = 0
            for p in params_data:
                if p['name'] in selected_params:
                    existing = design.userParameters.itemByName(p['name'])
                    if existing:
                        # If it exists, just update the expression and comment
                        existing.expression = p['expression']
                        existing.comment = p['comment']
                        updated += 1
                    else:
                        # If it doesn't exist, create it from scratch
                        design.userParameters.add(p['name'], adsk.core.ValueInput.createByString(p['expression']), p['unit'], p['comment'])
                        added += 1
            
            if added == 0 and updated == 0:
                ui.messageBox('No user parameters were selected to fetch.')
                return
                    
            ui.messageBox(f'Injected "{set_name}" into active design.\n\nAdded: {added}\nUpdated: {updated}')
        except:
            if ui:
                ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class FetchOpenParamsCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            
            html_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'openParams.html').replace('\\', '/')
            inputs.addBrowserCommandInput('openParamsBrowser', ' ', html_path, 250, 750)
                
            onExecute = FetchOpenParamsExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute)
            
            onHTML = FetchOpenParamsHTMLEventHandler()
            cmd.incomingFromHTML.add(onHTML)
            handlers.append(onHTML)
        except:
            pass

def run(context):
    global ui, app
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # Get the Add-Ins toolbar panel in the Design workspace
        workSpace = ui.workspaces.itemById('FusionSolidEnvironment')
        tbPanels = workSpace.toolbarPanels
        tbPanel = tbPanels.itemById('SolidScriptsAddinsPanel')

        # Create the Save Workspace button definition
        saveCmdDef = ui.commandDefinitions.itemById('fetchSaveCmd')
        if not saveCmdDef:
            saveCmdDef = ui.commandDefinitions.addButtonDefinition('fetchSaveCmd', 'Save Workspace', 'Save currently open files as a workspace.', './resources/saveWorkspace')
            saveCmdDef.tooltipDescription = 'Automatically grabs all open files and saves them to a named workspace list for quick access later.'
            # Set tooltip image
            tool_clip_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'saveWorkspace', 'tooltip.png')
            if os.path.exists(tool_clip_path):
                saveCmdDef.toolClipFilename = tool_clip_path
        saveCreated = FetchSaveCommandCreatedEventHandler()
        saveCmdDef.commandCreated.add(saveCreated)
        handlers.append(saveCreated)
        # Add the command to the panel.
        tbPanel.controls.addCommand(saveCmdDef)

        # Create the Open Workspace button definition
        openCmdDef = ui.commandDefinitions.itemById('fetchOpenCmd')
        if not openCmdDef:
            openCmdDef = ui.commandDefinitions.addButtonDefinition('fetchOpenCmd', 'Fetch Workspace!', 'Open a previously saved workspace.', './resources/openWorkspace')
            openCmdDef.tooltipDescription = 'Select a saved workspace to instantly reopen all associated files.\n\nGreat for picking up right where you left off!'
            # Set tooltip image
            tool_clip_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'openWorkspace', 'tooltip.png')
            if os.path.exists(tool_clip_path):
                openCmdDef.toolClipFilename = tool_clip_path
        openCreated = FetchOpenCommandCreatedEventHandler()
        openCmdDef.commandCreated.add(openCreated)
        handlers.append(openCreated)
        # Add the command to the panel and promote it.
        openCtrl = tbPanel.controls.addCommand(openCmdDef)
        openCtrl.isPromoted = True
        
        # Create the Save Parameters button definition
        saveParamsCmdDef = ui.commandDefinitions.itemById('fetchSaveParamsCmd')
        if not saveParamsCmdDef:
            saveParamsCmdDef = ui.commandDefinitions.addButtonDefinition('fetchSaveParamsCmd', 'Save Parameters', 'Save current user parameters to a set.', './resources/saveParams')
            saveParamsCmdDef.tooltipDescription = 'Extracts all user parameters from the active design and stores them in a reusable parameter set.'
            # Set tooltip image
            tool_clip_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'saveParams', 'tooltip.png')
            if os.path.exists(tool_clip_path):
                saveParamsCmdDef.toolClipFilename = tool_clip_path
        saveParamsCreated = FetchSaveParamsCreatedEventHandler()
        saveParamsCmdDef.commandCreated.add(saveParamsCreated)
        handlers.append(saveParamsCreated)
        # Add the command to the panel.
        tbPanel.controls.addCommand(saveParamsCmdDef)

        # Create the Fetch Parameters button definition
        openParamsCmdDef = ui.commandDefinitions.itemById('fetchOpenParamsCmd')
        if not openParamsCmdDef:
            openParamsCmdDef = ui.commandDefinitions.addButtonDefinition('fetchOpenParamsCmd', 'Fetch Parameters', 'Inject saved parameters into the active design.', './resources/openParams')
            openParamsCmdDef.tooltipDescription = 'Injects a previously saved set of user parameters into your current design.\n\nUpdates existing parameters or creates new ones from scratch.'
            # Set tooltip image
            tool_clip_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources', 'openParams', 'tooltip.png')
            if os.path.exists(tool_clip_path):
                openParamsCmdDef.toolClipFilename = tool_clip_path
        openParamsCreated = FetchOpenParamsCreatedEventHandler()
        openParamsCmdDef.commandCreated.add(openParamsCreated)
        handlers.append(openParamsCreated)
        # Add the command to the panel and promote it.
        openParamsCtrl = tbPanel.controls.addCommand(openParamsCmdDef)
        openParamsCtrl.isPromoted = True

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        # Clean up the UI buttons and definitions so they don't stick around after stopping the Add-in
        workSpace = ui.workspaces.itemById('FusionSolidEnvironment')
        tbPanels = workSpace.toolbarPanels
        tbPanel = tbPanels.itemById('SolidScriptsAddinsPanel')
            
        for cmdId in ['fetchSaveCmd', 'fetchOpenCmd', 'fetchSaveParamsCmd', 'fetchOpenParamsCmd']:
            control = tbPanel.controls.itemById(cmdId)
            if control: control.deleteMe()

            cmdDef = ui.commandDefinitions.itemById(cmdId)
            if cmdDef: cmdDef.deleteMe()
            
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))