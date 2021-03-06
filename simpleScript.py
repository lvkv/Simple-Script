# Simple Script
# Lukas Velikov
#
# Simple Script is a GUI app designed to make quick and simple mass file renames and relocations possible to clients
# without scripting experience. Built using Python's Tkinter package.

from tkinter import *  # Python 3.x
from tkinter import filedialog
from tkinter.ttk import *
import webbrowser
import shutil  # In case of moving files between drives
import os

class SimpleScript:
    TAB_NAMES = ['Rename Files', 'Move Files', 'About']
    FRAME_WIDTH = 400
    FRAME_HEIGHT = 250

    successful_rename = 'File/directory rename successful.'
    successful_move = 'File/directory relocation successful.'

    error_unexpected = 'Unexpected error occurred: '
    error_renamed_exists = 'Renamed file already exists: '
    error_moved_exists = 'Moved file already exists: '
    error_none_renamed = 'No files and/or directories were renamed'
    error_none_moved = 'No files were moved'
    error_dir_not_exist = 'Directory not found: '

    def __init__(self, master):
        master.title('Simple Script')
        master.resizable(0, 0)

        # Entry validation
        self.previous_bad_validation = False
        self.bad_chars = ['\\', '/', '¦', '*', '?', '"', '<', '>', '|']
        vcmd = (master.register(self.on_validate), '%S')

        # Initializing tabs and adding frames
        tabs = Notebook(master)
        rename_tab = Frame(width=self.FRAME_WIDTH, height=self.FRAME_HEIGHT)
        tabs.add(rename_tab, text=self.TAB_NAMES[0])
        move_tab = Frame(width=self.FRAME_WIDTH, height=self.FRAME_HEIGHT)
        tabs.add(move_tab, text=self.TAB_NAMES[1])
        about_tab = Frame(width=self.FRAME_WIDTH, height=self.FRAME_HEIGHT)
        tabs.add(about_tab, text=self.TAB_NAMES[2])
        tabs.bind_all('<<NotebookTabChanged>>', self.cycle_frame_text)
        tabs.grid()

        # "Rename Files" Tab - Variables
        self.completed_items = [False, False, True]  # choose dir, replace this, >=1 checkbox (one is already checked)
        self.dir_path = StringVar()
        self.replace_this = StringVar()
        self.with_this = StringVar()
        self.replace_this.set('')
        self.with_this.set('')
        self.rename_files = BooleanVar()
        self.rename_files.set(False)
        self.rename_subfiles = BooleanVar()
        self.rename_subfiles.set(False)
        self.rename_dirs = BooleanVar()
        self.rename_dirs.set(False)
        self.rename_subdirs = BooleanVar()
        self.rename_subdirs.set(False)

        # "Move Files" Tab - Variables
        self.completed_move_items = [False, False, True, False]  # choose source, destination, radio buttons, entry
        self.dir_path_move = StringVar()
        self.dir_path_move_to = StringVar()
        self.pre_suf_cont = IntVar()
        self.start_end_contain = StringVar()

        # "About" Tab
        self.label_credit = Label(about_tab, text='Lukas Velikov 2016\ngithub.com/lvkv')
        self.label_credit.config(foreground='grey', cursor='hand2')
        self.label_credit.bind('<Button-1>', self.open_github)
        self.label_credit.grid(padx=((self.FRAME_WIDTH/2)-50, 0), pady=((self.FRAME_HEIGHT/2)-20, 0))

        # "Rename Files" Tab - Creating GUI elements
        button_dir = Button(rename_tab, text='Choose Directory')
        self.rename_frame = LabelFrame(rename_tab, text='Find and Replace')
        self.label_txt_warn = Label(self.rename_frame,
                                    text='''File/directory names cannot contain:  \  /  ¦  *  ?  "  <  >  |''')
        self.label_txt_warn.config(foreground='red')
        self.label_blank = Label(self.rename_frame, text=' ')
        label_1 = Label(self.rename_frame, text='  Replace this:  ')
        label_2 = Label(self.rename_frame, text='  With this:  ')
        self.entry_replace_this = Entry(self.rename_frame, width=50, validate='key', validatecommand=vcmd)
        self.entry_with_this = Entry(self.rename_frame, width=50, validate='key', validatecommand=vcmd)
        self.rename_options_frame = LabelFrame(rename_tab, text='Options')
        self.checkbox_files = Checkbutton(self.rename_options_frame,
                                          text='Rename files',
                                          onvalue=True,
                                          offvalue=False,
                                          variable=self.rename_files)
        self.checkbox_subfiles = Checkbutton(self.rename_options_frame,
                                             text='Rename subdirectory files',
                                             onvalue=True,
                                             offvalue=False,
                                             variable=self.rename_subfiles)
        self.checkbox_dirs = Checkbutton(self.rename_options_frame,
                                         text='Rename directories',
                                         onvalue=True,
                                         offvalue=False,
                                         variable=self.rename_dirs)
        self.checkbox_subdirs = Checkbutton(self.rename_options_frame,
                                            text='Rename subdirectories',
                                            onvalue=True,
                                            offvalue=False,
                                            variable=self.rename_subdirs)

        self.source_rename_text = StringVar(value='')
        self.frame_rename_run = LabelFrame(rename_tab, text='Info and Run')
        self.label_entry_len = 32
        self.label_dir = Entry(self.frame_rename_run, textvariable=self.source_rename_text, width=self.label_entry_len,
                               state='readonly')
        self.scroll_dir_name = Scrollbar(self.frame_rename_run, orient=HORIZONTAL, command=self.label_dir.xview)
        self.label_dir.config(xscrollcommand=self.scroll_dir_name.set)
        self.button_run_rename = Button(self.frame_rename_run, text='Run', state=DISABLED)

        # "Move Files" Tab - Creating GUI elements
        self.choose_move_dir_frame = LabelFrame(move_tab, text='Choose Directories')
        self.button_dir_move = Button(self.choose_move_dir_frame, text='Choose Source Directory')
        self.button_dir_move_to = Button(self.choose_move_dir_frame, text='Choose Destination Directory')
        self.prefix_suffix_frame = LabelFrame(move_tab, text='Move files with names that...')
        self.radio_starts_with = Radiobutton(self.prefix_suffix_frame, text='Start with ', variable=self.pre_suf_cont,
                                             value=0)
        self.radio_ends_with = Radiobutton(self.prefix_suffix_frame, text='End with ', variable=self.pre_suf_cont,
                                           value=1)
        self.radio_contains = Radiobutton(self.prefix_suffix_frame, text='Contain ', variable=self.pre_suf_cont,
                                          value=2)
        self.label_move_blank = Label(self.prefix_suffix_frame, text='')
        self.label_txt_warn_move = Label(self.prefix_suffix_frame,
                                         text='''File/directory names cannot contain:  \  /  ¦  *  ?  "  <  >  |''')
        self.label_txt_warn_move.config(foreground='red')
        self.entry_pre_suf_cont = Entry(self.prefix_suffix_frame, width=62, validate='key', validatecommand=vcmd)
        self.source_text = 'Source: '
        self.dest_text = 'Destination: '
        self.label_source = Label(move_tab, text=self.source_text + 'None Selected')
        self.label_dest = Label(move_tab, text=self.dest_text + 'None Selected')
        self.button_run_move = Button(move_tab, text='Run', state=DISABLED)

        # "Rename Files" Tab - Binding functions
        button_dir.bind('<Button-1>', self.choose_dir)
        self.button_run_rename.bind('<Button-1>', self.run_rename)
        self.entry_replace_this.bind('<KeyRelease>', self.update_replace_this)
        self.entry_with_this.bind('<KeyRelease>', self.update_with_this)
        self.checkbox_files.bind('<ButtonRelease-1>', self.set_rename_files)
        self.checkbox_subfiles.bind('<ButtonRelease-1>', self.set_rename_subfiles)
        self.checkbox_dirs.bind('<ButtonRelease-1>', self.set_rename_dirs)
        self.checkbox_subdirs.bind('<ButtonRelease-1>', self.set_rename_subdirs)

        # "Move Files" Tab - Binding functions
        self.button_dir_move.bind('<Button-1>', self.choose_dir_move)
        self.button_dir_move_to.bind('<Button-1>', self.choose_dir_move_destination)
        self.entry_pre_suf_cont.bind('<KeyRelease>', self.update_pre_suf_cont)
        self.button_run_move.bind('<Button-1>', self.run_move)

        # "Rename Files" Tab - Gridding GUI elements
        button_dir.grid(columnspan=2, pady=(10, 2))
        self.rename_frame.grid(columnspan=2, padx=(5, 5))
        self.label_txt_warn.grid(columnspan=2, row=1, pady=(0, 5), sticky=S)
        self.label_txt_warn.grid_remove()  # label_txtWarn is only visible when an illegal character is entered
        self.label_blank.grid(columnspan=2, row=1, pady=(0, 5), sticky=S)
        label_1.grid(row=2, sticky=E, pady=(0, 10))
        label_2.grid(row=3, sticky=E, pady=(0, 20))
        self.entry_replace_this.grid(row=2, column=1, pady=(0, 10))
        self.entry_with_this.grid(row=3, column=1, pady=(0, 20))
        self.rename_options_frame.grid(row=3, column=0, padx=(5, 0), pady=(0, 5), sticky=W)
        self.checkbox_files.grid(row=4, column=0, sticky=W)
        self.checkbox_subfiles.grid(row=5, column=0, sticky=W)
        self.checkbox_dirs.grid(row=6, column=0, sticky=W)
        self.checkbox_subdirs.grid(row=7, column=0, sticky=W)
        self.frame_rename_run.grid(column=1, row=3, sticky=W)
        self.label_dir.grid(column=1, row=3, padx=(5, 5), sticky='ew')
        self.label_dir.grid_remove()
        self.scroll_dir_name.grid(column=1, row=4, sticky='ew')
        self.scroll_dir_name.grid_remove()
        self.button_run_rename.grid(column=1, row=5, padx=(5, 5), pady=(5, 5), sticky='ew')

        # "Move Files" Tab - Gridding GUI elements
        self.choose_move_dir_frame.grid(row=0, pady=(10, 5))
        self.button_dir_move.grid(column=0, row=0, padx=(5, 0), pady=(10, 5))
        self.button_dir_move_to.grid(column=1, row=0, padx=(5, 5), pady=(10, 5))
        self.prefix_suffix_frame.grid(column=0, row=1, padx=(5, 5))
        self.radio_starts_with.grid(row=0, column=0, pady=(5, 0))
        self.radio_ends_with.grid(row=0, column=1)
        self.radio_contains.grid(row=0, column=2)
        self.label_txt_warn_move.grid(row=1, columnspan=3)
        self.label_txt_warn_move.grid_remove()
        self.label_move_blank.grid(row=1, columnspan=3)
        self.entry_pre_suf_cont.grid(row=2, columnspan=3, padx=(5, 5), pady=(0, 10))
        self.label_source.grid(row=3, pady=(5, 5))
        self.label_dest.grid(row=4)
        self.button_run_move.grid(row=5, pady=(10, 5))

        # Text on bottom of window
        self.label = Label(master, text='')
        self.label.grid()

    def open_github(self, event):
        webbrowser.open('https://github.com/lvkv')

    def check_for_completion(self):  # Toggles "Rename Files" run button state after checking for a complete form
        for item in self.completed_items:
            if not item:
                self.button_run_rename.config(state=DISABLED)
                return
        self.button_run_rename.config(state='normal')

    def check_for_move_complete(self):  # Toggles "Move Files" run button state after checking for a complete form
        for item in self.completed_move_items:
            if not item:
                self.button_run_move.config(state=DISABLED)
                return
        self.button_run_move.config(state='normal')

    def set_rename_files(self, event):
        self.rename_files.set(not self.rename_files.get())
        self.checkbox_complete(event)
        self.rename_files.set(not self.rename_files.get())

    def set_rename_subfiles(self, event):
        self.rename_subfiles.set(not self.rename_subfiles.get())
        self.checkbox_complete(event)
        self.rename_subfiles.set(not self.rename_subfiles.get())

    def set_rename_dirs(self, event):
        self.rename_dirs.set(not self.rename_dirs.get())
        self.checkbox_complete(event)
        self.rename_dirs.set(not self.rename_dirs.get())

    def set_rename_subdirs(self, event):
        self.rename_subdirs.set(not self.rename_subdirs.get())
        self.checkbox_complete(event)
        self.rename_subdirs.set(not self.rename_subdirs.get())

    def checkbox_complete(self, event):  # Acknowledges the checkbox portion of the "Rename Files" tab as done or not
        if self.rename_files.get() or self.rename_dirs.get() or self.rename_subfiles.get() or self.rename_subdirs.get():
            self.completed_items[2] = True
        else:
            self.completed_items[2] = False
        self.check_for_completion()

    def choose_dir(self, event):  # User chooses "Rename Files" directory
        temp_dir = filedialog.askdirectory()
        if temp_dir != '':
            self.dir_path.set(temp_dir)
            self.update_rename_source(temp_dir)
            self.completed_items[0] = True
        else:
            self.completed_items[0] = False
        self.check_for_completion()

    def choose_dir_move(self, event):  # User chooses source directory when in "Move Files"
        temp_dir = filedialog.askdirectory()
        if temp_dir != '':
            self.dir_path_move.set(temp_dir)
            self.update_move_source(temp_dir)
            self.completed_move_items[0] = True
        else:
            self.completed_move_items[0] = False
        self.check_for_move_complete()

    def update_move_source(self, text):
        self.label_source.config(text=self.source_text + text)

    def update_move_dest(self, text):
        self.label_dest.config(text=self.dest_text + text)

    def update_rename_source(self, text):
        self.label_dir.grid()
        if len(text) > self.label_entry_len:
            self.scroll_dir_name.grid()
        else:
            self.scroll_dir_name.grid_remove()
        self.source_rename_text.set('' + text)

    def choose_dir_move_destination(self, event):
        temp_dir = filedialog.askdirectory()
        if temp_dir != '':
            self.dir_path_move_to.set(temp_dir)
            self.update_move_dest(temp_dir)
            self.completed_move_items[1] = True
        else:
            self.completed_move_items[1] = False
        self.check_for_move_complete()

    def run_rename(self, event):  # Renames files/dirs based on user specifications
        if str(self.button_run_rename['state']) == 'disabled':
            return
        if (not self.rename_subdirs.get()) and (not self.rename_subfiles.get()):  # Only doing root directory
            error_messages = []
            num_renamed = 0
            for f in os.scandir(self.dir_path.get()):
                file = self.dir_path.get() + "\\" + f.name
                if (self.rename_dirs.get() and os.path.isdir(file)) or (
                            self.rename_files.get() and os.path.isfile(file)):
                    mod = self.dir_path.get() + "\\" + f.name.replace(self.replace_this.get(), self.with_this.get())
                    if os.path.exists(mod) and mod != file:
                        error_messages.append(self.error_renamed_exists + mod + '\n')
                    else:
                        os.rename(file, mod)
                        num_renamed += 1
            if num_renamed == 0:
                error_messages.append(self.error_none_renamed)
            if len(error_messages) > 0:
                self.error_handle(error_messages)
            else:
                self.popup_window(self.successful_rename)
        else:  # Doing subdirectories
            error_messages = []
            for path, dirs, files in os.walk(self.dir_path.get()):
                if (self.rename_files and path == self.dir_path.get()) or (
                            self.rename_subfiles and path != self.dir_path.get()):
                    rename_report = self.walk_rename(files, path)
                    if len(rename_report) > 0:
                        for message in rename_report:
                            error_messages.append(message)
                elif (self.rename_dirs and path == self.dir_path.get()) or (
                            self.rename_subdirs and path != self.dir_path.get()):
                    rename_report = self.walk_rename(dirs, path)
                    if len(rename_report) > 0:
                        for message in rename_report:
                            error_messages.append(message)
            if len(error_messages) > 0:
                self.error_handle(error_messages)
            else:
                self.popup_window(self.successful_rename)

    def walk_rename(self, iterator, path):
        error_messages = []
        for item in iterator:
            full_path = path + "\\" + item
            modified_path = path + "\\" + item.replace(self.replace_this.get(), self.with_this.get())
            if os.path.exists(modified_path) and full_path != modified_path:
                error_messages.append(self.error_renamed_exists + modified_path + '\n')
            else:
                os.rename(full_path, modified_path)
        if len(error_messages) != 0:
            return error_messages
        else:
            return []

    def run_move(self, event):
        error_messages = []
        num_complete = 0
        for f in os.scandir(self.dir_path_move.get()):
            file = self.dir_path_move.get() + '\\' + f.name
            destination = self.dir_path_move_to.get() + '\\' + f.name
            if os.path.exists(destination):
                message = self.error_moved_exists + destination
                error_messages.append(message)
            elif (os.path.isfile(file) and len(f.name) > len(self.start_end_contain.get())) and (
                            ((self.pre_suf_cont.get() == 0) and (f.name.startswith(self.start_end_contain.get()))) or (
                                    (self.pre_suf_cont.get() == 1) and (
                                        f.name.endswith(self.start_end_contain.get()))) or (
                                (self.pre_suf_cont.get() == 2) and (self.start_end_contain.get() in f.name))):
                shutil.move(file, destination)
                num_complete += 1
        if num_complete == 0:
            error_messages.append(self.error_none_moved)
        if len(error_messages) > 0:
            self.error_handle(error_messages)
        else:
            self.popup_window(self.successful_move)

    def error_handle(self, message_bank):
        if len(message_bank) > 1:
            error_message = 'The following ' + str(len(message_bank)) + ' errors have occurred:\n'
        else:
            error_message = 'The following error has occurred:\n'
        for error in message_bank:
            error_message += error
        self.popup_window(error_message)

    def cycle_frame_text(self, event):  # Cycles text on window bottom to match selected tab
        tab_text = event.widget.tab(event.widget.index('current'), 'text')
        if tab_text == self.TAB_NAMES[0]:  # "Rename Files"
            self.label.configure(text='Find and replace phrases in file/directory names')
        elif tab_text == self.TAB_NAMES[1]:  # "Move Files"
            self.label.configure(text='Move select files to specified folders')
        elif tab_text == self.TAB_NAMES[2]:  # "About"
            self.label.configure(text='...')

    def update_replace_this(self, event):
        self.check_rename_entries(event)
        self.replace_this.set(self.entry_replace_this.get())

    def update_with_this(self, event):
        self.check_rename_entries(event)
        self.with_this.set(self.entry_with_this.get())

    def update_pre_suf_cont(self, event):
        self.check_move_entries(event)
        self.start_end_contain.set(self.entry_pre_suf_cont.get())

    def check_rename_entries(self, event):
        if self.entry_replace_this.get() != '':
            self.completed_items[1] = True
        else:
            self.completed_items[1] = False
        self.check_for_completion()

    def check_move_entries(self, event):
        if self.entry_pre_suf_cont.get() != '':
            self.completed_move_items[3] = True
        else:
            self.completed_move_items[3] = False
        self.check_for_move_complete()

    def flip_warnings(self, on_top):  # Turns text warnings on if on_top, else turns them off
        if on_top:
            self.label_move_blank.grid_remove()
            self.label_blank.grid_remove()
            self.label_txt_warn_move.grid()
            self.label_txt_warn.grid()
            self.previous_bad_validation = True
        else:
            self.label_txt_warn_move.grid_remove()
            self.label_txt_warn.grid_remove()
            self.label_move_blank.grid()
            self.label_blank.grid()
            self.previous_bad_validation = False

    def popup_window(self, message):
        top_level = Toplevel()
        top_level.resizable(0, 0)
        message_label = Label(top_level, text=message)
        message_label.grid(padx=(10, 10), pady=(10, 10))

    def on_validate(self, s):
        for character in self.bad_chars:
            for substring in s:
                if substring == character:
                    self.flip_warnings(True)
                    return False
        if self.previous_bad_validation:
            self.flip_warnings(False)
        return True


root = Tk()
sr = SimpleScript(root)
root.mainloop()
