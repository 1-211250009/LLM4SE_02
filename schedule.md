📌 Photo Watermark 2 开发路线图

🚀 阶段 0：项目初始化（Day 1-2）

 创建 GitHub 仓库，提交初始 README.md（需求说明已完成）。

 建立项目结构：

photo-watermark/
├─ main.py
├─ core/            # 核心逻辑
├─ ui/              # UI 文件（Qt Designer）
├─ utils/           # 工具类
├─ tests/           # 单元测试
└─ requirements.txt


 配置项目内虚拟环境venv，安装依赖：PySide6, Pillow, pytest, pyinstaller。

 提交第一个 GitHub commit：chore: 初始化项目结构与依赖。

📂 阶段 1：文件处理功能（Day 3-5）

 实现单张图片导入（拖拽/文件选择器）。

 支持批量导入和文件夹导入，显示缩略图和文件名列表。

 支持主流格式读取（JPEG, PNG, BMP, TIFF），验证透明通道支持。

 导出功能：指定输出文件夹、命名规则（原名/前缀/后缀）。

 GitHub 提交：feat: 实现图片导入与导出功能。

🖊 阶段 2：文本水印（Day 6-8）

 添加文本水印输入框。

 支持字体大小、透明度调节。

 在预览窗口实时显示水印。

 GitHub 提交：feat: 添加基本文本水印功能。

🔹 可选高级功能（后续迭代）：字体选择、颜色调色板、阴影/描边效果。

🖼 阶段 3：图片水印（Day 9-11）

 支持从本地选择 PNG Logo 作为水印。

 实现图片水印缩放和透明度调节。

 预览实时显示水印。

 GitHub 提交：feat: 支持图片水印功能。

🎛 阶段 4：水印布局与样式（Day 12-14）

 预设九宫格布局位置。

 支持在预览中拖拽水印。

 提供旋转水印的滑块。

 GitHub 提交：feat: 添加水印布局与旋转功能。

⚙️ 阶段 5：配置管理（Day 15-16）

 支持保存/加载水印模板（JSON 文件）。

 支持启动时加载上一次设置。

 GitHub 提交：feat: 支持水印模板保存与加载。

🛠 阶段 6：优化与发布（Day 17-19）

 增加 JPEG 输出质量调节功能。

 增加图片导出尺寸缩放选项。

 完善异常处理与用户提示。

 编写单元测试，确保主要功能可用。

 GitHub 提交：chore: 优化用户体验与测试覆盖。

📦 阶段 7：打包与发布（Day 20）

 使用 pyinstaller 打包 .app 应用。

 本地测试可运行。

 在 GitHub 创建 Release，上传 .dmg / .app 文件。

 GitHub 提交：release: 发布 v1.0.0 MacOS 可执行文件。