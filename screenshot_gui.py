import tkinter as tk
from tkinter import messagebox, simpledialog
import pyautogui
import win32clipboard
from PIL import ImageGrab
import io
import pygetwindow as gw
import pywinauto
import time

class ScreenshotApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Screenshot Sender')
        self.selected_window = None
        self.screenshot = None

        tk.Button(root, text='Take Screenshot', command=self.take_screenshot).pack(pady=5)
        tk.Button(root, text='Select Window', command=self.select_window).pack(pady=5)
        tk.Button(root, text='Send Screenshot', command=self.send_screenshot).pack(pady=5)

    def take_screenshot(self):
        self.screenshot = ImageGrab.grab()
        output = io.BytesIO()
        self.screenshot.save(output, 'BMP')
        data = output.getvalue()[14:]
        output.close()
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        messagebox.showinfo('Info', 'Screenshot taken and copied to clipboard.')

    def select_window(self):
        windows = gw.getAllTitles()
        windows = [w for w in windows if w.strip()]
        if not windows:
            messagebox.showerror('Error', 'No windows found.')
            return
        # Create a new top-level window for selection
        sel_win = tk.Toplevel(self.root)
        sel_win.title('Select Window')
        sel_win.geometry('400x300')
        tk.Label(sel_win, text='Click a window title to select:').pack(pady=5)
        listbox = tk.Listbox(sel_win, width=60, height=15)
        listbox.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        for w in windows:
            listbox.insert(tk.END, w)

        def on_select(event=None):
            selection = listbox.curselection()
            if selection:
                win = listbox.get(selection[0])
                self.selected_window = win
                messagebox.showinfo('Info', f'Selected window: {win}')
                sel_win.destroy()

        listbox.bind('<Double-Button-1>', on_select)
        tk.Button(sel_win, text='Select', command=on_select).pack(pady=5)

    def send_screenshot(self):
        if not self.selected_window:
            messagebox.showerror('Error', 'No window selected.')
            return
        try:
            app = pywinauto.Application().connect(title=self.selected_window)
            win = app.window(title=self.selected_window)
            win.set_focus()
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'v')
            messagebox.showinfo('Info', 'Screenshot pasted to selected window.')
        except Exception as e:
            messagebox.showerror('Error', f'Failed to send screenshot: {e}')

if __name__ == '__main__':
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.mainloop()
