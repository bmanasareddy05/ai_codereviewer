from dotenv import load_dotenv
load_dotenv()
import reflex as rx
from ai_codereviewer.pages.home import index as home
from ai_codereviewer.pages.analyzer import analyser
from ai_codereviewer.pages.history import history_page

app = rx.App()

app.add_page(home, route="/")
app.add_page(analyser, route="/analyser")
app.add_page(history_page, route="/history")