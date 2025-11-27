import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from PIL import Image
import logic  # Reusing your logic file
import requests
from io import BytesIO
import threading

# --- CONFIGURATION ---
DEFAULT_INPUT = "input_images"
DEFAULT_OUTPUT = "stego_output"
DEFAULT_EXTRACT = "extracted_data"

# Setup Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class BatchStegoUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Auto Pixel Stego Ultimate")
        self.geometry("600x700")
        
        self.lbl_title = ctk.CTkLabel(self, text="Steganography Automation Suite", font=("Roboto", 24, "bold"), text_color="#A8C7FA")
        self.lbl_title.pack(pady=(20, 10))

        # --- TABS ---
        self.tabview = ctk.CTkTabview(self, corner_radius=15)
        self.tabview.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.tab_gen = self.tabview.add("1. Encrypt & Generate")
        self.tab_ext = self.tabview.add("2. Batch Extract")

        self.setup_encrypt_tab()
        self.setup_extract_tab()

        # Status Bar
        self.status_var = ctk.StringVar(value="Ready")
        self.lbl_status = ctk.CTkLabel(self, textvariable=self.status_var, text_color="gray", font=("Consolas", 12))
        self.lbl_status.pack(side="bottom", pady=10)

    # =================================================
    #   TAB 1: ENCRYPT & GENERATE
    # =================================================
    def setup_encrypt_tab(self):
        # A. WHAT TO HIDE
        frame_secret = ctk.CTkFrame(self.tab_gen)
        frame_secret.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(frame_secret, text="Payload (Secret Data)", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        self.secret_mode = ctk.StringVar(value="text")
        frame_opts = ctk.CTkFrame(frame_secret, fg_color="transparent")
        frame_opts.pack(fill="x", padx=10)
        ctk.CTkRadioButton(frame_opts, text="Text Message", variable=self.secret_mode, value="text", command=self.toggle_secret_ui).pack(side="left", padx=10)
        ctk.CTkRadioButton(frame_opts, text="Secret File", variable=self.secret_mode, value="file", command=self.toggle_secret_ui).pack(side="left", padx=10)

        self.entry_text = ctk.CTkEntry(frame_secret, placeholder_text="Type secret message here...")
        self.entry_text.pack(fill="x", padx=10, pady=10)
        
        self.btn_file = ctk.CTkButton(frame_secret, text="Select File", fg_color="#2D2D2D", command=self.select_secret_file)
        self.lbl_file_sel = ctk.CTkLabel(frame_secret, text="No file selected", font=("Roboto", 11, "italic"))
        self.secret_file_path = None

        # B. COVER IMAGE SOURCE
        frame_source = ctk.CTkFrame(self.tab_gen)
        frame_source.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(frame_source, text="Cover Images", font=("Roboto", 14, "bold")).pack(anchor="w", padx=10, pady=5)

        self.source_mode = ctk.StringVar(value="generate")
        ctk.CTkRadioButton(frame_source, text="Download Real-Life Images (Internet)", variable=self.source_mode, value="generate", command=self.toggle_source_ui).pack(anchor="w", padx=20, pady=5)
        
        # Gen Options
        self.frame_gen = ctk.CTkFrame(frame_source, fg_color="transparent")
        self.frame_gen.pack(fill="x", padx=40, pady=5)
        self.entry_count = ctk.CTkEntry(self.frame_gen, width=60, placeholder_text="Qty")
        self.entry_count.insert(0, "3")
        self.entry_count.pack(side="left", padx=(0, 10))
        ctk.CTkLabel(self.frame_gen, text="images").pack(side="left")

        ctk.CTkRadioButton(frame_source, text="Use Local Folder", variable=self.source_mode, value="folder", command=self.toggle_source_ui).pack(anchor="w", padx=20, pady=5)
        self.btn_local_folder = ctk.CTkButton(frame_source, text="Select Input Folder", command=self.select_input_folder, state="disabled")
        self.btn_local_folder.pack(padx=40, pady=5, anchor="w")
        self.input_folder_path = DEFAULT_INPUT

        self.btn_run_enc = ctk.CTkButton(self.tab_gen, text="START BATCH ENCRYPTION", command=lambda: threading.Thread(target=self.run_encryption).start(), 
                                     fg_color="#0B57D0", height=45, font=("Roboto", 15, "bold"))
        self.btn_run_enc.pack(pady=20, padx=20, fill="x", side="bottom")

        self.toggle_secret_ui()
        self.toggle_source_ui()

    # =================================================
    #   TAB 2: BATCH EXTRACT
    # =================================================
    def setup_extract_tab(self):
        ctk.CTkLabel(self.tab_ext, text="Batch Decryption", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.btn_ext_input = ctk.CTkButton(self.tab_ext, text="Select Folder to Scan", command=self.select_extract_input)
        self.btn_ext_input.pack(pady=10)
        self.lbl_ext_input = ctk.CTkLabel(self.tab_ext, text="No folder selected", text_color="gray")
        self.lbl_ext_input.pack()
        self.ext_input_path = None

        ctk.CTkLabel(self.tab_ext, text="⬇").pack(pady=5)
        
        self.btn_ext_run = ctk.CTkButton(self.tab_ext, text="EXTRACT ALL SECRETS", command=lambda: threading.Thread(target=self.run_decryption).start(),
                                         fg_color="#34A853", height=45, font=("Roboto", 15, "bold"), state="disabled")
        self.btn_ext_run.pack(pady=20, padx=20, fill="x")

        self.textbox_log = ctk.CTkTextbox(self.tab_ext, height=200)
        self.textbox_log.pack(padx=10, pady=10, fill="both", expand=True)
        self.textbox_log.insert("0.0", "Log output will appear here...")

    # =================================================
    #   HELPER: THREAD-SAFE UI UPDATES
    # =================================================
    def safe_update_status(self, text):
        self.after(0, lambda: self.status_var.set(text))

    def safe_enable_buttons(self):
        self.after(0, lambda: self.btn_run_enc.configure(state="normal"))
        self.after(0, lambda: self.btn_ext_run.configure(state="normal"))

    def safe_log(self, msg):
        self.after(0, lambda: self.log(msg))
        
    def safe_messagebox(self, title, msg):
        self.after(0, lambda: messagebox.showinfo(title, msg))

    def safe_errorbox(self, title, msg):
        self.after(0, lambda: messagebox.showerror(title, msg))

    # =================================================
    #   LOGIC & UI
    # =================================================
    def toggle_secret_ui(self):
        if self.secret_mode.get() == "text":
            self.btn_file.pack_forget()
            self.lbl_file_sel.pack_forget()
            self.entry_text.pack(fill="x", padx=10, pady=10)
        else:
            self.entry_text.pack_forget()
            self.btn_file.pack(fill="x", padx=10, pady=(10,0))
            self.lbl_file_sel.pack(pady=5)

    def toggle_source_ui(self):
        if self.source_mode.get() == "generate":
            self.frame_gen.pack(fill="x", padx=40, pady=5)
            self.btn_local_folder.configure(state="disabled")
        else:
            self.frame_gen.pack_forget()
            self.btn_local_folder.configure(state="normal")

    def select_secret_file(self):
        path = filedialog.askopenfilename()
        if path: 
            self.secret_file_path = path
            self.lbl_file_sel.configure(text=os.path.basename(path))

    def select_input_folder(self):
        path = filedialog.askdirectory()
        if path: self.input_folder_path = path

    def select_extract_input(self):
        path = filedialog.askdirectory()
        if path:
            self.ext_input_path = path
            self.lbl_ext_input.configure(text=path)
            self.btn_ext_run.configure(state="normal")

    def download_image(self):
        url = "https://picsum.photos/600/400"
        print(f"Attempting to download from: {url}") # Debug print
        try:
            # FIX 1: Increased timeout to 15 seconds for slower connections
            # FIX 2: Added verify=False to bypass SSL errors common on some Windows setups
            response = requests.get(url, timeout=15, verify=False)
            
            if response.status_code == 200:
                print("Download successful!")
                return Image.open(BytesIO(response.content))
            else:
                 print(f"Download failed with status code: {response.status_code}")
        except Exception as e:
            # This will print the exact reason why it failed in your terminal window
            print(f"Error downloading image: {e}")
            return None
        return None

    # --- ENCRYPTION PROCESS ---
    def run_encryption(self):
        # NOTE: No direct UI calls here! Use self.after via helpers
        self.after(0, lambda: self.btn_run_enc.configure(state="disabled"))
        self.safe_update_status("Preparing Payload...")
        
        # 1. Prep Data
        data = b""
        try:
            if self.secret_mode.get() == "text":
                txt = self.entry_text.get()
                if not txt: raise ValueError("Empty text")
                data = txt.encode('utf-8')
            else:
                if not self.secret_file_path: raise ValueError("No file")
                fname = os.path.basename(self.secret_file_path)
                with open(self.secret_file_path, "rb") as f:
                    data = (f"__FILE__{fname}#####").encode('utf-8') + f.read()
        except Exception as e:
            self.safe_errorbox("Error", str(e))
            self.safe_enable_buttons()
            return

        # 2. Prep Output
        if not os.path.exists(DEFAULT_OUTPUT): os.makedirs(DEFAULT_OUTPUT)
        
        count = 0
        target_qty = 0

        if self.source_mode.get() == "generate":
            try:
                target_qty = int(self.entry_count.get())
            except: target_qty = 3
            
            for i in range(target_qty):
                self.safe_update_status(f"Downloading Image {i+1}/{target_qty}...")
                img = self.download_image()
                
                if img:
                    pass 
                else:
                    img = Image.new('RGB', (6, 4), color=(100, 100, 100))
                
                save_name = f"stego_gen_{i+1}.png"
                self.process_and_save(img, data, save_name)
                count += 1
        else:
            if not os.path.exists(self.input_folder_path):
                self.safe_errorbox("Error", "Input folder not found")
                self.safe_enable_buttons()
                return
            
            files = [f for f in os.listdir(self.input_folder_path) if f.lower().endswith(('.png','.jpg'))]
            target_qty = len(files)
            
            for i, f in enumerate(files):
                self.safe_update_status(f"Processing {i+1}/{target_qty}: {f}")
                try:
                    img = Image.open(os.path.join(self.input_folder_path, f))
                    save_name = f"stego_{f.split('.')[0]}.png"
                    self.process_and_save(img, data, save_name)
                    count += 1
                except: pass

        self.safe_update_status(f"Done! {count} images saved in '{DEFAULT_OUTPUT}'")
        self.safe_messagebox("Complete", f"Batch Complete.\nSaved {count} images to folder: {DEFAULT_OUTPUT}")
        self.safe_enable_buttons()

    def process_and_save(self, img, data, name):
        new_img = img.copy()
        logic.encode_enc(new_img, data)
        new_img.save(os.path.join(DEFAULT_OUTPUT, name))

    # --- DECRYPTION PROCESS ---
    def run_decryption(self):
        self.after(0, lambda: self.btn_ext_run.configure(state="disabled"))
        self.after(0, lambda: self.textbox_log.delete("0.0", "end"))
        
        if not os.path.exists(DEFAULT_EXTRACT): os.makedirs(DEFAULT_EXTRACT)
        
        try:
            files = [f for f in os.listdir(self.ext_input_path) if f.lower().endswith('.png')]
        except Exception as e:
            self.safe_errorbox("Error", f"Could not read folder: {e}")
            self.safe_enable_buttons()
            return

        self.safe_log(f"Found {len(files)} PNG files. Scanning...\n")
        
        found_count = 0
        
        for f in files:
            try:
                self.safe_update_status(f"Scanning {f}...")
                img = Image.open(os.path.join(self.ext_input_path, f))
                decoded = logic.decode_img(img)
                
                header = b"__FILE__"
                sep = b"#####"
                
                if decoded.startswith(header):
                    # It's a file
                    start = decoded.find(sep)
                    if start != -1:
                        fname = decoded[len(header):start].decode('utf-8')
                        content = decoded[start + len(sep):]
                        
                        save_path = os.path.join(DEFAULT_EXTRACT, f"extracted_{fname}")
                        with open(save_path, "wb") as out_f:
                            out_f.write(content)
                        self.safe_log(f"[FILE FOUND] {f} -> Saved as {save_path}")
                        found_count += 1
                else:
                    # Try text
                    try:
                        txt = decoded.decode('utf-8')
                        # Filter out noise
                        if len(txt) > 0 and all(32 <= ord(c) < 127 for c in txt[:10]):
                            self.safe_log(f"[TEXT FOUND] {f}: {txt}")
                            found_count += 1
                    except: pass
            except: pass

        self.safe_update_status("Extraction Complete")
        self.safe_log(f"\nScan finished. Found hidden data in {found_count} images.")
        self.safe_enable_buttons()

    def log(self, msg):
        self.textbox_log.insert("end", msg + "\n")
        self.textbox_log.see("end")

if __name__ == "__main__":
    app = BatchStegoUI()
    app.mainloop()