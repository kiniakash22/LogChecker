import ssh_login
from tkinter import *
import os

def clear_textbox(event):
    global user_name_textbox, password_textbox
    user_name_textbox.delete(0,END)
    password_textbox.delete(0,END)

def login_to_server(event):
    global user_name_textbox, password_textbox
    print(ssh_login.login(user_name_textbox.get(), password_textbox.get()))
    pass




root = Tk()

root.title("Welcome to check_tblog configuration")

root.geometry("300x160")

frame1 = Frame(root)
frame2 = Frame(root)

display_message_label = Label(frame1,text="Enter the credentials to login")
display_message_label.grid(row=0, column=0, sticky=W, columnspan=2, padx=5)

user_name_label = Label(frame1, text="User name: ")
user_name_label.grid(row=1, column=0, sticky=W, padx=5, pady=10)

user_name_textbox = Entry(frame1, text="User name: ")
user_name_textbox.grid(row=1, column=1)


password_label = Label(frame1, text="Password: ")
password_label.grid(row=2, column=0, sticky=W, padx=5, pady=5)

password_textbox = Entry(frame1, show="*")
password_textbox.grid(row=2, column=1)

submit_button = Button(frame2, text="Login")
submit_button.grid(row=0, column=0, padx=20, pady=5)
submit_button.bind("<Button>", login_to_server)

clear_button = Button(frame2, text="Clear")
clear_button.grid(row=0, column=1, padx=20)
clear_button.bind("<Button>", clear_textbox)

frame1.pack()
frame2.pack()

root.mainloop()






