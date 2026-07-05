def get_template_styles(template_name: str) -> dict:
    """Houses visual layout constraints configuration frameworks."""
    styles = {
        "Elegant": {"bg": "#FFFDF9", "text": "#2C2523", "accent": "#D4AF37"},
        "Luxury": {"bg": "#0D1117", "text": "#F0F6FC", "accent": "#C5A880"},
        "Minimal": {"bg": "#FFFFFF", "text": "#111111", "accent": "#777777"},
        "Dark Theme": {"bg": "#121212", "text": "#E0E0E0", "accent": "#BB86FC"}
    }
    return styles.get(template_name, styles["Elegant"])

