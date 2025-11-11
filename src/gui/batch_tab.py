"""
批次處理頁籤
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from typing import List


class BatchTab(ctk.CTkFrame):
    """批次處理頁籤類別"""
    
    def __init__(self, parent, ocr_engine, status_callback=None):
        super().__init__(parent)
        
        self.ocr_engine = ocr_engine
        self.status_callback = status_callback
        self.image_files: List[Path] = []
        self.is_processing = False
        self.stop_requested = False
        
        self.create_widgets()
    
    def create_widgets(self):
        """建立介面元件"""
        # 上方：控制區域
        control_frame = ctk.CTkFrame(self)
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # 按鈕列
        button_frame = ctk.CTkFrame(control_frame)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(button_frame, text="➕ 新增檔案", 
                     command=self.add_files, width=120).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="📁 新增資料夾", 
                     command=self.add_folder, width=120).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="🗑️ 清除列表", 
                     command=self.clear_list, width=120).pack(side="left", padx=5)
        
        # 檔案列表
        list_frame = ctk.CTkFrame(self)
        list_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(list_frame, text="檔案列表", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        # 使用 Textbox 顯示檔案列表
        self.file_listbox = ctk.CTkTextbox(list_frame, height=200, 
                                          font=("Consolas", 10))
        self.file_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.file_count_label = ctk.CTkLabel(list_frame, text="總計: 0 個檔案", 
                                            font=("Arial", 10))
        self.file_count_label.pack(pady=5)
        
        # 批次選項
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(options_frame, text="批次選項", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        # 選項行
        option_row = ctk.CTkFrame(options_frame)
        option_row.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(option_row, text="批次大小:", 
                    font=("Arial", 11)).pack(side="left", padx=5)
        self.batch_size_var = ctk.IntVar(value=4)
        ctk.CTkEntry(option_row, textvariable=self.batch_size_var, 
                    width=60).pack(side="left", padx=5)
        
        ctk.CTkLabel(option_row, text="輸出目錄:", 
                    font=("Arial", 11)).pack(side="left", padx=(20, 5))
        self.output_dir_var = ctk.StringVar(value="outputs/batch")
        ctk.CTkEntry(option_row, textvariable=self.output_dir_var, 
                    width=200).pack(side="left", padx=5)
        ctk.CTkButton(option_row, text="瀏覽", command=self.browse_output, 
                     width=60).pack(side="left", padx=5)
        
        self.auto_clear_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(options_frame, text="自動清理快取", 
                       variable=self.auto_clear_var).pack(anchor="w", padx=10, pady=5)
        
        # 控制按鈕
        control_buttons = ctk.CTkFrame(options_frame)
        control_buttons.pack(fill="x", padx=10, pady=10)
        
        self.start_button = ctk.CTkButton(control_buttons, text="🚀 開始批次處理", 
                                         command=self.start_batch, 
                                         height=40, fg_color="green")
        self.start_button.pack(side="left", padx=5, expand=True, fill="x")
        
        self.stop_button = ctk.CTkButton(control_buttons, text="⏹️ 停止", 
                                        command=self.stop_batch, 
                                        height=40, fg_color="red", 
                                        state="disabled")
        self.stop_button.pack(side="left", padx=5, expand=True, fill="x")
        
        # 進度顯示
        progress_frame = ctk.CTkFrame(self)
        progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(progress_frame, text="處理進度", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)
        
        self.progress_label = ctk.CTkLabel(progress_frame, text="等待開始...", 
                                          font=("Arial", 10))
        self.progress_label.pack(pady=5)
        
        self.current_file_label = ctk.CTkLabel(progress_frame, text="", 
                                              font=("Arial", 9))
        self.current_file_label.pack(pady=2)
        
        # 結果統計
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(stats_frame, text="結果統計", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 5))
        
        self.stats_label = ctk.CTkLabel(stats_frame, 
                                       text="✓ 成功: 0  ✗ 失敗: 0  ⏱️ 總時間: 0.0s", 
                                       font=("Arial", 11))
        self.stats_label.pack(pady=10)
    
    def add_files(self):
        """新增檔案"""
        filetypes = [
            ("圖片檔案", "*.png *.jpg *.jpeg *.bmp *.tiff *.webp"),
            ("所有檔案", "*.*")
        ]
        
        filenames = filedialog.askopenfilenames(
            title="選擇圖片檔案",
            filetypes=filetypes
        )
        
        if filenames:
            for filename in filenames:
                file_path = Path(filename)
                if file_path not in self.image_files:
                    self.image_files.append(file_path)
            
            self.update_file_list()
    
    def add_folder(self):
        """新增資料夾"""
        folder = filedialog.askdirectory(title="選擇圖片資料夾")
        
        if folder:
            folder_path = Path(folder)
            extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
            
            # 遞迴搜尋所有子資料夾
            for ext in extensions:
                for file_path in folder_path.rglob(f"*{ext}"):
                    if file_path.is_file() and file_path not in self.image_files:
                        self.image_files.append(file_path)
                for file_path in folder_path.rglob(f"*{ext.upper()}"):
                    if file_path.is_file() and file_path not in self.image_files:
                        self.image_files.append(file_path)
            
            self.update_file_list()
    
    def clear_list(self):
        """清除列表"""
        if self.is_processing:
            messagebox.showwarning("警告", "處理中無法清除列表")
            return
        
        self.image_files.clear()
        self.update_file_list()
        self.progress_bar.set(0)
        self.progress_label.configure(text="等待開始...")
        self.current_file_label.configure(text="")
        self.stats_label.configure(text="✓ 成功: 0  ✗ 失敗: 0  ⏱️ 總時間: 0.0s")
    
    def update_file_list(self):
        """更新檔案列表顯示"""
        self.file_listbox.delete("1.0", "end")
        
        for i, file_path in enumerate(self.image_files, 1):
            self.file_listbox.insert("end", f"{i}. {file_path.name}\n")
        
        self.file_count_label.configure(text=f"總計: {len(self.image_files)} 個檔案")
    
    def browse_output(self):
        """瀏覽輸出目錄"""
        folder = filedialog.askdirectory(title="選擇輸出目錄")
        if folder:
            self.output_dir_var.set(folder)
    
    def start_batch(self):
        """開始批次處理"""
        if not self.image_files:
            messagebox.showwarning("警告", "請先新增檔案")
            return
        
        if self.is_processing:
            messagebox.showwarning("警告", "已在處理中")
            return
        
        # 更新按鈕狀態
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.is_processing = True
        self.stop_requested = False
        
        # 在背景執行緒中處理
        thread = threading.Thread(target=self._batch_process_thread)
        thread.daemon = True
        thread.start()
    
    def stop_batch(self):
        """停止批次處理"""
        self.stop_requested = True
        self.stop_button.configure(state="disabled")
        if self.status_callback:
            self.status_callback("正在停止...")
    
    def _batch_process_thread(self):
        """批次處理執行緒"""
        import time
        
        total = len(self.image_files)
        successful = 0
        failed = 0
        start_time = time.time()
        
        try:
            # 確保模型已載入
            if not self.ocr_engine._model_loaded:
                self.after(0, lambda: self.progress_label.configure(text="載入模型..."))
                self.ocr_engine.load_model()
            
            # 處理每個檔案
            for i, image_path in enumerate(self.image_files):
                if self.stop_requested:
                    self.after(0, lambda: self.progress_label.configure(text="已停止"))
                    break
                
                # 更新進度
                progress = (i + 1) / total
                current_text = f"處理中: {i+1}/{total}"
                file_text = f"當前: {image_path.name}"
                
                self.after(0, lambda p=progress, t=current_text, f=file_text: self._update_progress(p, t, f))
                
                if self.status_callback:
                    self.status_callback(f"處理: {i+1}/{total} - {image_path.name}")
                
                # 處理圖片
                try:
                    result = self.ocr_engine.process_image(
                        image_path,
                        output_path=f"{self.output_dir_var.get()}/{image_path.stem}",
                        save_results=True
                    )
                    
                    if result.success:
                        successful += 1
                    else:
                        failed += 1
                
                except Exception as e:
                    failed += 1
                    print(f"處理 {image_path.name} 失敗: {e}")
                
                # 自動清理快取
                if self.auto_clear_var.get() and (i + 1) % 5 == 0:
                    from src import get_memory_manager
                    get_memory_manager().clear_cache()
            
            # 完成
            total_time = time.time() - start_time
            stats_text = f"✓ 成功: {successful}  ✗ 失敗: {failed}  ⏱️ 總時間: {total_time:.1f}s"
            
            self.after(0, lambda: self.stats_label.configure(text=stats_text))
            self.after(0, lambda: self.progress_label.configure(text="處理完成！"))
            
            if self.status_callback:
                self.status_callback(f"批次處理完成: {successful}/{total}")
            
            if not self.stop_requested:
                self.after(0, lambda: messagebox.showinfo("完成", 
                    f"批次處理完成！\n成功: {successful}\n失敗: {failed}\n總時間: {total_time:.1f}秒"))
        
        except Exception as e:
            error_msg = str(e)
            self.after(0, lambda msg=error_msg: messagebox.showerror("錯誤", f"批次處理失敗:\n{msg}"))
        
        finally:
            # 恢復按鈕狀態
            self.after(0, self._reset_buttons)
            self.is_processing = False
    
    def _update_progress(self, progress, text, file_text):
        """更新進度顯示"""
        self.progress_bar.set(progress)
        self.progress_label.configure(text=text)
        self.current_file_label.configure(text=file_text)
    
    def _reset_buttons(self):
        """重置按鈕狀態"""
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
