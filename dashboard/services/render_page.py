from playwright.sync_api import sync_playwright
from dashboard.services.generate_art import run_art_generation_pipeline, ImageProcessingContext
from dashboard.services.generate_art import ConsoleLogger
from dashboard.color_constants import EXTENDED_PALETTE_SET
from typing import cast

DEFAULT_W = 1200
DEFAULT_H = 1600

def render_png(url: str,*, width=DEFAULT_W, height=DEFAULT_H,
               wait_selector: str | None = None, extra_wait_ms: int = 0,
               no_sandbox: bool = False) -> bytes:
    launch_args = ["--disable-dev-shm-usage"]
    if no_sandbox:
        launch_args += ["--no-sandbox", "--disable-setuid-sandbox"]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=launch_args)
        context = browser.new_context(
            viewport={"width": width, "height": height},
            device_scale_factor=1,
            color_scheme="light",
            bypass_csp=True,
            java_script_enabled=True,
            locale="en-US",
        )
        page = context.new_page()

        # Freeze animations
        page.add_style_tag(content="""
            * { animation: none !important; transition: none !important; }
            html, body { overflow: hidden !important; }
        """)

        page.goto(url, wait_until="networkidle", timeout=5_000)
        if wait_selector:
            page.wait_for_selector(wait_selector, state="visible", timeout=30_000)

        page.evaluate("() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
        if extra_wait_ms:
            page.wait_for_timeout(extra_wait_ms)

        png_bytes = page.screenshot(full_page=False, omit_background=False, type="png")
        browser.close()
        return png_bytes
    
def run_eink_pipeline_for_page_in_memory(png_bytes: bytes)-> bytes:
    ctx: ImageProcessingContext = ImageProcessingContext(
        logger=ConsoleLogger(),
        pipeline=["quantize_to_palette","output_bytes"],
        pipeline_args=[(EXTENDED_PALETTE_SET,),("png",)],
    )
    return cast(bytes,run_art_generation_pipeline(png_bytes, context=ctx))

    