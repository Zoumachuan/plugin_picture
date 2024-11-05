# encoding:utf-8

import os
import random
import json

from bridge.bridge import Bridge
import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *

@plugins.register(name="PictureSelecter", desc="从本地图片库中随机选择一张图片", version="1.0", author="YourName")
class PictureSelecter(Plugin):
    def __init__(self):
        super().__init__()
        curdir = os.path.dirname(__file__)
        config_path = os.path.join(curdir, "config.json")
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                self.image_directory = config["image_directory"]
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            logger.info("[PictureSelecter] inited")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                logger.warn(f"[PictureSelecter] init failed, {config_path} not found.")
            else:
                logger.warn("[PictureSelecter] init failed, error: ", e)
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.IMAGE_CREATE:
            return
        
        logger.debug("[PictureSelecter] on_handle_context. content: %s" % e_context['context'].content)

        reply = Reply()
        try:
            image_path = self.get_random_image_path()
            if image_path:
                with open(image_path, 'rb') as img_file:
                    reply.type = ReplyType.IMAGE
                    reply.content = img_file.read()
                e_context.action = EventAction.BREAK_PASS  # 事件结束后，跳过处理context的默认逻辑
            else:
                reply.type = ReplyType.ERROR
                reply.content = "无法找到图片，请检查图片目录设置。"
                e_context.action = EventAction.CONTINUE
        except Exception as e:
            reply.type = ReplyType.ERROR
            reply.content = "[PictureSelecter] " + str(e)
            logger.error("[PictureSelecter] exception: %s" % e)
            e_context.action = EventAction.CONTINUE
        finally:
            e_context['reply'] = reply

    def get_random_image_path(self):
        image_files = []
        for root, _, files in os.walk(self.image_directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_files.append(os.path.join(root, file))
        
        if not image_files:
            return None
        return random.choice(image_files)
