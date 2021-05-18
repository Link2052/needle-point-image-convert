# General module imports

from tkinter import filedialog as F
from tkinter import messagebox as M
from tkinter import ttk
from tkinter import *

import os

# Built-in autoimport of needed external modules

try:
	from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb
except:
	os.system('python3 pip -m install webcolors')
	from webcolors import CSS3_HEX_TO_NAMES, hex_to_rgb
	
try:	
	from scipy.spatial import KDTree
except:
	os.system('python3 pip -m install scipy')
	from scipy.spatial import KDTree

try:
	from PIL import Image, ImageTk
except:
	os.system('python3 pip -m install PIL')
	from PIL import Image, ImageTk

# Image processing algorithm (not mine, cross-borrowed from several sources online)
# This chops the images into a grid and approximates each color in the grid into one 
#   of the 16 most-used colors of the original image  

def	pixelgrid(input_file):

	backgroundColor = (0,)*3
	pixelSize = 9

	image = Image.open(input_file)
	if image.mode != 'RGB':
		image = image.convert('RGB')
	image = image.resize((int(image.size[0]/pixelSize), int(image.size[1]/pixelSize)), Image.NEAREST)
	image = image.resize((image.size[0]*pixelSize, image.size[1]*pixelSize), Image.NEAREST)
	pixel = image.load()

	for i in range(0,image.size[0],pixelSize):
		for j in range(0,image.size[1],pixelSize):
			for r in range(pixelSize):
				pixel[i+r,j] = backgroundColor
				pixel[i,j+r] = backgroundColor
	
	image = image.quantize(16, method = Image.MAXCOVERAGE, kmeans = 16, dither = Image.FLOYDSTEINBERG)
	
	im = image.convert('RGB')
	
	color_list = '\n'.join([rgb_to_name(color) for color in set(list(im.getdata()))])
	
	return (image, color_list)

# Generalizes selected colors from processed image and converts the RGB to plain-text names so you can know what color thread to buy
# This will be saved as a .txt file in the same directory as the processed image, if the user saves that image.

def rgb_to_name(rgb):
	
	css3 = CSS3_HEX_TO_NAMES
	names = []
	rgb_values = []
	for color_hex, color_name in css3.items():
		names.append(color_name)
		rgb_values.append(hex_to_rgb(color_hex))
	
	kdt = KDTree(rgb_values)
	distance, index = kdt.query(rgb)

	return names[index]
	
# Tkinter GUI App, done as a class for smoother implementations and data management.
  
class App(Frame):
	
	def __init__(self, master):
	  
    # Initialise the frame, select the griding widget management process, give a lable name to the software
  
		Frame.__init__(self, master, width = 1000, height = 1000)
		self.parent = master
		self.grid()
		self.parent.title("Needle Point Image Converter")
		
    # Call the GUI build
    
		self.GUI()
		
	def GUI(self):
	
    # Build the main GUI
    
    # 2 Buffer labels on either (diagonal) end of the widgets so the window doesn't butt up to them
  
		self.bl0 = ttk.Label(self)
		self.bl0.grid(row = 0, column = 0)
		
		self.bl1 = ttk.Label(self)
		self.bl1.grid(row = 3, column = 3)
		
    # Button/label for the File name entry widget, button activated the built-in tkinter filedialog
    
		self.lb0 = ttk.Button(self, text = 'Image Name :', width = 16, command = self.load_image)
		self.lb0.grid(row = 1, column = 1, sticky = EW)
	
    # Entry for File name
  
		self.e0 = ttk.Entry(self, width = 60)
		self.e0.grid(row = 1, column = 2, sticky = EW)
    
    # The "Go" button to start image processing
    
		self.b0 = ttk.Button(self, text = 'Process Image', command = self.run_process)
		self.b0.grid(row = 2, column = 1, columnspan = 2, sticky = EW)
		
	def load_image(self):
		
    # Routine called when the "Image Name" (self.lb0) is pressed
    # Opens the built-in tkinter filedialog with the user's desktop as the initial directory
    # Also clears anything in the Entry widget (self.e0) and then puts the selected file directory there
    
		self.file_name = F.askopenfilename(initialdir = 'desktop')
		self.e0.delete(0, 'end')
		self.e0.insert(0, self.file_name)
	
	def run_process(self):
		
    # Main process for application
    
    # Set a flag for error catching
    
		flag_roster = 1
		
    # If the file name can't be read or some other error occured stop here and notify the user with a built-in tkinter messagebox
    
		try:
			self.__image__, self.color_list = pixelgrid(self.file_name)
			
		except:
			M.showerror(message = 'Error: Process failed!\n\nIs the selected file formatted properly?', title = 'Process Error!')
			flag_roster = 0
		
    # If there were no errors continue, and build a new Toplevel window to display the processed image.
    
		if flag_roster:
      
      # Formate the processed image so that it may be deisplayed by tkinter
      
		  rendered_image = ImageTk.PhotoImage(self.__image__)
      
      # Build the Toplevel and its' GUI
      
			self.sub_window = Toplevel()
			sub_window = self.sub_window
			sub_window.geometry('-440+155')
			sub_window.grid()
			sub_window.title('Image Processing Result')
			sub_window.resizable(width = False, height = False)
			
      # Add a menu button called "Save As" which opend the built-in tkinter filedialog **(user must provide file extension)**
      
			self.sub_window_mainmenu = Menu(sub_window)
			self.sub_window_mainmenu.add_command(label = 'Save As', command = self.save_image)
				
			sub_window.config(menu = self.sub_window_mainmenu)
			
      # Buffer label again
      
			self.std_bl0 = ttk.Label(self)
			self.std_bl0.grid(row = 0, column = 0)
			
      # Dynamically set the canvas size variables depending on the image (max of 800 pix high and 1000 pix wide)
      
			canvas_height = 800 if rendered_image.height() > 800 else rendered_image.height()
			canvas_width = 1000 if rendered_image.width() > 1000 else rendered_image.width()
	
      ### To be replaced by a Match-Case
    
      # Depending on image size, potentially add veritcal and/or horizontal scrollbars, or add neither
      # If present these are method-bound to the mouse-wheel (for vertial) and to Shift+mouse-wheel (for horizontal)
  
			if canvas_height == 800 and canvas_width < 1000:
				self.std_scb_vert = ttk.Scrollbar(sub_window, orient = 'vertical')
				self.std_scb_vert.grid(row = 1, column = 10, rowspan = 7, sticky = NS)
				
				self.img_canvas = Canvas(sub_window, width = canvas_width, height = canvas_height, yscrollcommand = self.std_scb_vert.set)
				self.img_canvas.grid(row = 1, column = 2, columnspan = 7, rowspan = 7, sticky = NSEW)
				self.img_canvas.create_image((0, 0), image = rendered_image, anchor = NW)
				self.img_canvas.image = rendered_image
			
				self.std_scb_vert.config(command = self.img_canvas.yview)
				self.img_canvas.config(scrollregion = self.img_canvas.bbox('all'))
				
				self.img_canvas.bind_all("<MouseWheel>", self.__mouse_scroll_y__)
			
			elif canvas_width == 1000 and canvas_height < 800:
				self.std_scb_horz = ttk.Scrollbar(sub_window, orient = 'horizontal')
				self.std_scb_horz.grid(row = 8, column = 1, columnspan = 10, sticky = EW)
				
				self.img_canvas = Canvas(sub_window, width = canvas_width, height = canvas_height, xscrollcommand = self.std_scb_horz.set)
				self.img_canvas.grid(row = 1, column = 2, columnspan = 7, rowspan = 7, sticky = NSEW)
				self.img_canvas.create_image((0, 0), image = rendered_image, anchor = NW)
				self.img_canvas.image = rendered_image
			
				self.std_scb_horz.config(command = self.img_canvas.xview)
				self.img_canvas.config(scrollregion = self.img_canvas.bbox('all'))
				
				self.img_canvas.bind_all("<MouseWheel>", self.__mouse_scroll_x__)
			
			elif canvas_width == 1000 and canvas_height == 800:
				self.std_scb_vert = ttk.Scrollbar(sub_window, orient = 'vertical')
				self.std_scb_vert.grid(row = 1, column = 10, rowspan = 7, sticky = NS)
				
				self.std_scb_horz = ttk.Scrollbar(sub_window, orient = 'horizontal')
				self.std_scb_horz.grid(row = 8, column = 1, columnspan = 10, sticky = EW)
			
				self.img_canvas = Canvas(sub_window, width = canvas_width, height = canvas_height, yscrollcommand = self.std_scb_vert.set, xscrollcommand = self.std_scb_horz.set)
				self.img_canvas.grid(row = 1, column = 2, columnspan = 7, rowspan = 7, sticky = NSEW)
				self.img_canvas.create_image((0, 0), image = rendered_image, anchor = NW)
				self.img_canvas.image = rendered_image
			
				self.std_scb_vert.config(command = self.img_canvas.yview)
				self.std_scb_horz.config(command = self.img_canvas.xview)
				self.img_canvas.config(scrollregion = self.img_canvas.bbox('all'))
				
				self.img_canvas.bind_all("<MouseWheel>", self.__mouse_scroll_y__)
				self.img_canvas.bind_all("<Shift-MouseWheel>", self.__mouse_scroll_x__)
				
			else:
				
				self.img_canvas = Canvas(sub_window, width = canvas_width, height = canvas_height)
				self.img_canvas.grid(row = 1, column = 2, columnspan = 7, rowspan = 7, sticky = NSEW)
				
				self.img_canvas.create_image((0, 0), image = rendered_image, anchor = NW)
				self.img_canvas.image = rendered_image

	def save_image(self):
		
    # Attempt to use the given file name to save the processed image (and the list of colors), if there is an error in this process,
    #   notify the user with a built-in tkinter messagebox
    
		try:
			save_file = F.asksaveasfilename(initialdir = 'desktop')
			text_file = save_file.split('.')[0]+'_color_list.txt'
			self.__image__.save(save_file)
			file = open(text_file, 'a')
			file.write(self.color_list)
			file.close()
		
		except:
			M.showerror(message = 'Error: File save failed!\n\nIs the file name formatted properly?', title = 'Save Error!')
	
  # Mouse-wheel event bindings
  
	def __mouse_scroll_y__(self, event):
		self.img_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
	
	def __mouse_scroll_x__(self, event):
		self.img_canvas.xview_scroll(int(-1*(event.delta/120)), "units")

# Generate the Tk window, pass it to the App class, preventing resizing, run it's mainloop
    
root = Tk()
root.resizable(width = False, height = False)
app = App(root)
app.mainloop()		
		
