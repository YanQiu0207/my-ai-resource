# 项目规则

## 版本管理（强制）

- 本项目使用 git 管理版本

## 文档规则

- TODO

## 代码规则

- Python 测试统一用标准库 `unittest`，不适用 `std-python` 的 pytest 默认——本仓库脚本是装机工具链，须裸 Python 可跑，不引入第三方依赖（pytest 可直接收集 unittest 用例，后续需要其工具链时无须改写）
