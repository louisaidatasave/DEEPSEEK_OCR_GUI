"""
主視窗類別
"""

import customtkinter as ctk
from tkinter import messagebox
import sys
from pathlib import Path

# 添加專案根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src import get_memory_manager, OCREngine
from src.version_info import PROJECT_NAME, PROJECT_VERSION
from .single_image_tab import SingleImageTab
from .batch_tab import BatchTab
from .pdf_tab import PDFTab
from .settings_dialog import SettingsDialog


class MainWindow(ctk.CTk):
    """主視窗類別"""
    
    def __init__(self):
        super().__init__()
        
        # 視窗設定
        self.title(f"{PROJECT_NAME} v{PROJECT_VERSION}")
        self.geometry("1200x800")
        
        # 置中顯示
        self.center_window()
        
        # 設定主題
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 初始化記憶體管理器和 OCR 引擎
        self.memory_manager = get_memory_manager()
        self.ocr_engine = None  # 延遲載入
        
        # 建立 UI
        self.create_menu()
        self.create_main_layout()
        self.create_status_bar()
        
        # 啟動監控更新
        self.update_status()
    
    def center_window(self):
        """將視窗置中"""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_menu(self):
        """建立選單列"""
        # CustomTkinter 不直接支援選單，使用 tkinter 的 Menu
        import tkinter as tk
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # 檔案選單
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="檔案(F)", menu=file_menu)
        file_menu.add_command(label="開啟檔案 (Ctrl+O)", command=self.open_file)
        file_menu.add_command(label="儲存結果 (Ctrl+S)", command=self.save_result)
        file_menu.add_separator()
        file_menu.add_command(label="退出 (Ctrl+Q)", command=self.quit_app)
        
        # 工具選單
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具(T)", menu=tools_menu)
        tools_menu.add_command(label="設定 (Ctrl+,)", command=self.open_settings)
        tools_menu.add_command(label="清理快取", command=self.clear_cache)
        tools_menu.add_separator()
        tools_menu.add_command(label="開啟輸出目錄", command=self.open_output_dir)
        
        # 說明選單
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="說明(H)", menu=help_menu)
        help_menu.add_command(label="使用說明", command=self.show_help)
        help_menu.add_command(label="關於", command=self.show_about)
        
        # 綁定快捷鍵
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-s>', lambda e: self.save_result())
        self.bind('<Control-q>', lambda e: self.quit_app())
        self.bind('<Control-comma>', lambda e: self.open_settings())
    
    def create_main_layout(self):
        """建立主要布局"""
        # 主容器
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        # 左側：頁籤區域
        self.left_frame = ctk.CTkFrame(self.main_container)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # 建立頁籤視圖
        self.tabview = ctk.CTkTabview(self.left_frame)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 添加頁籤
        self.tab_single = self.tabview.add("單張圖片 OCR")
        self.tab_batch = self.tabview.add("批次處理")
        self.tab_pdf = self.tabview.add("PDF 處理")
        
        # 初始化 OCR 引擎（延遲載入）
        self.init_ocr_engine()
        
        # 建立單張圖片頁籤
        self.single_image_tab = SingleImageTab(
            self.tab_single, 
            self.ocr_engine,
            status_callback=self.update_status_text
        )
        self.single_image_tab.pack(fill="both", expand=True)
        
        # 建立批次處理頁籤
        self.batch_tab = BatchTab(
            self.tab_batch,
            self.ocr_engine,
            status_callback=self.update_status_text
        )
        self.batch_tab.pack(fill="both", expand=True)
        
        # 建立 PDF 處理頁籤
        self.pdf_tab = PDFTab(
            self.tab_pdf,
            self.ocr_engine,
            status_callback=self.update_status_text
        )
        self.pdf_tab.pack(fill="both", expand=True)
        
        # 右側：監控面板
        self.right_frame = ctk.CTkFrame(self.main_container, width=200)
        self.right_frame.pack(side="right", fill="y", padx=(5, 0))
        self.right_frame.pack_propagate(False)
        
        self.create_monitor_panel()
    
    def create_monitor_panel(self):
        """建立監控面板"""
        # 標題
        title = ctk.CTkLabel(self.right_frame, text="系統監控", 
                            font=("Arial", 16, "bold"))
        title.pack(pady=(10, 20))
        
        # GPU 資訊
        gpu_frame = ctk.CTkFrame(self.right_frame)
        gpu_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(gpu_frame, text="GPU", font=("Arial", 12, "bold")).pack(pady=5)
        self.gpu_name_label = ctk.CTkLabel(gpu_frame, text="檢測中...", 
                                          font=("Arial", 10))
        self.gpu_name_label.pack()
        
        # VRAM 進度條
        vram_frame = ctk.CTkFrame(self.right_frame)
        vram_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(vram_frame, text="VRAM", font=("Arial", 12, "bold")).pack(pady=5)
        self.vram_progress = ctk.CTkProgressBar(vram_frame)
        self.vram_progress.pack(fill="x", padx=10, pady=5)
        self.vram_progress.set(0)
        
        self.vram_label = ctk.CTkLabel(vram_frame, text="0.0 / 0.0 GB", 
                                      font=("Arial", 10))
        self.vram_label.pack()
        
        # CPU 使用率
        cpu_frame = ctk.CTkFrame(self.right_frame)
        cpu_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(cpu_frame, text="CPU", font=("Arial", 12, "bold")).pack(pady=5)
        self.cpu_progress = ctk.CTkProgressBar(cpu_frame)
        self.cpu_progress.pack(fill="x", padx=10, pady=5)
        self.cpu_progress.set(0)
        
        self.cpu_label = ctk.CTkLabel(cpu_frame, text="0.0%", font=("Arial", 10))
        self.cpu_label.pack()
        
        # RAM 使用率
        ram_frame = ctk.CTkFrame(self.right_frame)
        ram_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(ram_frame, text="RAM", font=("Arial", 12, "bold")).pack(pady=5)
        self.ram_progress = ctk.CTkProgressBar(ram_frame)
        self.ram_progress.pack(fill="x", padx=10, pady=5)
        self.ram_progress.set(0)
        
        self.ram_label = ctk.CTkLabel(ram_frame, text="0 / 0 GB", font=("Arial", 10))
        self.ram_label.pack()
        
        # 分隔線
        ctk.CTkFrame(self.right_frame, height=2).pack(fill="x", padx=10, pady=20)
        
        # 快捷操作按鈕
        ctk.CTkButton(self.right_frame, text="🗑️ 清理快取", 
                     command=self.clear_cache).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.right_frame, text="🔄 重載模型", 
                     command=self.reload_model).pack(fill="x", padx=10, pady=5)
        ctk.CTkButton(self.right_frame, text="📁 開啟輸出", 
                     command=self.open_output_dir).pack(fill="x", padx=10, pady=5)
    
    def init_ocr_engine(self):
        """初始化 OCR 引擎"""
        try:
            self.ocr_engine = OCREngine(model_path="./models/deepseek-ocr")
            # 不立即載入模型，等到需要時再載入
        except Exception as e:
            messagebox.showerror("錯誤", f"初始化 OCR 引擎失敗:\n{e}")
            self.ocr_engine = None
    
    def create_status_bar(self):
        """建立狀態列"""
        self.status_bar = ctk.CTkFrame(self, height=30)
        self.status_bar.pack(fill="x", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="就緒", 
                                        font=("Arial", 10))
        self.status_label.pack(side="left", padx=10)
    
    def update_status_text(self, text):
        """更新狀態文字"""
        self.status_label.configure(text=text)
    
    def update_status(self):
        """更新狀態資訊"""
        try:
            # 更新 VRAM
            memory_info = self.memory_manager.get_vram_usage()
            
            if memory_info.cuda_available:
                self.gpu_name_label.configure(text=memory_info.device_name[:20])
                vram_percent = memory_info.vram_usage_percent / 100
                self.vram_progress.set(vram_percent)
                self.vram_label.configure(
                    text=f"{memory_info.vram_used_gb:.1f} / {memory_info.vram_total_gb:.1f} GB"
                )
            else:
                self.gpu_name_label.configure(text="CUDA 不可用")
                self.vram_progress.set(0)
                self.vram_label.configure(text="N/A")
            
            # 更新 CPU 和 RAM
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.1) / 100
            self.cpu_progress.set(cpu_percent)
            self.cpu_label.configure(text=f"{cpu_percent * 100:.1f}%")
            
            ram = psutil.virtual_memory()
            ram_percent = ram.percent / 100
            self.ram_progress.set(ram_percent)
            self.ram_label.configure(
                text=f"{ram.used / 1024**3:.1f} / {ram.total / 1024**3:.1f} GB"
            )
        
        except Exception as e:
            print(f"更新狀態失敗: {e}")
        
        # 每秒更新一次
        self.after(1000, self.update_status)
    
    # 選單命令
    def open_file(self):
        """開啟檔案"""
        messagebox.showinfo("提示", "開啟檔案功能開發中")
    
    def save_result(self):
        """儲存結果"""
        messagebox.showinfo("提示", "儲存結果功能開發中")
    
    def quit_app(self):
        """退出應用程式"""
        if messagebox.askokcancel("退出", "確定要退出嗎？"):
            self.quit()
    
    def open_settings(self):
        """開啟設定"""
        SettingsDialog(self)
    
    def clear_cache(self):
        """清理快取"""
        try:
            self.memory_manager.clear_cache()
            self.status_label.configure(text="快取已清理")
            messagebox.showinfo("成功", "快取清理完成")
        except Exception as e:
            messagebox.showerror("錯誤", f"清理快取失敗: {e}")
    
    def reload_model(self):
        """重載模型"""
        messagebox.showinfo("提示", "重載模型功能開發中")
    
    def open_output_dir(self):
        """開啟輸出目錄"""
        import os
        import subprocess
        output_dir = Path("outputs")
        output_dir.mkdir(exist_ok=True)
        
        if os.name == 'nt':  # Windows
            os.startfile(output_dir)
        else:
            subprocess.Popen(['xdg-open', output_dir])
    
    def show_help(self):
        """顯示使用說明"""
        help_text = """
DeepSeek-OCR 使用說明

快捷鍵:
  Ctrl+O - 開啟檔案
  Ctrl+S - 儲存結果
  Ctrl+Q - 退出
  Ctrl+, - 設定

功能:
  • 單張圖片 OCR
  • 批次處理
  • PDF 處理

更多資訊請參考 docs/SOP_v1.md
        """
        messagebox.showinfo("使用說明", help_text)
    
    def show_about(self):
        """顯示關於"""
        about_text = f"""
{PROJECT_NAME} v{PROJECT_VERSION}

DeepSeek-OCR 本地部署系統

功能:
  • 單張圖片 OCR
  • 批次處理
  • PDF 文件處理
  • 智慧記憶體管理
  • 效能追蹤

© 2025 DeepSeek-OCR
        """
        messagebox.showinfo("關於", about_text)
