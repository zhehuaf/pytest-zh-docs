# pytest 中文文档构建指南

## 本地构建

### 1. 安装依赖

```bash
cd /Users/zhangzhehua/Documents/GitHub/pytest
pip install -e ".[docs]"
```

或手动安装：
```bash
pip install sphinx furo sphinx-inline-tabs sphinxcontrib-trio sphinx-autodoc-typehints sphinx-removed-in
```

### 2. 构建 HTML 文档

```bash
cd /Users/zhangzhehua/Documents/GitHub/pytest/doc/zh-cn
make html
```

或直接在项目根目录：
```bash
sphinx-build doc/zh-cn doc/zh-cn/_build/html
```

### 3. 查看文档

构建完成后，打开 `doc/zh-cn/_build/html/index.html` 即可浏览。

## 部署到 Web

### 方案一：Netlify（推荐，最简单）

1. 将代码推送到 GitHub
2. 登录 [Netlify](https://www.netlify.com/)
3. 点击 "New site from Git"
4. 选择你的 GitHub 仓库
5. 构建设置：
   - Build command: `sphinx-build doc/zh-cn doc/zh-cn/_build/html`
   - Publish directory: `doc/zh-cn/_build/html`
6. 点击 "Deploy site"

### 方案二：GitHub Pages

1. 创建 GitHub Actions 工作流文件 `.github/workflows/docs.yml`：

```yaml
name: Deploy Docs
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install sphinx furo sphinx-inline-tabs sphinxcontrib-trio
      - run: sphinx-build doc/zh-cn doc/zh-cn/_build/html
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./doc/zh-cn/_build/html
```

2. 在 GitHub 设置中启用 GitHub Pages
3. 选择 "GitHub Actions" 作为部署源

### 方案三：Read the Docs

1. 登录 [Read the Docs](https://readthedocs.org/)
2. 导入你的 GitHub 仓库
3. 创建 `.readthedocs.yml`：

```yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.11"

python:
  install:
    - method: pip
      path: .
      extra_requirements:
        - docs

sphinx:
  configuration: doc/zh-cn/conf.py

formats:
  - html
```

## 文档结构

```
doc/zh-cn/
├── conf.py              # Sphinx 配置文件
├── index.rst            # 首页
├── getting-started.rst  # 入门指南
├── how-to/              # 操作指南
├── explanation/         # 概念解释
├── reference/           # API 参考
└── example/             # 示例代码
```

## 注意事项

1. 确保 `index.rst` 包含所有需要展示的文档的 toctree
2. 图片文件放在 `_static/` 和 `img/` 目录
3. 每次修改后重新构建才能看到效果
