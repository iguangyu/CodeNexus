import os
import json
import typer
from pathlib import Path

CONFIG_DIR = Path.home() / ".cli_knowledge"
CONFIG_FILE = CONFIG_DIR / "config.json"


def login():
    """本地登录，保存用户名和 token（可选）。"""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    username = typer.prompt("请输入用户名")
    token = typer.prompt("请输入Token（可选，直接回车跳过）", default="", hide_input=True)
    config = {"username": username, "token": token}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f)
    typer.echo(f"登录成功，欢迎 {username}！")

def logout():
    """登出，删除本地配置。"""
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        typer.echo("已登出。");
    else:
        typer.echo("未登录，无需登出。")

def get_current_user():
    """获取当前已登录用户名，没有则返回 None。"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("username")
    return None 