# 实景三维质检大数据支撑库 时空数据规范 第2部分 检测点

> 来源：实景三维质检大数据支撑库 时空数据规范 第2部分 检测点.pdf（增强版提取，已去目录/页眉/页码噪声）


第 2 部分 检测点

（草案）

2025 年7 月

前 言

本文件按照GB/T 1.1—2020《标准化工作导则  第1部分：标准化文件的结构和起草规则》的规定

起草。

第1部分 数据分类与基本规定

第3部分 检测线

第4部分 标志性地物

第5部分 重要要素

第6部分 高精度栅格数据

第7部分 资源数据

请注意本文件的某些内容可能涉及专利。本文件的发布机构不承担识别专利的责任。

起草单位：

起草人员：

引  言

为满足实景三维中国建设项目成果质量检验的快速响应需求，同时适应

大数据、人工智能等新技术的飞速发展对高可靠质检参考数据的要求，探索

构建高精度检测点数据库，本文件提出实景三维检测点数据采集、整理、建

库、质检要求，指导质检大数据支撑库检测点子库建设，实现实景三维成果

质检工作效率和成果质量的提升。

<!-- chapter_no=1; chapter_title=范围; section_type=范围; knowledge_type=scope_intro -->
# 1 范围

<!-- section_type=范围; knowledge_type=scope_intro -->
本文件规定了实景三维检测点数据成果的时空基准、数据采集、数据整理、数据库组织与建库和

<!-- section_type=范围; knowledge_type=scope_intro -->
质量要求等内容。

<!-- section_type=范围; knowledge_type=scope_intro -->
本文件适用于新型基础测绘与实景三维中国建设中实景三维位置精度检测点数据的采集、整理、

<!-- section_type=范围; knowledge_type=scope_intro -->
建库、质检等工作。

<!-- chapter_no=2; chapter_title=规范性引用文件; section_type=引用文件; knowledge_type=references -->
# 2 规范性引用文件

<!-- section_type=引用文件; knowledge_type=references -->
下列文件中的内容通过文中的规范性引用而构成本文件必不可少的条款。其中，注日期的引用文

<!-- section_type=引用文件; knowledge_type=references -->
件，仅该日期对应的版本适用于本文件；不注日期的引用文件，其最新版本(包括所有的修改单)适用

<!-- section_type=引用文件; knowledge_type=references -->
于本文件。

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 2260 中华人民共和国行政区划代码

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 14911 测绘基本术语

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 16820 地图学术语

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 18521 地名分类与类别代码编制规则

<!-- section_type=引用文件; knowledge_type=references -->
GB 22021 国家大地测量基本技术规定

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 23705 数字城市地理信息公共平台地名/地址编码规则

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 33176 国家基本比例尺地图 1：500 1：1000 1：2000 地形图

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 33453 基础地理信息数据库建设规范

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 39616 卫星导航定位基准站网络实时动态测量（RTK）规范

<!-- section_type=引用文件; knowledge_type=references -->
GB/T****地理实体空间身份编码规则

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 1020 1：500、1：1000、1：2000 地形图质量检验技术规程

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 2009 全球定位系统实时动态测量（RTK）技术规范

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 3003 低空数字航空摄影测量内业规范

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 3004 低空数字航空摄影测量外业规范

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 3005 低空数字航空摄影规范

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 6003 车载移动测量数据规范

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 6004 车载移动测量技术规程

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 8023 机载激光雷达数据处理技术规范

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 8024 机载激光雷达数据获取技术规范

<!-- section_type=引用文件; knowledge_type=references -->
CH/T****基础地理实体分类、粒度及精度基本要求

<!-- section_type=引用文件; knowledge_type=references -->
CH/T****基础地理实体数据元数据

<!-- section_type=引用文件; knowledge_type=references -->
T/CAGIS 15-2024 1：500 1：1000 1：2000 地形图检测点采集及建库技术要求

<!-- chapter_no=3; chapter_title=术语和定义; section_type=术语定义; knowledge_type=term_definition -->
# 3 术语和定义

<!-- section_type=术语定义; knowledge_type=term_definition -->
下列术语和定义适用于本文件。

<!-- chapter_no=3; chapter_title=1; knowledge_type=chapter_title -->
# 3 1

地理实体 Fundamental Geo-entity

现实世界中占据一定空间、具有同一属性或完整功能的地理对象。

<!-- chapter_no=3; chapter_title=2; knowledge_type=chapter_title -->
# 3 2

基础地理实体 Fundamental Geo-entity

通过基础测绘采集和表达的地理实体，是其他地理实体和相关信息的定位框架与承载基础，包括

自然地理实体、人工地理实体和管理地理实体三类。

<!-- chapter_no=3; chapter_title=3; knowledge_type=chapter_title -->
# 3 3

基础地理实体数据 Fundamental Geo-entity Data

基础地理实体空间、语义等信息在计算机系统中的数字化描述。

<!-- chapter_no=3; chapter_title=4; knowledge_type=chapter_title -->
# 3 4

基础地理实体数据表达模型 Fundamental Geo-entity Representation Model

用于在计算机系统内对基础地理实体空间信息进行概括或精细表示的数学模型。

注：依据表达尺度、几何结构等空间信息差异，同一基础地理实体可包含多种表达模型。

<!-- chapter_no=3; chapter_title=5; knowledge_type=chapter_title -->
# 3 5

基础地理实体数据成果 Fundamental Geo-entity Data Products

对一定空间范围内基础地理实体空间位置、几何形态、属性信息、相互关系、空间分布等进行数

字化描述，且满足一定精度、粒度及表达模型等技术要求的基础地理实体数据集。

注 1:依据不同空间尺度的应用需求差异， 同一空间范围内基础地理实体数据可划分为不同层级数

据成果。

注 2:基础地理实体数据成果为成果管理单位统一对外提供、满足一定技术指标要求、具有标准格

式的最终形式数据集，与数据采集、建库阶段形成的阶段性数据成果，应有所区分。

<!-- chapter_no=3; chapter_title=6; knowledge_type=chapter_title -->
# 3 6

图元 Geometry Element

空间内单一、连通并用于表达实体几何特征的图形对象，一般表达为点、线、面、体。

注 1:点、线、面图元属于二维图元；体图元属于三维图元。

注 2:图元不指代比基础地理实体粒度更小的地理对象。

<!-- chapter_no=4; chapter_title=时空基准; section_type=时空基准; knowledge_type=data_spec -->
# 4 时空基准

<!-- chapter_no=4.1; chapter_title=空间参考; section_type=时空基准; knowledge_type=data_spec -->
## 4.1 空间参考

<!-- section_type=时空基准; knowledge_type=data_spec -->
检测点数据应采用国家规定的、统一的地理空间参考系，应满足下列要求：

<!-- section_type=时空基准; knowledge_type=data_spec -->
a) 大地基准为 2000 国家大地坐标系，或采用依法批准的独立坐标系，并与 2000 国家大地坐标系

<!-- section_type=时空基准; knowledge_type=data_spec -->
建立联系。

<!-- section_type=时空基准; knowledge_type=data_spec -->
b) 高程基准为 1985 国家高程基准。

<!-- section_type=时空基准; knowledge_type=data_spec -->
c) 投影采用高斯-克吕格投影，3°分带。

<!-- chapter_no=4.2; chapter_title=时间参考; section_type=时空基准; knowledge_type=data_spec -->
## 4.2 时间参考

<!-- section_type=时空基准; knowledge_type=data_spec -->
日期应采用公历纪元，时间应采用北京时间。

<!-- chapter_no=5; chapter_title=数据采集; section_type=数据采集; knowledge_type=data_spec -->
# 5 数据采集

<!-- chapter_no=5.1; chapter_title=基本要求; section_type=数据采集; knowledge_type=quality_rule -->
## 5.1 基本要求

<!-- chapter_no=5.1.1; chapter_title=检测点数据; section_type=数据采集; knowledge_type=data_spec -->
### 5.1.1 检测点数据

<!-- section_type=数据采集; knowledge_type=quality_rule -->
检测点数据应满足以下基本要求：

<!-- section_type=数据采集; knowledge_type=data_spec -->
a) 检测点数据一般包括检测点坐标文件、采集登记表、实地照片、标注了检测点的影像图等。

<!-- section_type=数据采集; knowledge_type=data_spec -->
b) 空间位置数据以点要素的信息方式存储。

<!-- section_type=数据采集; knowledge_type=data_spec -->
c) 检测点坐标文件存储点要素的空间坐标位置信息， 作为录入矢量信息的主要数据源， 检测点数据

<!-- section_type=数据采集; knowledge_type=data_spec -->
内容见 6.2。

<!-- section_type=数据采集; knowledge_type=data_spec -->
d) 采集登记表存储检测点项目信息，采集登记表见附录 A。

<!-- chapter_no=5.1.2; chapter_title=其他数据; section_type=数据采集; knowledge_type=data_spec -->
### 5.1.2 其他数据

<!-- section_type=数据采集; knowledge_type=data_spec -->
用于辅助检测点显示及查询的水系、 交通、 地形、行政区界线矢量数据、地名地址数据、1：500 1：

<!-- section_type=数据采集; knowledge_type=data_spec -->
1000 1：2000 标准分幅范围等其他数据。

<!-- chapter_no=5.2; chapter_title=采集要求; section_type=数据采集; knowledge_type=quality_rule -->
## 5.2 采集要求

<!-- chapter_no=5.2.1; chapter_title=仪器检定; section_type=数据采集; knowledge_type=quality_rule -->
### 5.2.1 仪器检定

<!-- section_type=数据采集; knowledge_type=quality_rule -->
检测点采集所使用仪器应经过计量检定合格后，在有效期内使用。

<!-- chapter_no=5.2.2; chapter_title=采集范围划定; section_type=数据采集; knowledge_type=data_spec -->
### 5.2.2 采集范围划定

<!-- section_type=数据采集; knowledge_type=quality_rule -->
检测点采集范围划定应满足下列要求：

<!-- section_type=数据采集; knowledge_type=data_spec -->
a) 地理场景数据1宜以“幅”为单位划定采集范围，涉及全域成果时，一般以县级行政区或乡镇行

<!-- section_type=数据采集; knowledge_type=data_spec -->
政区为单位划定采集范围。

<!-- section_type=数据采集; knowledge_type=data_spec -->
b) 转换生产实体数据、 采集生产地理实体数据宜以行政区划单元为单位划定采集范围（其中， 地形

<!-- section_type=数据采集; knowledge_type=data_spec -->
级实体数据宜以县级行政区 （市辖区、 县等） 为单位划定， 城市级实体数据宜以乡级行政区 （街道、 乡、

<!-- section_type=数据采集; knowledge_type=data_spec -->
镇等）为单位划定），也可结合成果实际情况，以生产单元等为单位划定采集范围。

<!-- section_type=数据采集; knowledge_type=data_spec -->
c) 城市三维模型（LOD1.3 级）成果宜以乡级行政区 （街道、 乡、镇等）为单位划定采集范围， 也可

<!-- section_type=数据采集; knowledge_type=data_spec -->
结合成果实际情况，以存储的三维模型数据文件、建模单元为单位划定采集范围。

<!-- chapter_no=5.2.3; chapter_title=采集点位选择; section_type=数据采集; knowledge_type=data_spec -->
### 5.2.3 采集点位选择

<!-- section_type=数据采集; knowledge_type=quality_rule -->
采集检测点点位选择应满足下列要求：

<!-- section_type=数据采集; knowledge_type=data_spec -->
a) 城区街道（办事处）宜以“田”字型布设采集路线，均匀采集区域内街道办、社区服务中心、学

<!-- section_type=数据采集; knowledge_type=data_spec -->
校、机关院落等重要地物，主干道、小区、商场、运动场等配套地物。

<!-- section_type=数据采集; knowledge_type=data_spec -->
b) 乡镇宜以“回”字型布设采集路线，均匀采集镇中心、街道办、学校、医院、村（居）委会等重

<!-- section_type=数据采集; knowledge_type=data_spec -->
要地物。

<!-- section_type=数据采集; knowledge_type=data_spec -->
c) 点位可补充其他重要单位、要素等，如水库、县级及以上公路及其桥梁、测量控制点（涉军涉密

<!-- section_type=数据采集; knowledge_type=data_spec -->
除外）。

<!-- chapter_no=5.2.4; chapter_title=采集数量与方式; section_type=数据采集; knowledge_type=data_spec -->
### 5.2.4 采集数量与方式

<!-- section_type=数据采集; knowledge_type=data_spec -->
每个点位采用组合方式采集，每个村（居）定位点及附近区域，数量不低于 5 个、总体不低于

<!-- section_type=数据采集; knowledge_type=data_spec -->
100 个（平面检测点大于 50 个，高程检测点大于 50 个，平高点可同时按平面检测点和高程检测点计

<!-- section_type=数据采集; knowledge_type=data_spec -->
数），并按如下组合进行采集：

<!-- section_type=数据采集; knowledge_type=data_spec -->
a) 房檐角+房角底点对 ≥ 1；

<!-- section_type=数据采集; knowledge_type=data_spec -->
b) 路面高程点 ≥ 1；

<!-- section_type=数据采集; knowledge_type=data_spec -->
c) 标志线或道路边线交叉点 ≥ 1；

<!-- section_type=数据采集; knowledge_type=data_spec -->
d) 独立地物（路灯、电杆、井盖、路牌、信号灯柱等） ≥ 1；

<!-- section_type=数据采集; knowledge_type=data_spec -->
e) 耕地（农村地区水田、旱地中心高程） ≥ 1；

<!-- section_type=数据采集; knowledge_type=data_spec -->
f) 其他地物，结合定位点周边实际地物分布情况采集；

<!-- section_type=数据采集; knowledge_type=data_spec -->
g) 近景拍摄乡镇/街道办事处、村（居）委会、学校院落等重要单位，水库、县级及以上公路及其

<!-- section_type=数据采集; knowledge_type=data_spec -->
桥梁等重要要素名称牌匾，远景拍摄重要单位、要素及周边环境；

<!-- chapter_no=1; chapter_title=《实景三维中国建设成果质量核验方案（2023-2025 年）》质量检查与验收、质量核查涉及的主要数据成果包括 5 米; knowledge_type=chapter_title -->
# 1 《实景三维中国建设成果质量核验方案（2023-2025 年）》质量检查与验收、质量核查涉及的主要数据成果包括 5 米

格网数字高程模型（DEM）、数字表面模型（DSM）、优于 2 米格网 DEM、DSM、近岸海域 10 米以浅 DEM、2 米分辨

率数字正射影像（DOM）、优于 1 米分辨率 DOM、优于 0.5 米分辨率 DOM、地形级基础地理实体数据、城市级基础地

理实体数据。

h) 外业采集时需录入地物外业代码，代码见表 C.1。

<!-- chapter_no=5.2.5; chapter_title=平面检测点采集; knowledge_type=chapter_title -->
### 5.2.5 平面检测点采集

平面检测点采集应满足下列要求：

a) 平面精度应不低于相应比例尺地形图的明显特征点位精度要求。

b) 采集数量视地物复杂程度、比例尺等具体情况确定，按照 5.2.4 要求执行。

c) 位置应均匀分布，应选择明显点状地物、线状地物交叉点、地物角点和拐点等，如房屋角点、围

墙角点、电杆、通讯杆、路灯、消防栓、检修井盖中心点等。

d) 采用采集检测点时的实地照片、检测点叠加影像图或检测地形图的截图辅助判读 平面检测点位

置。

<!-- chapter_no=5.2.6; chapter_title=高程检测点采集; knowledge_type=chapter_title -->
### 5.2.6 高程检测点采集

高程检测点采集满足下列要求：

a) 高程精度应不低于相应比例尺地形图的高程注记点精度要求。

b) 采集数量视地物复杂程度、比例尺等具体情况确定，按照5.2.4 要求执行。

c) 位置应均匀分布，应选取实地能准确判读的明显地形地貌特征点，避免选择高程急剧变化处。

d) 同名高程注记点采集位置宜准确， 避免选择难以准确判读的高程注记点； 城区内高程注记点应注

重选取城区的街道中心线、街道交叉中心、桥面、广场、较大庭院内或空地上等特征点。

e) 可采用采集检测点时的实地照片、检测点叠加影像图或检测地形图的截图辅助判读高程检测点

位置。

<!-- chapter_no=5.2.7; chapter_title=平高检测点采集; knowledge_type=chapter_title -->
### 5.2.7 平高检测点采集

平高检测点应同时满足 5.2.5 和 5.2.6 的要求。

<!-- chapter_no=5.2.8; chapter_title=实地照片和影像图采集; knowledge_type=chapter_title -->
### 5.2.8 实地照片和影像图采集

实地照片和影像图采集满足下列要求：

a) 实地照片宜把采集检测点时拍摄的主体地物点置于图面中间， 有一定的位置参照物， 拍摄距离宜

为 5m～20m，能清晰表现地物。顺序拍摄近景（竖屏）、远景（横屏）各不少于 1 张实地照片。

b) 影像图应从参考数据中裁切， 以检测点位置为中心点， 以明显标识标注检测点位置， 裁剪长宽为

511 像素511 像素大小的图像。

<!-- chapter_no=5.3; chapter_title=采集方法; knowledge_type=chapter_title -->
## 5.3 采集方法

<!-- chapter_no=5.3.1; chapter_title=GNSS RTK 实测法; knowledge_type=chapter_title -->
### 5.3.1 GNSS RTK 实测法

GNSS RTK 实测法采集检测点应满足 GB/T 39616 或 CH/T 2009 相关要求，此方法包括利用影像 RTK

采集检测点，也可采集实地照片。宜采用控制点或地形点模式进行采集，要求如下：

a) 采用控制点测量模式时：

1) 采用固定值测量，观测测回数大于等于 1；

2) 观测前设置平面收敛阈值不大于 2cm、高程收敛阈值不大于 3cm；

3) 观测采用三脚架/手持对中、整平，每次观测历元数应不少于 10 个，采样间隔应不小于

2s；

4) 各次测量的大地高较差不应大于 4cm；

5) 各次测量的平面坐标较差不应大于 4cm；

6) 采用多次测量时应取各次测量的平均坐标中数作为最终结果。

b) 采用地形点测量模式时：

1) 采用固定值测量；

2) 观测前设置平面收敛阈值不大于 2cm、高程收敛阈值不大于 3cm；

3) 每次观测历元数应不少于 10 个，采样间隔应不小于 2s。

<!-- chapter_no=5.3.2; chapter_title=全站仪实测法; knowledge_type=chapter_title -->
### 5.3.2 全站仪实测法

全站仪实测法使用全站仪极坐标法采集检测点，应满足 CH/T 1020 相关要求。

<!-- chapter_no=5.3.3; chapter_title=摄影测量法; knowledge_type=chapter_title -->
### 5.3.3 摄影测量法

使用低空无人机航空摄影测量方法采集检测点，应满足 CH/T 3003、CH/T 3004 和 CH/T 3005 相关要

求。

<!-- chapter_no=5.3.4; chapter_title=激光雷达实测法; knowledge_type=chapter_title -->
### 5.3.4 激光雷达实测法

使用无人机搭载机载激光雷达扫描仪采集激光雷达点云数据， 提取检测点应满足CH/T 8023 和 CH/T

8024 相关要求；使用车载移动测量系统采集车载激光点云数据，提取检测点应满足 CH/T 6003 和 CH/T

6004 相关要求。

<!-- chapter_no=5.3.5; chapter_title=其他方法; knowledge_type=chapter_title -->
### 5.3.5 其他方法

可从质量检验合格的成果中采集检测点，包括但不限于空中三角测量成果、实景三维成果等。

<!-- chapter_no=6; chapter_title=数据整理; section_type=数据整理; knowledge_type=data_spec -->
# 6 数据整理

<!-- chapter_no=6.1; chapter_title=检测点编号; section_type=数据整理; knowledge_type=field_rule -->
## 6.1 检测点编号

<!-- section_type=数据整理; knowledge_type=field_rule -->
检测点数据以县级行政区为单元， 按照统一规则入库编号。 检测点编号由类别、 行政区划、 采集日

<!-- section_type=数据整理; knowledge_type=field_rule -->
期及序号组成，编号共 19 位，具体编号规则如图 1 所示。检测点编号应满足下列要求：

<!-- section_type=数据整理; knowledge_type=field_rule -->
a) 检测点获取方式取 1 位，“Y”代表外业实测检测点，“N”代表从已有成果数据内业提取。

<!-- section_type=数据整理; knowledge_type=data_spec -->
b) 行政区代码由县（区）6 位区划代码组成。行政区代码与 GB/T 2260 规定保持一致。

<!-- section_type=数据整理; knowledge_type=field_rule -->
c) 根据采集时间对每个基本单元内的检测点进行流水编号。采集日期取至年月日，保留8 位。

<!-- section_type=数据整理; knowledge_type=data_spec -->
d) 序号保留 4 位，不足四位前补“0”。

<!-- section_type=数据整理; knowledge_type=data_spec -->
x         xxxxxx       xxxxxxxx        xxxx

<!-- section_type=数据整理; knowledge_type=data_spec -->
获取方式    行政区代码     采集日期        序号

<!-- section_type=数据整理; knowledge_type=field_rule -->
图 1 检测点编号规则

<!-- chapter_no=6.2; chapter_title=坐标文件整理; section_type=数据整理; knowledge_type=field_rule -->
## 6.2 坐标文件整理

<!-- section_type=数据整理; knowledge_type=field_rule -->
检测点坐标文件整理满足如下要求：

<!-- section_type=数据整理; knowledge_type=field_rule -->
a) 使用测量仪器采集检测点时， 坐标文件应从测量仪器中直接导出， 以检测仪器为单位， 整理到一

<!-- section_type=数据整理; knowledge_type=field_rule -->
个检测点坐标文件中。原始坐标文件一般包含名称、代码、北坐标、东坐标、高程、目标纬度、目标经

<!-- section_type=数据整理; knowledge_type=data_spec -->
度、 目标大地高、 天线类型、 天线高、 测量方法、 观测卫星数、PDOP、HDOP、VDOP、GDOP 水平误差、

<!-- section_type=数据整理; knowledge_type=data_spec -->
垂直误差、RMS 误差、开始时刻、结束时刻、观测数。

<!-- section_type=数据整理; knowledge_type=field_rule -->
b) 应在采集登记表中登记检测点坐标文件相关信息，采集登记表见附录A。

<!-- section_type=数据整理; knowledge_type=field_rule -->
c) 利用已有成果采集检测点时，应将已有成果范围内采集的检测点整理到一个检测点坐标文件中。

<!-- section_type=数据整理; knowledge_type=field_rule -->
d) 原始数据仅采集了平面坐标和高程的， 应进行坐标转换获取经纬度坐标， 检测点记录格式为： 流

<!-- section_type=数据整理; knowledge_type=data_spec -->
水号、检测点类型、纬度、经度、大地高、北坐标、东坐标、高程、仪器高、地物代码、地物名称、重

<!-- section_type=数据整理; knowledge_type=data_spec -->
要要素名称。

<!-- section_type=数据整理; knowledge_type=data_spec -->
e) 检测点坐标经纬度，单位为“度”，取值至小数点后 9 位；平面坐标、大地高、高程，单位为

<!-- section_type=数据整理; knowledge_type=data_spec -->
“米”，取值至小数点后 3 位，采用独立坐标系时需转换为 2000 国家大地坐标系坐标。

<!-- section_type=数据整理; knowledge_type=field_rule -->
f) 坐标文件命名为“仪器编号或软件名称+采集方式+采集日期”，文件名备注“原始数据” “成果

<!-- section_type=数据整理; knowledge_type=data_spec -->
数据”，区分原始数据和整理成果数据。

<!-- chapter_no=6.3; chapter_title=实地照片和影像图整理; section_type=数据整理; knowledge_type=data_spec -->
## 6.3 实地照片和影像图整理

<!-- section_type=数据整理; knowledge_type=data_spec -->
实地照片和影像图整理满足如下要求：

<!-- section_type=数据整理; knowledge_type=field_rule -->
a) 实地照片、标注了检测点的影像图应按类别建立文件夹以图片文件方式存储。

<!-- section_type=数据整理; knowledge_type=field_rule -->
b) 图片文件命名应唯一， 文件命名应包含检测点编号， 并附加标识码和图片序号， 其命名规则为：

<!-- section_type=数据整理; knowledge_type=field_rule -->
“标识码+检测点编号+图片序号”，其中实地照片标识码用字母“ZP”代替，影像图以“YX”代替。

<!-- section_type=数据整理; knowledge_type=field_rule -->
c) 图片序号按照每个检测点所包含的实地照片 （或影像图） 数量进行流水编号， 图片序号保留2 位，

<!-- section_type=数据整理; knowledge_type=data_spec -->
不足两位前补“0”。

<!-- chapter_no=6.4; chapter_title=检测点数据目录组织; section_type=数据整理; knowledge_type=field_rule -->
## 6.4 检测点数据目录组织

<!-- section_type=数据整理; knowledge_type=field_rule -->
检测点整理后成果目录以“年度+地级市+县级行政区名称+项目名称检测点数据”命名，存放该项

<!-- section_type=数据整理; knowledge_type=field_rule -->
目采集的检测点坐标文件、采集登记表等资料。目录组织如表 1 所示：

<!-- section_type=数据整理; knowledge_type=field_rule -->
表 1 外业检测点目录组织方式

<!-- section_type=数据整理; knowledge_type=data_spec -->
目 录 结 构 示例

<!-- section_type=数据整理; knowledge_type=data_spec -->
年度+地级市+县级行政区名称+项目名称+检

<!-- section_type=数据整理; knowledge_type=data_spec -->
测点数据

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……仪仪仪仪+仪仪仪仪+仪仪仪仪（成果

<!-- section_type=数据整理; knowledge_type=data_spec -->
数据）.csv

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……仪仪仪仪+仪仪仪仪+仪仪仪仪（原始

<!-- section_type=数据整理; knowledge_type=data_spec -->
数据）.csv

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……仪仪仪仪仪仪仪仪

<!-- section_type=数据整理; knowledge_type=field_rule -->
|……采集登记表.xlsx

<!-- section_type=数据整理; knowledge_type=field_rule -->
|……地物管径记录表.xlsx

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……仪器检定证书（扫描件）.pdf

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……数据真实性申明（扫描件）.pdf

<!-- section_type=数据整理; knowledge_type=data_spec -->
XXXX 年 XX 市 XX 县（市、区）+项目名称+检测点数据

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……88888888GNSSRTK 实测 20250101（成果数据）.csv

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……88888888GNSSRTK仪仪20250101仪仪仪数据仪.csv

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……仪仪仪仪仪仪仪仪

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……ZPY42010020250101000101.jpg

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……YXN42010020250101000101.jpg

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……ZPY42010020250101000102.jpg

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……YXN42010020250101000102.jpg

<!-- section_type=数据整理; knowledge_type=data_spec -->
……

<!-- section_type=数据整理; knowledge_type=field_rule -->
|……采集登记表.xlsx

<!-- section_type=数据整理; knowledge_type=field_rule -->
|……地物管径记录表.xlsx

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……仪器检定证书（扫描件）.pdf

<!-- section_type=数据整理; knowledge_type=data_spec -->
|……数据真实性申明（扫描件）.pdf

<!-- chapter_no=6.5; chapter_title=数据汇交; section_type=数据整理; knowledge_type=data_spec -->
## 6.5 数据汇交

<!-- section_type=数据整理; knowledge_type=data_spec -->
检测数据采集完成，提交以下成果资料：

<!-- section_type=数据整理; knowledge_type=field_rule -->
a) 按目录组织的检测点数据（采集登记表、坐标文件、实地照片、影像图、仪器检定证书、数据真

<!-- section_type=数据整理; knowledge_type=data_spec -->
实性申明等）；

<!-- section_type=数据整理; knowledge_type=data_spec -->
b) 任务区范围线；

<!-- section_type=数据整理; knowledge_type=field_rule -->
c) 项目成果结合表；

<!-- section_type=数据整理; knowledge_type=data_spec -->
d) 其他有关资料。

<!-- section_type=数据整理; knowledge_type=data_spec -->
以上资料按照实景三维检测点档案管理规定进行管理。

<!-- chapter_no=7; chapter_title=数据库组织与建库; section_type=数据库; knowledge_type=field_rule -->
# 7 数据库组织与建库

<!-- chapter_no=7.1; chapter_title=数据组织; section_type=数据库; knowledge_type=field_rule -->
## 7.1 数据组织

<!-- chapter_no=7.1.1; chapter_title=数据关联及组织; section_type=数据库; knowledge_type=field_rule -->
### 7.1.1 数据关联及组织

<!-- section_type=数据库; knowledge_type=field_rule -->
检测点数据库实体间建立逻辑关联，并采用优化的数据结构和组织方法，减少数据冗

<!-- section_type=数据库; knowledge_type=field_rule -->
余。数据组织采用分类组织方式，检测点数据库数据组织关系如图2 所示。

<!-- section_type=数据库; knowledge_type=data_spec -->
检测点数据库

<!-- section_type=数据库; knowledge_type=data_spec -->
矢量数据

<!-- section_type=数据库; knowledge_type=data_spec -->
原始文件

<!-- section_type=数据库; knowledge_type=data_spec -->
影像数据

<!-- section_type=数据库; knowledge_type=data_spec -->
行政区划

<!-- section_type=数据库; knowledge_type=data_spec -->
坐标文件

<!-- section_type=数据库; knowledge_type=field_rule -->
采集登记表

<!-- section_type=数据库; knowledge_type=data_spec -->
检测点数据

<!-- section_type=数据库; knowledge_type=data_spec -->
其他数据

<!-- section_type=数据库; knowledge_type=data_spec -->
地名地址

<!-- section_type=数据库; knowledge_type=data_spec -->
水系

<!-- section_type=数据库; knowledge_type=data_spec -->
交通

<!-- section_type=数据库; knowledge_type=data_spec -->
地形

<!-- section_type=数据库; knowledge_type=data_spec -->
图幅范围

<!-- section_type=数据库; knowledge_type=data_spec -->
实地照片

<!-- section_type=数据库; knowledge_type=data_spec -->
影像图

<!-- section_type=数据库; knowledge_type=data_spec -->
属性数据

<!-- section_type=数据库; knowledge_type=field_rule -->
图 2 检测点数据库数据组织关系

<!-- chapter_no=7.1.2; chapter_title=矢量数据组织; section_type=数据库; knowledge_type=field_rule -->
### 7.1.2 矢量数据组织

<!-- section_type=数据库; knowledge_type=field_rule -->
矢量数据以点要素表示，以地理坐标存储。

<!-- chapter_no=7.1.3; chapter_title=属性数据组织; section_type=数据库; knowledge_type=field_rule -->
### 7.1.3 属性数据组织

<!-- section_type=数据库; knowledge_type=data_spec -->
属性数据内容及定义按照附录 B 执行。

<!-- chapter_no=7.1.4; chapter_title=原始文件组织; section_type=数据库; knowledge_type=field_rule -->
### 7.1.4 原始文件组织

<!-- section_type=数据库; knowledge_type=field_rule -->
原始文件包括坐标文件、采集登记表，以文件方式存储。

<!-- chapter_no=7.1.5; chapter_title=影像数据组织; section_type=数据库; knowledge_type=field_rule -->
### 7.1.5 影像数据组织

<!-- section_type=数据库; knowledge_type=data_spec -->
影像图包括实地照片、影像图，以图片文件方式存储，按类别建立文件夹存储不同类

<!-- section_type=数据库; knowledge_type=data_spec -->
别的图片。

<!-- chapter_no=7.1.6; chapter_title=其他数据组织; section_type=数据库; knowledge_type=field_rule -->
### 7.1.6 其他数据组织

<!-- section_type=数据库; knowledge_type=data_spec -->
其他数据为矢量或栅格数据，以地理坐标存储。

<!-- chapter_no=7.1.7; chapter_title=数据库命名与构成; section_type=数据库; knowledge_type=data_spec -->
### 7.1.7 数据库命名与构成

<!-- section_type=数据库; knowledge_type=data_spec -->
数据集命名和构成应满足如下要求：

<!-- section_type=数据库; knowledge_type=data_spec -->
a) 检测点数据库一般包含检测点数据集、其他数据集。检测点数据集命名为“JCD”，

<!-- section_type=数据库; knowledge_type=data_spec -->
其他数据集命名“QT”。

<!-- section_type=数据库; knowledge_type=data_spec -->
b) 检测点数据集包括 1 个检测点数据层。

<!-- section_type=数据库; knowledge_type=data_spec -->
c) 其他数据集一般包括行政区划数据层、地名地址数据层等。

<!-- chapter_no=7.2; chapter_title=数据库建设; section_type=数据库; knowledge_type=data_spec -->
## 7.2 数据库建设

<!-- chapter_no=7.2.1; chapter_title=库体创建; section_type=数据库; knowledge_type=data_spec -->
### 7.2.1 库体创建

<!-- section_type=数据库; knowledge_type=field_rule -->
按照数据库组织要求， 对每类数据分配物理空间， 设置相关参数， 创建数据表等， 物理

<!-- section_type=数据库; knowledge_type=data_spec -->
空间分配时应考虑数据库的扩充性。

<!-- chapter_no=7.2.2; chapter_title=数据准备; section_type=数据库; knowledge_type=data_spec -->
### 7.2.2 数据准备

<!-- section_type=数据库; knowledge_type=field_rule -->
对整理后的检测点坐标文件按照数据组织的要求进行一致性转换，主要包括代码转换、

<!-- section_type=数据库; knowledge_type=data_spec -->
格式转换、坐标变换、投影转换等。

<!-- chapter_no=7.2.3; chapter_title=数据入库; section_type=数据库; knowledge_type=data_spec -->
### 7.2.3 数据入库

<!-- section_type=数据库; knowledge_type=field_rule -->
根据数据组织方式进行检测点空间数据及属性入库。 数据入库可以选用手动添加或程序

<!-- section_type=数据库; knowledge_type=data_spec -->
批量入库。

<!-- chapter_no=7.2.4; chapter_title=检测点文件存储; section_type=数据库; knowledge_type=data_spec -->
### 7.2.4 检测点文件存储

<!-- section_type=数据库; knowledge_type=data_spec -->
检测点文件以文件方式存储， 按项目名称命名文件夹， 依次存放检测点坐标文件、采集

<!-- section_type=数据库; knowledge_type=field_rule -->
登记表、实地照片目录、影像图目录。

<!-- chapter_no=7.3; chapter_title=数据库更新; section_type=数据库; knowledge_type=data_spec -->
## 7.3 数据库更新

<!-- section_type=数据库; knowledge_type=data_spec -->
数据库中的检测点数据应按需求对数据进行更新，保持数据的现势性。

<!-- chapter_no=7.4; chapter_title=安全要求; section_type=数据库; knowledge_type=data_spec -->
## 7.4 安全要求

<!-- section_type=数据库; knowledge_type=data_spec -->
数据库安全防护、保密和数据库备份与恢复应符合 GB/T 33453 的规定。

<!-- chapter_no=8; chapter_title=质量要求; section_type=质量要求; knowledge_type=quality_rule -->
# 8 质量要求

<!-- section_type=质量要求; knowledge_type=quality_rule -->
数据库的质量要求应符合 GB/T 33453 的规定，同时满足以下要求：

<!-- section_type=质量要求; knowledge_type=data_spec -->
a) 完整性： 检测点坐标文件、 影像图应完整， 与入库数据保持一致、 数据无重复入库。

<!-- section_type=质量要求; knowledge_type=data_spec -->
b) 逻辑一致性：

<!-- section_type=质量要求; knowledge_type=quality_rule -->
1) 概念一致性：检测点数据的数据集、数据层表结构应符合 7.1 的规定；

<!-- section_type=质量要求; knowledge_type=data_spec -->
2) 值域一致性：属性项的取值应在值域界定的范围内；

<!-- section_type=质量要求; knowledge_type=data_spec -->
3) 格式一致性：应与规定格式保持一致。

<!-- section_type=质量要求; knowledge_type=quality_rule -->
c) 属性精度：数据的属性项及属性值等应正确。

<!-- section_type=质量要求; knowledge_type=data_spec -->
附录A

<!-- section_type=质量要求; knowledge_type=data_spec -->
（资料性）

<!-- section_type=质量要求; knowledge_type=data_spec -->
采集登记表

<!-- section_type=质量要求; knowledge_type=data_spec -->
采集登记表见表 A.1。

<!-- section_type=质量要求; knowledge_type=data_spec -->
表 A.1 采集登记表

<!-- section_type=质量要求; knowledge_type=data_spec -->
项目名称：

<!-- section_type=质量要求; knowledge_type=data_spec -->
类型代码 原始坐标文件 中央子午线 仪器品牌型号 仪器编号/软件名称 采集单位 采集人员 采集日期

<!-- section_type=质量要求; knowledge_type=data_spec -->
P/G/PG

<!-- section_type=质量要求; knowledge_type=data_spec -->
注 1：P 为平面检测点类型代码，G 为高程检测点类型代码，PG 为平高检测点类型代码。

<!-- section_type=质量要求; knowledge_type=data_spec -->
注 2：检测点采用内业采集方式时，不填写仪器品牌型号。

<!-- section_type=质量要求; knowledge_type=data_spec -->
附录 B

<!-- section_type=质量要求; knowledge_type=data_spec -->
（规范性）

<!-- section_type=质量要求; knowledge_type=data_spec -->
检测点属性表结构

<!-- section_type=质量要求; knowledge_type=data_spec -->
检测点属性表结构见表 B.1。

<!-- section_type=质量要求; knowledge_type=data_spec -->
表 B.1 检测点属性表结构

<!-- section_type=质量要求; knowledge_type=data_spec -->
序

<!-- section_type=质量要求; knowledge_type=data_spec -->
号

<!-- section_type=质量要求; knowledge_type=data_spec -->
字段

<!-- section_type=质量要求; knowledge_type=data_spec -->
名称

<!-- section_type=质量要求; knowledge_type=data_spec -->
字段

<!-- section_type=质量要求; knowledge_type=data_spec -->
代码

<!-- section_type=质量要求; knowledge_type=data_spec -->
字段

<!-- section_type=质量要求; knowledge_type=data_spec -->
类型

<!-- section_type=质量要求; knowledge_type=data_spec -->
字段

<!-- section_type=质量要求; knowledge_type=data_spec -->
长度

<!-- section_type=质量要求; knowledge_type=data_spec -->
小数

<!-- section_type=质量要求; knowledge_type=data_spec -->
位数

<!-- section_type=质量要求; knowledge_type=data_spec -->
值域 约束/条件 备注

<!-- chapter_no=1; chapter_title=检测点编号 BH 字符型 20 — — M 见注 2; knowledge_type=chapter_title -->
# 1 检测点编号 BH 字符型 20 — — M 见注 2

<!-- chapter_no=2; chapter_title=纬度值 B 双精度型 — 9; knowledge_type=chapter_title -->
# 2 纬度值 B 双精度型 — 9

DD.DDDD

DDDDD

M 见注 3

<!-- chapter_no=3; chapter_title=经度值 L 双精度型 — 9; knowledge_type=chapter_title -->
# 3 经度值 L 双精度型 — 9

DDD.DDD

DDDDDD

M 见注 4

<!-- chapter_no=4; chapter_title=大地高 H 双精度型 — 3 —; knowledge_type=chapter_title -->
# 4 大地高 H 双精度型 — 3 —

C/能获取大地

高时必填

见注 5

<!-- chapter_no=5; chapter_title=北坐标 x 双精度型 — 3 ≥0; knowledge_type=chapter_title -->
# 5 北坐标 x 双精度型 — 3 ≥0

C/能获取平面

坐标时必填

见注 6

<!-- chapter_no=6; chapter_title=东坐标 y 双精度型 — 3 ≥0; knowledge_type=chapter_title -->
# 6 东坐标 y 双精度型 — 3 ≥0

C/能获取平面

坐标时必填

见注 7

<!-- chapter_no=7; chapter_title=高程 h1 双精度型 — 3 —; knowledge_type=chapter_title -->
# 7 高程 h1 双精度型 — 3 —

C/能获取高程

时必填

见注 8

<!-- chapter_no=8; chapter_title=中央子午线; knowledge_type=chapter_title -->
# 8 中央子午线

ZYZW

X

双精度型 — — ≥0 M 见注 9

<!-- chapter_no=9; chapter_title=投影面高程 h0 双精度型 — 3 — O 见注 10; knowledge_type=chapter_title -->
# 9 投影面高程 h0 双精度型 — 3 — O 见注 10

<!-- chapter_no=10; chapter_title=仪器高 YQG 双精度型 — 3 ≥0 O —; knowledge_type=chapter_title -->
# 10 仪器高 YQG 双精度型 — 3 ≥0 O —

<!-- chapter_no=11; chapter_title=地物代码; knowledge_type=chapter_title -->
# 11 地物代码

DWD

M

字符型 10 — — M 注 11

<!-- chapter_no=12; chapter_title=地物名称; knowledge_type=chapter_title -->
# 12 地物名称

DWM

C

字符型 10 — — O 注 12

<!-- chapter_no=13; chapter_title=检测点类型 LX 字符型 10 — P/G/PG M —; knowledge_type=chapter_title -->
# 13 检测点类型 LX 字符型 10 — P/G/PG M —

<!-- chapter_no=14; chapter_title=平面精度 PMJD 双精度型 — — ≥0; knowledge_type=chapter_title -->
# 14 平面精度 PMJD 双精度型 — — ≥0

C/类型为“P”

或“PG”时必填

见注 13

<!-- chapter_no=15; chapter_title=高程精度 GCJD 双精度型 — — ≥0; knowledge_type=chapter_title -->
# 15 高程精度 GCJD 双精度型 — — ≥0

C/类型为“G”

或“PG”时必填

见注 14

<!-- chapter_no=16; chapter_title=采集方式 CJFS 字符型 20 — — M 见注 15; knowledge_type=chapter_title -->
# 16 采集方式 CJFS 字符型 20 — — M 见注 15

<!-- chapter_no=17; chapter_title=位置描述 MS 字符型 254 — — O 见注 16; knowledge_type=chapter_title -->
# 17 位置描述 MS 字符型 254 — — O 见注 16

<!-- chapter_no=18; chapter_title=影像截图 YX 字符型 254 — — O 见注 17; knowledge_type=chapter_title -->
# 18 影像截图 YX 字符型 254 — — O 见注 17

<!-- chapter_no=19; chapter_title=实地照片 ZP 字符型 254 — — O 见注 18; knowledge_type=chapter_title -->
# 19 实地照片 ZP 字符型 254 — — O 见注 18

序

号

字段

名称

字段

代码

字段

类型

字段

长度

小数

位数

值域 约束/条件 备注

<!-- chapter_no=20; chapter_title=采集日期 RQ 日期型 — —; knowledge_type=chapter_title -->
# 20 采集日期 RQ 日期型 — —

YYYY/MM

/DD

M 见注 19

<!-- chapter_no=21; chapter_title=行政区代码; knowledge_type=chapter_title -->
# 21 行政区代码

XZQD

M

整型 10 — — M 见注 20

<!-- chapter_no=22; chapter_title=项目名称; knowledge_type=chapter_title -->
# 22 项目名称

XMM

C

字符型 60 — — O 见注 21

<!-- chapter_no=23; chapter_title=是否可用 SFKY 字符型 254 — — O 见注 22; knowledge_type=chapter_title -->
# 23 是否可用 SFKY 字符型 254 — — O 见注 22

<!-- chapter_no=24; chapter_title=备注 BZ 字符型 254 — — O; knowledge_type=chapter_title -->
# 24 备注 BZ 字符型 254 — — O

注 1：约束/条件：“M”为必选项，即必须填写的信息；“C”为条件必选项，即满足某一条件或要求时必

须填写的信息；“O”为可选项，可根据实际情况选择填写。

注 2：进行全库统一编码。

注 3：检测点纬度地理坐标，单位为“度”，小数点后保留有效位数 9 位。

注 4：检测点经度地理坐标，单位为“度”，小数点后保留有效位数 9 位。

注 5：单位：米。采集时的地物点大地高，保留 3 位小数，RTK 采集时必须填写原始大地高。其他方

式、内业图解方式采集时，此项填写 0。

注 6：北坐标（投影平面 x 坐标），全站仪极坐标采集坐标必填。

注 7：东坐标（投影平面 y 坐标），全站仪极坐标采集坐标必填。

注 8： 检测点高程，DLG/DOM 平面位置检测点不位于地面时， 即代码为P 不需要求取高程值， 如房檐、

房角等，否则代码为 G、PG 时必填。

注 9：中央子午线，根据项目实际的中央子午线填写。

注 10：投影面高程，根据项目实际的投影面高程填写。

注 11：检测地物代码，以 3 位代码表示，取值见附录 C.1。

注 12：地物名称，采集地物的名称，取值见附录 C.1。

注 13：平面精度，实测法采集时，填写仪器的平面位置标称精度；图解法采集时，填写数据源的平

面位置标称精度，单位为“米”。

注 14：高程精度，实测法采集时，填写仪器的高程标称精度；图解法采集时，填写数据源的高程标

称精度，单位为“米”。

注 15：外业采集：GNSS-RTK 实测法、全站仪实测法、激光雷达实测法；内业采集：已有成果提取，

如空中三角测量、实景三维模型采集等。

注 16：位置描述，如：花坛西南角点等。

注 17：存储影像图文件所在的物理路径及文件名，当文件名不存在时此项为空。

注 18：存储实地照片文件所在的物理路径及文件名，当文件名不存在时此项为空。

注 19：属性值域为“YYYY/MM/DD”表示日期，其中“Y”表示年份，“M”表示月份，“D”表示日，不足位

的用 0 补足，例如“2024/03/06”。

注 20：填写该检测点所属县级行政区代码。

注 21：可填写项目名称或编号。填写检测点采集项目编号时，可以年份+顺序号表示，如 2024-001。

注 22：记录检测点是否可用状态，如当检测点对应地物发生变化时，说明变化状态。

附录C

（规范性）

采集地物内外业代码对照表

采集地物内外业代码对照关系见表 C.1.

表 C.1 采集地物内外业代码对照表

序号

外业代码

（地物+检测点类型）

地物名称 地物代码

检测点

类型

含义 采集说明

控制测量方式下

是否偏心

<!-- chapter_no=1; chapter_title=BZJPG 标志角 BZJ PG 标志线角点 地面标志线角点，如车位线等 否; knowledge_type=chapter_title -->
# 1 BZJPG 标志角 BZJ PG 标志线角点 地面标志线角点，如车位线等 否

<!-- chapter_no=2; chapter_title=BZXP 标志线 BZX P 标志线平面点 交通标志线顶点 否; knowledge_type=chapter_title -->
# 2 BZXP 标志线 BZX P 标志线平面点 交通标志线顶点 否

<!-- chapter_no=3; chapter_title=DLMG 道路面 DLM G 路面高程点 道路交叉口中心点 否; knowledge_type=chapter_title -->
# 3 DLMG 道路面 DLM G 路面高程点 道路交叉口中心点 否

<!-- chapter_no=4; chapter_title=DLMPG 道路面 DLM PG 路面平高点 道路面内带有标志的平高点 否; knowledge_type=chapter_title -->
# 4 DLMPG 道路面 DLM PG 路面平高点 道路面内带有标志的平高点 否

<!-- chapter_no=5; chapter_title=DLXPG 道路线 DLX PG 道路线平高点 道路边线交叉点 否; knowledge_type=chapter_title -->
# 5 DLXPG 道路线 DLX PG 道路线平高点 道路边线交叉点 否

<!-- chapter_no=6; chapter_title=DZJPG 地砖角 DZJ PG 地砖角平高点 广场地砖不同色块界线角点 否; knowledge_type=chapter_title -->
# 6 DZJPG 地砖角 DZJ PG 地砖角平高点 广场地砖不同色块界线角点 否

<!-- chapter_no=7; chapter_title=DXGPG 电线杆 DXG PG 电线杆平高点 电线杆外边缘 是; knowledge_type=chapter_title -->
# 7 DXGPG 电线杆 DXG PG 电线杆平高点 电线杆外边缘 是

<!-- chapter_no=8; chapter_title=FJDP 房角点 FJD P 房角平面点 不落地的房角 否; knowledge_type=chapter_title -->
# 8 FJDP 房角点 FJD P 房角平面点 不落地的房角 否

<!-- chapter_no=9; chapter_title=FJDPG 房角点 FJD PG 房角平高点 房屋墙基脚点 否; knowledge_type=chapter_title -->
# 9 FJDPG 房角点 FJD PG 房角平高点 房屋墙基脚点 否

<!-- chapter_no=10; chapter_title=FYDPG 房檐点 FYD PG 房檐平高点 房檐角点 否; knowledge_type=chapter_title -->
# 10 FYDPG 房檐点 FYD PG 房檐平高点 房檐角点 否

<!-- chapter_no=11; chapter_title=GSCP 固水池 GSC P 水池平面点 固化水池角点 否; knowledge_type=chapter_title -->
# 11 GSCP 固水池 GSC P 水池平面点 固化水池角点 否

<!-- chapter_no=12; chapter_title=HTJPG 花坛角 HTJ PG 花坛平高点 花坛角点 否; knowledge_type=chapter_title -->
# 12 HTJPG 花坛角 HTJ PG 花坛平高点 花坛角点 否

<!-- chapter_no=13; chapter_title=JGXPG 井盖中心点 JGX PG 井盖平高点 地面井盖中心点 否; knowledge_type=chapter_title -->
# 13 JGXPG 井盖中心点 JGX PG 井盖平高点 地面井盖中心点 否

<!-- chapter_no=14; chapter_title=LDGPG 路灯杆 LDG PG 路灯平高点 路灯杆外边缘 是; knowledge_type=chapter_title -->
# 14 LDGPG 路灯杆 LDG PG 路灯平高点 路灯杆外边缘 是

<!-- chapter_no=15; chapter_title=QGYP 旗杆 QGY P 旗杆平面点 旗杆外缘底点 是; knowledge_type=chapter_title -->
# 15 QGYP 旗杆 QGY P 旗杆平面点 旗杆外缘底点 是

序号

外业代码

（地物+检测点类型）

地物名称 地物代码

检测点

类型

含义 采集说明

控制测量方式下

是否偏心

<!-- chapter_no=16; chapter_title=QCJPG 球场角 QCJ PG 球场平高点 球场不同色块界线角点 否; knowledge_type=chapter_title -->
# 16 QCJPG 球场角 QCJ PG 球场平高点 球场不同色块界线角点 否

<!-- chapter_no=17; chapter_title=TJJPG 台阶角 TJJ PG 台阶平高点 台阶角点 否; knowledge_type=chapter_title -->
# 17 TJJPG 台阶角 TJJ PG 台阶平高点 台阶角点 否

<!-- chapter_no=18; chapter_title=TXGPG 通讯杆 TXG PG 通讯杆平高点 通讯杆外边缘 是; knowledge_type=chapter_title -->
# 18 TXGPG 通讯杆 TXG PG 通讯杆平高点 通讯杆外边缘 是

<!-- chapter_no=19; chapter_title=WQJPG 围墙角 WQJ PG 围墙角平高点 围墙角点 否; knowledge_type=chapter_title -->
# 19 WQJPG 围墙角 WQJ PG 围墙角平高点 围墙角点 否

<!-- chapter_no=20; chapter_title=WSBPG 污水篦子 WSB PG 污水篦子平高点 污水篦子中心点 否; knowledge_type=chapter_title -->
# 20 WSBPG 污水篦子 WSB PG 污水篦子平高点 污水篦子中心点 否

<!-- chapter_no=21; chapter_title=XHSPG 消火栓 XHS PG 消火栓中心点 消火栓中心点 是; knowledge_type=chapter_title -->
# 21 XHSPG 消火栓 XHS PG 消火栓中心点 消火栓中心点 是

<!-- chapter_no=22; chapter_title=LPJPG 楼牌角 LPJ PG 楼牌角点平高点 较大楼牌的角点 否; knowledge_type=chapter_title -->
# 22 LPJPG 楼牌角 LPJ PG 楼牌角点平高点 较大楼牌的角点 否

<!-- chapter_no=23; chapter_title=PLJPG 飘楼角 PLJ PG 飘楼角点平高点 飘楼角点 否; knowledge_type=chapter_title -->
# 23 PLJPG 飘楼角 PLJ PG 飘楼角点平高点 飘楼角点 否

<!-- chapter_no=24; chapter_title=YTJPG 阳台角 YTJ PG 阳台角点平高点 阳台角点 否; knowledge_type=chapter_title -->
# 24 YTJPG 阳台角 YTJ PG 阳台角点平高点 阳台角点 否

<!-- chapter_no=25; chapter_title=MDJPG 门墩角 MDJ PG 门墩角点平高点 门墩地面角点 否; knowledge_type=chapter_title -->
# 25 MDJPG 门墩角 MDJ PG 门墩角点平高点 门墩地面角点 否

<!-- chapter_no=26; chapter_title=ZZJPG 支柱角 ZZJ PG 支柱角点平高点 支柱地面角点 否; knowledge_type=chapter_title -->
# 26 ZZJPG 支柱角 ZZJ PG 支柱角点平高点 支柱地面角点 否

<!-- chapter_no=27; chapter_title=XHDPG 信号灯柱 XHD PG 信号灯平高点 信号灯外缘平高点 是; knowledge_type=chapter_title -->
# 27 XHDPG 信号灯柱 XHD PG 信号灯平高点 信号灯外缘平高点 是

<!-- chapter_no=28; chapter_title=JKGPG 监控杆 JKG PG 监控杆平高点 监控杆外缘平高点 是; knowledge_type=chapter_title -->
# 28 JKGPG 监控杆 JKG PG 监控杆平高点 监控杆外缘平高点 是

<!-- chapter_no=29; chapter_title=HDDG 旱地 HDD G 旱地中心高程 平坦旱地地块中心 否; knowledge_type=chapter_title -->
# 29 HDDG 旱地 HDD G 旱地中心高程 平坦旱地地块中心 否

<!-- chapter_no=30; chapter_title=STDG 水田 STD G 水田中心高程 水田地块高程 否; knowledge_type=chapter_title -->
# 30 STDG 水田 STD G 水田中心高程 水田地块高程 否

<!-- chapter_no=31; chapter_title=YLDG 院落地面点 YLD G 单位院落高程 单位院落中心点 否; knowledge_type=chapter_title -->
# 31 YLDG 院落地面点 YLD G 单位院落高程 单位院落中心点 否

<!-- chapter_no=32; chapter_title=PFJPG 棚房角 PFJ PG 棚房角点平高点 棚房角地面点 否; knowledge_type=chapter_title -->
# 32 PFJPG 棚房角 PFJ PG 棚房角点平高点 棚房角地面点 否

<!-- chapter_no=33; chapter_title=QLMG 桥梁 QLM G 桥梁中心高程 桥梁面中心点 否; knowledge_type=chapter_title -->
# 33 QLMG 桥梁 QLM G 桥梁中心高程 桥梁面中心点 否

参 考 文 献

[1] GB/T 13923—2022 基础地理信息要素分类与代码

[2] GB/T 20257.1—2017 国家基本比例尺地图图式 第 1 部分：1：500 1：1000 1：2000

地形图图式

[3] GB/T 20258.1—2019 基础地理信息要素数据字典 第 1 部分：1：500 1 ：1000 1 ：

2000 比例尺

[4] GB/T 24356-2023 测绘成果质量检查与验收

[5] CH/T 1025—2011 数字线划图（DLG）质量检验技术规程

[6] CH/T 1026—2012 数字高程模型质量检验技术规程
