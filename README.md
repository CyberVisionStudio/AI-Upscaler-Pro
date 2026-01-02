# AI Upscaler Pro | Mike Robart Edition

A professional-grade web application built with **Python Flask** that leverages advanced image processing algorithms to transform low-resolution images into high-fidelity assets. Featuring a modern **Glassmorphism** UI/UX.

---

## 🚀 Live Demo
Experience the application live here: [**AI Upscaler Pro - Official Website**](https://ai-upscaler-pro-352p.vercel.app/)

## ✨ Key Features
- **AI-Powered Upscaling**: Uses Lanczos resampling and neural-style sharpness filters.
- **Multiple Formats**: Export processed images to **PNG**, **JPG**, or **SVG**.
- **Resolution Control**: Scale images up to **2x (HD)** or **4x (Ultra 4K)**.
- **Glassmorphism UI**: A sleek, translucent interface for a premium experience.
- **Custom Branding**: Output files are named `ai-upscaler-pro` automatically.

## 🛠️ Tech Stack
- **Backend**: Python 3.x, Flask
- **Image Processing**: Pillow (PIL)
- **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript
- **Deployment**: Vercel

## 📂 Project Structure
```text
.
├── static/               # Favicon and brand assets
├── templates/            # index.html (Frontend Interface)
├── app.py                # Core Flask backend & AI logic
├── requirements.txt      # Project dependencies
├── vercel.json           # Vercel deployment configuration
└── README.md             # Project documentation
