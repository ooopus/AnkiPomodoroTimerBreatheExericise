# 番茄钟 & 呼吸训练 Anki 插件

这是一个为Anki设计的插件，结合了番茄工作法和呼吸训练功能，帮助你在学习时保持专注和放松。

## 功能特点

- 🍅 番茄钟计时器（默认25分钟）
- 🌬️ 呼吸训练（吸气-屏住-呼气循环）
- ⏱️ 状态栏实时显示剩余时间
- 🎯 长休息机制（连续完成指定番茄数后）
- ⚙️ 完全可配置的参数设置

## 安装方法

1. 在Anki中点击"工具" > "插件" > "获取插件"
2. 填入<code>1953077949</code>进行安装
3. 重启Anki

## 使用方法

### 基本使用

1. 开始复习卡片时，插件会自动启动番茄钟计时器
2. 状态栏会显示剩余时间（如"🍅 24:59"）和完成进度
3. 番茄钟结束后会自动进入休息时间
4. 休息结束后自动进入呼吸训练
5. 呼吸训练完成后会返回牌组浏览器

### 休息机制

- 每个番茄钟结束后会进入短休息
- 完成指定数量的番茄钟后会触发长休息
- 休息时间显示在状态栏，带有特殊提示图标
- 可配置最大休息时长，防止过度休息

### 呼吸训练说明

呼吸训练包含以下可配置的阶段：
- 吸气（默认4秒）
- 屏住（默认禁用）
- 呼气（默认6秒）

### 快捷键

- 无特定快捷键，所有操作通过界面完成

### 计时器窗口

- 可选的圆形计时器窗口，显示剩余时间进度
- 窗口可设置为"始终置顶"模式
- 支持四种位置配置：左上角、右上角、左下角、右下角
- 实时显示番茄钟和休息时间进度

## 配置选项

通过"工具" > "番茄钟 & 呼吸设置..."可以配置以下选项：

### 常规设置
- 启用/禁用插件
- 显示/隐藏状态栏计时器
- 显示/隐藏圆形计时器窗口
- 计时器窗口位置（左上角/右上角/左下角/右下角）
- 番茄钟时长（1-180分钟）
- 连续番茄数量设置（触发长休息）
- 长休息时长设置
- 最大休息时间限制

### 呼吸训练设置
- 循环次数（0-50次）
- 各阶段启用/禁用
- 各阶段持续时间（0-60秒）

设置界面会实时显示预计的总训练时间。

## 开发相关

### 环境要求
- Python 3.9
- aqt >= 25.0

### 国际化 (i18n)

#### 翻译文件结构
```
locales/
├── en_US/
│   └── LC_MESSAGES/
│       ├── messages.mo
│       └── messages.po
└── zh_CN/
    └── LC_MESSAGES/
        ├── messages.mo
        └── messages.po
```

#### 翻译工作流程

1. 提取需要翻译的字符串：
```bash
cd AnkiPomodoroTimerBreatheExericise
pybabel extract -F babel.cfg -o locales/messages.pot .
```

2. 初始化新语言（如果是第一次添加该语言）：
```bash
pybabel init -i locales/messages.pot -d locales -l <语言代码>
```
例如：`pybabel init -i locales/messages.pot -d locales -l zh_CN`

3. 更新现有翻译文件：
```bash
pybabel update -i locales/messages.pot -d locales
```

4. 编辑 .po 文件添加翻译内容
- 编辑 `locales/<语言代码>/LC_MESSAGES/messages.po`
- 为每个 msgid 添加对应的 msgstr 翻译

5. 编译翻译文件：
```bash
pybabel compile -d locales
```

#### 添加新的翻译字符串

1. 在代码中使用 `_()` 函数包装需要翻译的字符串：
```python
from .translator import _
message = _("需要翻译的文本")
```

2. 重复上述工作流程步骤 1-5

#### 支持的语言
- 英语 (en_US)
- 简体中文 (zh_CN)

#### 贡献翻译
1. Fork 本仓库
2. 按照上述工作流程添加新语言或改进现有翻译
3. 提交 Pull Request

### 开发指南

#### 目录结构
```
AnkiPomodoroTimerBreatheExericise/
├── __init__.py          # 插件入口
├── babel.cfg            # Babel 配置文件
├── breathing.py         # 呼吸训练相关
├── config.py           # 配置管理
├── constants.py        # 常量定义
├── hooks.py            # Anki 钩子函数
├── locales/            # 翻译文件
├── pomodoro.py         # 番茄钟功能
├── timer_utils.py      # 计时器工具
├── translator.py       # 翻译器
└── ui/                 # 用户界面
```

#### 代码风格
- 使用 Python 类型注解
- 遵循 PEP 8 规范
- 所有用户可见的字符串都需要使用 `_()` 包装以支持翻译

### 问题反馈
如果你发现任何问题或有改进建议，请在 GitHub 仓库提交 Issue。
