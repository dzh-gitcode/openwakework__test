# Git 分支操作记录：openWakeWord + Whisper 项目

本文件记录将「Whisper 持续监听 + 中文关键词匹配」版本作为新分支上传到 GitHub 的完整流程，以及后续分支切换指令。

---

## 1. 分支概述

| 分支名 | 说明 | 唤醒词方案 |
|--------|------|-----------|
| `main` | 原始版本 | openWakeWord（固定英文唤醒词：hey jarvis 等） |
| `feature/whisper-chinese-wakeword` | 新分支 | Whisper 持续监听 + 中文关键词匹配（支持任意中文唤醒词，无需训练） |

### 两个分支的核心差异

| 对比项 | `main` 分支 | `feature/whisper-chinese-wakeword` 分支 |
|--------|-------------|----------------------------------------|
| openWakeWord 依赖 | ✅ 有 | ❌ 已移除 |
| 中文唤醒词 | ❌ 不支持 | ✅ 支持（小助手、你好助手等） |
| 监听机制 | openWakeWord 小模型推理 | Whisper base 每 3 秒识别一次 |
| 唤醒词修改 | 需重新训练模型 | 改一行代码即可 |

---

## 2. 本次操作的完整指令（历史记录）

以下是将修改内容作为新分支上传到 GitHub 的一整套指令：

### 2.1 查看当前状态

```bash
# 查看当前仓库状态（所在分支、修改的文件）
git status

# 输出示例：
# On branch main
# Your branch is up to date with 'origin/main'.
#
# Changes not staged for commit:
#   modified:   README.md
#   modified:   main.py
#   modified:   requirements.txt
#   modified:   test_full.py
```

### 2.2 查看远程仓库和现有分支

```bash
# 查看远程仓库地址和分支列表
git remote -v
git branch

# 输出示例：
# origin  https://github.com/dzh-gitcode/openwakework__test.git (fetch)
# origin  https://github.com/dzh-gitcode/openwakework__test.git (push)
# * main
```

### 2.3 创建并切换到新分支

```bash
# 基于当前 main 分支的修改，创建新分支并切换过去
git checkout -b feature/whisper-chinese-wakeword

# 输出：
# Switched to a new branch 'feature/whisper-chinese-wakeword'
```

> **说明**：`git checkout -b <branch>` = 创建新分支 + 立即切换到新分支。
> 创建新分支时，当前工作区的修改（未提交的）会被带过去。

### 2.4 将修改的文件加入暂存区并提交

```bash
# 将所有修改的文件加入暂存区
git add README.md main.py requirements.txt test_full.py

# 也可以用这个更简单的写法（添加当前目录所有修改）：
# git add .

# 提交到本地仓库，带上清晰的 commit message
git commit -m "feat: 使用 Whisper 持续监听 + 中文关键词匹配替代 openWakeWord

- 移除 openWakeWord 依赖，改用 Whisper 持续监听中文关键词
- 支持中文唤醒词：小助手、你好助手、助手、你好小助手、嘿小助手
- 两阶段设计：监听阶段(3秒) + 命令阶段(10秒)
- 更新 README、requirements.txt 和测试脚本"
```

> **提示**：commit message 规范
> - 第一行：简要说明（50 字以内最佳）
> - 空一行后：详细的变更点列表
> - 使用英文动词开头（feat, fix, refactor, docs, chore 等）便于阅读

### 2.5 将新分支推送到 GitHub

```bash
# 推送到远程仓库 origin，并设置本地分支跟踪远程同名分支
git push -u origin feature/whisper-chinese-wakeword

# 输出示例：
# Enumerating objects: 11, done.
# Counting objects: 100% (11/11), done.
# Delta compression using up to 32 threads...
# Writing objects: 100% (6/6), 6.11 KiB | 3.06 MiB/s, done.
# remote: Resolving deltas: 100% (1/1), completed with 1 local object.
# remote:
# remote: Create a pull request for 'feature/whisper-chinese-wakeword' on GitHub by visiting:
# remote:      https://github.com/dzh-gitcode/openwakework__test/pull/new/feature/whisper-chinese-wakeword
# * [new branch]      feature/whisper-chinese-wakeword -> feature/whisper-chinese-wakeword
# branch 'feature/whisper-chinese-wakeword' set up to track 'origin/feature/whisper-chinese-wakeword'.
```

> **参数说明**：`-u` = `--set-upstream`，设置本地分支和远程分支的关联关系。
> 这样以后在这个分支直接用 `git push` 和 `git pull` 就不用再加参数了。

### 2.6 验证结果

```bash
# 查看最近 3 个 commit
git log --oneline -3

# 查看所有分支（本地 + 远程）
git branch -a

# 输出示例：
# 6398dd8 feat: 使用 Whisper 持续监听 + 中文关键词匹配替代 openWakeWord
# 88efbbb first commit
# * feature/whisper-chinese-wakeword
#   main
#   remotes/origin/feature/whisper-chinese-wakeword
#   remotes/origin/main
```

> `*` 号表示当前所在的分支。`remotes/origin/` 开头的是远程仓库的分支。

---

## 3. 后续常用指令（速查表）

### 3.1 查看分支和切换分支

```bash
# 查看所有本地分支
git branch

# 查看所有分支（本地 + 远程）
git branch -a

# 切换到 main 分支（原始 openWakeWord 版本）
git checkout main

# 切换到中文唤醒词分支
git checkout feature/whisper-chinese-wakeword

# Git 2.23+ 也可以用 switch（语义更清晰）：
# git switch main
# git switch feature/whisper-chinese-wakeword
```

> **重要**：切换分支前最好确保当前工作区没有未提交的修改。
> 如果有未提交的修改但想切换分支，可以用 `git stash` 暂存起来，切换后再用 `git stash pop` 恢复。

### 3.2 拉取最新更新

```bash
# 拉取当前分支的最新更新（在团队协作场景常用）
git pull

# 拉取所有远程分支的最新信息（不合并到本地）
git fetch --all

# 查看远程有哪些分支
git remote show origin
```

### 3.3 查看差异和历史

```bash
# 查看当前分支与 main 分支的差异
git diff main..feature/whisper-chinese-wakeword

# 只看哪些文件被修改了
git diff main..feature/whisper-chinese-wakeword --stat

# 查看 commit 历史
git log --oneline
git log --oneline -5        # 最近 5 个
git log --graph --oneline   # 图形化显示
```

### 3.4 在新分支上继续修改

```bash
# 假设在 feature 分支上继续改代码...

# 1. 修改文件后
git add <file1> <file2>
git commit -m "fix: 修正唤醒词检测逻辑"

# 2. 推送到远程（第一次 push 后这里就不需要 -u 了）
git push
```

### 3.5 创建其他新分支的通用流程

```bash
# 通用模板：在 main 分支基础上创建新分支
git checkout main              # 1. 先切换到基础分支
git pull                       # 2. 确保是最新的
git checkout -b feature/xxx    # 3. 创建并切换到新分支
# 然后修改代码...
git add .                      # 4. 添加修改
git commit -m "描述变更内容"    # 5. 提交
git push -u origin feature/xxx # 6. 推送到 GitHub
```

---

## 4. 分支工作流图示

```
    GitHub (origin)
    ┌─────────────────────────────────────────────┐
    │                                             │
    │  main ──────●──────●─────  (openWakeWord)   │
    │                ╲                            │
    │                 ╲                           │
    │  feature/... ────●─────●─────  (中文唤醒词)  │
    │                                             │
    └─────────────────────────────────────────────┘
           ▲                  ▲
           │                  │
     git push           git push
           │                  │
    ┌──────────────┐   ┌──────────────┐
    │  本地仓库     │   │  本地仓库     │
    │  (你的电脑)   │   │  (你的电脑)   │
    │  main 分支    │   │  feature 分支 │
    └──────────────┘   └──────────────┘
```

---

## 5. 快捷指令汇总（一键复制）

### 常用：在两个分支间切换

```bash
# 查看所有分支
git branch -a

# 切换到 main（openWakeWord 版本）
git checkout main

# 切换到中文唤醒词版本
git checkout feature/whisper-chinese-wakeword

# 拉取当前分支的最新更新
git pull
```

### 创建新分支完整流程

```bash
# 基于 main 创建新分支
git checkout main
git pull
git checkout -b feature/<branch-name>

# 修改代码后提交
git add .
git commit -m "<描述你的变更>"
git push -u origin feature/<branch-name>
```

### 删除分支（慎用！）

```bash
# 删除本地分支（需要先切换到其他分支）
git branch -d feature/<branch-name>       # 仅在分支已合并后删除
git branch -D feature/<branch-name>       # 强制删除（不管是否合并）

# 删除远程分支
git push origin --delete feature/<branch-name>
```

---

## 6. 常见问题

### Q1: 切换分支时报 "error: Your local changes to the following files would be overwritten..."

**A**: 当前分支有未提交的修改，切换分支会被覆盖。解决方法：

```bash
# 方案一：先提交修改
git add .
git commit -m "保存当前工作"
git checkout <other-branch>

# 方案二：暂存修改（稍后可恢复）
git stash                       # 暂存当前修改
git checkout <other-branch>    # 切换分支
# 想恢复暂存的修改时：
git checkout <original-branch>
git stash pop                   # 恢复最近一次 stash
```

### Q2: 想查看两个分支的具体差异

```bash
# 看所有文件差异
git diff main..feature/whisper-chinese-wakeword

# 只看某个文件的差异
git diff main..feature/whisper-chinese-wakeword -- main.py

# 用图形化工具查看（如果配置了）
git difftool main..feature/whisper-chinese-wakeword
```

### Q3: 推送时报错 "fatal: The current branch xxx has no upstream branch"

**A**: 第一次推送新分支时没加 `-u` 参数。补上即可：

```bash
git push -u origin feature/<branch-name>
```

### Q4: 在 GitHub 上如何对比两个分支？

**A**: 直接访问 GitHub 提供的 URL，将分支对比：

```
https://github.com/dzh-gitcode/openwakework__test/compare/main...feature/whisper-chinese-wakeword
```

或者在 GitHub 项目页面点击「Compare & pull request」按钮。

---

## 7. Commit Message 推荐规范（可选但实用）

```
<type>: <subject>
<空行>
<body>
```

常用的 `<type>`：

| type | 说明 |
|------|------|
| `feat` | 新功能（feature） |
| `fix` | 修复 bug |
| `docs` | 文档变更（如 README） |
| `style` | 代码格式调整（不影响逻辑） |
| `refactor` | 代码重构（不加功能也不修 bug） |
| `perf` | 性能优化 |
| `test` | 测试相关 |
| `chore` | 构建/工具链/依赖等辅助性变更 |

示例：

```
feat: 支持语音命令识别

- 实现监听阶段(3秒) + 命令阶段(10秒) 的两阶段设计
- 支持中文唤醒词：小助手、你好助手
- 增加停止命令识别（"停止"/"stop"）
```

---

*本文件生成于 2025-06-15，记录 openWakeWord + Whisper 项目的分支管理操作。*
