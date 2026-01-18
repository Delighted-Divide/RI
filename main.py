import flet as ft
import os
import re

def main(page: ft.Page):
    page.title = "RI Reader Offline"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.scroll = "auto"

    # Settings for word/token counting
    # encoding = tiktoken.get_encoding("cl100k_base") # Removed to avoid compilation issues on Android
    CHAPTER_FOLDER = "chapters"

    # UI Elements
    chap_input = ft.TextField(
        value="1", 
        label="Chapter Number", 
        width=150, 
        text_align=ft.TextAlign.CENTER,
        keyboard_type=ft.KeyboardType.NUMBER
    )
    
    title_text = ft.Text("Reverend Insanity", style=ft.TextThemeStyle.HEADLINE_MEDIUM, weight="bold")
    content_text = ft.Text("Load a chapter to start reading...", Selectable=True)
    
    stat_words = ft.Text("Words: 0", color="blue")
    stat_lines = ft.Text("Lines: 0", color="green")
    stat_tokens = ft.Text("Tokens: 0", color="orange")

    def load_chapter_data(num):
        try:
            filename = f"chapter_{int(num):04d}.txt"
            path = os.path.join(CHAPTER_FOLDER, filename)
            if not os.path.exists(path):
                return "Error", "Chapter file not found.", 0, 0, 0
            
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            lines = content.split("\n")
            words = len(content.split())
            # tokens = len(encoding.encode(content))
            tokens = int(words * 1.3) # Approximate token count
            
            return lines[0], content, words, len(lines), tokens
        except Exception as e:
            return "Error", str(e), 0, 0, 0

    def handle_load(e):
        title, content, w, l, t = load_chapter_data(chap_input.value)
        title_text.value = title
        content_text.value = content
        stat_words.value = f"Words: {w}"
        stat_lines.value = f"Lines: {l}"
        stat_tokens.value = f"Tokens: {t}"
        page.update()

    def handle_copy_next(e):
        # 1. Load current
        title, content, w, l, t = load_chapter_data(chap_input.value)
        
        # 2. Update UI
        title_text.value = title
        content_text.value = content
        stat_words.value = f"Words: {w}"
        stat_lines.value = f"Lines: {l}"
        stat_tokens.value = f"Tokens: {t}"
        
        # 3. Copy to Clipboard
        page.set_clipboard(content)
        
        # 4. Increment
        current_num = int(chap_input.value)
        chap_input.value = str(current_num + 1)
        
        # 5. Show Snack Bar
        page.snack_bar = ft.SnackBar(ft.Text(f"Copied Chapter {current_num}! Next: {current_num + 1}"), duration=1000)
        page.snack_bar.open = True
        page.update()

    # Layout
    page.add(
        ft.Row([
            chap_input,
            ft.ElevatedButton("Load", icon=ft.Icons.REFRESH, on_click=handle_load)
        ], alignment=ft.MainAxisAlignment.CENTER),
        
        ft.Container(
            content=ft.Column([
                ft.ElevatedButton(
                    "COPY & NEXT CHAPTER", 
                    icon=ft.Icons.COPY, 
                    on_click=handle_copy_next,
                    style=ft.ButtonStyle(
                        bgcolor=ft.Colors.INDIGO_700,
                        color=ft.Colors.WHITE,
                        padding=20,
                    ),
                    height=60,
                    width=400
                ),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            margin=ft.margin.only(top=10, bottom=20)
        ),
        
        ft.Row([stat_words, stat_lines, stat_tokens], alignment=ft.MainAxisAlignment.SPACE_AROUND),
        ft.Divider(),
        title_text,
        content_text
    )

ft.app(target=main)
