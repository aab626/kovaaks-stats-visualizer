import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

# custom messagebox for the app
class KSVMessageBox(tk.Toplevel):
	def __init__(self, parent, title, message, icon_path = None):
		tk.Toplevel.__init__(self)

		self.parent = parent
		self.title = title

		self.grab_set()
		self.parent.attributes('-disabled', True)

		self.bell()
		self.bind("<Destroy>", lambda e:self.parent.attributes('-disabled', False))

		content = ttk.Frame(self, padding=5)
		content.grid(row=0, column=0, sticky='news')
		content.columnconfigure(0, weight=1)
		content.rowconfigure((0,1,2), weight=1)

		if icon_path is not None:
			icon = ImageTk.PhotoImage(Image.open(icon_path))
			icon_label = ttk.Label(content)
			icon_label.image = icon
			icon_label.configure(image=icon)
			icon_label.grid(row=0, column=0, rowspan=2, sticky='w', padx=(0, 20))

		text_label = ttk.Label(content, text=message)
		text_label.grid(row=0, column=1, columnspan=2, sticky='e')

		ok_button = ttk.Button(content, text='Ok', command=lambda:self.destroy())
		ok_button.grid(row=1, column=2, sticky='es')