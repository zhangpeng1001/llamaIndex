# 实景三维质检大数据支撑库 时空数据规范 第5部分 重要要素

> 来源：实景三维质检大数据支撑库 时空数据规范 第5部分 重要要素.pdf（增强版提取，已去目录/页眉/页码噪声）


第5 部分 重要要素

（草案）

2025 年 7 月

I

目  次

I

前 言

本文件按照GB/T 1.1—2020《标准化工作导则  第1部分：标准化文件的结构和起草规

则》的规定起草。

第1部分 数据分类与基本规定

第2部分 检测点

第3部分 检测线

第4部分 标志性地物

第6部分 高精度栅格数据

第7部分 资源数据

请注意本文件的某些内容可能涉及专利。本文件的发布机构不承担识别专利的责任。

起草单位：

起草人员：

I

引  言

面对实景三维质检供给服务能力提升需求， 以及适应大数据、 人工智能等新技术的飞速

发展对高可靠质检参考数据的要求， 充分利用高可信的时空信息数据， 开展实景三维质检大

数据支撑库重要要素库建设，包括重要要素数据要求、数据结构、 数据处理、数据更新、检

查方法等内容， 通过该数据库建设， 提升实景三维数据质量检验效率及正确性， 推进高质量

发展，支撑质量强国建设。

<!-- chapter_no=1; chapter_title=范围; section_type=范围; knowledge_type=scope_intro -->
# 1 范围

<!-- section_type=范围; knowledge_type=scope_intro -->
本数据规范规定了实景三维质检大数据支撑库重要要素数据要求、 数据结构、 数据处理、

<!-- section_type=范围; knowledge_type=scope_intro -->
数据更新、检查方法等内容。

<!-- section_type=范围; knowledge_type=scope_intro -->
本数据规范适用于辅助实景三维、 基础测绘等不同类型测绘成果中框架性或重大要素的

<!-- section_type=范围; knowledge_type=scope_intro -->
完整性、现势性及正确性的快速人工检查和软件自动比对。

<!-- chapter_no=2; chapter_title=规范性引用文件; section_type=引用文件; knowledge_type=references -->
# 2 规范性引用文件

<!-- section_type=引用文件; knowledge_type=references -->
下列文件的内容通过文中的规范性引用而构成本文件必不可少的条款。 其中， 注日期的

<!-- section_type=引用文件; knowledge_type=references -->
引用文件， 仅该日期对应的版本适用于本文件； 不注日期的引用文件， 其最新版本 （包括所

<!-- section_type=引用文件; knowledge_type=references -->
有的修改单）适用于本文件。

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 18316-2008 数字测绘成果质量检查与验收

<!-- section_type=引用文件; knowledge_type=references -->
GB/T 24356-2023 测绘成果质量检查与验收

<!-- section_type=引用文件; knowledge_type=references -->
CH/T 9006-2010 1∶5000 1∶10000基础地理信息数字产品更新规范

<!-- section_type=引用文件; knowledge_type=references -->
DB33/T 817-2010 基础地理信息要素分类与图形表达代码

<!-- chapter_no=3; chapter_title=术语与定义; section_type=术语定义; knowledge_type=term_definition -->
# 3 术语与定义

<!-- section_type=术语定义; knowledge_type=term_definition -->
下列术语与定义适用于本文件。

<!-- chapter_no=3; chapter_title=1; knowledge_type=chapter_title -->
# 3 1

重要要素 important elements

重要要素是指在测绘过程、 成果或应用中， 对目标实现、 精度保障、 法律有效性起决定

性作用的关键成分。其缺失或偏差会直接导致测绘成果失效、应用出错甚至产生法律风险。

<!-- chapter_no=4; chapter_title=数据要求; section_type=数据采集; knowledge_type=quality_rule -->
# 4 数据要求

<!-- chapter_no=4.1; chapter_title=时空基准; section_type=时空基准; knowledge_type=data_spec -->
## 4.1 时空基准

<!-- section_type=时空基准; knowledge_type=data_spec -->
a)坐标系统：2000 国家大地坐标系，采用地理坐标系，单位为度；

<!-- section_type=时空基准; knowledge_type=data_spec -->
b)高程基准：1985 国家高程基准，单位为米；

<!-- section_type=时空基准; knowledge_type=data_spec -->
c)时间基准：公元纪年和北京时间。

<!-- chapter_no=4.2; chapter_title=数据存储; section_type=时空基准; knowledge_type=data_spec -->
## 4.2 数据存储

<!-- section_type=时空基准; knowledge_type=data_spec -->
重要要素数据库以*.gdb 格式存储，水系、交通、居民地、境界等不同类别数据分别以

<!-- section_type=时空基准; knowledge_type=data_spec -->
“数据集”形式存储，各数据集中的重要要素以点、线、面图层形式分类存储。

<!-- chapter_no=4.3; chapter_title=重要要素构成; section_type=时空基准; knowledge_type=data_spec -->
## 4.3 重要要素构成

<!-- chapter_no=4.3.1; chapter_title=水系要素; section_type=时空基准; knowledge_type=data_spec -->
### 4.3.1 水系要素

<!-- section_type=时空基准; knowledge_type=data_spec -->
水系重要要素主要包含以下内容：

<!-- section_type=时空基准; knowledge_type=data_spec -->
a）行政区划内主要水系干流及沿岸主要堤坝、标准海塘；

<!-- section_type=时空基准; knowledge_type=data_spec -->
b）小二型以上水库以及配套的溢洪道。

<!-- chapter_no=4.3.2; chapter_title=交通要素; section_type=时空基准; knowledge_type=data_spec -->
### 4.3.2 交通要素

<!-- section_type=时空基准; knowledge_type=data_spec -->
交通重要要素主要包含以下内容：

<!-- section_type=时空基准; knowledge_type=data_spec -->
a）国道、省道、快速路、高架路及其相应的重要附属设施，如大型桥梁、隧道、高速

<!-- section_type=时空基准; knowledge_type=data_spec -->
公路出入口\互通\枢纽、服务区、收费站、汽车渡口等；

<!-- section_type=时空基准; knowledge_type=data_spec -->
b）高铁、地铁（轻轨、磁浮铁轨） 、普通铁路及其相应的重要附属设施；

<!-- section_type=时空基准; knowledge_type=data_spec -->
c）民用机场。

<!-- chapter_no=4.3.3; chapter_title=居民地要素; section_type=时空基准; knowledge_type=data_spec -->
### 4.3.3 居民地要素

<!-- section_type=时空基准; knowledge_type=data_spec -->
居民地重要要素主要包含以下内容：

<!-- section_type=时空基准; knowledge_type=data_spec -->
a）乡级以上政府；

<!-- section_type=时空基准; knowledge_type=data_spec -->
b）教育行政主管机构中明确要求的大学、中学及小学；

<!-- section_type=时空基准; knowledge_type=data_spec -->
c）三级医院及其他著名的医院。

<!-- chapter_no=4.3.4; chapter_title=境界要素; section_type=时空基准; knowledge_type=data_spec -->
### 4.3.4 境界要素

<!-- section_type=时空基准; knowledge_type=data_spec -->
境界重要要素主要包含乡镇及以上行政区域。

<!-- chapter_no=5; chapter_title=数据结构; section_type=数据整理; knowledge_type=data_spec -->
# 5 数据结构

<!-- section_type=数据整理; knowledge_type=field_rule -->
重要要素数据库数据结构如表1。

<!-- section_type=数据整理; knowledge_type=field_rule -->
表 1 重要要素数据结构

<!-- section_type=数据整理; knowledge_type=data_spec -->
序号 数据集名称 图层名称 图层别名 图层类型

<!-- section_type=数据整理; knowledge_type=data_spec -->
水系数据集

<!-- section_type=数据整理; knowledge_type=data_spec -->
HYD_SXGL_LN 水系干流（结构线） 线图层

<!-- chapter_no=2; chapter_title=HYD_SXGL_PY 水系干流（范围面） 面图层; knowledge_type=chapter_title -->
# 2 HYD_SXGL_PY 水系干流（范围面） 面图层

<!-- chapter_no=3; chapter_title=HYD_GLDB_LN 干流堤坝（线） 线图层; knowledge_type=chapter_title -->
# 3 HYD_GLDB_LN 干流堤坝（线） 线图层

<!-- chapter_no=4; chapter_title=HYD_SK_PY 大中型水库（范围面） 面图层; knowledge_type=chapter_title -->
# 4 HYD_SK_PY 大中型水库（范围面） 面图层

<!-- chapter_no=5; chapter_title=HYD_YHD_PY 溢洪道（范围面） 面图层; knowledge_type=chapter_title -->
# 5 HYD_YHD_PY 溢洪道（范围面） 面图层

交通数据集

TRA_GS_LN 高速（结构线） 线图层

<!-- chapter_no=7; chapter_title=TRA_GD_LN 国道（结构线） 线图层; knowledge_type=chapter_title -->
# 7 TRA_GD_LN 国道（结构线） 线图层

<!-- chapter_no=8; chapter_title=TRA_SD_LN 省道（结构线） 线图层; knowledge_type=chapter_title -->
# 8 TRA_SD_LN 省道（结构线） 线图层

<!-- chapter_no=9; chapter_title=TRA_KS_LN 快速路及高架路（结构线） 线图层; knowledge_type=chapter_title -->
# 9 TRA_KS_LN 快速路及高架路（结构线） 线图层

<!-- chapter_no=10; chapter_title=TRA_GT_LN 高铁（结构线） 线图层; knowledge_type=chapter_title -->
# 10 TRA_GT_LN 高铁（结构线） 线图层

<!-- chapter_no=11; chapter_title=TRA_DT_LN 地铁（结构线） 线图层; knowledge_type=chapter_title -->
# 11 TRA_DT_LN 地铁（结构线） 线图层

<!-- chapter_no=12; chapter_title=TRA_PTDL_LN 普通铁路（结构线） 线图层; knowledge_type=chapter_title -->
# 12 TRA_PTDL_LN 普通铁路（结构线） 线图层

<!-- chapter_no=13; chapter_title=TRA_FSSS_PT 附属设施（点） 点图层; knowledge_type=chapter_title -->
# 13 TRA_FSSS_PT 附属设施（点） 点图层

<!-- chapter_no=14; chapter_title=TRA_FSSS_LN 附属设施（线） 线图层; knowledge_type=chapter_title -->
# 14 TRA_FSSS_LN 附属设施（线） 线图层

<!-- chapter_no=15; chapter_title=TRA_FSSS_PY 附属设施（面） 面图层; knowledge_type=chapter_title -->
# 15 TRA_FSSS_PY 附属设施（面） 面图层

<!-- chapter_no=16; chapter_title=TRA_MYJC_PY 民用机场（范围面） 面图层; knowledge_type=chapter_title -->
# 16 TRA_MYJC_PY 民用机场（范围面） 面图层

居民地数据集

RES_ZF_PT 乡级以上政府 点图层

<!-- chapter_no=18; chapter_title=RES_XX_PT 学校 点图层; knowledge_type=chapter_title -->
# 18 RES_XX_PT 学校 点图层

<!-- chapter_no=19; chapter_title=RES_YY_PT 医院 点图层; knowledge_type=chapter_title -->
# 19 RES_YY_PT 医院 点图层

境界数据集

BOU_PRO_PY 省级境界 面图层

<!-- chapter_no=21; chapter_title=BOU_CIT_PY 地级境界 面图层; knowledge_type=chapter_title -->
# 21 BOU_CIT_PY 地级境界 面图层

<!-- chapter_no=22; chapter_title=BOU_COU_PY 县级境界 面图层; knowledge_type=chapter_title -->
# 22 BOU_COU_PY 县级境界 面图层

序号 数据集名称 图层名称 图层别名 图层类型

<!-- chapter_no=23; chapter_title=BOU_TOW_PY 乡级境界 面图层; knowledge_type=chapter_title -->
# 23 BOU_TOW_PY 乡级境界 面图层

<!-- chapter_no=5.1; chapter_title=水系数据集; knowledge_type=chapter_title -->
## 5.1 水系数据集

水系数据集主要包含水系干流（结构线） 、水系干流（范围面） 、干流堤坝（线） 、大中

型水库、溢洪道 （范围面）等5 个图层。 各图层的字段属性均来源各参考数据源， 其中仅分

类代码、 更新源、 现势性等字段属性为必填字段， 其他字段属性均为条件必填， 即参考数据

源中有相关属性并正确时应填写，其他数据集填写要求相同，各图层属性结构如表2-表 5。

表 2 水系干流（结构线）图层属性结构表

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=FNAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 FNAME 名称 Text（50） 条件必填 /

<!-- chapter_no=3; chapter_title=FNAME2 名称 2 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 3 FNAME2 名称 2 Text（50） 条件必填 /

<!-- chapter_no=4; chapter_title=SUPRIVER 上级河流 Text（50） 条件必填; knowledge_type=chapter_title -->
# 4 SUPRIVER 上级河流 Text（50） 条件必填

<!-- chapter_no=5; chapter_title=HYDCODE 水利编码 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 5 HYDCODE 水利编码 Text（50） 条件必填 /

<!-- chapter_no=6; chapter_title=HYDCODE2 水利编码 2 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 6 HYDCODE2 水利编码 2 Text（50） 条件必填 /

<!-- chapter_no=7; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 7 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=8; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 8 UPDATETIME 现势性 Text（14） 必填 /

表 3 水系干流（范围面） 、大中型水库等图层属性结构表

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=FNAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 FNAME 名称 Text（50） 条件必填 /

<!-- chapter_no=3; chapter_title=FNAME2 名称 2 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 3 FNAME2 名称 2 Text（50） 条件必填 /

<!-- chapter_no=4; chapter_title=FNAME3 名称 3 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 4 FNAME3 名称 3 Text（50） 条件必填 /

<!-- chapter_no=5; chapter_title=HYDCODE 水利编码 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 5 HYDCODE 水利编码 Text（50） 条件必填 /

<!-- chapter_no=6; chapter_title=HYDCODE2 水利编码 2 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 6 HYDCODE2 水利编码 2 Text（50） 条件必填 /

<!-- chapter_no=7; chapter_title=HYDCODE3 水利编码 3 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 7 HYDCODE3 水利编码 3 Text（50） 条件必填 /

<!-- chapter_no=8; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 8 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=9; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 9 UPDATETIME 现势性 Text（14） 必填 /

表 4 干流堤坝（线）图层属性结构表

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=FNAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 FNAME 名称 Text（50） 条件必填 /

<!-- chapter_no=3; chapter_title=FWIDTH 堤顶宽度 DOUBLE 条件必填 /; knowledge_type=chapter_title -->
# 3 FWIDTH 堤顶宽度 DOUBLE 条件必填 /

<!-- chapter_no=4; chapter_title=ELEVATION 堤顶高程 DOUBLE 条件必填 /; knowledge_type=chapter_title -->
# 4 ELEVATION 堤顶高程 DOUBLE 条件必填 /

<!-- chapter_no=5; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 5 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=6; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 6 UPDATETIME 现势性 Text（14） 必填 /

表 5 溢洪道（范围面）图层属性结构表

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=FNAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 FNAME 名称 Text（50） 条件必填 /

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=3; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 3 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=4; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 4 UPDATETIME 现势性 Text（14） 必填 /

<!-- chapter_no=5.2; chapter_title=交通数据集; knowledge_type=chapter_title -->
## 5.2 交通数据集

交通数据集主要包含高速（结构线） 、国道（结构线） 、省道（结构线） 、快速路及高架

路（结构线） 、高铁（结构线） 、地铁（结构线） 、普通铁路（结构线） 、附属设施（点、线、

面） 、民用机场（范围面）等11 个图层。各图层属性结构表6-表 8。

表 6 高速、国道、省道、快速路及高架路等图层属性结构表

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=FCODE2 分类代码 2 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 FCODE2 分类代码 2 Text（50） 条件必填 /

<!-- chapter_no=3; chapter_title=FCODE3 分类代码 3 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 3 FCODE3 分类代码 3 Text（50） 条件必填 /

<!-- chapter_no=4; chapter_title=FCODE4 分类代码 4 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 4 FCODE4 分类代码 4 Text（50） 条件必填 /

<!-- chapter_no=5; chapter_title=FNAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 5 FNAME 名称 Text（50） 条件必填 /

<!-- chapter_no=6; chapter_title=FNAME2 名称 2 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 6 FNAME2 名称 2 Text（50） 条件必填 /

<!-- chapter_no=7; chapter_title=FNAME3 名称 3 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 7 FNAME3 名称 3 Text（50） 条件必填 /

<!-- chapter_no=8; chapter_title=FNAME4 名称 4 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 8 FNAME4 名称 4 Text（50） 条件必填 /

<!-- chapter_no=9; chapter_title=ROADCODE 路线编码 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 9 ROADCODE 路线编码 Text（50） 条件必填 /

<!-- chapter_no=10; chapter_title=ROADCODE2 路线编码 2 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 10 ROADCODE2 路线编码 2 Text（50） 条件必填 /

<!-- chapter_no=11; chapter_title=ROADCODE3 路线编码 3 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 11 ROADCODE3 路线编码 3 Text（50） 条件必填 /

<!-- chapter_no=12; chapter_title=ROADCODE4 路线编码 4 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 12 ROADCODE4 路线编码 4 Text（50） 条件必填 /

<!-- chapter_no=13; chapter_title=FWIDTH 宽度 Double 条件必填 /; knowledge_type=chapter_title -->
# 13 FWIDTH 宽度 Double 条件必填 /

<!-- chapter_no=14; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 14 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=15; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 15 UPDATETIME 现势性 Text（14） 必填 /

表 7 高铁、地铁、普通铁路等图层属性结构表

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=FNAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 FNAME 名称 Text（50） 条件必填 /

<!-- chapter_no=3; chapter_title=ROADCODE 路线编码 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 3 ROADCODE 路线编码 Text（50） 条件必填 /

<!-- chapter_no=4; chapter_title=FDESC 描述 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 4 FDESC 描述 Text（50） 条件必填 /

<!-- chapter_no=5; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 5 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=6; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 6 UPDATETIME 现势性 Text（14） 必填 /

表 8 附属设施、民用机场等图层属性结构表

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=FNAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 FNAME 名称 Text（50） 条件必填 /

<!-- chapter_no=3; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 3 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=4; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 4 UPDATETIME 现势性 Text（14） 必填 /

<!-- chapter_no=5.3; chapter_title=居民地数据集; knowledge_type=chapter_title -->
## 5.3 居民地数据集

居民地数据集主要包含乡级以上政府、 学校、 医院等3 个图层。 各图层属性结构如表9。

表 9 乡级以上政府、学校、医院等图层属性结构

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=FNAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 FNAME 名称 Text（50） 条件必填 /

<!-- chapter_no=3; chapter_title=FTYPE 类别（级别） Text（50） 条件必填; knowledge_type=chapter_title -->
# 3 FTYPE 类别（级别） Text（50） 条件必填

主要填写点要素所属的类别，如

政府要素填写 “乡级” “县级” 等，

医院要素填写“一级甲等”等，

学校填写“小学” “中学”等。

<!-- chapter_no=4; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 4 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=5; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 5 UPDATETIME 现势性 Text（14） 必填 /

<!-- chapter_no=5.4; chapter_title=境界数据集; knowledge_type=chapter_title -->
## 5.4 境界数据集

境界数据集主要包含省级境界、 地级境界、 县级境界、 乡级境界等4 个图层。各图层属

性结构如表10。

表 10 境界数据集图层属性结构

序号 字段名 字段中文名 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=FCODE 分类代码 Text（50） 必填 /; knowledge_type=chapter_title -->
# 1 FCODE 分类代码 Text（50） 必填 /

<!-- chapter_no=2; chapter_title=NAME 名称 Text（50） 条件必填 /; knowledge_type=chapter_title -->
# 2 NAME 名称 Text（50） 条件必填 /

<!-- chapter_no=3; chapter_title=USOURCE 更新源 Text（50） 必填 /; knowledge_type=chapter_title -->
# 3 USOURCE 更新源 Text（50） 必填 /

<!-- chapter_no=4; chapter_title=UPDATETIME 现势性 Text（14） 必填 /; knowledge_type=chapter_title -->
# 4 UPDATETIME 现势性 Text（14） 必填 /

<!-- chapter_no=6; chapter_title=数据处理; section_type=数据库; knowledge_type=data_spec -->
# 6 数据处理

<!-- section_type=数据库; knowledge_type=data_spec -->
以 1∶10000 基础地理信息、天地图等数据为主要数据源构建，以 1∶500 及 1∶2000

<!-- section_type=数据库; knowledge_type=data_spec -->
基础地理信息、 城市国土空间监测、 收集的知识名录等数据为补充， 辅助验证重大要素正确

<!-- section_type=数据库; knowledge_type=data_spec -->
性、 完整性及现势性。 数据处理技术流程主要包含数据源搜集及整理、 重大要素筛选及提取、

<!-- section_type=数据库; knowledge_type=data_spec -->
重大要素检查及补充、数据入库等四个环节，技术流程如图1。

<!-- section_type=数据库; knowledge_type=data_spec -->
图 1 技术流程图

<!-- chapter_no=6.1; chapter_title=数据源收集及整理; section_type=数据库; knowledge_type=data_spec -->
## 6.1 数据源收集及整理

<!-- section_type=数据库; knowledge_type=data_spec -->
数据源分为主要数据源和辅助数据源。

<!-- section_type=数据库; knowledge_type=data_spec -->
主要数据源包含1∶10000 基础地理信息和天地图数据。主要数据源为必要数据，收集

<!-- section_type=数据库; knowledge_type=data_spec -->
时应注意数据源的完整性、 现势性和有效性。 同时， 在收集成果数据时应注意收集与成果相

<!-- section_type=数据库; knowledge_type=field_rule -->
对应的分类代码表。

<!-- section_type=数据库; knowledge_type=data_spec -->
辅助数据源主要为1∶500 及 1∶2000 基础地理信息、城市国土空间监测、收集的知识

<!-- section_type=数据库; knowledge_type=data_spec -->
名录等相关数据。辅助数据源为非必要数据， 秉持 “应收尽收”原则，收集时应注意数据源

<!-- section_type=数据库; knowledge_type=data_spec -->
的现势性、 有效性和权威性。 其中， 知识名录主要为相关行政主管部门或新闻媒体发布的与

<!-- section_type=数据库; knowledge_type=data_spec -->
重大要素相关且具有权威性的信息。 同时， 在收集成果数据时应注意收集与成果相对应的分

<!-- section_type=数据库; knowledge_type=field_rule -->
类代码表。

<!-- section_type=数据库; knowledge_type=data_spec -->
数据源完成收集后应按类别进行整理归类。

<!-- chapter_no=6.2; chapter_title=重要要素筛选及提取; section_type=数据库; knowledge_type=data_spec -->
## 6.2 重要要素筛选及提取

<!-- section_type=数据库; knowledge_type=data_spec -->
根据重要要素库中确定各类要素内容，结合1∶10000 基础地理信息等主要数据源的分

<!-- section_type=数据库; knowledge_type=field_rule -->
类代码表， 清洗、 筛选形成相应的重大要素分类代码表。 根据重大要素分类代码表从主要数

<!-- section_type=数据库; knowledge_type=data_spec -->
据源中对依次对各类别重大要素开展筛选及提取工作， 按数据集进行归类整理， 形成重要要

<!-- section_type=数据库; knowledge_type=data_spec -->
素库底版。

<!-- chapter_no=6.3; chapter_title=重要要素检查及补充; section_type=数据库; knowledge_type=data_spec -->
## 6.3 重要要素检查及补充

<!-- section_type=数据库; knowledge_type=data_spec -->
基于 1∶500 及 1∶2000 基础地理信息、城市国土空间监测、收集的知识名录等相关数

<!-- section_type=数据库; knowledge_type=data_spec -->
据，套合相关高分辨率影像数据，对筛选及提取形成的重要要素库中的重大要素的正确性、

<!-- section_type=数据库; knowledge_type=data_spec -->
完整性及现势性进行检查、 修正和补充， 如个别重大要素漏采集或辅助要素现势性更强， 则

<!-- section_type=数据库; knowledge_type=data_spec -->
对底版数据进行补采集或更新； 如个别重大要素属性与权威属性不一致或漏填写， 则根据权

<!-- section_type=数据库; knowledge_type=data_spec -->
威数据进行属性补充等。

<!-- chapter_no=6.4; chapter_title=数据映射入库; section_type=数据库; knowledge_type=data_spec -->
## 6.4 数据映射入库

<!-- section_type=数据库; knowledge_type=field_rule -->
根据重要要素库数据结构及图层属性结构要求构建重要要素标准库； 同时， 根据底版库

<!-- section_type=数据库; knowledge_type=field_rule -->
与标准库之间的图层与字段的映射关系， 制作数据映射关系表， 实现底版库到标准库的数据

<!-- section_type=数据库; knowledge_type=data_spec -->
映射及入库，并对标准库数据进行检查和核实。

<!-- chapter_no=7; chapter_title=数据更新; section_type=数据整理; knowledge_type=data_spec -->
# 7 数据更新

<!-- section_type=数据整理; knowledge_type=data_spec -->
为更好的保证质检大数据支撑库重要要素数据的现势性、 正确性及完整性， 宜安排专门

<!-- section_type=数据整理; knowledge_type=data_spec -->
人员定期对数据库开展治理及更新工作。 数据更新方式主要包含数据源定期比对、 更新信息

<!-- section_type=数据整理; knowledge_type=data_spec -->
定期搜集、质检工作日常发现等三种。

<!-- chapter_no=7.1; chapter_title=数据源定期比对; section_type=数据整理; knowledge_type=data_spec -->
## 7.1 数据源定期比对

<!-- section_type=数据整理; knowledge_type=data_spec -->
根据 1∶10000 基础地理信息和天地图数据等主要数据源的更新频率和更新变化信息，

<!-- section_type=数据整理; knowledge_type=data_spec -->
定期对重要要素库中的重大要素进行比对分析， 对已经发生变化的要素进行更新补充， 并填

<!-- section_type=数据整理; knowledge_type=data_spec -->
写更新要素的现势性信息。数据源比对更新频次一般以一个季度为周期。

<!-- chapter_no=7.2; chapter_title=更新信息定期搜集; section_type=数据整理; knowledge_type=data_spec -->
## 7.2 更新信息定期搜集

<!-- section_type=数据整理; knowledge_type=data_spec -->
根据信息化检索技术定期从网络上检索与重大要素相关的新闻报道等权威信息， 专员定

<!-- section_type=数据整理; knowledge_type=data_spec -->
期对信息进行清理、核实及整理汇编，对核实无误的信息按一定周期更新至重要要素库中。

<!-- section_type=数据整理; knowledge_type=data_spec -->
更新信息定期搜集更新周期一般以一个月为周期。

<!-- chapter_no=7.3; chapter_title=质检工作日常发现; section_type=数据整理; knowledge_type=data_spec -->
## 7.3 质检工作日常发现

<!-- section_type=数据整理; knowledge_type=field_rule -->
技术人员在开展日常的质检工作中发现的重大要素变化信息应按相应格式登记或提取

<!-- section_type=数据整理; knowledge_type=data_spec -->
变化信息矢量数据， 定期汇交至数据库管理专员， 有专员对变化信息核实后更新入库。 质检

<!-- section_type=数据整理; knowledge_type=data_spec -->
工作日常发现更新周期一般以一个月为周期。

<!-- chapter_no=8; chapter_title=检查方法; section_type=质量要求; knowledge_type=quality_rule -->
# 8 检查方法

<!-- section_type=质量要求; knowledge_type=quality_rule -->
质检大数据支撑库重要要素库主要应用于对受检成果中重大要素的快速检查， 以提升质

<!-- section_type=质量要求; knowledge_type=data_spec -->
检工作效率和保障成果质量。重要要素库的应用方式主要有人工套合比对和软件自动比对两

<!-- section_type=质量要求; knowledge_type=data_spec -->
种应用路径。

<!-- chapter_no=8.1; chapter_title=人工套合检查; section_type=质量要求; knowledge_type=quality_rule -->
## 8.1 人工套合检查

<!-- section_type=质量要求; knowledge_type=quality_rule -->
人工套合检查方式主要由技术人员在检查时， 将重要要素库数据加载到相应的地理信息

<!-- section_type=质量要求; knowledge_type=quality_rule -->
软件中，与待检成果开展比对分析，检查待检成果中重大要素更新的完整性、正确性。

<!-- chapter_no=8.2; chapter_title=软件自动比对; section_type=质量要求; knowledge_type=data_spec -->
## 8.2 软件自动比对

<!-- section_type=质量要求; knowledge_type=quality_rule -->
软件自动比对方式主要由自动化检查软件以重要要素库中的重重大要素为参考数据， 对

<!-- section_type=质量要求; knowledge_type=quality_rule -->
待检成果开展位置比对分析或属性比对分析， 以检查同名位置的重大要素更新的完整性及属

<!-- section_type=质量要求; knowledge_type=data_spec -->
性的正确性。

<!-- section_type=质量要求; knowledge_type=data_spec -->
参 考 文 献

<!-- section_type=质量要求; knowledge_type=data_spec -->
[1]浙江省1∶10000 比例尺基础地理信息数据更新（2024 年）技术设计书
