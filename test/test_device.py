import torch
from transformers import AutoModel

print("=" * 60)
print("檢查 device_map 參數用法")
print("=" * 60)
print()

print("CUDA 可用:", torch.cuda.is_available())
print("CUDA 版本:", torch.version.cuda if torch.cuda.is_available() else "N/A")
print()

print("device_map 參數說明:")
print("  device_map='cuda'  ← 錯誤！這不是有效的 device_map 值")
print("  device_map='auto'  ← 正確！自動選擇最佳裝置")
print("  device_map={'': 0} ← 正確！指定到 GPU 0")
print()

print("正確的模型載入方式:")
print("方法 1: 使用 device_map='auto'")
print("  model = AutoModel.from_pretrained(..., device_map='auto')")
print()
print("方法 2: 手動指定裝置")
print("  model = AutoModel.from_pretrained(...)")
print("  model = model.to('cuda')")
print()

print("=" * 60)
print("問題診斷:")
print("=" * 60)
print()
print("當前代碼使用: device_map=self.device (值為 'cuda')")
print("問題: device_map='cuda' 不是有效值，可能被忽略")
print("結果: 模型可能載入到 CPU")
print()
print("解決方案:")
print("1. 改用 device_map='auto'")
print("2. 或者不用 device_map，改用 .to(device)")
