"""
版本資訊模組
記錄和檢查系統版本資訊
"""

import sys
import platform
from typing import Dict
import logging

logger = logging.getLogger(__name__)

# 專案版本
PROJECT_VERSION = "1.0.0"
PROJECT_NAME = "DeepSeek-OCR"


def get_python_version() -> str:
    """取得 Python 版本"""
    return sys.version.split()[0]


def get_torch_version() -> str:
    """取得 PyTorch 版本"""
    try:
        import torch
        return torch.__version__
    except ImportError:
        return "未安裝"


def get_cuda_version() -> str:
    """取得 CUDA 版本"""
    try:
        import torch
        if torch.cuda.is_available():
            return torch.version.cuda
        return "不可用"
    except:
        return "未知"


def get_transformers_version() -> str:
    """取得 Transformers 版本"""
    try:
        import transformers
        return transformers.__version__
    except ImportError:
        return "未安裝"


def get_pillow_version() -> str:
    """取得 Pillow 版本"""
    try:
        import PIL
        return PIL.__version__
    except ImportError:
        return "未安裝"


def get_gradio_version() -> str:
    """取得 Gradio 版本"""
    try:
        import gradio
        return gradio.__version__
    except ImportError:
        return "未安裝"


def get_pdf2image_version() -> str:
    """取得 pdf2image 版本"""
    try:
        import pdf2image
        return pdf2image.__version__ if hasattr(pdf2image, '__version__') else "已安裝"
    except ImportError:
        return "未安裝"


def get_system_info() -> Dict[str, str]:
    """取得系統資訊"""
    return {
        'os': platform.system(),
        'os_version': platform.version(),
        'platform': platform.platform(),
        'architecture': platform.machine(),
        'processor': platform.processor()
    }


def get_gpu_info() -> Dict[str, str]:
    """取得 GPU 資訊"""
    try:
        import torch
        if torch.cuda.is_available():
            return {
                'available': True,
                'device_count': torch.cuda.device_count(),
                'device_name': torch.cuda.get_device_name(0),
                'cuda_version': torch.version.cuda,
                'cudnn_version': torch.backends.cudnn.version() if torch.backends.cudnn.is_available() else "不可用"
            }
        return {'available': False}
    except:
        return {'available': False, 'error': '無法取得 GPU 資訊'}


def get_all_versions() -> Dict[str, any]:
    """取得所有版本資訊"""
    return {
        'project': {
            'name': PROJECT_NAME,
            'version': PROJECT_VERSION
        },
        'python': {
            'version': get_python_version(),
            'implementation': platform.python_implementation()
        },
        'system': get_system_info(),
        'packages': {
            'torch': get_torch_version(),
            'cuda': get_cuda_version(),
            'transformers': get_transformers_version(),
            'pillow': get_pillow_version(),
            'gradio': get_gradio_version(),
            'pdf2image': get_pdf2image_version()
        },
        'gpu': get_gpu_info()
    }


def print_version_info():
    """列印版本資訊"""
    info = get_all_versions()
    
    print("=" * 60)
    print(f"{info['project']['name']} v{info['project']['version']}")
    print("=" * 60)
    print()
    
    print("【Python】")
    print(f"  版本: {info['python']['version']}")
    print(f"  實作: {info['python']['implementation']}")
    print()
    
    print("【系統】")
    print(f"  作業系統: {info['system']['os']}")
    print(f"  平台: {info['system']['platform']}")
    print(f"  架構: {info['system']['architecture']}")
    print()
    
    print("【套件】")
    for name, version in info['packages'].items():
        print(f"  {name:15s}: {version}")
    print()
    
    print("【GPU】")
    gpu = info['gpu']
    if gpu.get('available'):
        print(f"  狀態: ✓ 可用")
        print(f"  裝置: {gpu['device_name']}")
        print(f"  數量: {gpu['device_count']}")
        print(f"  CUDA: {gpu['cuda_version']}")
        print(f"  cuDNN: {gpu['cudnn_version']}")
    else:
        print(f"  狀態: ✗ 不可用")
        if 'error' in gpu:
            print(f"  錯誤: {gpu['error']}")
    
    print()
    print("=" * 60)


def check_requirements() -> Dict[str, bool]:
    """檢查必要套件是否安裝"""
    requirements = {
        'torch': False,
        'transformers': False,
        'pillow': False
    }
    
    try:
        import torch
        requirements['torch'] = True
    except ImportError:
        pass
    
    try:
        import transformers
        requirements['transformers'] = True
    except ImportError:
        pass
    
    try:
        import PIL
        requirements['pillow'] = True
    except ImportError:
        pass
    
    return requirements


def verify_installation() -> bool:
    """驗證安裝是否完整"""
    requirements = check_requirements()
    all_installed = all(requirements.values())
    
    if not all_installed:
        logger.error("部分必要套件未安裝:")
        for pkg, installed in requirements.items():
            status = "✓" if installed else "✗"
            logger.error(f"  {status} {pkg}")
        return False
    
    logger.info("所有必要套件已安裝")
    return True


def get_version_string() -> str:
    """取得版本字串"""
    return f"{PROJECT_NAME} v{PROJECT_VERSION}"


def compare_version(version1: str, version2: str) -> int:
    """
    比較版本號
    
    Args:
        version1: 版本 1
        version2: 版本 2
        
    Returns:
        1 if version1 > version2
        0 if version1 == version2
        -1 if version1 < version2
    """
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]
    
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
    
    if len(v1_parts) > len(v2_parts):
        return 1
    elif len(v1_parts) < len(v2_parts):
        return -1
    
    return 0
