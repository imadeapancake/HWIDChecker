import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import subprocess
import threading
from datetime import datetime
import time

def get_info(command):
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        lines = output.decode().strip().split('\n')
        return lines[1].strip() if len(lines) > 1 else "N/A"
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving information with command '{command}': {e.output.decode().strip()}")
        return "N/A"

def convert_bios_date(date_str):
    try:
        return datetime.strptime(date_str.split('.')[0], "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error converting BIOS date '{date_str}':", e)
        return date_str

def get_mac_addresses():
    try:
        output = subprocess.check_output("wmic nic where NetEnabled=true get MACAddress", shell=True, stderr=subprocess.STDOUT)
        lines = output.decode().strip().split('\n')
        mac_addresses = [line.strip() for line in lines if line.strip() and "MACAddress" not in line]
        return mac_addresses
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving MAC addresses: {e.output.decode().strip()}")
        return ["N/A"]

def get_disk_drives():
    try:
        output = subprocess.check_output("wmic diskdrive get SerialNumber,Model", shell=True, stderr=subprocess.STDOUT)
        lines = output.decode().strip().split('\n')[1:]  # Skip the header line
        disks = [line.strip() for line in lines if line.strip()]
        return disks
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving disk drives: {e.output.decode().strip()}")
        return ["N/A"]

def get_system_info():
    info = {
        "System Manufacturer": get_info("wmic computersystem get Manufacturer"),
        "System Model": get_info("wmic computersystem get Model"),
        "System SKU": get_info("wmic computersystem get SystemSKUNumber"),
        "System Serial Number": get_info("wmic csproduct get IdentifyingNumber"),
        "OS Name": get_info("wmic os get Caption"),
        "OS Version": get_info("wmic os get Version"),
        "OS Architecture": get_info("wmic os get OSArchitecture"),
        "CPU": get_info("wmic cpu get Name"),
        "CPU Cores": get_info("wmic cpu get NumberOfCores"),
        "CPU Threads": get_info("wmic cpu get NumberOfLogicalProcessors"),
        "Total Memory": get_info("wmic computersystem get TotalPhysicalMemory"),
        "GPU": get_info("wmic path win32_videocontroller get Name"),
        "Network Adapters": "\n".join([
            f"MAC Address {i + 1}: {mac}" for i, mac in enumerate(get_mac_addresses())
        ]),
        "BIOS Release Date": convert_bios_date(get_info("wmic bios get ReleaseDate")),
        "BIOS Vendor": get_info("wmic bios get Manufacturer"),
        "BIOS Version": get_info("wmic bios get SMBIOSBIOSVersion"),
        "SMBIOS Family": get_info("wmic computersystem get SystemFamily"),
        "Product Name": get_info("wmic computersystem get Name"),
        "Motherboard Manufacturer": get_info("wmic baseboard get Manufacturer"),
        "Motherboard Product": get_info("wmic baseboard get Product"),
        "Chassis Manufacturer": get_info("wmic systemenclosure get Manufacturer"),
        "Chassis Serial Number": get_info("wmic systemenclosure get SerialNumber"),
        "Chassis Version": get_info("wmic systemenclosure get Version")
    }
    return info

def get_hwid_values():
    hwid = {
        "Motherboard Serial Number": get_info("wmic baseboard get SerialNumber"),
        "Disk Drives": "\n".join([
            f"Disk {i + 1}: {disk}" for i, disk in enumerate(get_disk_drives())
        ]),
        "MAC Addresses": "\n".join([
            f"MAC Address {i + 1}: {mac}" for i, mac in enumerate(get_mac_addresses())
        ]),
        "CPU Serial Number": get_info("wmic cpu get ProcessorId"),
        "GPU Serial Number": get_info("wmic path win32_videocontroller get PNPDeviceID")
    }
    return hwid

def display_info():
    system_info = get_system_info()
    system_tree["columns"] = ("Parameter", "Value")

    max_len_param = max(len(str(key)) for key in system_info.keys())
    max_len_value = max(len(str(value)) for value in system_info.values())

    system_tree.column("#0", width=0)
    system_tree.column("Parameter", width=max_len_param * 10)
    system_tree.column("Value", width=max_len_value * 10)

    for col in system_tree["columns"]:
        system_tree.heading(col, text=col)

    for key, value in system_info.items():
        system_tree.insert("", "end", values=(key, value))

    hwid_values = get_hwid_values()
    hwid_tree["columns"] = ("Parameter", "Value")

    max_len_param = max(len(str(key)) for key in hwid_values.keys())
    max_len_value = max(len(str(value)) for value in hwid_values.values())

    hwid_tree.column("#0", width=0)
    hwid_tree.column("Parameter", width=max_len_param * 10)
    hwid_tree.column("Value", width=max_len_value * 10)

    for col in hwid_tree["columns"]:
        hwid_tree.heading(col, text=col)

    for key, value in hwid_values.items():
        hwid_tree.insert("", "end", values=(key, value))

def refresh_info():
    for item in system_tree.get_children():
        system_tree.delete(item)
    for item in hwid_tree.get_children():
        hwid_tree.delete(item)
    display_info()

def monitor_hardware_changes():
    def hwid_check():
        initial_hwid = get_hwid_values()
        while True:
            current_hwid = get_hwid_values()
            if initial_hwid != current_hwid:
                messagebox.showwarning("Hardware Change Detected", "A change in hardware has been detected!")
                start_time = datetime.now()
                while (datetime.now() - start_time).seconds < 15:
                    current_info = get_system_info()
                    time.sleep(1)
                messagebox.showinfo("HWID Change Details",
                                    f"Old HWID: {initial_hwid}\nNew HWID: {current_hwid}")
                refresh_info()
                initial_hwid = current_hwid
            time.sleep(1)
    
    hwid_thread = threading.Thread(target=hwid_check, daemon=True)
    hwid_thread.start()

root = ttk.Window(themename="darkly")
root.title("Pancake's HWID Checker")
root.geometry("1200x800")



style = ttk.Style()
style.configure("Treeview", rowheight=33, font=("Helvetica", 10))
style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"))

notebook = ttk.Notebook(root, bootstyle="dark")
notebook.pack(expand=True, fill="both", padx=(10, 0))

system_frame = ttk.Frame(notebook)
notebook.add(system_frame, text="System Info")

system_tree_frame = ttk.Frame(system_frame)
system_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

system_tree = ttk.Treeview(system_tree_frame, show="headings")
system_tree.pack(fill=tk.BOTH, expand=True)

hwid_frame = ttk.Frame(notebook)
notebook.add(hwid_frame, text="HWID Info")

hwid_tree_frame = ttk.Frame(hwid_frame)
hwid_tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

hwid_tree = ttk.Treeview(hwid_tree_frame, show="headings")
hwid_tree.pack(fill=tk.BOTH, expand=True)

refresh_button = ttk.Button(root, text="Refresh", command=refresh_info, bootstyle="success")
refresh_button.pack(pady=10)

monitor_hardware_changes()
display_info()

root.mainloop()
