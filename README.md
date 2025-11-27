# Automated_Image_Steganography

It is a comprehensive automated steganography suite designed for bulk data hiding and extraction. It leverages the **Least Significant Bit (LSB)** algorithm to embed secret text messages or sensitive files covertly inside images. Built with a modern `CustomTkinter` GUI, it features multi-threading for responsive performance and an automation engine capable of generating its own cover images from the internet.

---
## ✨ Contributors  
@Viston-Shon
@leema16
@lahari-i
    
---  

## 🚀 Key Features

### 1. Dual-Mode Payload Encryption
* **Text Mode:** Hide secret text strings directly into images.
* **File Mode:** Embed entire files (PDFs, ZIPs, TXT, etc.) covertly. The system automatically injects a custom header (`__FILE__filename#####`) to ensure the decoder can identify and reconstruct the original file perfectly.

### 2. Intelligent Cover Image Sourcing
* **Auto-Generation (Internet):** Automatically downloads high-quality, random "real-life" images from the web (via Picsum) to use as cover carriers. This ensures every payload looks like a unique, harmless photo.
* **Local Folder Support:** Option to process an entire directory of your own images (`input_images`) in bulk.

### 3. Automated Batch Processing
* **Bulk Encryption:** Generate dozens of stego-images in seconds without manual intervention.
* **Batch Extraction:** Point the tool at a folder of suspicious images, and it will automatically scan all of them, identifying and extracting any hidden text or files.

### 4. Robust & Responsive Architecture
* **Modern Interface:** Clean, dark-themed GUI using `CustomTkinter`.
* **Multithreading:** Heavy tasks (downloading images, scanning folders) run on background threads, preventing UI freezes.
* **Network Resilience:** Includes robust error handling and SSL bypass to ensure reliable image downloading even on restrictive networks.

---

## 🛠️ Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/YourUsername/AutoPixelStego.git](https://github.com/YourUsername/AutoPixelStego.git)
    cd AutoPixelStego
    ```

2.  **Install Dependencies**
    Ensure you have Python installed, then run:
    ```bash
    pip install customtkinter pillow requests
    ```

---

## 💻 Usage Guide

### Launching the Application
Run the main automation script:
```bash
python automation.py
