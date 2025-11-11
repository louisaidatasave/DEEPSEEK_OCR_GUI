"""
PDF 處理頁籤
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading


class PDFTab(ctk.CTkFrame):
    """PDF 處理頁籤類別"""
    
    def __init__(self, parent, ocr_engine, status_callback=None):
        super().__init__(parent)
        
        self.ocr_engine = ocr_engine
        self.status_callback = status_callback
        self.current_pdf_path = None
        self.is_processing = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """建立介面元件"""
        # PDF 選擇區域
        select_frame = ctk.CTkFrame(self)
        select_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(select_frame, text="📄 選擇 PDF", 
                     command=self.select_pdf, height=40).pack(fill="x", padx=10, pady=10)
        
        # PDF 資訊
        info_frame = ctk.CTkFrame(self)
        info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(info_frame, text="PDF 資訊", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        self.pdf_info_text = ctk.CTkTextbox(info_frame, height=100, 
                                           font=("Arial", 10))
        self.pdf_info_text.pack(fill="x", padx=10, pady=10)
        self.pdf_info_text.insert("1.0", "尚未選擇 PDF 檔案")
        
        # 頁碼設定
        page_frame = ctk.CTkFrame(self)
        page_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(page_frame, text="頁碼設定", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        self.page_mode_var = ctk.StringVar(value="all")
        
        ctk.CTkRadioButton(page_frame, text="全部頁面", 
                          variable=self.page_mode_var, 
                          value="all").pack(anchor="w", padx=10, pady=5)
        
        range_frame = ctk.CTkFrame(page_frame)
        range_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkRadioButton(range_frame, text="指定範圍:", 
                          variable=self.page_mode_var, 
                          value="range").pack(side="left", padx=5)
        
        ctk.CTkLabel(range_frame, text="從").pack(side="left", padx=5)
        self.start_page_var = ctk.IntVar(value=1)
        ctk.CTkEntry(range_frame, textvariable=self.start_page_var, 
                    width=60).pack(side="left", padx=5)
        
        ctk.CTkLabel(range_frame, text="到").pack(side="left", padx=5)
        self.end_page_var = ctk.IntVar(value=1)
        ctk.CTkEntry(range_frame, textvariable=self.end_page_var, 
                    width=60).pack(side="left", padx=5)
        
        max_frame = ctk.CTkFrame(page_frame)
        max_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(max_frame, text="最大處理頁數:").pack(side="left", padx=5)
        self.max_pages_var = ctk.IntVar(value=100)
        ctk.CTkEntry(max_frame, textvariable=self.max_pages_var, 
                    width=80).pack(side="left", padx=5)
        
        # 轉換選項
        convert_frame = ctk.CTkFrame(self)
        convert_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(convert_frame, text="轉換選項", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        option_row1 = ctk.CTkFrame(convert_frame)
        option_row1.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(option_row1, text="DPI:").pack(side="left", padx=5)
        self.dpi_var = ctk.IntVar(value=200)
        ctk.CTkEntry(option_row1, textvariable=self.dpi_var, 
                    width=80).pack(side="left", padx=5)
        
        ctk.CTkLabel(option_row1, text="格式:").pack(side="left", padx=(20, 5))
        self.format_var = ctk.StringVar(value="PNG")
        ctk.CTkComboBox(option_row1, values=["PNG", "JPEG"], 
                       variable=self.format_var, width=100).pack(side="left", padx=5)
        
        option_row2 = ctk.CTkFrame(convert_frame)
        option_row2.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(option_row2, text="輸出目錄:").pack(side="left", padx=5)
        self.output_dir_var = ctk.StringVar(value="outputs/pdf_ocr")
        ctk.CTkEntry(option_row2, textvariable=self.output_dir_var, 
                    width=250).pack(side="left", padx=5)
        ctk.CTkButton(option_row2, text="瀏覽", command=self.browse_output, 
                     width=60).pack(side="left", padx=5)
        
        # 處理按鈕
        self.process_button = ctk.CTkButton(self, text="🚀 開始處理", 
                                           command=self.start_process, 
                                           height=50, fg_color="green")
        self.process_button.pack(fill="x", padx=10, pady=10)
        
        # 進度顯示
        progress_frame = ctk.CTkFrame(self)
        progress_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(progress_frame, text="處理進度", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        # 步驟 1: PDF 轉圖片
        ctk.CTkLabel(progress_frame, text="步驟 1: PDF 轉圖片", 
                    font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 2))
        self.convert_progress = ctk.CTkProgressBar(progress_frame)
        self.convert_progress.pack(fill="x", padx=10, pady=5)
        self.convert_progress.set(0)
        self.convert_label = ctk.CTkLabel(progress_frame, text="等待開始...", 
                                         font=("Arial", 9))
        self.convert_label.pack(anchor="w", padx=10, pady=2)
        
        # 步驟 2: OCR 處理
        ctk.CTkLabel(progress_frame, text="步驟 2: OCR 處理", 
                    font=("Arial", 11)).pack(anchor="w", padx=10, pady=(10, 2))
        self.ocr_progress = ctk.CTkProgressBar(progress_frame)
        self.ocr_progress.pack(fill="x", padx=10, pady=5)
        self.ocr_progress.set(0)
        self.ocr_label = ctk.CTkLabel(progress_frame, text="等待開始...", 
                                     font=("Arial", 9))
        self.ocr_label.pack(anchor="w", padx=10, pady=2)
        
        # 已處理頁面
        self.pages_label = ctk.CTkLabel(progress_frame, text="", 
                                       font=("Arial", 10))
        self.pages_label.pack(pady=10)
    
    def select_pdf(self):
        """選擇 PDF"""
        filename = filedialog.askopenfilename(
            title="選擇 PDF 檔案",
            filetypes=[("PDF 檔案", "*.pdf"), ("所有檔案", "*.*")]
        )
        
        if filename:
            self.current_pdf_path = Path(filename)
            self.load_pdf_info()
    
    def load_pdf_info(self):
        """載入 PDF 資訊"""
        if not self.current_pdf_path:
            return
        
        try:
            from src import get_pdf_info
            
            info = get_pdf_info(self.current_pdf_path)
            
            self.pdf_info_text.delete("1.0", "end")
            
            if info.get('exists'):
                if 'error' in info:
                    self.pdf_info_text.insert("1.0", f"錯誤: {info['error']}")
                else:
                    info_text = f"""檔案: {info['file_name']}
大小: {info['file_size_mb']:.2f} MB
總頁數: {info['total_pages']} 頁
第一頁尺寸: {info['first_page_size']}
預估轉換時間: {info['estimated_conversion_time']} 秒"""
                    self.pdf_info_text.insert("1.0", info_text)
                    
                    # 更新頁碼範圍
                    self.end_page_var.set(info['total_pages'])
            else:
                self.pdf_info_text.insert("1.0", f"錯誤: {info.get('error', '未知錯誤')}")
        
        except Exception as e:
            self.pdf_info_text.delete("1.0", "end")
            self.pdf_info_text.insert("1.0", f"載入 PDF 資訊失敗:\n{e}")
    
    def browse_output(self):
        """瀏覽輸出目錄"""
        folder = filedialog.askdirectory(title="選擇輸出目錄")
        if folder:
            self.output_dir_var.set(folder)
    
    def start_process(self):
        """開始處理"""
        if not self.current_pdf_path:
            messagebox.showwarning("警告", "請先選擇 PDF 檔案")
            return
        
        if self.is_processing:
            messagebox.showwarning("警告", "已在處理中")
            return
        
        # 禁用按鈕
        self.process_button.configure(state="disabled", text="處理中...")
        self.is_processing = True
        
        # 在背景執行緒中處理
        thread = threading.Thread(target=self._process_pdf_thread)
        thread.daemon = True
        thread.start()
    
    def _process_pdf_thread(self):
        """PDF 處理執行緒"""
        import time
        from src import PDFConverter
        
        try:
            # 步驟 1: 轉換 PDF
            self.after(0, lambda: self.convert_label.configure(text="正在轉換 PDF..."))
            
            # 建立轉換器
            converter = PDFConverter(
                dpi=self.dpi_var.get(),
                output_format=self.format_var.get(),
                max_pages=self.max_pages_var.get()
            )
            
            # 設定頁碼範圍
            page_range = None
            if self.page_mode_var.get() == "range":
                page_range = (self.start_page_var.get(), self.end_page_var.get())
            
            # 轉換 PDF
            pdf_images_dir = Path(self.output_dir_var.get()) / "pdf_images"
            conversion_result = converter.convert_pdf(
                self.current_pdf_path,
                pdf_images_dir,
                page_range=page_range,
                prefix=self.current_pdf_path.stem
            )
            
            if not conversion_result.success:
                raise Exception(conversion_result.error_message)
            
            self.after(0, lambda: self.convert_progress.set(1.0))
            self.after(0, lambda: self.convert_label.configure(
                text=f"✓ 完成: {conversion_result.converted_pages} 頁"))
            
            # 步驟 2: OCR 處理
            self.after(0, lambda: self.ocr_label.configure(text="正在進行 OCR..."))
            
            # 確保模型已載入
            if not self.ocr_engine._model_loaded:
                self.ocr_engine.load_model()
            
            # 批次處理圖片
            image_paths = [Path(p) for p in conversion_result.image_paths]
            total = len(image_paths)
            successful = 0
            
            for i, image_path in enumerate(image_paths):
                # 更新進度
                progress = (i + 1) / total
                self.after(0, lambda p=progress: self.ocr_progress.set(p))
                self.after(0, lambda i=i, t=total: self.ocr_label.configure(
                    text=f"處理中: {i+1}/{t}"))
                
                # 處理圖片
                try:
                    result = self.ocr_engine.process_image(
                        image_path,
                        output_path=f"{self.output_dir_var.get()}/page_{i+1:04d}",
                        save_results=True
                    )
                    
                    if result.success:
                        successful += 1
                
                except Exception as e:
                    print(f"處理頁面 {i+1} 失敗: {e}")
            
            # 完成
            self.after(0, lambda: self.ocr_label.configure(
                text=f"✓ 完成: {successful}/{total} 頁"))
            self.after(0, lambda: self.pages_label.configure(
                text=f"成功處理 {successful} 頁，失敗 {total - successful} 頁"))
            
            if self.status_callback:
                self.status_callback(f"PDF 處理完成: {successful}/{total} 頁")
            
            self.after(0, lambda: messagebox.showinfo("完成", 
                f"PDF 處理完成！\n成功: {successful} 頁\n失敗: {total - successful} 頁"))
        
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: messagebox.showerror("錯誤", f"PDF 處理失敗:\n{msg}"))
        
        finally:
            # 恢復按鈕
            self.after(0, lambda: self.process_button.configure(
                state="normal", text="🚀 開始處理"))
            self.is_processing = False
    
