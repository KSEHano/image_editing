import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from tkinter import filedialog, messagebox
from skimage.color.colorconv import rgba2rgb
from skimage.feature import canny
from skimage.io import imread
from scipy.ndimage import gaussian_gradient_magnitude, gaussian_filter, gaussian_laplace
from skimage import color, transform, filters
from skimage.segmentation import slic, mark_boundaries, felzenszwalb


root = Tk()
root.title('Image Editing')
root.iconbitmap('./icon.ico')

#find file
def search_file():
    root.filename = filedialog.askopenfilename(initialdir = '.', title = 'Select a File', filetypes = (('jpg files', '*.jpg'),('png files', '*.png')))
    path.delete(0, END)
    path.insert(0,root.filename)

#save file
def save_file(image):
    
    top.filename = filedialog.asksaveasfile(mode='w', defaultextension=".jpg", filetypes= [('jpg Files', '.jpg')])
    if top.filename is None: # ask saveasfile return `None` if dialog closed with "cancel".
        return
    fig.savefig(top.filename.name)
    
    
#activate only necessary fields
def deactivate_entries(method):
    '''
    deactivate depending on methos selcted
    '''
    #method = clicked.get()
    if(method == options[4] or method == options[5] or method == options[6]):
        ent_sig['state'] = NORMAL
        ent_seg['state'] = NORMAL
        che_lin['state'] = NORMAL
        if(method == options[6]):
            lab_seg.config(text = "Segment Size")
        else:
            lab_seg.config(text = "Segments")
        
    else:
        ent_sig['state'] = NORMAL
        ent_seg['state'] = DISABLED
        che_lin['state'] = DISABLED
        lab_seg.config(text = "Segmente")

#changes the picture depending on the method
def calculate_picture():
    #get all information
    try:
        image = imread(path.get())
    except FileNotFoundError:
        messagebox.showwarning("File Warning","The file does not exist.")
        return
    except ValueError:
        messagebox.showwarning("No File", "An image file must be given.")
        return
    
    #transform rgba image
    if('.png' in root.filename):       
        image = rgba2rgb(image)
    
    method = clicked.get()
    lines = has_lines.get()

    #empty/ disabled field
    if (not ent_seg.get() and ent_seg['state'] == DISABLED):
        #activate because insert only works in NORMAL state
        #so there is no warning if the field is disabled
        ent_seg['state'] = NORMAL
        ent_seg.insert(0, default_seg)
        ent_seg['state'] = DISABLED
        
    try:
        sig = float(ent_sig.get())
        seg = int(ent_seg.get())
           
    except ValueError:
        messagebox.showwarning("Input Warning","You must enter a number")
        return

    try:
        image = transform.rescale(image, (0.5, 0.5, 1), anti_aliasing=False)
    except ValueError:
        image = transform.rescale(image, 0.5, anti_aliasing=False)
    
    image_gray = color.rgb2gray(image)

    #prepare the picture as figure
    global fig
    fig = plt.figure()
    ax = plt.Axes(fig,[0., 0., 1., 1.])
    ax.set_axis_off()
    fig.add_axes(ax)
    global result
    #Different options
    #grey
    if(method == options[0]):
        result = gaussian_filter(image_gray, sig)
        plt.imshow(result, cmap= 'gray')

    #hue
    elif(method == options[1]):
        result = color.rgb2hsv(gaussian_filter(image, sig))
        plt.imshow(result)

    #'Gauss Filter', 
    elif(method == options[2]):
        result = gaussian_filter(image, sig)
        plt.imshow(result)

    #'ni_black',
    elif(method == options[3]):
        result = gaussian_filter(image_gray, sig)
        threshold = filters.threshold_niblack(result)
        result = (result > threshold)*1
        plt.imshow(result, cmap = 'gray')
        
    # Segmentation
    elif(method == options[4]):
        result = slic(image,n_segments=seg, compactness=10, sigma=sig, start_label=1)
        if lines:
            result = mark_boundaries(image, result)
        
        plt.imshow(result)
    
    # Segmentation mean
    elif(method == options[5]):
        result = slic(image,n_segments=seg, compactness=10, sigma=sig, start_label=1)
        if lines:
            plt.imshow(mark_boundaries(color.label2rgb(result,image,kind = 'avg', bg_label=0), result))

        else:
            plt.imshow(color.label2rgb(result,image, kind = 'avg', bg_label=0))

    #'Felzenszwalb',
    elif(method == options[6]):
        result = felzenszwalb(image ,scale = 2, sigma=sig, min_size= seg)
        if lines :
            result = mark_boundaries(image, result)
            plt.imshow(result)
        else:
            #plt.imshow(result)
            plt.imshow(color.label2rgb(result,image, kind = 'avg', bg_label=0))

    #Edge with Gauss,
    elif(method == options[7]):
        result = gaussian_gradient_magnitude(image_gray, sig)
        plt.imshow(result, cmap = 'gray')
    
    #'Edge with Canny',
    elif(method == options[8]):
        result = canny(image_gray, sig)
        plt.imshow(result, cmap = 'gray')

    #'Blobs with Laplace'  
    elif(method == options[9]):
        result = gaussian_laplace(image_gray, sig)
        plt.imshow(result, cmap = 'gray')


    #make a new window
    global top
    top = Toplevel()
    top.title("Edited image")
    top.iconbitmap('./icon.ico')
    
    #add picture to window
    canvas = FigureCanvasTkAgg(fig, master = top)
    canvas.draw()
    canvas.get_tk_widget().grid(row =0, column = 0, padx = 10, pady = 10)
    
    #Save Button
    but_save = Button(top, text = "Save", command= lambda: save_file(result))
    but_save.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = 'E')
    


#labels
lab_pic = Label(root, text = 'Select an image:')
lab_met = Label(root, text = 'Method')
lab_sig = Label(root, text = 'Sigma')
lab_seg = Label(root, text = 'Segments')
lab_lin = Label(root, text = 'Lines')

#checkbox
has_lines = BooleanVar()
che_lin = Checkbutton(root, variable = has_lines, onvalue = True, offvalue = False)
che_lin.deselect()

#buttons
but_calc = Button(root, text = "Calculate", command = lambda: calculate_picture())
but_find = Button(root, text = "Search", command = lambda: search_file())

#drop down value
global options
options = [
    'Grey',
    'Hue' ,
    'Gauss Filter', 
    'ni_black',
    'Segmentation',
    'Segmentation Mean',
    'Felzenszwalb',
    'Edge with  Gauss',
    'Edge with Canny',
    'Blobs with Laplace'
    
]
#drop down menu
global clicked
clicked = StringVar()
clicked.set(options[0])

drop = OptionMenu(root, clicked, *options, command=deactivate_entries)

#entry widgets7
path = Entry(root, width = 75)
ent_sig = Entry(root)
ent_seg = Entry(root)

#default values
default_sig = 0
default_seg = 100
ent_sig.insert(0,default_sig)
ent_seg.insert(0, default_seg)


#positioning labels
lab_pic.grid(row = 0, column = 0, padx = 10, pady = 10, sticky='W')
lab_met.grid(row = 2, column = 1, sticky = 'W')
lab_sig.grid(row = 3, column = 1, sticky = 'W')
lab_seg.grid(row = 6, column = 1, sticky = 'W')
lab_lin.grid(row = 7, column = 1, sticky = 'W')

#positioning entries
path.grid(row = 1, column = 0, columnspan = 3, padx = 10, pady = 0)
drop.grid(row = 2, column = 0, padx = 5, pady = 5, sticky = 'E')
ent_sig.grid(row = 3, column = 0, padx = 5, pady = 5, sticky = 'E')
ent_seg.grid(row = 6, column = 0, padx = 5, pady = 5, sticky = 'E')
che_lin.grid(row = 7, column = 0, padx = 5, pady = 5, sticky = 'E')


#position buttons
but_find.grid(row = 1, column = 3, padx = 10, pady = 10)
but_calc.grid(row = 7, column = 3, padx = 10, pady = 10)

#do after program start
deactivate_entries(clicked.get())

#programm loop
root.mainloop()