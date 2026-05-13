from pathlib import Path
import unittest


WEB_DIR = Path(__file__).resolve().parents[1] / "app" / "web"


class FrontendStaticTests(unittest.TestCase):
    def test_frontend_assets_exist(self) -> None:
        self.assertTrue((WEB_DIR / "index.html").exists())
        self.assertTrue((WEB_DIR / "static" / "styles.css").exists())
        self.assertTrue((WEB_DIR / "static" / "app.js").exists())

    def test_corporate_trust_design_signatures_are_present(self) -> None:
        html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        css = (WEB_DIR / "static" / "styles.css").read_text(encoding="utf-8")

        self.assertIn("gradient-text", html)
        self.assertIn("language-select", html)
        self.assertNotIn("Language switchboard", html)
        self.assertNotIn('href="/docs"', html)
        self.assertIn("--gradient", css)
        self.assertIn("box-shadow: var(--shadow-card)", css)
        self.assertIn("border-radius: 1rem", css)
        self.assertIn("overflow-wrap: anywhere", css)


if __name__ == "__main__":
    unittest.main()
