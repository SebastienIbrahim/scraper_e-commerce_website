import tkinter as tk
from tkinter import ttk
LARGE_FRONT = ("Verdana", 20)
NORM_FRONT = ("Helvetica", 10)
SMALL_FRONT = ("Helvetica", 8)
import os
DURATION = 1 # milliseconds
FREQ = 440 # Hz

def beep_sound(freq, duration):
    os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))

def popupmsg(msg, freq=FREQ, duration=DURATION):
    #duration *= 1_000
    beep_sound(freq, duration)
    popup = tk.Tk()
    scroll_bar = tk.Scrollbar(popup)
    text_widget = tk.Text(popup, height=5, width=40)
    popup.geometry("600x250")
    scroll_bar.pack(side=tk.RIGHT)
    popup.wm_title("!")
    scroll_bar.pack()
    text_widget.pack()
    B1 = ttk.Button(popup, text="Okay", command=popup.destroy)
    B1.pack()
    text_widget.insert(tk.END, msg)
    popup.mainloop()