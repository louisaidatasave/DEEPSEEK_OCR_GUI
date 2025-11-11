"""
單張圖片 OCR 頁籤
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import threading


class SingleImageTab(ctk.CTkFrame):
    """單張圖片 OCR 頁籤類別"""
    
    def __init__(self, parent, ocr_engine, status_callback=None):
        super().__init__(parent)
        
        self.ocr_engine = ocr_engine
        self.status_callback = status_callback
        self.current_image_path = None
        self.current_result = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """建立介面元件"""
        # 左側：圖片區域
        left_frame = ctk.CTkFrame(self)
        left_frame.pack(side="left", fill="both", expand=True, padx=(10, 5), pady=10)
        
        # 圖片預覽
        preview_label = ctk.CTkLabel(left_frame, text="圖片預覽", 
                                    font=("Arial", 14, "bold"))
        preview_label.pack(pady=(10, 5))
        
        self.image_frame = ctk.CTkFrame(left_frame, width=400, height=400)
        self.image_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.image_frame.pack_propagate(False)
        
        self.image_label = ctk.CTkLabel(self.image_frame, text="拖放圖片到這裡\n或點擊下方按鈕選擇", 
                                       font=("Arial", 16))
        self.image_label.pack(expand=True)
        
        # 圖片資訊
        self.info_label = ctk.CTkLabel(left_frame, text="", font=("Arial", 10))
        self.info_label.pack(pady=5)
        
        # 選擇檔案按鈕
        ctk.CTkButton(left_frame, text="📁 選擇圖片", 
                     command=self.select_image, height=40).pack(fill="x", padx=10, pady=5)
        
        # 右側：控制和結果區域
        right_frame = ctk.CTkFrame(self)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        # 處理選項
        options_frame = ctk.CTkFrame(right_frame)
        options_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(options_frame, text="處理選項", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        # Base Size
        ctk.CTkLabel(options_frame, text="Base Size:", 
                    font=("Arial", 11)).pack(anchor="w", padx=10, pady=(5, 0))
        self.base_size_var = ctk.IntVar(value=1024)
        self.base_size_slider = ctk.CTkSlider(options_frame, from_=512, to=4096, 
                                             variable=self.base_size_var, 
                                             number_of_steps=7)
        self.base_size_slider.pack(fill="x", padx=10, pady=5)
        self.base_size_label = ctk.CTkLabel(options_frame, text="1024")
        self.base_size_label.pack()
        self.base_size_var.trace_add("write", self.update_base_size_label)
        
        # Image Size
        ctk.CTkLabel(options_frame, text="Image Size:", 
                    font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 0))
        self.image_size_var = ctk.IntVar(value=1024)
        self.image_size_slider = ctk.CTkSlider(options_frame, from_=512, to=4096, 
                                              variable=self.image_size_var, 
                                              number_of_steps=7)
        self.image_size_slider.pack(fill="x", padx=10, pady=5)
        self.image_size_label = ctk.CTkLabel(options_frame, text="1024")
        self.image_size_label.pack()
        self.image_size_var.trace_add("write", self.update_image_size_label)
        
        # 選項
        self.crop_mode_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(options_frame, text="裁切模式", 
                       variable=self.crop_mode_var).pack(anchor="w", padx=10, pady=5)
        
        self.save_results_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="儲存結果", 
                       variable=self.save_results_var).pack(anchor="w", padx=10, pady=5)
        
        # 控制按鈕
        button_frame = ctk.CTkFrame(options_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        self.process_button = ctk.CTkButton(button_frame, text="🚀 開始處理", 
                                           command=self.process_image, 
                                           height=40, fg_color="green")
        self.process_button.pack(fill="x", pady=5)
        
        ctk.CTkButton(button_frame, text="🗑️ 清除", 
                     command=self.clear_all, height=35).pack(fill="x", pady=5)
        
        # OCR 結果
        result_frame = ctk.CTkFrame(right_frame)
        result_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(result_frame, text="OCR 結果", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        self.result_text = ctk.CTkTextbox(result_frame, wrap="word", 
                                         font=("Consolas", 11))
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 結果按鈕
        result_button_frame = ctk.CTkFrame(result_frame)
        result_button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(result_button_frame, text="📋 複製結果", 
                     command=self.copy_result).pack(side="left", padx=5)
        ctk.CTkButton(result_button_frame, text="💾 儲存結果", 
                     command=self.save_result).pack(side="left", padx=5)
        
        # 處理資訊
        self.process_info_label = ctk.CTkLabel(result_frame, text="", 
                                              font=("Arial", 10))
        self.process_info_label.pack(pady=5)
    
    def update_base_size_label(self, *args):
        """更新 Base Size 標籤"""
        self.base_size_label.configure(text=str(self.base_size_var.get()))
    
    def update_image_size_label(self, *args):
        """更新 Image Size 標籤"""
        self.image_size_label.configure(text=str(self.image_size_var.get()))
    
    def select_image(self):
        """選擇圖片"""
        filetypes = [
            ("圖片檔案", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
            ("所有檔案", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="選擇圖片",
            filetypes=filetypes
        )
        
        if filename:
            self.load_image(filename)
    
    def load_image(self, image_path):
        """載入並顯示圖片"""
        try:
            self.current_image_path = image_path
            
            # 載入圖片
            image = Image.open(image_path)
            
            # 調整大小以適應預覽框
            display_size = (380, 380)
            image.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # 轉換為 PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # 顯示圖片
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo  # 保持引用
            
            # 顯示圖片資訊
            original_image = Image.open(image_path)
            width, height = original_image.size
            file_size = Path(image_path).stat().st_size / 1024  # KB
            
            info_text = f"{Path(image_path).name}\n{width} x {height} px | {file_size:.1f} KB"
            self.info_label.configure(text=info_text)
            
            if self.status_callback:
                self.status_callback(f"已載入: {Path(image_path).name}")
        
        except Exception as e:
            messagebox.showerror("錯誤", f"載入圖片失敗:\n{e}")
    
    def process_image(self):
        """處理圖片"""
        if not self.current_image_path:
            messagebox.showwarning("警告", "請先選擇圖片")
            return
        
        # 禁用按鈕
        self.process_button.configure(state="disabled", text="處理中...")
        
        if self.status_callback:
            self.status_callback("正在處理圖片...")
        
        # 在背景執行緒中處理
        thread = threading.Thread(target=self._process_image_thread)
        thread.daemon = True
        thread.start()
    
    def _process_image_thread(self):
        """在背景執行緒中處理圖片"""
        try:
            # 確保模型已載入
            if not self.ocr_engine._model_loaded:
                self.ocr_engine.load_model()
            
            # 執行 OCR
            result = self.ocr_engine.process_image(
                self.current_image_path,
                base_size=self.base_size_var.get(),
                image_size=self.image_size_var.get(),
                crop_mode=self.crop_mode_var.get(),
                save_results=self.save_results_var.get(),
                output_path="outputs/gui_single"
            )
            
            self.current_result = result
            
            # 更新 UI（必須在主執行緒）
            self.after(0, self._update_result_ui, result)
        
        except Exception as e:
            self.after(0, self._show_error, str(e))
    
    def _update_result_ui(self, result):
        """更新結果 UI"""
        # 啟用按鈕
        self.process_button.configure(state="normal", text="🚀 開始處理")
        
        if result.success:
            # 顯示結果
            self.result_text.delete("1.0", "end")
            self.result_text.insert("1.0", result.text_content)
            
            # 顯示處理資訊
            info_text = (f"處理時間: {result.processing_time:.2f}s | "
                        f"VRAM: {result.vram_used_gb:.2f} GB | "
                        f"{result.image_size[0]} x {result.image_size[1]} px")
            self.process_info_label.configure(text=info_text)
            
            if self.status_callback:
                self.status_callback(f"處理完成 ({result.processing_time:.2f}s)")
            
            messagebox.showinfo("成功", "OCR 處理完成！")
        else:
            self._show_error(result.error_message)
    
    def _show_error(self, error_message):
        """顯示錯誤"""
        self.process_button.configure(state="normal", text="🚀 開始處理")
        
        if self.status_callback:
            self.status_callback("處理失敗")
        
        messagebox.showerror("錯誤", f"OCR 處理失敗:\n{error_message}")
    
    def copy_result(self):
        """複製結果到剪貼簿"""
        result_text = self.result_text.get("1.0", "end-1c")
        if result_text.strip():
            self.clipboard_clear()
            self.clipboard_append(result_text)
            messagebox.showinfo("成功", "結果已複製到剪貼簿")
        else:
            messagebox.showwarning("警告", "沒有可複製的結果")
    
    def save_result(self):
        """儲存結果到檔案"""
        result_text = self.result_text.get("1.0", "end-1c")
        if not result_text.strip():
            messagebox.showwarning("警告", "沒有可儲存的結果")
            return
        
        filename = filedialog.asksaveasfilename(
            title="儲存結果",
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("文字檔案", "*.txt"), ("所有檔案", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result_text)
                messagebox.showinfo("成功", f"結果已儲存至:\n{filename}")
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存失敗:\n{e}")
    
    def clear_all(self):
        """清除所有內容"""
        self.current_image_path = None
        self.current_result = None
        
        self.image_label.configure(image="", text="拖放圖片到這裡\n或點擊下方按鈕選擇")
        self.image_label.image = None
        self.info_label.configure(text="")
        self.result_text.delete("1.0", "end")
        self.process_info_label.configure(text="")
        
        if self.status_callback:
            self.status_callback("已清除")
