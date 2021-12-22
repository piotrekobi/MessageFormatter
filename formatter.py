from jaraco import clipboard
from tkinter.ttk import Frame, Entry, Button
import markdown
import tkinter as tk
import re
import json


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("680x400")
        self.attributes("-topmost", 1)
        self.title("Message formatter")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.eval('tk::PlaceWindow . center')

        self.visible_entries = 1
        self.frame = None
        self.load_tags()
        self.menu_frame()
        self.update_entry_visibility()

    def load_tags(self):
        with open("tags.json", "r") as f:
            self.tags = json.load(f)

    def copy_text(self):
        text = ""
        for entry in self.entries:
            entry_text = entry.get("1.0", "end-1c")
            if entry_text != "":

                text += "* "
                text += entry_text
                text += "\n"

        text = re.sub(
            r"#(\d\d\d\d\d)",
            r"[#\1](https://github.com/PaddlePaddle/Paddle/pull/\1)", text)
        text = re.sub(r"(PADDLEQ-\d\d\d\d)",
                      r"[\1](https://jira.devtools.intel.com/browse/\1)", text)

        found_tags = []
        found_tags.extend(re.findall(r"#\d\d\d\d\d", text))
        found_tags.extend(re.findall(r"PADDLEQ-\d\d\d\d", text))
        new_tags = set([tag for tag in found_tags if tag not in self.tags])
        self.tags.extend(new_tags)
        self.update_list_box()

        output = markdown.markdown(text)
        clipboard.copy_html(output)

    def update_entry_visibility(self):
        for i, entry in enumerate(self.entries):
            if i < self.visible_entries:
                entry.grid(row=i + 1, column=0, columnspan=3, sticky="NESW")
            else:
                entry.grid_remove()

    def on_close(self):
        with open("tags.json", "w") as f:
            json.dump(self.tags, f)
        self.destroy()

    def insert_tag(self, event):
        list_item = self.tagListBox.curselection()
        tag = self.tagListBox.get(list_item[0])
        self.last_entry.insert(self.last_index, tag)
        self.last_entry.focus_set()

    def text_focus_out(self, event):
        self.last_entry = event.widget
        self.last_index = self.last_entry.index(tk.INSERT)

    def add_entry(self):
        if self.visible_entries < 10:
            self.visible_entries += 1
            self.update_entry_visibility()

    def remove_entry(self):
        if self.visible_entries > 1:
            self.visible_entries -= 1
            self.update_entry_visibility()

    def new_frame(self):
        if self.frame is not None:
            self.frame.destroy()

        self.frame = Frame(self)
        self.frame.pack(expand=True, fill='y')

    def update_list_box(self):
        self.tagListBox.delete(0, tk.END)
        for i, product in enumerate(self.tags, start=1):
            self.tagListBox.insert(i, product)

    def menu_frame(self):
        self.new_frame()
        self.entries = [
            tk.Text(self.frame, width=70, height=3) for _ in range(10)
        ]
        self.last_entry = self.entries[0]
        self.last_index = "1.0"

        for entry in self.entries:
            entry.bind("<FocusOut>", lambda event: self.text_focus_out(event))

        addButton = Button(self.frame, text="+", command=self.add_entry)
        removeButton = Button(self.frame, text="-", command=self.remove_entry)
        copyButton = Button(self.frame,
                            text="Copy to clipboard",
                            command=self.copy_text)
        self.tagListBox = tk.Listbox(self.frame, width=15, height=15)

        addButton.grid(row=0, column=0, sticky="NESW")
        removeButton.grid(row=0, column=1, sticky="NESW")
        copyButton.grid(row=0, column=2, sticky="NESW")
        self.tagListBox.grid(row=1, column=3, rowspan=5, sticky="NESW")
        self.update_list_box()

        self.tagListBox.bind("<Double-Button-1>",
                             lambda event: self.insert_tag(event))


app = App()

app.mainloop()
