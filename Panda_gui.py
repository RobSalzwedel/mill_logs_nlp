import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from matplotlib import style
import matplotlib.pyplot as plt
import ttk
import Tkinter as tk

import json
import urllib2
import numpy as np
import pandas as pd

LARGE_FONT = ("Verdanna",12)
style.use("ggplot")

df = pd.read_csv('tinker_test.csv')
df['label_status'] = False

f = Figure()
a = f.add_subplot(111)

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
        label = tk.Label(self, text = "Welcome, do you agree to the terms and conditions of use", 
                         font = LARGE_FONT)
        
        label.pack(pady = 10, padx = 10)
        button = tk.Button(self, text = "Agree", 
                            command=lambda: controller.show_frame(TextLabel))
        button.pack()
        button2 = tk.Button(self, text = "Disagree", command=quit)
        button2.pack()
  
        
class TextLabel(tk.Frame):
    
    def __init__(self, parent, controller):
        
        tk.Frame.__init__(self, parent)
        
        label = tk.Label(self, text = "Graph Page", font = LARGE_FONT)
        #label.pack(pady = 10, padx = 10)
        
        #button1 = tk.Button(self, text = "Back to home", 
        #                    command = lambda: controller.show_frame(StartPage))
        #button1.pack()
        
        button2 = tk.Button(self, text = 'delete display', 
                            command = self.delete_display)
        button2.pack(side = 'top')
         
        button3 = tk.Button(self, text = "display", 
                            command = self.display)
        button3.pack(side='top')
        
        button4= tk.Button(self, text = "label", 
                            command = self.label)
        button4.pack(side='top')
        
        sb_cluster = tk.Spinbox(self, from_=0, to=10)
        sb_cluster.pack(side = 'top')

         
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
        for key in self.var:
            print self.var[key].get()
            if self.var[key].get():
                df['label_status'][key] = True

        print '-----'
        print df
    

    def display(self):
        'Displays the unlabeled data in a scrollable list of checkboxes'
        self.vsb = tk.Scrollbar(self, orient = "vertical")
        self.text = tk.Text(self, width = 40, height = 20, 
                            yscrollcommand=self.vsb.set)
        self.vsb.config(command = self.text.yview)
        self.vsb.pack(side = "right", fill = "y")
        self.text.pack(side = "left", fill = "both", expand = True)
        
        # Dictionaries of checkboxes (cb), & checkbox_status (var), 
        #key = df.index, value = df['data'][index] if not labeled
        self.cb = {}
        self.var = {}
        for i in df.index:
            if not df['label_status'][i]:
                self.var[i] = tk.IntVar()
                self.var[i].labelled = False
                self.cb[i] = tk.Checkbutton(self, text = str(df['data'][i]), width = 50, 
                                     justify = tk.LEFT, variable = self.var[i],
                                     wraplength = 300)
                self.text.window_create("end", window = self.cb[i])            
                self.text.insert("end", "\n") # to force one checkbox per line
    
    def delete_display(self):
        self.text.destroy()
        self.vsb.destroy()
        
app = Spookfish()
app.geometry("700x400")
#ani = animation.FuncAnimation(f, animate, interval = 5000)
app.mainloop()

 