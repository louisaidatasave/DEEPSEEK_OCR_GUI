"""
GUI 主題配置
"""

# 顏色配置
COLORS = {
    "primary": "#1f538d",
    "success": "#2fa572",
    "warning": "#e67e22",
    "error": "#e74c3c",
    "info": "#3498db",
    "dark": "#2b2b2b",
    "light": "#f0f0f0",
}

# 字體配置
FONTS = {
    "title": ("Arial", 16, "bold"),
    "heading": ("Arial", 14, "bold"),
    "normal": ("Arial", 11),
    "small": ("Arial", 9),
    "code": ("Consolas", 10),
}

# 尺寸配置
SIZES = {
    "button_height": 40,
    "input_width": 200,
    "padding": 10,
    "margin": 5,
}

# 主題設定
THEMES = {
    "dark": {
        "appearance_mode": "dark",
        "color_theme": "blue",
    },
    "light": {
        "appearance_mode": "light",
        "color_theme": "blue",
    },
}


def apply_theme(theme_name: str = "dark"):
    """
    套用主題
    
    Args:
        theme_name: 主題名稱 (dark/light)
    """
    import customtkinter as ctk
    
    theme = THEMES.get(theme_name, THEMES["dark"])
    ctk.set_appearance_mode(theme["appearance_mode"])
    ctk.set_default_color_theme(theme["color_theme"])


def get_color(color_name: str) -> str:
    """
    取得顏色
    
    Args:
        color_name: 顏色名稱
        
    Returns:
        顏色代碼
    """
    return COLORS.get(color_name, COLORS["primary"])


def get_font(font_name: str) -> tuple:
    """
    取得字體
    
    Args:
        font_name: 字體名稱
        
    Returns:
        字體元組
    """
    return FONTS.get(font_name, FONTS["normal"])
