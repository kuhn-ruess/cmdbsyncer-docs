import glob
import os


NOTICES_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "cmdbsyncer", "notices")
)


def on_page_markdown(markdown, page, config, files):
    if page.file.src_path != "updates/update_notes.md":
        return markdown

    notices = []
    for filepath in sorted(glob.glob(os.path.join(NOTICES_DIR, "*.txt"))):
        with open(filepath, encoding="utf-8") as f:
            content = f.read().strip()

        name = os.path.splitext(os.path.basename(filepath))[0]
        title = name.replace("_", " ").title()

        lines = [f'!!! warning "{title}"']
        for line in content.splitlines():
            lines.append(("    " + line) if line else "")
        notices.append("\n".join(lines))

    if not notices:
        return markdown.replace("<!-- NOTICES -->", "")

    notice_block = "\n\n".join(notices)
    return markdown.replace("<!-- NOTICES -->", notice_block)
