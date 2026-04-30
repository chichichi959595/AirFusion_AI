from pathlib import Path
import unittest


WEB_DIR = Path(__file__).resolve().parents[1] / "app" / "web"


class FrontendStaticTests(unittest.TestCase):
    def test_frontend_assets_exist(self) -> None:
        self.assertTrue((WEB_DIR / "index.html").exists())
        self.assertTrue((WEB_DIR / "static" / "styles.css").exists())
        self.assertTrue((WEB_DIR / "static" / "app.js").exists())

    def test_retro_design_signatures_are_present(self) -> None:
        html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        css = (WEB_DIR / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("marquee-track", html)
        self.assertIn("rainbow-text", html)
        self.assertIn("hit-counter", html)
        self.assertIn("construction-zone", html)
        self.assertIn("@keyframes rainbow", css)
        self.assertIn("border-radius: 0", css)
        self.assertIn("repeating-linear-gradient", css)


if __name__ == "__main__":
    unittest.main()
