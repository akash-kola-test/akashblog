import logging
import logging.config
import os
import re

from logging_configs.logger import setup_logging

logger = logging.getLogger("image_processor")
logger.setLevel(logging.INFO)


posts_dir = r"C:\Users\datag\Desktop\Hugo\akashblog\content\posts"


def process_dir(posts_dir: str):
    logging.info("processing directory %s", posts_dir)

    for filename in os.listdir(posts_dir):
        changes_made = False
        if os.path.isdir(os.path.join(posts_dir, filename)):
            process_dir(os.path.join(posts_dir, filename))
            continue

        if not filename.endswith(".md"):
            logging.info("skipping the file %s as it is not MD file", filename)
            continue

        if filename == "InfluxDB.md":
            print()

        logging.info("processing file %s", filename)
        filepath = os.path.join(posts_dir, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        section_links:list[str] = re.findall(r"\[\[#([- A-Za-z0-9_.]+)\]\]", content)
        
        for section_link in section_links:
            logging.info("processing section link %s", section_link)
            formatted_section_link = section_link.lower().replace(" ", "-")
            content = content.replace(f"[[#{section_link}]]", f"[{section_link}](#{formatted_section_link})")
            changes_made = True

        if not changes_made:
            continue

        logging.info("writing back the content to file %s", filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

setup_logging("logging_configs/config.json")
process_dir(posts_dir)

logger.info("Markdown files processed and images copied successfully.")
