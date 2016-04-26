import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.pyplot as plt
import ttk
import Tkinter as tk
from PIL import Image, ImageTk
import os
import pickle

import tkMessageBox
import json
import urllib2
import numpy as np
import pandas as pd

LARGE_FONT = ("Verdanna",12)
style.use("ggplot")

df = pd.read_csv('tkinter_test.csv')
df['label_status'] = False
#TODO Save and load labels, and label status rather than setting to empty
df['label'] = ''

#Load the lables dictionary
try:
    labels = pickle.load( open( "labels_dict.p", "rb" ) )
except IOError:   
    labels = {}
    pickle.dump(labels, open( "labels_dict.p", "wb" ) )


def printstuff(stuff = 'empty test'):
    print stuff

def animate(i):
    dataLink = 'https://btc-e.com/api/3/trades/btc_usd?limit=2000'
    data = urllib2.urlopen(dataLink).read()
    data = data.decode("utf-8")
    data = json.loads(data)
    
    data = data["btc_usd"]
    data = pd.DataFrame(data)
    
    buys = data[(data['type'] == 'bid')]  
    buys['datestamp'] = np.array(buys['timestamp']).astype('datetime64[s]')
    buyDates = (buys["datestamp"]).tolist()
    
    sells = data[(data['type'] == 'ask')]  
    sells["datestamp"] = np.array(sells["timestamp"]).astype("datetime64[s]")
    sellDates = (sells["datestamp"]).tolist()
    
    a.clear()
    a.plot_date(buyDates, buys["price"], '#05668D', label = 'buy')
    a.plot_date(sellDates, sells["price"], '#02C39A', label = 'sell')
    
class Spookfish(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args,**kwargs)
        tk.Tk.resizable(self, width= False, height=False)

        tk.Tk.wm_title(self, "Spookfish")
        
        container = tk.Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)
        
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Settings", command=None)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command = quit)
        menubar.add_cascade(label='File', menu = filemenu)
        
        tk.Tk.config(self, menu = menubar) 
        
        self.frames = {}
        for F in (StartPage, TextLabel):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row = 0, column = 0, sticky = 'nsew') 

        self.show_frame(StartPage)
        
    def show_frame (self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        

class StartPage(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text = '''Welcome to spookfish text labelling app, Rob Salzwedel is a boss.''',
                         font = LARGE_FONT)
        
        label.pack(pady = 10, padx = 10)
        button = tk.Button(self, text = "Agree", 
                            command=lambda: controller.show_frame(TextLabel))
        button.pack()
        button2 = tk.Button(self, text = "Disagree", command=quit)
        button2.pack()
        

        image = Image.open("spookfish.jpg")
        photo = ImageTk.PhotoImage(image)
         
        label = tk.Label(self,image=photo)
        label.image = photo # keep a reference!
        label.pack(side = 'bottom', fill = 'both',expand = 'true')

  
        
class TextLabel(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        
        
        #button1 = tk.Button(self, text = "Back to home", 
        #                    command = lambda: controller.show_frame(StartPage))
        #button1.pack()
        
        
        #New frame for all the actions widgets on the right
        frame1 = tk.Frame(self)
        frame1.pack(side='right',fill='y')
        
        #Create progress bar and progress label
        self.prog_int = tk.IntVar()
        self.prog_int.set(float(df['label_status'].sum())/len(df))
        self.progress_bar = ttk.Progressbar(frame1, orient = 'horizontal', 
                                            mode = 'determinate', variable = self.prog_int)
        self.progress_bar.pack(side = 'bottom', fill = 'x')
        
        self.prog_var = tk.StringVar()
        self.prog_var.set("Progress: %d/%d"% (df['label_status'].sum(), len(df)))
        self.progress_label = tk.Label(frame1, textvariable =self.prog_var , font = LARGE_FONT)
        self.progress_label.pack(side = 'bottom', pady = 10, padx = 10)
        
        
        #Entry for new labels        
        # use entry widget to display/edit selection
        self.entr_labels = tk.Entry(frame1, width=40)
        self.entr_labels.insert(0, 'Click on an item in the listbox')
        self.entr_labels.pack(side = 'top')
        # pressing the return key will update edited line
        self.entr_labels.bind('<Return>', self.add_label)
        # or double click left mouse button to update line
        #entr_labels.bind('<Double-1>')
        
        
        #Create listbox with labels 
        self.lb_labels = tk.Listbox(frame1, width = 40, height = 20, selectmode = 'multiple',
                                    bd = 0)
        self.lb_labels.pack(side='top',fill='x')
        for label in labels:
            self.lb_labels.insert(tk.END, label)
            
            
        
        button1= tk.Button(frame1, text = "Label", 
                            command = self.label)
        button1.pack(side='top', fill='x')
        button2= tk.Button(frame1, text = "Select all", 
                            command = self.select_all)
        button2.pack(side='top', fill='x')
        self.sb_cluster = tk.Spinbox(frame1, from_ = 0, to = 100, command = self.refresh_display)
        self.sb_cluster.pack(side = 'top')

        #Adding matplot lib to tkinter window 
        #canvas = FigureCanvasTkAgg(f, self)
        #canvas.show()
        #canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = True)        
        
        #Adding matplotlib navigation bar
        #toolbar = NavigationToolbar2TkAgg(canvas, self)
        #toolbar.update()
        #canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)

        self.display()
       
    def label (self):
        '''Labels the selected items and updates the display, the progress label
        variable and the progress bar variable'''
        selected_keys = [self.lb_labels.get(idx) for idx in self.lb_labels.curselection()]
        label_class = [labels[key] for key in selected_keys]
        
        for key in self.var:
            print self.var[key].get()
            if self.var[key].get():
                df['label_status'][key] = True
                df['label'][key] = ' '.join(label_class)
        print '-----'
        print df
        self.refresh_display()
        
        #Update progress bar variables
        self.prog_var.set("Progress: %d/%d"% (df['label_status'].sum(), len(df)))
        self.prog_int.set(float(df['label_status'].sum())/len(df)*100)
 
    def add_label(self, event):
        ''''Adds a label from the entry box to the listbox and the labels dictionary'''
        

        
        #TODO: Check if the list box is empty
        
        #TODO: Check if the label already exists
        
        #TODO: Add the label to the list box
        
        #TODO: Add the label to the
        
        if self.entr_labels.get() not in labels.keys():
            self.lb_labels.insert(tk.END, self.entr_labels.get())
            labels[self.entr_labels.get()] = ' c%d'%len(labels)
            
        else:
            #print 'This item already exists under label ' + labels[self.entr_labels.get()]
            tkMessageBox.showinfo("Warning", 'This item already exists under label ' + labels[self.entr_labels.get()])

        print labels
        
        
        
        
        
        
        
    def display(self):
        '''Displays the unlabeled data matching the cluster selected in the spin
        box as a scrollable list of checkboxes'''
        
        self.progress_bar.value = float(df['label_status'].sum())/len(df)
        self.vsb = tk.Scrollbar(self, orient = "vertical")
        self.text = tk.Text(self, width = 40, height = 20, bd = 0,  
                            yscrollcommand=self.vsb.set, state='disabled')
        self.vsb.config(command = self.text.yview)
        self.vsb.pack(side = "right", fill = "y")
        self.text.pack(side = "left", fill = "both", expand = True)
        
        # Dictionaries of checkboxes (cb), & checkbox_status (var), 
        #key = df.index, value = df['data'][index] if not labeled
        self.cb = {}
        self.var = {}
        for i in df.index:
            if int(self.sb_cluster.get()) == int(df['cluster'][i]):
                if not df['label_status'][i]:
                    self.var[i] = tk.IntVar()
                    self.var[i].labelled = False
                    self.cb[i] = tk.Checkbutton(self, text = str(df['data'][i]), 
                                         justify = tk.LEFT, variable = self.var[i],
                                         wraplength = 1000, width = 120, activebackground = 'red')
                    self.text.window_create("end", window = self.cb[i])            
                    self.text.insert("end", "\n") # to force one checkbox per line
    
    def delete_display(self):
        '''Deletes the text display'''
        self.text.destroy()
        self.vsb.destroy()
    
    def refresh_display(self):
        self.delete_display()
        self.display()
   
    def test(self):
        print type(self.sb_cluster.get())
        print float(df['label_status'].sum())/len(df)
        print df['label_status'].sum()
        self.progress_bar
        self.prog_int.set(50)
        
    def select_all(self):
        for key in self.var:
            self.var[key].set(1)

            
app = Spookfish()
app.geometry("1440x850")
#ani = animation.FuncAnimation(f, animate, interval = 5000)
app.mainloop()

 