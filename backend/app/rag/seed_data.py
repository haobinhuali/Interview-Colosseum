JOB_PROFILES = {
    "AI Agent 开发工程师": {
        "techs": [
            "LangChain", "RAG", "Chroma", "Prompt Engineering", "Function Calling",
            "LangGraph", "CrewAI", "AutoGen", "Semantic Kernel", "Vector Database",
            "Embedding", "ReAct", "Chain of Thought", "Few-shot Learning", "Fine-tuning",
            "LlamaIndex", "Haystack", "Transformers", "Hugging Face", "OpenAI API"
        ],
        "concepts": [
            "Agent自主决策", "工具调用协议", "多Agent协同", "状态机编排",
            "上下文窗口管理", "对话记忆压缩", "幻觉检测与缓解", "检索增强生成",
            "向量相似度搜索", "知识分块策略", "Rerank重排序", "混合检索",
            "Prompt模板设计", "输出格式约束", "思维链推理", "多模态理解",
            "流式输出处理", "Token消耗优化", "并发会话管理", "评估指标设计"
        ],
        "problems": [
            "LLM幻觉问题", "上下文窗口限制", "多轮对话记忆丢失", "检索结果不相关",
            "Agent死循环", "工具调用失败", "并发会话状态冲突", "Token消耗过高",
            "响应延迟过大", "输出格式不稳定", "Prompt注入攻击", "知识库更新滞后"
        ],
        "scenarios": [
            "支持百万级用户的AI对话系统", "多模态智能客服系统", "企业知识库问答平台",
            "自动化代码审查Agent", "多Agent协作的招聘系统", "实时数据分析Agent"
        ],
        "criticisms": [
            "LangChain过度封装、性能差", "RAG检索到的内容完全无关时LLM还是会胡说",
            "多Agent协同不就是几个if-else切换prompt", "思考链可能是LLM在编造理由",
            "SQLite支撑不了高并发", "Prompt Engineering不算真正的技术"
        ]
    },
    "后端开发工程师": {
        "techs": [
            "Spring Boot", "MySQL", "Redis", "Kafka", "RabbitMQ",
            "PostgreSQL", "MongoDB", "Elasticsearch", "Nginx", "Docker",
            "gRPC", "GraphQL", "MyBatis", "Hibernate", "ShardingSphere",
            "Zookeeper", "Nacos", "Sentinel", "Feign", "Gateway"
        ],
        "concepts": [
            "微服务架构", "分布式事务", "CAP定理", "BASE理论",
            "服务熔断降级", "负载均衡策略", "数据库分库分表", "缓存穿透击穿雪崩",
            "消息队列削峰填谷", "接口幂等性", "分布式锁", "限流算法",
            "读写分离", "主从复制", "集群高可用", "服务注册发现",
            "配置中心", "链路追踪", "日志聚合", "灰度发布"
        ],
        "problems": [
            "高并发下的数据一致性", "分布式事务回滚失败", "缓存与数据库双写不一致",
            "消息队列消息丢失", "接口响应超时", "数据库慢查询", "内存泄漏",
            "线程池耗尽", "服务雪崩", "热点Key问题"
        ],
        "scenarios": [
            "秒杀系统设计", "订单系统高可用架构", "支付系统分布式事务",
            "社交平台Feed流系统", "电商搜索推荐系统", "物流追踪实时系统"
        ],
        "criticisms": [
            "微服务拆得太细反而增加复杂度", "Redis缓存方案在数据一致性上有天然缺陷",
            "消息队列引入了更多故障点", "分布式事务性能太差不如最终一致性",
            "你的系统设计没有考虑容灾", "过度设计反而降低了开发效率"
        ]
    },
    "前端开发工程师": {
        "techs": [
            "React", "Vue", "TypeScript", "Webpack", "Vite",
            "Next.js", "Nuxt.js", "Tailwind CSS", "Redux", "Pinia",
            "React Query", "Ant Design", "Element Plus", "Sass", "Less",
            "Jest", "Cypress", "Storybook", "Micro Frontend", "PWA"
        ],
        "concepts": [
            "虚拟DOM", "响应式原理", "组件化设计", "状态管理",
            "路由懒加载", "代码分割", "Tree Shaking", "SSR服务端渲染",
            "SSG静态生成", "CSR客户端渲染", "Hydration", "Fiber架构",
            "Diff算法", "Hooks设计模式", "Composition API", "依赖注入",
            "前端监控", "性能优化", "无障碍设计", "国际化"
        ],
        "problems": [
            "首屏加载白屏时间过长", "大列表渲染卡顿", "内存泄漏导致页面崩溃",
            "跨域请求被拦截", "状态管理混乱", "组件重渲染性能差",
            "移动端适配问题", "浏览器兼容性问题", "XSS攻击防护", "CSRF防护"
        ],
        "scenarios": [
            "大型SPA应用架构设计", "低代码平台前端引擎", "在线协作编辑器",
            "实时数据可视化大屏", "跨平台移动应用", "微前端架构改造"
        ],
        "criticisms": [
            "React Hooks不如Class组件直观", "TypeScript增加了开发成本但收益有限",
            "微前端方案过于复杂", "SSR的Hydration问题根本没解决",
            "前端过度工程化", "你的性能优化没有量化数据支撑"
        ]
    },
    "数据工程师": {
        "techs": [
            "Spark", "Flink", "Kafka", "Hadoop", "Hive",
            "Airflow", "dbt", "Snowflake", "Delta Lake", "Iceberg",
            "Presto", "ClickHouse", "Doris", "Hudi", "DataHub",
            "Great Expectations", "Spark Streaming", "Flink SQL", "Superset", "Grafana"
        ],
        "concepts": [
            "ETL数据管道", "数据仓库建模", "数据湖架构", "流批一体",
            "数据质量治理", "数据血缘追踪", "维度建模", "缓慢变化维",
            "数据分区策略", "数据倾斜处理", "Exactly-Once语义", "水位线机制",
            "状态管理", "窗口计算", "CDC变更捕获", "数据脱敏",
            "元数据管理", "数据目录", "数据资产", "数据中台"
        ],
        "problems": [
            "数据倾斜导致任务超时", "数据质量问题影响下游", "实时与离线数据不一致",
            "小文件过多影响查询性能", "数据管道延迟过高", "数据血缘断裂",
            "存储成本持续增长", "数据安全合规风险"
        ],
        "scenarios": [
            "实时数仓建设方案", "PB级数据湖架构设计", "实时推荐特征工程平台",
            "数据质量监控平台", "跨源数据联邦查询系统", "数据治理平台"
        ],
        "criticisms": [
            "数据中台是伪概念", "Lambda架构维护两套代码成本太高",
            "数据质量工具形同虚设", "实时数仓的ROI根本不值得",
            "你的数据治理方案没有落地", "数据湖变成了数据沼泽"
        ]
    },
    "DevOps工程师": {
        "techs": [
            "Docker", "Kubernetes", "Jenkins", "GitLab CI", "Terraform",
            "Ansible", "Prometheus", "Grafana", "ELK Stack", "ArgoCD",
            "Helm", "Istio", "Consul", "Vault", "Harbor",
            "SonarQube", "Trivy", "Flux", "Pulumi", "Crossplane"
        ],
        "concepts": [
            "CI/CD流水线", "基础设施即代码", "GitOps", "容器编排",
            "服务网格", "蓝绿部署", "金丝雀发布", "混沌工程",
            "可观测性三支柱", "SRE实践", "SLI/SLO/SLA", "事故响应流程",
            "变更管理", "配置管理", "密钥管理", "镜像安全扫描",
            "资源配额管理", "自动扩缩容", "多集群管理", "云原生安全"
        ],
        "problems": [
            "CI/CD流水线不稳定", "K8s资源浪费严重", "镜像安全漏洞",
            "配置漂移", "日志采集丢失", "监控告警风暴",
            "部署回滚失败", "多环境配置不一致"
        ],
        "scenarios": [
            "千人规模研发团队的CI/CD平台", "多集群多地域的K8s管理平台",
            "全链路可观测性平台", "零停机发布系统", "云成本优化平台",
            "安全合规自动化平台"
        ],
        "criticisms": [
            "K8s过度复杂不如直接用ECS", "GitOps在大型团队中根本推不动",
            "你的监控告警全是噪音", "DevOps就是让开发兼运维的借口",
            "基础设施即代码反而增加了维护成本", "服务网格性能开销不值得"
        ]
    },
    "算法工程师": {
        "techs": [
            "PyTorch", "TensorFlow", "Scikit-learn", "XGBoost", "LightGBM",
            "Hugging Face", "ONNX", "TensorRT", "DeepSpeed", "Megatron",
            "Ray", "MLflow", "Weights & Biases", "Optuna", "FAISS",
            "vLLM", "TGI", "ColossalAI", "Deepspeed", "Accelerate"
        ],
        "concepts": [
            "Transformer架构", "注意力机制", "位置编码", "预训练与微调",
            "LoRA/QLoRA", "RLHF", "模型量化", "知识蒸馏", "数据增强",
            "特征工程", "交叉验证", "超参搜索", "A/B测试", "模型部署",
            "推理优化", "分布式训练", "梯度累积", "混合精度训练",
            "模型压缩", "多模态融合"
        ],
        "problems": [
            "模型过拟合", "训练不收敛", "推理延迟过高",
            "GPU显存不足", "数据标注质量差", "模型偏见",
            "冷启动问题", "特征漂移"
        ],
        "scenarios": [
            "千亿参数大模型训练平台", "实时推荐系统", "多模态内容理解平台",
            "智能风控模型系统", "搜索排序系统", "自动驾驶感知系统"
        ],
        "criticisms": [
            "大模型微调的效果不如预期", "你的模型指标好但线上效果差",
            "RLHF的标注成本你考虑过吗", "模型量化后精度下降你验证了吗",
            "深度学习就是炼丹没有理论支撑", "你的A/B测试样本量不够结论不可靠"
        ]
    },
    "全栈开发工程师": {
        "techs": [
            "Node.js", "React", "Vue", "Python", "Java",
            "PostgreSQL", "MongoDB", "Redis", "Docker", "Nginx",
            "Express", "NestJS", "Next.js", "TypeScript", "GraphQL",
            "Prisma", "TypeORM", "Tailwind CSS", "Vercel", "AWS"
        ],
        "concepts": [
            "前后端分离", "BFF中间层", "API网关", "全链路追踪",
            "响应式设计", "渐进式增强", "Serverless", "Jamstack",
            "边缘计算", "Web安全", "数据库设计", "缓存策略",
            "认证授权", "WebSocket", "SSE", "文件存储",
            "日志系统", "错误处理", "性能调优", "技术选型"
        ],
        "problems": [
            "前后端接口对接效率低", "技术栈广度与深度难以兼顾", "全栈项目质量难以保证",
            "部署流程复杂", "技术债务积累", "跨团队协作困难",
            "性能瓶颈定位困难", "安全漏洞频发"
        ],
        "scenarios": [
            "从零搭建SaaS产品", "企业内部工具平台", "电商全栈系统",
            "内容管理系统", "在线教育平台", "社交应用全栈方案"
        ],
        "criticisms": [
            "全栈就是什么都会什么都不精", "一个人做全栈项目质量能保证吗",
            "你的前端/后端深度不够", "全栈工程师的代码可维护性差",
            "技术选型没有充分论证", "你的系统设计缺乏专业性"
        ]
    },
    "移动端开发工程师": {
        "techs": [
            "Swift", "Kotlin", "Flutter", "React Native", "SwiftUI",
            "Jetpack Compose", "RxSwift", "Combine", "Core Data", "Room",
            "Alamofire", "Retrofit", "Kingfisher", "Glide", "Lottie",
            "WebKit", "Core Animation", "Metal", "ARKit", "ML Kit"
        ],
        "concepts": [
            "响应式编程", "组件化架构", "路由设计", "状态管理",
            "内存管理", "线程安全", "离线缓存", "热修复",
            "动态化方案", "包体积优化", "启动优化", "卡顿优化",
            "电量优化", "网络优化", "安全防护", "逆向防护",
            "推送机制", "跨平台方案", "混合开发", "插件化"
        ],
        "problems": [
            "OOM崩溃", "启动速度慢", "列表滑动卡顿",
            "内存泄漏", "包体积过大", "热修复失败",
            "跨平台性能差", "iOS审核被拒"
        ],
        "scenarios": [
            "千万级DAU的社交App", "跨平台电商App", "实时音视频通讯App",
            "地图导航应用", "短视频应用", "IoT设备控制App"
        ],
        "criticisms": [
            "Flutter的性能不如原生", "React Native的体验比原生差太多",
            "组件化架构增加了开发成本", "你的启动优化没有量化数据",
            "跨平台方案在复杂交互场景下根本不够用", "热修复方案有合规风险"
        ]
    },
    "安全工程师": {
        "techs": [
            "Burp Suite", "Nmap", "Metasploit", "OWASP ZAP", "Nessus",
            "Wireshark", "Snort", "Suricata", "OSSEC", "Wazuh",
            "HashiCorp Vault", "OpenSSL", "GPG", "YARA", "Volatility",
            "Cuckoo Sandbox", "Ghidra", "IDA Pro", "Cobalt Strike", "BloodHound"
        ],
        "concepts": [
            "渗透测试", "漏洞挖掘", "安全审计", "威胁建模",
            "零信任架构", "纵深防御", "最小权限", "加密算法",
            "数字签名", "PKI体系", "SOC运营", "应急响应",
            "安全开发生命周期", "代码审计", "供应链安全", "云安全",
            "容器安全", "API安全", "数据分类分级", "合规审计"
        ],
        "problems": [
            "0day漏洞应急响应", "APT攻击检测困难", "安全与业务效率冲突",
            "安全工具误报率高", "安全意识培训效果差", "供应链攻击防护",
            "数据泄露溯源困难", "合规成本过高"
        ],
        "scenarios": [
            "企业零信任安全架构", "金融级安全防护体系", "云原生安全平台",
            "安全运营中心(SOC)", "数据安全治理平台", "DevSecOps流水线"
        ],
        "criticisms": [
            "你的安全方案严重影响了业务效率", "渗透测试报告都是已知漏洞没有新发现",
            "零信任架构成本太高不切实际", "安全合规就是走过场",
            "你的应急响应流程根本没演练过", "WAF规则绕过太容易了"
        ]
    },
    "云架构师": {
        "techs": [
            "AWS", "Azure", "GCP", "Terraform", "Pulumi",
            "Kubernetes", "Istio", "Knative", "AWS Lambda", "Azure Functions",
            "CloudFormation", "CDK", "CloudFront", "S3", "DynamoDB",
            "Aurora", "ElastiCache", "CloudWatch", "X-Ray", "Step Functions"
        ],
        "concepts": [
            "云原生架构", "微服务设计", "事件驱动架构", "无服务器架构",
            "多区域部署", "灾备切换", "成本优化", "FinOps",
            "Well-Architected Framework", "基础设施即代码", "GitOps",
            "服务网格", "API网关", "分布式追踪", "混沌工程",
            "自动扩缩容", "容量规划", "网络设计", "安全合规", "混合云"
        ],
        "problems": [
            "云成本失控", "多区域数据一致性", "供应商锁定",
            "网络延迟过高", "安全合规审计", "资源利用率低",
            "架构复杂度失控", "技术选型决策困难"
        ],
        "scenarios": [
            "全球化多区域高可用架构", "云成本优化治理平台", "混合云架构设计",
            "Serverless事件驱动平台", "企业级云原生转型", "多云管理平台"
        ],
        "criticisms": [
            "你的架构设计没有考虑成本", "多云方案增加了运维复杂度",
            "Serverless有冷启动问题不适合生产", "你的高可用方案没有经过故障演练",
            "云原生架构过于复杂不如传统架构", "IaC在大型团队中维护成本极高"
        ]
    },
    "测试工程师": {
        "techs": [
            "Selenium", "Appium", "JMeter", "Postman", "Cypress",
            "Playwright", "Pytest", "JUnit", "TestNG", "Allure",
            "Jenkins", "SonarQube", "Locust", "Gatling", "K6",
            "Robot Framework", "Cucumber", "ZAP", "OWASP", "Charles"
        ],
        "concepts": [
            "测试金字塔", "单元测试", "集成测试", "端到端测试",
            "性能测试", "压力测试", "稳定性测试", "兼容性测试",
            "安全测试", "自动化测试", "持续测试", "测试左移",
            "测试右移", "探索性测试", "风险驱动测试", "测试数据管理",
            "Mock与Stub", "契约测试", "混沌测试", "A/B测试"
        ],
        "problems": [
            "自动化测试维护成本高", "测试用例覆盖率虚高", "测试环境不稳定",
            "测试数据准备困难", "回归测试耗时过长", "性能测试结果不可复现",
            "安全测试覆盖不全", "跨团队测试协作困难"
        ],
        "scenarios": [
            "千人研发团队的测试平台", "全链路压测方案", "自动化回归测试体系",
            "质量门禁系统", "测试数据管理平台", "安全合规测试体系"
        ],
        "criticisms": [
            "你的自动化测试ROI是负的", "测试覆盖率80%但线上bug还是很多",
            "性能测试没有模拟真实场景", "你的测试策略没有区分优先级",
            "测试左移就是让测试做开发的活", "安全测试就是走形式"
        ]
    },
    "嵌入式开发工程师": {
        "techs": [
            "C", "C++", "RTOS", "Linux Kernel", "ARM",
            "STM32", "ESP32", "FPGA", "Verilog", "VHDL",
            "Yocto", "Buildroot", "Device Tree", "I2C", "SPI",
            "UART", "CAN", "USB", "BLE", "Zigbee"
        ],
        "concepts": [
            "实时操作系统", "中断处理", "DMA传输", "内存管理",
            "设备驱动开发", "硬件抽象层", "交叉编译", "Bootloader",
            "固件升级(OTA)", "功耗优化", "时序分析", "信号处理",
            "嵌入式Linux", "进程间通信", "看门狗机制", "安全启动",
            "外设接口", "传感器融合", "边缘计算", "物联网协议"
        ],
        "problems": [
            "内存溢出导致系统崩溃", "中断优先级冲突", "实时性无法保证",
            "功耗过高", "固件升级失败变砖", "硬件兼容性问题",
            "调试困难", "安全漏洞"
        ],
        "scenarios": [
            "智能硬件固件架构", "车载嵌入式系统", "工业控制系统",
            "IoT网关设备", "低功耗可穿戴设备", "机器人控制系统"
        ],
        "criticisms": [
            "你的RTOS选型没有经过充分评估", "C++在嵌入式中的开销你考虑过吗",
            "OTA升级方案没有回滚机制", "你的功耗优化没有实测数据",
            "嵌入式Linux太重了不适合资源受限设备", "安全启动方案增加了启动时间"
        ]
    }
}

QUESTION_PATTERNS = {
    "TECH": {
        "技术基础": [
            ("请解释{tech}的核心原理及其在实际项目中的应用场景。", "需要从{tech}的设计目标、核心机制和适用场景三个维度回答，结合实际项目经验说明。"),
            ("什么是{concept}？它在现代软件开发中扮演什么角色？", "需要定义{concept}的概念，说明其解决的问题，以及在现代架构中的价值。"),
            ("请比较{tech_a}和{tech_b}的区别，以及各自适用的场景。", "需要从设计理念、核心特性、性能特点和适用场景四个维度进行对比分析。"),
            ("{tech}中的{concept}机制是如何工作的？请详细说明。", "需要深入{tech}的内部实现，解释{concept}的工作流程和关键设计决策。"),
            ("在实际项目中，你如何选择和使用{tech}？有哪些最佳实践？", "需要结合项目经验，说明选型依据、使用方式和踩过的坑。"),
            ("请解释{concept}的实现原理，以及它解决了什么问题。", "需要从问题背景出发，解释{concept}的设计思路和实现机制。"),
            ("{tech}有哪些常见的使用模式？请举例说明。", "需要列举{tech}的典型使用场景和对应的代码/配置模式。"),
            ("请说明{concept}的优缺点，以及在什么情况下应该避免使用。", "需要客观分析{concept}的优势和局限，给出明确的使用边界。"),
        ],
        "项目深挖": [
            ("你在项目中是如何使用{tech}的？遇到了什么挑战？", "需要描述{tech}在项目中的具体应用、遇到的困难和解决方案。"),
            ("请描述你在项目中实现{concept}的具体过程和关键决策。", "需要从需求分析、方案设计、实现细节和效果评估四个方面回答。"),
            ("你在使用{tech}时遇到过{problem}吗？是如何解决的？", "需要描述问题的具体表现、排查过程和最终解决方案。"),
            ("请详细说明你项目中{tech}的架构设计和技术选型理由。", "需要从业务需求出发，解释架构选择和技术决策的权衡过程。"),
            ("你在项目中如何评估{tech}的效果？关注哪些指标？", "需要说明评估方法、关键指标和实际数据。"),
            ("描述一个你使用{concept}解决实际问题的案例。", "需要包含问题背景、方案设计、实现过程和最终效果。"),
            ("你在项目中如何处理{problem}？有什么经验教训？", "需要描述问题场景、解决思路、具体方案和反思总结。"),
            ("请说明你项目中{tech}的演进过程，为什么做这些改变？", "需要从初始方案到当前架构的演进路径，解释每次变更的原因。"),
        ],
        "系统设计": [
            ("如果要设计{scenario}，你会如何架构？请说明关键设计决策。", "需要从需求分析、架构设计、技术选型和扩展性考虑四个方面回答。"),
            ("如何设计一个高可用的{tech}系统？需要考虑哪些因素？", "需要从可用性、一致性、分区容错性和运维成本等维度分析。"),
            ("请设计{scenario}的数据模型和存储方案。", "需要考虑数据量、读写比例、一致性要求和查询模式。"),
            ("如果要实现{scenario}，你会如何处理{problem}？", "需要分析问题的根本原因，提出多种解决方案并比较优劣。"),
            ("如何设计{tech}的监控和告警体系？", "需要从指标设计、采集方案、告警规则和可视化四个方面回答。"),
            ("请设计{scenario}的容灾和高可用方案。", "需要考虑RPO/RTO、故障检测、自动切换和数据一致性。"),
        ],
        "代码质量": [
            ("你如何保证{tech}项目的代码质量？有哪些具体措施？", "需要从代码规范、静态分析、Code Review和自动化测试四个维度回答。"),
            ("在{concept}的实现中，如何编写可维护的代码？", "需要说明设计模式、命名规范、注释策略和重构方法。"),
            ("你如何对{tech}相关代码进行单元测试？有什么策略？", "需要说明测试框架选择、Mock策略、覆盖率目标和CI集成。"),
            ("请说明你在{tech}项目中如何进行代码审查。", "需要描述Review流程、关注点和常见问题。"),
        ],
        "性能优化": [
            ("{tech}的性能瓶颈通常在哪里？如何进行优化？", "需要从CPU、内存、IO和网络四个维度分析瓶颈和优化方案。"),
            ("如何评估和优化{concept}的性能？", "需要说明性能测试方法、瓶颈定位手段和优化策略。"),
            ("在{scenario}中，你会如何进行性能优化？", "需要从架构层面、代码层面和基础设施层面提出优化方案。"),
            ("请说明{tech}的{concept}优化策略，以及如何衡量效果。", "需要描述优化前后的性能指标对比和优化思路。"),
        ]
    },
    "PRESSURE": {
        "压力追问": [
            ("你说你用了{tech}，但{tech}存在{problem}的问题，你怎么解决？", "需要承认问题存在，分析根本原因，提出缓解方案和替代方案。"),
            ("你的简历上写了'{claim}'，但{criticism}，你怎么回应？", "需要客观面对质疑，用数据和事实支撑观点，承认不足并提出改进方向。"),
            ("如果{scenario}的流量突然增长10倍，你的方案还能撑住吗？", "需要分析当前方案的瓶颈，提出扩展方案，并说明成本和复杂度权衡。"),
            ("你刚才提到的{tech}方案，有没有考虑过{problem}？", "需要诚实回答是否考虑过，如果没考虑过则现场分析并提出方案。"),
            ("{criticism}，你怎么看？", "需要客观分析批评的合理性，既不完全否定也不盲目接受，给出自己的判断。"),
            ("你说{tech}解决了{problem}，但有没有可能引入了新的问题？", "需要分析方案的trade-off，说明新引入的风险和应对措施。"),
        ],
        "边界挑战": [
            ("如果{tech}完全不可用，你会怎么替代？", "需要提出备选方案，分析替代方案的优劣和迁移成本。"),
            ("在{problem}的极端情况下，你的系统会怎样？", "需要分析系统的极限状态、降级策略和恢复方案。"),
            ("如果要求你不用{tech}实现同样的功能，你会怎么做？", "需要展示对问题本质的理解，而不是对特定工具的依赖。"),
            ("{scenario}中如果发生{problem}，你的系统如何自保？", "需要说明熔断、降级、限流等保护机制。"),
        ],
        "技术批判": [
            ("很多人批评{criticism}，你为什么还选择它？", "需要客观分析优缺点，说明在当前场景下的合理性，承认局限性。"),
            ("{tech}的{concept}设计被广泛认为是有问题的，你同意吗？", "需要展示独立思考能力，不盲从社区观点，给出自己的分析。"),
            ("你觉得{tech}会被什么技术取代？为什么？", "需要展示对技术趋势的理解，分析替代技术的优势和{tech}的不可替代性。"),
        ]
    },
    "COMPREHENSIVE": {
        "综合评估": [
            ("如果让你把{scenario}扩展到支持百万用户，你会怎么设计？", "需要从架构演进、数据分片、缓存策略和成本控制四个方面回答。"),
            ("从{concept}的角度，你如何看待{problem}？", "需要展示跨领域思考能力，将{concept}的原理应用到{problem}的分析中。"),
            ("如果让你重新设计{scenario}，你会做哪些不同的选择？", "需要反思现有方案的不足，提出改进方向，说明理由。"),
            ("如何设计一个公平的{tech}评估系统，避免偏见？", "需要从数据多样性、评估指标、人工审核和可解释性四个维度回答。"),
        ],
        "架构设计": [
            ("请设计{scenario}的整体架构，并说明关键组件的职责。", "需要画出架构图，说明组件间的交互和依赖关系。"),
            ("如果{tech}数据量翻10倍，你的架构需要做哪些调整？", "需要分析当前架构的扩展性瓶颈，提出具体的调整方案。"),
            ("如何设计{scenario}的技术选型方案？你会考虑哪些因素？", "需要从团队能力、社区生态、性能要求和成本预算四个维度分析。"),
        ],
        "团队协作": [
            ("在{scenario}项目中，你如何与不同角色的团队成员协作？", "需要说明沟通机制、职责划分和冲突解决方式。"),
            ("如果团队对{tech}的选型有分歧，你会如何推动决策？", "需要展示技术决策的方法论，包括调研、PoC、数据驱动决策。"),
            ("你如何向非技术人员解释{concept}的价值？", "需要展示抽象概念的具象化表达能力，用业务语言解释技术价值。"),
            ("在{scenario}中，你如何进行技术知识分享和团队赋能？", "需要说明知识分享的机制、培训方案和文档建设。"),
        ]
    }
}


def generate_all_questions() -> list[dict]:
    questions = []
    qid = 1

    for job_type, profile in JOB_PROFILES.items():
        techs = profile["techs"]
        concepts = profile["concepts"]
        problems = profile["problems"]
        scenarios = profile["scenarios"]
        criticisms = profile["criticisms"]

        for stage, categories in QUESTION_PATTERNS.items():
            for category, patterns in categories.items():
                for question_tmpl, answer_tmpl in patterns:
                    if "{tech_a}" in question_tmpl and "{tech_b}" in question_tmpl:
                        for i in range(0, len(techs) - 1, 2):
                            q = question_tmpl.format(tech_a=techs[i], tech_b=techs[i + 1])
                            a = answer_tmpl.format(tech_a=techs[i], tech_b=techs[i + 1])
                            questions.append({
                                "id": qid, "category": category, "stage": stage,
                                "job_type": job_type, "question": q, "reference_answer": a
                            })
                            qid += 1
                    elif "{tech}" in question_tmpl and "{problem}" in question_tmpl:
                        for tech in techs[:6]:
                            for problem in problems[:3]:
                                q = question_tmpl.format(tech=tech, problem=problem)
                                a = answer_tmpl.format(tech=tech, problem=problem)
                                questions.append({
                                    "id": qid, "category": category, "stage": stage,
                                    "job_type": job_type, "question": q, "reference_answer": a
                                })
                                qid += 1
                    elif "{tech}" in question_tmpl and "{concept}" in question_tmpl:
                        for tech in techs[:6]:
                            for concept in concepts[:4]:
                                q = question_tmpl.format(tech=tech, concept=concept)
                                a = answer_tmpl.format(tech=tech, concept=concept)
                                questions.append({
                                    "id": qid, "category": category, "stage": stage,
                                    "job_type": job_type, "question": q, "reference_answer": a
                                })
                                qid += 1
                    elif "{tech}" in question_tmpl:
                        for tech in techs[:8]:
                            q = question_tmpl.format(tech=tech)
                            a = answer_tmpl.format(tech=tech)
                            questions.append({
                                "id": qid, "category": category, "stage": stage,
                                "job_type": job_type, "question": q, "reference_answer": a
                            })
                            qid += 1
                    elif "{concept}" in question_tmpl and "{problem}" in question_tmpl:
                        for concept in concepts[:4]:
                            for problem in problems[:3]:
                                q = question_tmpl.format(concept=concept, problem=problem)
                                a = answer_tmpl.format(concept=concept, problem=problem)
                                questions.append({
                                    "id": qid, "category": category, "stage": stage,
                                    "job_type": job_type, "question": q, "reference_answer": a
                                })
                                qid += 1
                    elif "{concept}" in question_tmpl:
                        for concept in concepts[:8]:
                            q = question_tmpl.format(concept=concept)
                            a = answer_tmpl.format(concept=concept)
                            questions.append({
                                "id": qid, "category": category, "stage": stage,
                                "job_type": job_type, "question": q, "reference_answer": a
                            })
                            qid += 1
                    elif "{scenario}" in question_tmpl and "{problem}" in question_tmpl:
                        for scenario in scenarios:
                            for problem in problems[:2]:
                                q = question_tmpl.format(scenario=scenario, problem=problem)
                                a = answer_tmpl.format(scenario=scenario, problem=problem)
                                questions.append({
                                    "id": qid, "category": category, "stage": stage,
                                    "job_type": job_type, "question": q, "reference_answer": a
                                })
                                qid += 1
                    elif "{scenario}" in question_tmpl:
                        for scenario in scenarios:
                            q = question_tmpl.format(scenario=scenario)
                            a = answer_tmpl.format(scenario=scenario)
                            questions.append({
                                "id": qid, "category": category, "stage": stage,
                                "job_type": job_type, "question": q, "reference_answer": a
                            })
                            qid += 1
                    elif "{claim}" in question_tmpl:
                        for criticism in criticisms[:4]:
                            q = question_tmpl.format(claim="相关技术经验", criticism=criticism)
                            a = answer_tmpl.format(criticism=criticism)
                            questions.append({
                                "id": qid, "category": category, "stage": stage,
                                "job_type": job_type, "question": q, "reference_answer": a
                            })
                            qid += 1
                    elif "{criticism}" in question_tmpl:
                        for criticism in criticisms:
                            q = question_tmpl.format(criticism=criticism)
                            a = answer_tmpl.format(criticism=criticism)
                            questions.append({
                                "id": qid, "category": category, "stage": stage,
                                "job_type": job_type, "question": q, "reference_answer": a
                            })
                            qid += 1
                    elif "{problem}" in question_tmpl:
                        for problem in problems:
                            q = question_tmpl.format(problem=problem)
                            a = answer_tmpl.format(problem=problem)
                            questions.append({
                                "id": qid, "category": category, "stage": stage,
                                "job_type": job_type, "question": q, "reference_answer": a
                            })
                            qid += 1

    return questions


SEED_QUESTIONS = generate_all_questions()
