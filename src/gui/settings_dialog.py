"""
設定對話框
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
from pathlib import Path
import json


class SettingsDialog(ctk.CTkToplevel):
    """設定對話框類別"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("系統設定")
        self.geometry("600x700")
        
        # 置中顯示
        self.center_window()
        
        # 載入當前設定
        self.load_settings()
        
        # 建立 UI
        self.create_widgets()
        
        # 設為模態對話框
        self.transient(parent)
        self.grab_set()
    
    def center_window(self):
        """將視窗置中"""
        self.update_idletasks()
        width = 600
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_settings(self):
        """載入設定"""
        try:
            config_file = Path("config/system_config.json")
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.settings = self.get_default_settings()
        except Exception as e:
            print(f"載入設定失敗: {e}")
            self.settings = self.get_default_settings()
    
    def get_default_settings(self):
        """取得預設設定"""
        return {
            "device": {
                "type": "cuda",
                "fallback_to_cpu": True,
                "cuda_device_id": 0
            },
            "model": {
                "torch_dtype": "bfloat16",
                "base_size": 1024,
                "image_size": 1024,
                "crop_mode": False
            },
            "memory": {
                "vram_threshold": 0.9,
                "auto_clear_cache": True,
                "max_batch_size": 8
            },
            "paths": {
                "model_dir": "./models/deepseek-ocr",
                "output_dir": "./outputs",
                "log_dir": "./outputs/logs"
            },
            "pdf": {
                "dpi": 200,
                "output_format": "PNG",
                "max_pages": 100
            },
            "logging": {
                "level": "INFO",
                "console_output": True,
                "file_output": True,
                "colored": True
            }
        }
    
    def create_widgets(self):
        """建立介面元件"""
        # 建立捲動框架
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 裝置設定
        device_frame = ctk.CTkFrame(main_frame)
        device_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(device_frame, text="裝置設定", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        device_row = ctk.CTkFrame(device_frame)
        device_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(device_row, text="運算裝置:").pack(side="left", padx=5)
        self.device_var = ctk.StringVar(value=self.settings["device"]["type"])
        ctk.CTkComboBox(device_row, values=["cuda", "cpu"], 
                       variable=self.device_var, width=100).pack(side="left", padx=5)
        
        self.fallback_var = ctk.BooleanVar(value=self.settings["device"]["fallback_to_cpu"])
        ctk.CTkCheckBox(device_frame, text="GPU 失敗時自動切換 CPU", 
                       variable=self.fallback_var).pack(anchor="w", padx=10, pady=5)
        
        # 模型設定
        model_frame = ctk.CTkFrame(main_frame)
        model_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(model_frame, text="模型設定", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        model_row1 = ctk.CTkFrame(model_frame)
        model_row1.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(model_row1, text="Base Size:").pack(side="left", padx=5)
        self.base_size_var = ctk.IntVar(value=self.settings["model"]["base_size"])
        ctk.CTkEntry(model_row1, textvariable=self.base_size_var, 
                    width=80).pack(side="left", padx=5)
        
        ctk.CTkLabel(model_row1, text="Image Size:").pack(side="left", padx=(20, 5))
        self.image_size_var = ctk.IntVar(value=self.settings["model"]["image_size"])
        ctk.CTkEntry(model_row1, textvariable=self.image_size_var, 
                    width=80).pack(side="left", padx=5)
        
        self.crop_mode_var = ctk.BooleanVar(value=self.settings["model"]["crop_mode"])
        ctk.CTkCheckBox(model_frame, text="預設啟用裁切模式", 
                       variable=self.crop_mode_var).pack(anchor="w", padx=10, pady=5)
        
        # 記憶體設定
        memory_frame = ctk.CTkFrame(main_frame)
        memory_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(memory_frame, text="記憶體設定", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        memory_row1 = ctk.CTkFrame(memory_frame)
        memory_row1.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(memory_row1, text="VRAM 警戒值 (%):").pack(side="left", padx=5)
        self.vram_threshold_var = ctk.IntVar(
            value=int(self.settings["memory"]["vram_threshold"] * 100))
        ctk.CTkEntry(memory_row1, textvariable=self.vram_threshold_var, 
                    width=80).pack(side="left", padx=5)
        
        ctk.CTkLabel(memory_row1, text="最大批次大小:").pack(side="left", padx=(20, 5))
        self.max_batch_var = ctk.IntVar(value=self.settings["memory"]["max_batch_size"])
        ctk.CTkEntry(memory_row1, textvariable=self.max_batch_var, 
                    width=80).pack(side="left", padx=5)
        
        self.auto_clear_var = ctk.BooleanVar(value=self.settings["memory"]["auto_clear_cache"])
        ctk.CTkCheckBox(memory_frame, text="自動清理快取", 
                       variable=self.auto_clear_var).pack(anchor="w", padx=10, pady=5)
        
        # 路徑設定
        paths_frame = ctk.CTkFrame(main_frame)
        paths_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(paths_frame, text="路徑設定", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        # 模型路徑
        model_path_row = ctk.CTkFrame(paths_frame)
        model_path_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(model_path_row, text="模型目錄:").pack(side="left", padx=5)
        self.model_dir_var = ctk.StringVar(value=self.settings["paths"]["model_dir"])
        ctk.CTkEntry(model_path_row, textvariable=self.model_dir_var, 
                    width=300).pack(side="left", padx=5)
        ctk.CTkButton(model_path_row, text="瀏覽", 
                     command=lambda: self.browse_dir(self.model_dir_var), 
                     width=60).pack(side="left", padx=5)
        
        # 輸出路徑
        output_path_row = ctk.CTkFrame(paths_frame)
        output_path_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(output_path_row, text="輸出目錄:").pack(side="left", padx=5)
        self.output_dir_var = ctk.StringVar(value=self.settings["paths"]["output_dir"])
        ctk.CTkEntry(output_path_row, textvariable=self.output_dir_var, 
                    width=300).pack(side="left", padx=5)
        ctk.CTkButton(output_path_row, text="瀏覽", 
                     command=lambda: self.browse_dir(self.output_dir_var), 
                     width=60).pack(side="left", padx=5)
        
        # PDF 設定
        pdf_frame = ctk.CTkFrame(main_frame)
        pdf_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(pdf_frame, text="PDF 設定", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        pdf_row = ctk.CTkFrame(pdf_frame)
        pdf_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(pdf_row, text="預設 DPI:").pack(side="left", padx=5)
        self.pdf_dpi_var = ctk.IntVar(value=self.settings["pdf"]["dpi"])
        ctk.CTkEntry(pdf_row, textvariable=self.pdf_dpi_var, 
                    width=80).pack(side="left", padx=5)
        
        ctk.CTkLabel(pdf_row, text="格式:").pack(side="left", padx=(20, 5))
        self.pdf_format_var = ctk.StringVar(value=self.settings["pdf"]["output_format"])
        ctk.CTkComboBox(pdf_row, values=["PNG", "JPEG"], 
                       variable=self.pdf_format_var, width=100).pack(side="left", padx=5)
        
        ctk.CTkLabel(pdf_row, text="最大頁數:").pack(side="left", padx=(20, 5))
        self.pdf_max_pages_var = ctk.IntVar(value=self.settings["pdf"]["max_pages"])
        ctk.CTkEntry(pdf_row, textvariable=self.pdf_max_pages_var, 
                    width=80).pack(side="left", padx=5)
        
        # 日誌設定
        log_frame = ctk.CTkFrame(main_frame)
        log_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(log_frame, text="日誌設定", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        log_row = ctk.CTkFrame(log_frame)
        log_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(log_row, text="日誌等級:").pack(side="left", padx=5)
        self.log_level_var = ctk.StringVar(value=self.settings["logging"]["level"])
        ctk.CTkComboBox(log_row, values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                       variable=self.log_level_var, width=100).pack(side="left", padx=5)
        
        self.log_console_var = ctk.BooleanVar(value=self.settings["logging"]["console_output"])
        ctk.CTkCheckBox(log_frame, text="終端機輸出", 
                       variable=self.log_console_var).pack(anchor="w", padx=10, pady=2)
        
        self.log_file_var = ctk.BooleanVar(value=self.settings["logging"]["file_output"])
        ctk.CTkCheckBox(log_frame, text="檔案輸出", 
                       variable=self.log_file_var).pack(anchor="w", padx=10, pady=2)
        
        self.log_colored_var = ctk.BooleanVar(value=self.settings["logging"]["colored"])
        ctk.CTkCheckBox(log_frame, text="彩色輸出", 
                       variable=self.log_colored_var).pack(anchor="w", padx=10, pady=2)
        
        # 按鈕
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="💾 儲存", 
                     command=self.save_settings, 
                     width=120, fg_color="green").pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="🔄 重置為預設值", 
                     command=self.reset_to_default, 
                     width=120).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="❌ 取消", 
                     command=self.destroy, 
                     width=120).pack(side="right", padx=5)
    
    def browse_dir(self, var):
        """瀏覽目錄"""
        folder = filedialog.askdirectory(title="選擇目錄")
        if folder:
            var.set(folder)
    
    def save_settings(self):
        """儲存設定"""
        try:
            # 更新設定
            self.settings["device"]["type"] = self.device_var.get()
            self.settings["device"]["fallback_to_cpu"] = self.fallback_var.get()
            
            self.settings["model"]["base_size"] = self.base_size_var.get()
            self.settings["model"]["image_size"] = self.image_size_var.get()
            self.settings["model"]["crop_mode"] = self.crop_mode_var.get()
            
            self.settings["memory"]["vram_threshold"] = self.vram_threshold_var.get() / 100
            self.settings["memory"]["max_batch_size"] = self.max_batch_var.get()
            self.settings["memory"]["auto_clear_cache"] = self.auto_clear_var.get()
            
            self.settings["paths"]["model_dir"] = self.model_dir_var.get()
            self.settings["paths"]["output_dir"] = self.output_dir_var.get()
            
            self.settings["pdf"]["dpi"] = self.pdf_dpi_var.get()
            self.settings["pdf"]["output_format"] = self.pdf_format_var.get()
            self.settings["pdf"]["max_pages"] = self.pdf_max_pages_var.get()
            
            self.settings["logging"]["level"] = self.log_level_var.get()
            self.settings["logging"]["console_output"] = self.log_console_var.get()
            self.settings["logging"]["file_output"] = self.log_file_var.get()
            self.settings["logging"]["colored"] = self.log_colored_var.get()
            
            # 儲存到檔案
            config_file = Path("config/system_config.json")
            config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("成功", "設定已儲存！\n部分設定需要重新啟動才會生效。")
            self.destroy()
        
        except Exception as e:
            messagebox.showerror("錯誤", f"儲存設定失敗:\n{e}")
    
    def reset_to_default(self):
        """重置為預設值"""
        if messagebox.askyesno("確認", "確定要重置為預設值嗎？"):
            self.settings = self.get_default_settings()
            self.destroy()
            # 重新開啟對話框
            SettingsDialog(self.master)
