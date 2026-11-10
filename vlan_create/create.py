import tkinter as tk
from tkinter import messagebox, filedialog

def generate_config():
    try:
        vlan_id = vlan_id_entry.get()
        vlan_name = vlan_name_entry.get()
        enable_firewall = firewall_var.get()

        if not vlan_id or not vlan_name:
            messagebox.showerror("Error", "VLAN ID and Name are required!")
            return

        vlan_id_int = int(vlan_id)
        if vlan_id_int < 1 or vlan_id_int > 4094:
            raise ValueError("VLAN ID must be between 1-4094")

        # Auto IP scheme
        network = f"172.16.{vlan_id}.0/24"
        gateway = f"172.16.{vlan_id}.1"
        pool_start = f"172.16.{vlan_id}.100"
        pool_end = f"172.16.{vlan_id}.200"

        config = []

        config.append(f"# VLAN {vlan_id} - {vlan_name}")
        config.append(f"/interface vlan add name={vlan_name} vlan-id={vlan_id} interface=bridge")

        config.append(f"/ip pool add name={vlan_name}_POOL ranges={pool_start}-{pool_end}")
        config.append(f"/ip address add address={gateway}/24 interface={vlan_name}")

        config.append(f"/ip dhcp-server add name={vlan_name}_DHCP interface={vlan_name} address-pool={vlan_name}_POOL disabled=no")
        config.append(f"/ip dhcp-server network add address={network} gateway={gateway} dns-server=8.8.8.8")

        if enable_firewall:
            config.append(f"/ip firewall filter add chain=forward action=accept src-address={network}")

        final_config = "\n".join(config)

        output_box.delete("1.0", tk.END)
        output_box.insert(tk.END, final_config)

    except Exception as e:
        messagebox.showerror("Error", str(e))


def copy_to_clipboard():
    content = output_box.get("1.0", tk.END)
    if not content.strip():
        messagebox.showerror("Error", "Nothing to copy!")
        return

    root.clipboard_clear()
    root.clipboard_append(content)
    messagebox.showinfo("Copied", "Configuration copied to clipboard!")


def export_rsc():
    content = output_box.get("1.0", tk.END).strip()
    if not content:
        messagebox.showerror("Error", "Nothing to export!")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".rsc",
        filetypes=[("MikroTik Script", "*.rsc")]
    )

    if file_path:
        with open(file_path, "w") as f:
            f.write(content)
        messagebox.showinfo("Success", "Exported successfully!")


# ================= UI =================

root = tk.Tk()
root.title("MikroTik VLAN Generator Pro")
root.geometry("800x800")
root.minsize(700, 800)

# -------- Input Section --------
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="VLAN ID").grid(row=0, column=0, padx=5, pady=5, sticky="e")
vlan_id_entry = tk.Entry(input_frame, width=20)
vlan_id_entry.grid(row=0, column=1, padx=5)

tk.Label(input_frame, text="VLAN Name").grid(row=1, column=0, padx=5, pady=5, sticky="e")
vlan_name_entry = tk.Entry(input_frame, width=20)
vlan_name_entry.grid(row=1, column=1, padx=5)

firewall_var = tk.BooleanVar()
tk.Checkbutton(input_frame, text="Include Firewall Rule", variable=firewall_var).grid(row=2, columnspan=2, pady=5)

tk.Button(root, text="Generate Config", command=generate_config, height=2, width=20).pack(pady=10)

# -------- Output Section --------
output_frame = tk.Frame(root)
output_frame.pack(fill="both", expand=True, padx=10, pady=10)

scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side="right", fill="y")

output_box = tk.Text(
    output_frame,
    yscrollcommand=scrollbar.set,
    wrap="none",  # prevents line wrapping (better for configs)
    font=("Consolas", 10)
)
output_box.pack(fill="both", expand=True)

scrollbar.config(command=output_box.yview)

# -------- Bottom Buttons --------
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Copy to Clipboard", command=copy_to_clipboard, width=20).grid(row=0, column=0, padx=10)
tk.Button(button_frame, text="Export as .rsc", command=export_rsc, width=20).grid(row=0, column=1, padx=10)

root.mainloop()