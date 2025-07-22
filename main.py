# nvda translation helper
# built by ömer Yılmaz
# allows usage of l10nUtil.exe through a gui interface

import wx
import os
import subprocess

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='NVDA Translation Helper')

        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

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

        download_button = wx.Button(self.panel, label='Download')
        upload_button = wx.Button(self.panel, label='Upload')
        download_button.Bind(wx.EVT_BUTTON, self.on_download)
        upload_button.Bind(wx.EVT_BUTTON, self.on_upload)

        preview_label = wx.StaticText(self.panel, label='Preview XLIFF as HTML')
        doc_types = ['userGuide', 'changes', 'keyCommands']
        self.doc_type_choice = wx.Choice(self.panel, choices=doc_types)
        self.doc_type_choice.SetSelection(0)
        convert_button = wx.Button(self.panel, label='Convert to HTML')
        convert_button.Bind(wx.EVT_BUTTON, self.on_convert)

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
        action_button_sizer.Add(download_button, 1, wx.ALL | wx.EXPAND, 5)
        action_button_sizer.Add(upload_button, 1, wx.ALL | wx.EXPAND, 5)

        preview_sizer = wx.BoxSizer(wx.HORIZONTAL)
        preview_sizer.Add(self.doc_type_choice, 1, wx.ALL | wx.EXPAND, 5)
        preview_sizer.Add(convert_button, 1, wx.ALL | wx.EXPAND, 5)

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

    def get_l10n_util_path(self):
        possible_paths = [
            'C:\\Program Files (x86)\\NVDA\\l10nUtil.exe',
            'l10nUtil.exe'
        ]
        for path in possible_paths:
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
                            return True
                        except IOError as e:
                            wx.MessageBox(f"Could not save API token file:\n{e}", "Error", wx.OK | wx.ICON_ERROR)
                            return False
                # User pressed Cancel or entered nothing.
                return False
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
        if self.run_command(command_args):
            wx.MessageBox(f'Successfully downloaded {crowdin_file}', 'Success', wx.OK | wx.ICON_INFORMATION)

    def on_upload(self, event):
        lang = self.lang_input.GetValue()
        local_file = self.local_file_input.GetValue()
        crowdin_file = self.get_crowdin_file()
        if not lang or not local_file or not crowdin_file:
            wx.MessageBox('Please enter a language, choose a Crowdin file name, and select a local file.', 'Error', wx.OK | wx.ICON_ERROR)
            return
        command_args = f'uploadTranslationFile {lang} "{crowdin_file}" "{local_file}"'
        if self.run_command(command_args):
            wx.MessageBox(f'Successfully uploaded {local_file}', 'Success', wx.OK | wx.ICON_INFORMATION)

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
        if self.run_command(command_args):
            wx.MessageBox(f'Successfully converted to {output_html}', 'Success', wx.OK | wx.ICON_INFORMATION)

    def run_command(self, command_args):
        if not self.check_and_get_api_token():
            wx.MessageBox("Crowdin API Token is required to proceed.", "Operation Canceled", wx.OK | wx.ICON_WARNING)
            return False

        l10n_util_path = self.get_l10n_util_path()
        if not l10n_util_path:
            wx.MessageBox('l10nUtil.exe not found. Please ensure NVDA is installed or place the helper in the NVDA folder.', 'Error', wx.OK | wx.ICON_ERROR)
            return False

        full_command = f'"{l10n_util_path}" {command_args}'
        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(full_command, check=True, text=True, capture_output=True, startupinfo=startupinfo, shell=True)
            return True
        except subprocess.CalledProcessError as e:
            wx.MessageBox(f'An error occurred:\n\n{e.stderr}', 'Error', wx.OK | wx.ICON_ERROR)
            return False

if __name__ == '__main__':
    app = wx.App(False)
    frame = MainFrame()
    app.MainLoop()