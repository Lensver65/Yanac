import json
import re
import html

INPUT_FILE = "wp_posts.json"
OUTPUT_FILE = "clean_posts.txt"


def strip_html(text: str) -> str:
    if not text:
        return ""

    # Remove WordPress block comments: <!-- wp:... --> ... <!-- /wp:... -->
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)

    # Decode HTML entities (&nbsp;, &amp;, etc.)
    text = html.unescape(text)

    # Normalize whitespace (collapse multiple blank lines)
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text).strip()

    return text


with open(INPUT_FILE, "r", encoding="utf-8") as f:
    root = json.load(f)

# Locate the phpMyAdmin "table" block and its rows
table_obj = next(item for item in root if isinstance(item, dict) and item.get("type") == "table")
posts = table_obj.get("data", [])

with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
    for post in posts:
        post_id = str(post.get("ID", "")).strip()
        title = (post.get("post_title") or "").strip()
        content = strip_html(post.get("post_content") or "")
        tags = (post.get("tags") or "").strip()

        out.write("=" * 80 + "\n")
        out.write(f"{title}\n")
        if post_id:
            out.write(f"ID: {post_id}\n")
        out.write(f"Tags: {tags if tags else 'None'}\n")
        out.write("-" * 80 + "\n\n")
        out.write(content + "\n\n\n")

print(f"Done. Clean content saved to: {OUTPUT_FILE}")
