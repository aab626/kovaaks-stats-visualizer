import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

# custom messagebox for the app
class KSVConfirmBox(tk.Toplevel):
	def __init__(self, parent, title, message, icon_path, text_option1, f_option1, text_option2, f_option2 = None):
		tk.Toplevel.__init__(self)

		self.parent = parent
		self.title = title

		self.grab_set()
		self.parent.attributes('-disabled', True)

		# self.bell()
		self.bind("<Destroy>", lambda e:self.parent.attributes('-disabled', False))

		icon = ImageTk.PhotoImage(Image.open(icon_path))

		content = ttk.Frame(self, padding=5)
		content.grid(row=0, column=0, sticky='news')
		content.columnconfigure(0, weight=1)
		content.rowconfigure((0,1,2), weight=1)

		icon_label = ttk.Label(content)
		icon_label.image = icon
		icon_label.configure(image=icon)
		icon_label.grid(row=0, column=0, rowspan=3, sticky='w', padx=(0, 20))

		text_label = ttk.Label(content, text=message)
		text_label.grid(row=0, column=1, columnspan=2, sticky='e')

		opt1_button = ttk.Button(content, text=text_option1, command= lambda:[f_option1(), self.destroy()])
		opt1_button.grid(row=1, column=2, sticky='es', padx=(0, 5))

		if f_option2 is None:
			f_option2 = lambda: self.destroy()
		opt2_button = ttk.Button(content, text=text_option2, command=lambda:[f_option2(), self.destroy()])
		opt2_button.grid(row=1, column=3, sticky='es', padx=(0, 5))
