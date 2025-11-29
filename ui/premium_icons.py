"""
Premium SVG Icons for Streamlit Dashboard
Figma-style modern icon set
"""

def get_icon(name: str, size: int = 24, color: str = "#374151") -> str:
    """Get SVG icon by name"""

    icons = {
        "upload": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M17 8L12 3L7 8" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 3V15" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',

        "dashboard": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="3" y="3" width="7" height="7" rx="1" stroke="{color}" stroke-width="2"/>
                <rect x="14" y="3" width="7" height="7" rx="1" stroke="{color}" stroke-width="2"/>
                <rect x="3" y="14" width="7" height="7" rx="1" stroke="{color}" stroke-width="2"/>
                <rect x="14" y="14" width="7" height="7" rx="1" stroke="{color}" stroke-width="2"/>
            </svg>
        ''',

        "chart": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 3V21H21" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 13L12 8L16 12L21 7" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M21 11V7H17" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',

        "ai": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="9" stroke="{color}" stroke-width="2"/>
                <path d="M12 6C12 6 9 8 9 12C9 16 12 18 12 18" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
                <path d="M12 6C12 6 15 8 15 12C15 16 12 18 12 18" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="12" r="2" fill="{color}"/>
            </svg>
        ''',

        "settings": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="3" stroke="{color}" stroke-width="2"/>
                <path d="M12 1V3M12 21V23M4.22 4.22L5.64 5.64M18.36 18.36L19.78 19.78M1 12H3M21 12H23M4.22 19.78L5.64 18.36M18.36 5.64L19.78 4.22" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            </svg>
        ''',

        "analytics": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M3 15L9 9L13 13L21 5" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <rect x="3" y="17" width="3" height="4" rx="1" fill="{color}"/>
                <rect x="9" y="13" width="3" height="8" rx="1" fill="{color}"/>
                <rect x="15" y="9" width="3" height="12" rx="1" fill="{color}"/>
                <rect x="21" y="6" width="3" height="15" rx="1" fill="{color}"/>
            </svg>
        ''',

        "health": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20.84 4.61C20.3292 4.099 19.7228 3.69364 19.0554 3.41708C18.3879 3.14052 17.6725 2.99817 16.95 2.99817C16.2275 2.99817 15.5121 3.14052 14.8446 3.41708C14.1772 3.69364 13.5708 4.099 13.06 4.61L12 5.67L10.94 4.61C9.9083 3.57831 8.50903 2.99871 7.05 2.99871C5.59096 2.99871 4.19169 3.57831 3.16 4.61C2.1283 5.64169 1.54871 7.04097 1.54871 8.5C1.54871 9.95903 2.1283 11.3583 3.16 12.39L4.22 13.45L12 21.23L19.78 13.45L20.84 12.39C21.351 11.8792 21.7564 11.2728 22.0329 10.6054C22.3095 9.93789 22.4518 9.22248 22.4518 8.5C22.4518 7.77752 22.3095 7.06211 22.0329 6.39464C21.7564 5.72718 21.351 5.12075 20.84 4.61Z" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',

        "data": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="12" cy="5" rx="9" ry="3" stroke="{color}" stroke-width="2"/>
                <path d="M21 12C21 13.66 16.97 15 12 15C7.03 15 3 13.66 3 12" stroke="{color}" stroke-width="2"/>
                <path d="M3 5V19C3 20.66 7.03 22 12 22C16.97 22 21 20.66 21 19V5" stroke="{color}" stroke-width="2"/>
            </svg>
        ''',

        "filter": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M22 3H2L10 12.46V19L14 21V12.46L22 3Z" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',

        "play": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="{color}" stroke-width="2"/>
                <path d="M10 8L16 12L10 16V8Z" fill="{color}"/>
            </svg>
        ''',

        "check": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="{color}" stroke-width="2"/>
                <path d="M8 12L11 15L16 9" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',

        "warning": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M10.29 3.86L1.82 18C1.64537 18.3024 1.55296 18.6453 1.55199 18.9945C1.55101 19.3437 1.64151 19.6871 1.81442 19.9905C1.98733 20.2939 2.23672 20.5467 2.53771 20.7239C2.83869 20.9011 3.18082 20.9962 3.53 21H20.47C20.8192 20.9962 21.1613 20.9011 21.4623 20.7239C21.7633 20.5467 22.0127 20.2939 22.1856 19.9905C22.3585 19.6871 22.449 19.3437 22.448 18.9945C22.447 18.6453 22.3546 18.3024 22.18 18L13.71 3.86C13.5317 3.56611 13.2807 3.32312 12.9812 3.15448C12.6817 2.98585 12.3437 2.89725 12 2.89725C11.6563 2.89725 11.3183 2.98585 11.0188 3.15448C10.7193 3.32312 10.4683 3.56611 10.29 3.86Z" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <line x1="12" y1="9" x2="12" y2="13" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="17" r="1" fill="{color}"/>
            </svg>
        ''',

        "info": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="{color}" stroke-width="2"/>
                <line x1="12" y1="11" x2="12" y2="16" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="8" r="1" fill="{color}"/>
            </svg>
        ''',

        "search": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="11" cy="11" r="8" stroke="{color}" stroke-width="2"/>
                <path d="M21 21L16.65 16.65" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            </svg>
        ''',

        "download": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7 10L12 15L17 10" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 15V3" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',

        "customize": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 17L12 22L22 17" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M2 12L12 17L22 12" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        ''',

        "pipeline": f'''
            <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="5" cy="12" r="3" stroke="{color}" stroke-width="2"/>
                <circle cx="19" cy="12" r="3" stroke="{color}" stroke-width="2"/>
                <path d="M8 12H16" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
                <path d="M12 8V16" stroke="{color}" stroke-width="2" stroke-linecap="round"/>
            </svg>
        ''',
    }

    return icons.get(name, icons["info"])


def icon_with_text(icon_name: str, text: str, icon_size: int = 20, color: str = "#374151") -> str:
    """Create icon with text label"""
    icon = get_icon(icon_name, icon_size, color)
    return f'''
        <div style="display: flex; align-items: center; gap: 8px;">
            {icon}
            <span style="color: {color}; font-weight: 500;">{text}</span>
        </div>
    '''
