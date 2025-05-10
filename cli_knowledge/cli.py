import typer
from . import auth
from . import repo_scanner
from . import vectorizer
from . import categorizer
import os

app = typer.Typer(help="个人代码知识库 CLI 工具")

@app.command()
def login():
    """用户登录"""
    auth.login()

@app.command()
def logout():
    """用户登出"""
    auth.logout()

@app.command()
def status():
    """显示当前登录状态"""
    user = auth.get_current_user()
    if user:
        typer.echo(f"已登录用户: {user}")
    else:
        typer.echo("未登录，请先运行 uvx login")

@app.command()
def scan(
    path: str = typer.Option(..., help="要扫描的代码目录"),
    category: str = typer.Option("", help="分类标签，逗号分隔，可选")
):
    """扫描本地 Python 代码仓库，抽取函数和类片段。"""
    user = auth.get_current_user()
    if not user:
        typer.echo("请先登录 (uvx login)")
        raise typer.Exit()
    categories = [c.strip() for c in category.split(",") if c.strip()] if category else []
    typer.echo(f"开始扫描 {path} ...")
    snippets = repo_scanner.scan_python_files(path, categories)
    output_dir = os.path.expanduser(f"~/.cli_knowledge/{user}")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "snippets.json")
    repo_scanner.save_snippets(snippets, output_path)
    typer.echo(f"扫描完成，已保存 {len(snippets)} 个片段到 {output_path}")

@app.command()
def vectorize():
    """对已扫描的代码片段进行向量化并存入本地知识库。"""
    user = auth.get_current_user()
    if not user:
        typer.echo("请先登录 (uvx login)")
        raise typer.Exit()
    data_dir = os.path.expanduser(f"~/.cli_knowledge/{user}")
    snippets_path = os.path.join(data_dir, "snippets.json")
    if not os.path.exists(snippets_path):
        typer.echo("请先运行 uvx scan 扫描代码片段")
        raise typer.Exit()
    typer.echo("开始向量化代码片段...")
    snippets = vectorizer.load_snippets(snippets_path)
    vectors, meta = vectorizer.vectorize_snippets(snippets)
    index_path = os.path.join(data_dir, "faiss.index")
    meta_path = os.path.join(data_dir, "meta.json")
    vectorizer.save_faiss_index(vectors, meta, index_path, meta_path)
    typer.echo(f"向量化完成，已保存向量库到 {index_path}，元数据到 {meta_path}")

@app.command()
def search(
    query: str = typer.Argument(..., help="检索内容"),
    category: str = typer.Option("", help="按分类过滤，可选")
):
    """检索知识库，返回最相关的代码片段。"""
    user = auth.get_current_user()
    if not user:
        typer.echo("请先登录 (uvx login)")
        raise typer.Exit()
    data_dir = os.path.expanduser(f"~/.cli_knowledge/{user}")
    index_path = os.path.join(data_dir, "faiss.index")
    meta_path = os.path.join(data_dir, "meta.json")
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        typer.echo("请先运行 uvx vectorize 生成知识库")
        raise typer.Exit()
    results = vectorizer.search(query, index_path, meta_path, category=category if category else None)
    if not results:
        typer.echo("未找到相关代码片段。"); return
    for i, item in enumerate(results, 1):
        typer.secho(f"[{i}] {item['type']} {item['name']} (文件: {item['file_path']})", fg=typer.colors.CYAN)
        typer.echo(f"分类: {', '.join(item.get('category', []))}")
        typer.echo(item['code'])
        typer.echo("-"*40)

categories_app = typer.Typer(help="分类管理")

@categories_app.command("list")
def list_categories():
    """列出所有分类"""
    user = auth.get_current_user()
    if not user:
        typer.echo("请先登录 (uvx login)")
        raise typer.Exit()
    data_dir = os.path.expanduser(f"~/.cli_knowledge/{user}")
    cats = categorizer.get_categories(data_dir)
    if not cats:
        typer.echo("暂无分类")
    else:
        for c in cats:
            typer.echo(f"- {c}")

@categories_app.command("add")
def add_category(name: str = typer.Option(..., help="分类名")):
    """新增分类"""
    user = auth.get_current_user()
    if not user:
        typer.echo("请先登录 (uvx login)")
        raise typer.Exit()
    data_dir = os.path.expanduser(f"~/.cli_knowledge/{user}")
    categorizer.add_category(data_dir, name)
    typer.echo(f"已添加分类: {name}")

@categories_app.command("remove")
def remove_category(name: str = typer.Option(..., help="分类名")):
    """删除分类"""
    user = auth.get_current_user()
    if not user:
        typer.echo("请先登录 (uvx login)")
        raise typer.Exit()
    data_dir = os.path.expanduser(f"~/.cli_knowledge/{user}")
    categorizer.remove_category(data_dir, name)
    typer.echo(f"已删除分类: {name}")

app.add_typer(categories_app, name="categories", help="分类管理相关命令")

if __name__ == "__main__":
    app() 