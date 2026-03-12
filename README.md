# -arxiv-ai-
Arxiv-AI-Reporter: 专业天体物理日报自动生成器
Arxiv-AI-Reporter 是一个专为天文从业者和爱好者设计的自动化情报工具。它不仅仅是翻译，更是通过 AI 模拟资深科学家的视角，对每日更新的 astro-ph.ga（星系物理）论文进行深度扫描、分类索引并生成可以直接发布在公众号、知乎、小红书等平台的HTML简报。

GA_Sync_Report_2026-03-12.pdf 为2025.3.12的arxiv星系文章报告的样例。

✨ 核心亮点
📅 严格公告周期同步：自动模拟 arXiv 官方公告窗口（美国东部时间 14:00 截断），确保生成的报告与官网 New 列表在篇数和内容上 1:1 精准对齐。

🎓 学术大牛自动识别：内置资深学者图谱，自动识别并高亮领域顶尖 PI（如 Norman Murray, Luis Ho, Sunyaev 等），助你一眼锁定重磅研究。

🍱 结构化双层排版：

一、领域归类索引：快速了解今日 AGN、星系演化、引力理论等子领域的更新热度 。

二、论文条目详情：包含中文标题、作者高亮、方法标签及 2-3 句深度物理总结 。

📱 多端适配输出：生成的 HTML 采用内联样式，支持一键粘贴至微信公众号，且对移动端阅读进行了专门优化。

🚀 快速开始
1. 环境准备

确保你的环境中已安装 Python 3.8+，并安装必要依赖：

Bash
pip install arxiv openai pytz
2. 配置 API

在脚本中配置你的 API Key 和 Base URL：

Python
MY_API_KEY = "你的_API_KEY"
MY_BASE_URL = "你的_API_代理地址"
MY_MODEL = "claude-3-5-sonnet-20240620" # 建议使用 Sonnet 以获得最佳速度/智能比
3. 运行

Bash
python daily_arxiv.py
运行结束后，你会得到一个名为 GA_Daily_YYYY-MM-DD.html 的文件。

🎨 简报预览

[18] Abell 402中央星系中心的千秒差距尺度恒星空腔
作者：Michael McDonald ★(Famous Scholar), ... Priyamvada Natarajan ★(Famous Scholar)
研究方法：Observation

核心物理结果：JWST/NIRCam 揭示了 Abell 402 中心星系存在 2 kpc 尺度的恒星密度空腔，推断存在质量高达 6×10 
10 M⊙的超巨质量黑洞，可能是目前已知最重的双黑洞系统之一。

🛠️ 项目结构
daily_arxiv.py: 主逻辑脚本，包含时区计算、数据抓取与 AI 调用。

outputs/: 存放每日生成的 HTML 报告。

License: MIT

💡为什么需要这个工具？

在信息爆炸的时代，天文研究者每天面临几十篇新论文。这个工具的存在不是为了替代阅读，而是为了降低筛选成本。它帮你把 1 小时的刷 arXiv 时间缩短到 5 分钟，把精力留给真正需要精读的论文。
