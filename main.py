# nvda translation helper
# built by ömer Yılmaz
# allows usage of l10nUtil.exe through a gui interface

import wx
import os
import subprocess
import json
import threading

# Persistent configuration
CONFIG_PATH = os.path.expanduser('~/.nvda_config.json')


def load_config():
    """
    Load persistent configuration for language_code.
    Returns a dict with key: language_code.
    If the config file does not exist or is invalid, returns defaults.
    """
    if not os.path.exists(CONFIG_PATH):
        return {'language_code': None}
    try:
        with open(CONFIG_PATH, 'r') as f:
            data = json.load(f)
            # Normalize missing keys
            return {
                'language_code': data.get('language_code')
            }
    except Exception:
        return {'language_code': None}


def save_config(language_code=None):
    """
    Persist language_code to the configuration file.
    Only writes provided fields; preserves existing values if not provided.
    """
    cfg = load_config() # load_config now only loads language_code
    if language_code is not None:
        cfg['language_code'] = language_code
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(cfg, f)
    except Exception:
        # Best-effort persistence; ignore write failures
        pass

def set_control_accessible_name(control, name):
    """
    Sets the accessible name for a wxPython control.
    This is a helper function to improve screen reader accessibility.
    """
    if hasattr(control, 'SetLabel'): # For controls like StaticText
        control.SetLabel(name)
    else: # For other controls like TextCtrl
        control.SetName(name)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='NVDA Translation Helper')
        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Read-only multi-line output box for l10nUtil.exe
        self.output_box = wx.TextCtrl(self.panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH | wx.HSCROLL)
        self.output_box.SetMinSize((-1, 120))
        self._output_lock = threading.Lock()

        # Expose a small helper to append text safely from other threads
        self._append_text = self._safe_append_text

        # Ensure we layout the new widget
        # Create a StaticBox to serve as the label and container for accessibility
        output_static_box = wx.StaticBox(self.panel, label='l10nUtil.exe Output:')
        output_box_sizer = wx.StaticBoxSizer(output_static_box, wx.VERTICAL)
        output_box_sizer.Add(self.output_box, 1, wx.EXPAND | wx.ALL, 5)
        set_control_accessible_name(self.output_box, "Application status and processing messages.")

        self.main_sizer.Add(output_box_sizer, 0, wx.EXPAND | wx.ALL, 5)
        # Load existing config and apply if present
        self.config = load_config()

        # --- Language Input ---
        lang_label = wx.StaticText(self.panel, label='Language Code (e.g., tr):')
        self.lang_input = wx.TextCtrl(self.panel)

        crowdin_file_label = wx.StaticText(self.panel, label='Crowdin File Name:')
        crowdin_files = ['nvda.po', 'userGuide.xliff', 'changes.xliff', 'Custom']
        self.crowdin_file_choice = wx.ComboBox(self.panel, choices=crowdin_files, style=wx.CB_READONLY)
        self.crowdin_file_choice.SetSelection(0)
        self.crowdin_file_choice.Bind(wx.EVT_COMBOBOX, self.on_crowdin_file_select)

        self.custom_crowdin_file_label = wx.StaticText(self.panel, label='Custom File Name:')
        self.custom_crowdin_file_input = wx.TextCtrl(self.panel)
        self.custom_crowdin_file_label.Hide()
        self.custom_crowdin_file_input.Hide()

        local_file_label = wx.StaticText(self.panel, label='Local File Path:')
        self.local_file_input = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        browse_button = wx.Button(self.panel, label='Browse for processing...')
        browse_button.Bind(wx.EVT_BUTTON, self.on_browse)

        self.download_button = wx.Button(self.panel, label='Download')
        self.upload_button = wx.Button(self.panel, label='Upload')
        self.download_button.Bind(wx.EVT_BUTTON, self.on_download)
        self.upload_button.Bind(wx.EVT_BUTTON, self.on_upload)

        preview_label = wx.StaticText(self.panel, label='Preview XLIFF as HTML')
        doc_types = ['userGuide', 'changes', 'keyCommands']
        self.doc_type_choice = wx.Choice(self.panel, choices=doc_types)
        self.doc_type_choice.SetSelection(0)
        self.convert_button = wx.Button(self.panel, label='Convert to HTML')
        self.convert_button.Bind(wx.EVT_BUTTON, self.on_convert)

        lang_sizer = wx.BoxSizer(wx.HORIZONTAL)
        lang_sizer.Add(lang_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        lang_sizer.Add(self.lang_input, 1, wx.ALL | wx.EXPAND, 5)

        crowdin_file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        crowdin_file_sizer.Add(crowdin_file_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        crowdin_file_sizer.Add(self.crowdin_file_choice, 1, wx.ALL | wx.EXPAND, 5)

        self.custom_crowdin_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.custom_crowdin_sizer.Add(self.custom_crowdin_file_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        self.custom_crowdin_sizer.Add(self.custom_crowdin_file_input, 1, wx.ALL | wx.EXPAND, 5)

        local_file_sizer = wx.BoxSizer(wx.HORIZONTAL)
        local_file_sizer.Add(local_file_label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
        local_file_sizer.Add(self.local_file_input, 1, wx.ALL | wx.EXPAND, 5)
        local_file_sizer.Add(browse_button, 0, wx.ALL, 5)

        action_button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_button_sizer.Add(self.download_button, 1, wx.ALL | wx.EXPAND, 5)
        action_button_sizer.Add(self.upload_button, 1, wx.ALL | wx.EXPAND, 5)

        preview_sizer = wx.BoxSizer(wx.HORIZONTAL)
        preview_sizer.Add(self.doc_type_choice, 1, wx.ALL | wx.EXPAND, 5)
        preview_sizer.Add(self.convert_button, 1, wx.ALL | wx.EXPAND, 5)

        self.main_sizer.Add(lang_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(crowdin_file_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(self.custom_crowdin_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(local_file_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(action_button_sizer, 0, wx.EXPAND)
        self.main_sizer.Add(wx.StaticLine(self.panel), 0, wx.ALL|wx.EXPAND, 5)
        self.main_sizer.Add(preview_label, 0, wx.ALL, 5)
        self.main_sizer.Add(preview_sizer, 0, wx.EXPAND)

        self.panel.SetSizer(self.main_sizer)
        self.Fit()
        self.Show()

        # If a language code exists in config, prepopulate the input
        if self.config.get('language_code'):
            self.lang_input.SetValue(self.config['language_code'])

    def _safe_append_text(self, text):
        """Thread-safe method to append text to the output box."""
        # Ensure GUI updates happen on the main thread
        wx.CallAfter(self.output_box.AppendText, text)

    def _show_command_result_message(self, command_type, success, filename=None):
        """Displays a message box on the main thread based on command result."""
        if success:
            if command_type == 'download':
                message = f'Successfully downloaded {filename}'
            elif command_type == 'upload':
                message = f'Successfully uploaded {filename}'
            elif command_type == 'convert':
                message = f'Successfully converted to {filename}'
            title = 'Success'
            style = wx.OK | wx.ICON_INFORMATION
        else:
            message = f'{command_type.capitalize()} operation failed.'
            title = 'Error'
            style = wx.OK | wx.ICON_ERROR
        wx.MessageBox(message, title, style)

    def _set_buttons_enabled(self, enable):
        """Enables or disables relevant action buttons."""
        wx.CallAfter(self.download_button.Enable, enable)
        wx.CallAfter(self.upload_button.Enable, enable)
        wx.CallAfter(self.convert_button.Enable, enable)

    def run_l10n_util_threaded(self, command_args):
        """
        Runs l10nUtil.exe in a separate thread and streams its output to the GUI.
        """
        self._set_buttons_enabled(False) # Disable buttons before starting thread

        l10n_util_path = self.get_l10n_util_path()
        if not l10n_util_path:
            self._safe_append_text('Error: l10nUtil.exe not found.\n')
            wx.CallAfter(wx.MessageBox, 'l10nUtil.exe not found. Please ensure NVDA is installed or place the helper in the NVDA folder.', 'Error', wx.OK | wx.ICON_ERROR)
            return False

        full_command = f'"{l10n_util_path}" {command_args}'
        self._safe_append_text(f"Running command: {full_command}\n")
        self._safe_append_text("Please wait for the command to finish...\n")

        def _run_in_thread():
            try:
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                
                process = subprocess.Popen(
                    full_command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, # Merge stderr into stdout
                    text=True, # Decode stdout/stderr as text
                    shell=True, # Use shell to handle command parsing
                    startupinfo=startupinfo
                )

                # Stream output line by line
                for line in iter(process.stdout.readline, ''):
                    self._safe_append_text(line)
                process.stdout.close()
                return_code = process.wait()

                success = (return_code == 0)
                if success:
                    self._safe_append_text("\nCommand finished successfully.\n")
                else:
                    self._safe_append_text(f"\nCommand failed with exit code {return_code}.\n")

                # Determine command type and filename for the message box
                cmd_type = "unknown"
                file_name = None
                if "downloadTranslationFile" in full_command:
                    cmd_type = "download"
                    # Extract filename from command_args, assuming it's the last quoted argument
                    parts = command_args.split('"')
                    if len(parts) > 1:
                        file_name = parts[-2]
                elif "uploadTranslationFile" in full_command:
                    cmd_type = "upload"
                    # Extract local file from command_args
                    parts = command_args.split('"')
                    if len(parts) > 3: # Assuming uploadTranslationFile lang "crowdin_file" "local_file"
                        file_name = parts[-2]
                elif "xliff2html" in full_command:
                    cmd_type = "convert"
                    # Extract output html file from command_args
                    parts = command_args.split('"')
                    if len(parts) > 1: # Assuming xliff2html -t docType "xliff_file" "output_html"
                        file_name = parts[-2]

                wx.CallAfter(self._show_command_result_message, cmd_type, success, file_name)

            except Exception as e:
                self._safe_append_text(f"\nAn error occurred while running the command: {e}\n")
                wx.CallAfter(self._show_command_result_message, "general", False)
            finally:
                self._set_buttons_enabled(True) # Re-enable buttons after thread finishes

        threading.Thread(target=_run_in_thread, daemon=True).start()
        return True

    def get_l10n_util_path(self):
        import platform
        bitness = platform.architecture()[0]

        program_files_x86 = os.environ.get('ProgramFiles(x86)')
        program_files = os.environ.get('ProgramFiles')

        possible_paths = []

        # Prioritize local directory for l10nUtil.exe if it's placed there
        possible_paths.append('l10nUtil.exe')

        # Add Program Files (x86) path for NVDA on 64-bit systems
        if bitness == '64bit' and program_files_x86:
            possible_paths.append(os.path.join(program_files_x86, 'NVDA', 'l10nUtil.exe'))
        # Add Program Files path for NVDA on 32-bit systems or if NVDA is installed in Program Files on 64-bit
        if program_files:
            possible_paths.append(os.path.join(program_files, 'NVDA', 'l10nUtil.exe'))
        
        # Fallback to common 32-bit path if ProgramFiles(x86) not found but it's a 32-bit system
        if bitness == '32bit' and not program_files_x86:
            # This handles cases where 'Program Files (x86)' might not be an env var but the dir exists
            # or on true 32-bit systems where Program Files is the 32-bit one.
            possible_paths.append('C:\\Program Files\\NVDA\\l10nUtil.exe')
            
        # Add the specific path for 32-bit systems if it's not already covered
        if bitness == '32bit' and program_files_x86: # This might be redundant with the above, but good for explicit coverage.
            possible_paths.append('C:\\Program Files (x86)\\NVDA\\l10nUtil.exe')
            
        # Remove duplicates and check existence
        for path in list(dict.fromkeys(possible_paths)): # Use dict.fromkeys to preserve order and remove duplicates
            if os.path.exists(path):
                return path
        return None

    def check_and_get_api_token(self):
        token_path = os.path.expanduser('~/.nvda_crowdin')
        if not os.path.exists(token_path):
            message = (
                "Crowdin API Token not found.\n\n"
                "Please create a Personal Access Token on your Crowdin Account Settings -> API page.\n"
                "Paste your token below:"
            )
            with wx.TextEntryDialog(self, message, "Enter Crowdin API Token") as dlg:
                if dlg.ShowModal() == wx.ID_OK:
                    token = dlg.GetValue()
                    if token:
                        try:
                            with open(token_path, 'w') as f:
                                f.write(token)
                            # Persist token and current language code
                            save_config(language_code=self.lang_input.GetValue())
                            return True
                        except IOError as e:
                            wx.MessageBox(f"Could not save API token file:\n{e}", "Error", wx.OK | wx.ICON_ERROR)
                            return False
                # User pressed Cancel or entered nothing.
                return False
        else:
            # Token exists; persist current language code
            save_config(language_code=self.lang_input.GetValue())
        return True

    def on_crowdin_file_select(self, event):
        is_custom = self.crowdin_file_choice.GetValue() == 'Custom'
        self.custom_crowdin_file_label.Show(is_custom)
        self.custom_crowdin_file_input.Show(is_custom)
        self.panel.Layout()
        self.Fit()

    def get_crowdin_file(self):
        if self.crowdin_file_choice.GetValue() == 'Custom':
            return self.custom_crowdin_file_input.GetValue()
        return self.crowdin_file_choice.GetValue()

    def on_browse(self, event):
        with wx.FileDialog(self, "Open file", wildcard="All files (*.*)|*.*",
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            self.local_file_input.SetValue(fileDialog.GetPath())

    def on_download(self, event):
        lang = self.lang_input.GetValue()
        crowdin_file = self.get_crowdin_file()
        if not lang or not crowdin_file:
            wx.MessageBox('Please enter a language code and either choose or enter a custom file name.', 'Error', wx.OK | wx.ICON_ERROR)
            return
        command_args = f'downloadTranslationFile {lang} "{crowdin_file}"'
        self.run_command(command_args) # Message box handled by thread callback
        # Persist language
        save_config(language_code=lang)

    def on_upload(self, event):
        lang = self.lang_input.GetValue()
        local_file = self.local_file_input.GetValue()
        crowdin_file = self.get_crowdin_file()
        if not lang or not local_file or not crowdin_file:
            wx.MessageBox('Please enter a language, choose a Crowdin file name, and select a local file.', 'Error', wx.OK | wx.ICON_ERROR)
            return
        command_args = f'uploadTranslationFile {lang} "{crowdin_file}" "{local_file}"'
        self.run_command(command_args) # Message box handled by thread callback
        # Persist language
        save_config(language_code=lang)

    def on_convert(self, event):
        doc_type = self.doc_type_choice.GetString(self.doc_type_choice.GetSelection())
        xliff_file = self.local_file_input.GetValue()
        if not xliff_file:
            wx.MessageBox('Please browse for an .xliff file to convert.', 'Error', wx.OK | wx.ICON_ERROR)
            return
        base_name = os.path.basename(xliff_file)
        name_without_ext = os.path.splitext(base_name)[0]
        output_html = f"{name_without_ext}.html"
        command_args = f'xliff2html -t {doc_type} "{xliff_file}" "{output_html}"'
        self.run_command(command_args) # Message box handled by thread callback

    def run_command(self, command_args):
        if not self.check_and_get_api_token():
            wx.MessageBox("Crowdin API Token is required to proceed.", "Operation Canceled", wx.OK | wx.ICON_WARNING)
            return False
        
        # Now use the threaded runner for l10nUtil.exe
        return self.run_l10n_util_threaded(command_args)

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()