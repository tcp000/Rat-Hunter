import os
import ctypes
import psutil
import shutil
from colorama import Fore, Style, init

init(autoreset=True)

TARGET_EXTENSIONS = ['.exe', '.bat', '.vbs', '.ps1']
TEMP_DIR = os.environ.get('TEMP')
STARTUP_DIR = os.path.join(os.environ['APPDATA'], 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')

def is_file_hidden(filepath):
    try:
        attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
        if attrs == -1:
            return False
        return bool(attrs & 0x2) or bool(attrs & 0x4)
    except:
        return False

def is_process_running(pid):
    if not pid:
        return False
    try:
        p = psutil.Process(pid)
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def find_process_by_filename(filename):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and proc.info['name'].lower() == filename.lower():
                return proc
        except:
            continue
    return None

def remove_startup_files(filename):
    removed = False
    lnk_path = os.path.join(STARTUP_DIR, filename + '.lnk')
    if os.path.exists(lnk_path):
        try:
            os.remove(lnk_path)
            removed = True
        except:
            pass

    for ext in TARGET_EXTENSIONS:
        file_path = os.path.join(STARTUP_DIR, filename + ext)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                removed = True
            except:
                pass
    return removed

def scan_and_prompt_removal():
    temp_files = []

    for root, _, files in os.walk(TEMP_DIR):
        for file in files:
            if any(file.lower().endswith(ext) for ext in TARGET_EXTENSIONS):
                temp_files.append(os.path.join(root, file))

    if not temp_files:
        print(f"{Fore.BLUE}Your Device Is Clean.{Style.RESET_ALL}\n")
        return

    for file_path in temp_files:
        filename = os.path.basename(file_path)
        proc = find_process_by_filename(filename)
        pid = proc.pid if proc else None
        running = is_process_running(pid)
        hidden = is_file_hidden(file_path)

        net_info = ""
        if running and pid:
            try:
                conns = psutil.Process(pid).net_connections(kind='inet')
                for c in conns:
                    if c.status == psutil.CONN_ESTABLISHED:
                        laddr = f"{c.laddr.ip}:{c.laddr.port}"
                        raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "N/A"
                        proto = "TCP" if c.type == 1 else "UDP"
                        net_info = f"{laddr} -> {raddr} ({proto})"
                        break
            except:
                net_info = "Unable To Retrieve Network Info"

        print(f"{Fore.CYAN}File Name       : {Fore.WHITE}{filename}")
        print(f"{Fore.CYAN}Temp File Path  : {Fore.WHITE}{file_path}")
        print(f"{Fore.CYAN}Process Running : {Fore.GREEN if running else Fore.RED}{'Yes' if running else 'No'}")
        print(f"{Fore.CYAN}File Hidden     : {Fore.YELLOW if hidden else Fore.WHITE}{'Yes' if hidden else 'No'}")
        print(f"{Fore.CYAN}Network Conn    : {Fore.WHITE}{net_info if net_info else 'No active network connections'}")
        print(Style.RESET_ALL)

        if running or hidden:
            choice = input(f"{Fore.MAGENTA}Remove This File & Kill This Process? (y/n): {Fore.RESET}").strip().lower()
            if choice == 'y':
                try:
                    if running:
                        proc.terminate()
                        proc.wait(timeout=5)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    removed_startup = remove_startup_files(os.path.splitext(filename)[0])
                    print(f"{Fore.GREEN}Removal successful.{Style.RESET_ALL}\n")
                except Exception as e:
                    print(f"{Fore.RED}Error during removal: {e}{Style.RESET_ALL}\n")
        else:
            print(f"{Fore.BLUE}No action needed.\n")

def cleanup_temporary_files():
    deleted = 0
    for root, _, files in os.walk(TEMP_DIR):
        for file in files:
            if any(file.lower().endswith(ext) for ext in TARGET_EXTENSIONS):
                full_path = os.path.join(root, file)
                try:
                    attrs = ctypes.windll.kernel32.GetFileAttributesW(full_path)
                    if attrs & 0x1 or attrs & 0x2 or attrs & 0x4:
                        ctypes.windll.kernel32.SetFileAttributesW(full_path, 0x80)
                    os.remove(full_path)
                    deleted += 1
                except:
                    continue
    print(f"{Fore.GREEN}Deleted {deleted} temporary files.{Style.RESET_ALL}")
def print_credits():

    print(f"{Fore.WHITE}Made By Mikey{Style.RESET_ALL}")
    print(f"{Fore.WHITE}GBYT TEAM : discord.gg/bytt{Style.RESET_ALL}")
    print(f"{Fore.WHITE}My Github : https://github.com/tcp000{Style.RESET_ALL}")
def print_banner():
    banner = f"""
{Fore.WHITE}
 ██████╗  █████╗ ████████╗    ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ 
 ██╔══██╗██╔══██╗╚══██╔══╝    ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗
 ██████╔╝███████║   ██║       ███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝
 ██╔══██╗██╔══██║   ██║       ██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗
 ██║  ██║██║  ██║   ██║       ██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║
 ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝                                                                                                                                                                                   
                                                                                 
                </:>
   Version: 1.0 / Author: Mikey
    

{Style.RESET_ALL}
"""
    print(banner)

def main():
    print_banner()

    while True:
        print(f"{Fore.CYAN}Options{Style.RESET_ALL}")
        print(f"{Fore.YELLOW} 1 - Scan & Remove Rats")
        print(f" 2 - CleanUp Temporary Files")
        print(f" 3 - Credits")
        print(f" 0 - Exit{Style.RESET_ALL}")

        choice = input(f"{Fore.MAGENTA}Select An Option: {Fore.RESET}").strip()

        if choice == '1':
            scan_and_prompt_removal()
        elif choice == '2':
            cleanup_temporary_files()
        elif choice == '3':
            print_credits()
        elif choice == '0':
            print(f"{Fore.GREEN}Exiting... Stay Secure!{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
