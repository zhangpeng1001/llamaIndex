# 实景三维质检大数据支撑库 时空数据规范 第1部分 数据分类与基本规定

> 来源：实景三维质检大数据支撑库 时空数据规范 第1部分 数据分类与基本规定.pdf（增强版提取，已去目录/页眉/页码噪声）


第1部分 数据分类及基本规定

（草案）

部属单位： 国家测绘产品质量检验测试中心

省级单位： 北京市测绘设计研究院

浙江省测绘科学技术研究院

广东省测绘产品质量监督检验中心

甘肃省测绘产品质量监督检验站

湖北省测绘质量监督检验站

参与单位： 土豆数据科技集团有限公司

2025年7月

前 言

本文件按照GB/T 1.1—2020《标准化工作导则  第1部分：标准化文件的结构和起草规

则》的规定起草。

第2部分 检测点

第3部分 检测线

第4部分 标志性地物

第5部分 重要要素

第6部分 高精度栅格数据

第7部分 资源数据

请注意本文件的某些内容可能涉及专利。本文件的发布机构不承担识别专利的责任。

起草单位：

起草人员：

<!-- chapter_no=1; chapter_title=范围; section_type=范围; knowledge_type=scope_intro -->
# 1 范围

<!-- section_type=范围; knowledge_type=scope_intro -->
定。

<!-- section_type=范围; knowledge_type=scope_intro -->
本文件适用于支撑实景三维数据质检的时空大数据的组织、 管理及支撑库建

<!-- section_type=范围; knowledge_type=scope_intro -->
设、管理系统研发等

<!-- chapter_no=2; chapter_title=规范性引用文件; section_type=引用文件; knowledge_type=references -->
# 2 规范性引用文件

<!-- section_type=引用文件; knowledge_type=references -->
下列文件中的内容通过文中的规范性引用而构成本文件必不可少的条款。其中，注日

<!-- section_type=引用文件; knowledge_type=references -->
期的引用文件，仅该日期对应的版本适用于本文件；不注日期的引用文件，其最新版本

<!-- section_type=引用文件; knowledge_type=references -->
(包括所有的修改单)适用于本文件。

<!-- chapter_no=3; chapter_title=术语和定义; section_type=术语定义; knowledge_type=term_definition -->
# 3 术语和定义

<!-- section_type=术语定义; knowledge_type=term_definition -->
下列术语和定义适用于本文件。

<!-- chapter_no=3; chapter_title=1; knowledge_type=chapter_title -->
# 3 1

质检支撑库 Quality Inspection Support Repository

质检支撑库是基于统一数据架构构建的专用数据库系统，用以存储和管理支

撑质检时空数据、 标准规范等数据， 并支持数据的查询检索、 数据评估、 数据推

送等。

<!-- chapter_no=3; chapter_title=2; knowledge_type=chapter_title -->
# 3 2

时空大数据 spatio-temporal big data

具有大数据的基本特征， 描述地理实体的时间、 空间和专题特征，或业务管

理、生活服务等时空过程与状态的数据集。

[来源：GB/T 42528-2023，3.1]

<!-- chapter_no=4; chapter_title=时空数据分类; knowledge_type=chapter_title -->
# 4 时空数据分类

时空数据作为重要质检支撑数据由背景数据、 标准数据及资源数据组成，如

图 1 所示。

背景数据。 背景数据指进行数据查询检索时可作为背景，以表达被查询数据

在空间上的位置、完整性等特点。

标准数据。标准数据指支撑质检的常用数据，必须保证其准确性、完整性，

且需要持续更新。 包括检测点数据、 标志性地物数据、 重要要素数据、 高精度影

像数据等。

资源数据。 资源数据指可作为支撑质检的备用数据，但较标准数据应用频率

低。

时空数据

标准数据

资源数据

背景数据

检查点数据

全国矢量数据（缺省打开）

基本比例尺接图表

影像数据

行政区划数据

特征数据

标志性地物数据

重要要素数据

高精影像数据

专题（项）数据

基本比例尺地形图

(需要再细化吗？) 1：10000

1：50000

……

实景三维 LOD1.3

基础地理实体

调查监测 基础调查

专项调查

全球 核心要素

影像

OSM

DOM

DEM

LiDAR 原始数据

分类数据

图 1 时空数据框架

<!-- chapter_no=5; chapter_title=基本规定; knowledge_type=chapter_title -->
# 5 基本规定

<!-- chapter_no=5.1; chapter_title=时空基准; knowledge_type=chapter_title -->
## 5.1 时空基准

<!-- chapter_no=5.1.1; chapter_title=空间基准; knowledge_type=chapter_title -->
### 5.1.1 空间基准

大地基准为 2000 国家大地坐标系， 或采用依法批准的独立坐标系， 并与2000

国家大地坐标系建立联系。

高程基准为 1985 国家高程基准。

投影采用高斯-克吕格投影，3 度或 6 度分带。

<!-- chapter_no=5.1.2; chapter_title=时间基准; knowledge_type=chapter_title -->
### 5.1.2 时间基准

日期应采用公历纪元，时间应采用北京时间。

<!-- chapter_no=5.2; chapter_title=数据组织与格式; knowledge_type=chapter_title -->
## 5.2 数据组织与格式

<!-- chapter_no=5.2.1; chapter_title=数据单元划分; knowledge_type=chapter_title -->
### 5.2.1 数据单元划分

当数据范围、 数据量较大时， 标准数据与资源数据一般按行政区划或标准分

幅进行组织。

<!-- chapter_no=5.2.2; chapter_title=数据格式; knowledge_type=chapter_title -->
### 5.2.2 数据格式

常用时空数据格式如下：

矢量数据一般采用 shape file 、mdb、或 file geodatabase 格式。

影像数据一般采用 Tiff world 或 img 格式。

参 考 文 献

[1] GB/T 42528-2023 时空大数据技术规范

[2] GB/T 24356-2023 测绘成果质量检查与验收

[3] GB/T 18316-2008 数字测绘成果质量检查与验收
