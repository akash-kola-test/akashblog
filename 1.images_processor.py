import logging
import logging.config
import os
import re
import shutil

from logging_configs.logger import setup_logging

logger = logging.getLogger("image_processor")
logger.setLevel(logging.INFO)


posts_dir = r"C:\Users\datag\Desktop\Hugo\akashblog\content\posts"
attachments_dir = r"C:\Users\datag\Desktop\Obsidian\Obsidian Akash - Datagrokr\Attachments"
static_images_dir = r"C:\Users\datag\Desktop\Hugo\akashblog\static\images"


def process_dir(posts_dir: str):
    logging.info("processing directory %s", posts_dir)

    for filename in os.listdir(posts_dir):
        if os.path.isdir(os.path.join(posts_dir, filename)):
            process_dir(os.path.join(posts_dir, filename))
            continue

        if not filename.endswith(".md"):
            logging.info("skipping the file %s as it is not MD file", filename)
            continue

        logging.info("processing file %s", filename)
        filepath = os.path.join(posts_dir, filename)

        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()

        images = re.findall(r"!\[\[([^]]*\.png)\]\]", content)
        for image in images:
            logging.info("processing image %s", image)
            markdown_image = f"[{image.split('.png')[0]}](images/{image.replace(' ', '%20')})"
            content = content.replace(f"[[{image}]]", markdown_image)

            logging.info("copying image to static directory")
            image_source = os.path.join(attachments_dir, image)
            if os.path.exists(image_source):
                shutil.copy(image_source, static_images_dir)

        logging.info("writing back the content to file %s", filename)
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)

setup_logging("logging_configs/config.json")
process_dir(posts_dir)

logger.info("Markdown files processed and images copied successfully.")
