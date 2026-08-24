# 实景三维质检大数据支撑库 时空数据规范 第6部分 高精度栅格数据

> 来源：实景三维质检大数据支撑库 时空数据规范 第6部分 高精度栅格数据.pdf（增强版提取，已去目录/页眉/页码噪声）


第 6 部分 高精度栅格数据

（草案）

2025 年 7 月

I

目  次

II

前 言

本文件按照GB/T 1.1—2020《标准化工作导则  第1部分：标准化文件的结构和起草规则》的规定

起草。

第1部分 数据分类与基本规定

第2部分 检测点

第3部分 检测线

第4部分 标准性地物

第5部分 重要要素

第7部分 资源数据

请注意本文件的某些内容可能涉及专利。本文件的发布机构不承担识别专利的责任。

起草单位：

起草人员：

<!-- chapter_no=1; chapter_title=范围; section_type=范围; knowledge_type=scope_intro -->
# 1 范围

<!-- section_type=范围; knowledge_type=scope_intro -->
本规程给出了质检大数据支撑库中资源库的数据的一般规定， 规定了资源库数据的数据类型、字段

<!-- section_type=范围; knowledge_type=scope_intro -->
名称、数据项以及数据组织形式。

<!-- section_type=范围; knowledge_type=scope_intro -->
本规程适用于质检大数据支撑库资源库数据获取、处理、整合、建库、更新和服务。

<!-- chapter_no=2; chapter_title=规范性引用文件; section_type=引用文件; knowledge_type=references -->
# 2 规范性引用文件

<!-- section_type=引用文件; knowledge_type=references -->
下列文件对于本文件的应用是必不可少的。 凡是注日期的引用文件， 仅所注日期的版本适用于本文

<!-- section_type=引用文件; knowledge_type=references -->
件。凡是不注日期的引用文件，其最新版本（包括所有的修改单）适用于本文件。

<!-- chapter_no=3; chapter_title=术语和定义; section_type=术语定义; knowledge_type=term_definition -->
# 3 术语和定义

<!-- chapter_no=3; chapter_title=1; section_type=术语定义; knowledge_type=term_definition -->
# 3 1

<!-- section_type=术语定义; knowledge_type=term_definition -->
栅格数据 raster data

<!-- section_type=术语定义; knowledge_type=term_definition -->
将地理空间划分成按行、列规则排列的单元，且各单元带有不同“值”的数据集

<!-- section_type=术语定义; knowledge_type=term_definition -->
[来源：GB/T 14911-2008 ]

<!-- chapter_no=4; chapter_title=数据内容; section_type=术语定义; knowledge_type=term_definition -->
# 4 数据内容

<!-- section_type=术语定义; knowledge_type=term_definition -->
数据内容由数栅格数据及其元数据组成。

<!-- section_type=术语定义; knowledge_type=term_definition -->
——栅格数据。栅格数据作为按文件进行存储和管理。

<!-- section_type=术语定义; knowledge_type=term_definition -->
——元数据是数据的说明文件，采用空间元数据形式进行存储和管理，以矢量面表示数据集范围，

<!-- section_type=术语定义; knowledge_type=term_definition -->
以属性信息记录数据集的来源、质量、管理等信息。

<!-- chapter_no=5; chapter_title=基本要求; section_type=术语定义; knowledge_type=term_definition -->
# 5 基本要求

<!-- chapter_no=5.1; chapter_title=影像数据要求; section_type=术语定义; knowledge_type=term_definition -->
## 5.1 影像数据要求

<!-- section_type=术语定义; knowledge_type=term_definition -->
高精度影像数据要求如下：

<!-- section_type=术语定义; knowledge_type=term_definition -->
——分辨率优于2米；

<!-- section_type=术语定义; knowledge_type=term_definition -->
——位置精度优化于5米；

<!-- section_type=术语定义; knowledge_type=term_definition -->
——区域特征稳定，特征易识别。

<!-- chapter_no=5.2; chapter_title=数字高程模型要求; section_type=术语定义; knowledge_type=term_definition -->
## 5.2 数字高程模型要求

<!-- section_type=术语定义; knowledge_type=term_definition -->
高精度数字高程模型数据要求：

<!-- section_type=术语定义; knowledge_type=term_definition -->
——分辨率优于5米；

<!-- section_type=术语定义; knowledge_type=term_definition -->
——位置精度优化于5米；

<!-- section_type=术语定义; knowledge_type=term_definition -->
——地形地貌特征稳定。

<!-- chapter_no=5.3; chapter_title=文件格式; section_type=术语定义; knowledge_type=term_definition -->
## 5.3 文件格式

<!-- chapter_no=5.3.1; chapter_title=影像数据; section_type=术语定义; knowledge_type=term_definition -->
### 5.3.1 影像数据

<!-- section_type=术语定义; knowledge_type=term_definition -->
影像数据一般采用ERDAS IMG、TIFF World等常用格式。

<!-- chapter_no=5.3.2; chapter_title=数字高程模型; section_type=术语定义; knowledge_type=term_definition -->
### 5.3.2 数字高程模型

<!-- section_type=术语定义; knowledge_type=term_definition -->
数字高程模型一般采用img、ASCII Grid等常用格式。

<!-- chapter_no=5.3.3; chapter_title=空间元数据文件; section_type=术语定义; knowledge_type=term_definition -->
### 5.3.3 空间元数据文件

<!-- section_type=术语定义; knowledge_type=term_definition -->
空间元数据文件采用Shape Files、Personal Geodatabase或File Geodatabase格式的面文件。

<!-- chapter_no=6; chapter_title=元数据属性结构; section_type=术语定义; knowledge_type=term_definition -->
# 6 元数据属性结构

<!-- section_type=术语定义; knowledge_type=term_definition -->
元数据属性结构见表1。

<!-- section_type=术语定义; knowledge_type=term_definition -->
表1 元数据属性结构

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束

<!-- section_type=术语定义; knowledge_type=term_definition -->
条件 备注

<!-- chapter_no=1; chapter_title=ID 数据 id 字符型 M  2  Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据 id 字符型 M  2  Datum_Geodetic 大地基准 字符型 M

<!-- chapter_no=3; chapter_title=Datum_ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 Datum_ele 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- chapter_no=5; chapter_title=cntMerdian 中央经线 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 cntMerdian 中央经线 双精度浮点型 M

<!-- chapter_no=6; chapter_title=PixelWidth 像元宽度 浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 6 PixelWidth 像元宽度 浮点型 O

<!-- chapter_no=7; chapter_title=PixelHeight 像元高度 浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 7 PixelHeight 像元高度 浮点型 O

<!-- chapter_no=8; chapter_title=RowsNum 行总数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 8 RowsNum 行总数 整型 O

<!-- chapter_no=9; chapter_title=ColumnsNum 列总数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 9 ColumnsNum 列总数 整型 O

<!-- chapter_no=10; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 10 AdminRegion 所属行政区划 字符型 M

<!-- chapter_no=11; chapter_title=SheetNumber 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 11 SheetNumber 分幅号 字符型 M

<!-- chapter_no=12; chapter_title=DOM\DEM 数据类型 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 12 DOM\DEM 数据类型 字符型 M

<!-- chapter_no=13; chapter_title=FilePath 文件路径/存储地址 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 13 FilePath 文件路径/存储地址 字符型 M

<!-- chapter_no=14; chapter_title=DateName 数据名称 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 14 DateName 数据名称 字符型 M

<!-- chapter_no=15; chapter_title=ThumbnailName 缩略图名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 15 ThumbnailName 缩略图名称 字符型 O

<!-- chapter_no=16; chapter_title=ImageSource 影像来源类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 16 ImageSource 影像来源类型 字符型 O

<!-- chapter_no=17; chapter_title=BandsNum 波段数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 17 BandsNum 波段数 整型 O

<!-- chapter_no=18; chapter_title=DepthType 位深类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 18 DepthType 位深类型 字符型 O

<!-- chapter_no=19; chapter_title=InvalidValue 无效值 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 InvalidValue 无效值 整型 O

<!-- chapter_no=20; chapter_title=EffectiveArea 有效面积 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 20 EffectiveArea 有效面积 双精度浮点型 O

<!-- chapter_no=21; chapter_title=LeftUpper x 四至左上角 x 坐标 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 21 LeftUpper x 四至左上角 x 坐标 双精度浮点型 O

<!-- chapter_no=22; chapter_title=LeftUpper y 四至左上角 y 坐标 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 22 LeftUpper y 四至左上角 y 坐标 双精度浮点型 O

<!-- chapter_no=23; chapter_title=LowerRight x 四至右下角 x 坐标 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 23 LowerRight x 四至右下角 x 坐标 双精度浮点型 O

<!-- chapter_no=24; chapter_title=LowerRight y 四至右下角 y 坐标 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 24 LowerRight y 四至右下角 y 坐标 双精度浮点型 O

<!-- chapter_no=25; chapter_title=Accy_H 高程精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 25 Accy_H 高程精度 双精度浮点型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束

<!-- section_type=术语定义; knowledge_type=term_definition -->
条件 备注

<!-- chapter_no=26; chapter_title=Accy_V 平面精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 26 Accy_V 平面精度 双精度浮点型 M

<!-- chapter_no=27; chapter_title=QuaData 数据质量 字符型 O 分 数 / 质; section_type=术语定义; knowledge_type=term_definition -->
# 27 QuaData 数据质量 字符型 O 分 数 / 质

<!-- section_type=术语定义; knowledge_type=term_definition -->
量等级

<!-- chapter_no=28; chapter_title=QuaDescri 质量问题描述 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 28 QuaDescri 质量问题描述 字符型 O

<!-- chapter_no=29; chapter_title=Program 所属项目 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 29 Program 所属项目 字符型 M

<!-- chapter_no=30; chapter_title=Producer 数据来源或生产（更新）; section_type=术语定义; knowledge_type=term_definition -->
# 30 Producer 数据来源或生产（更新）

<!-- section_type=术语定义; knowledge_type=term_definition -->
单位全称 字符型 O

<!-- chapter_no=31; chapter_title=DataDate 数据源时间 字符型 O YYYYMMDD; section_type=术语定义; knowledge_type=term_definition -->
# 31 DataDate 数据源时间 字符型 O YYYYMMDD

<!-- chapter_no=32; chapter_title=DataAvaila 数据可用性 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 32 DataAvaila 数据可用性 字符型 O

<!-- chapter_no=33; chapter_title=Userid 数据处理人员 整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 33 Userid 数据处理人员 整型 M

<!-- chapter_no=34; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 34 Notes 备注 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
注：

<!-- section_type=术语定义; knowledge_type=term_definition -->
（1）M 代表必填字段，O 代表选填字段；

<!-- section_type=术语定义; knowledge_type=term_definition -->
（2）像元宽度、像元高度单元为米，指地面分辨率。

<!-- section_type=术语定义; knowledge_type=term_definition -->
（3）数据可用性值“可用”“作废”

<!-- section_type=术语定义; knowledge_type=term_definition -->
参考文献

<!-- section_type=术语定义; knowledge_type=term_definition -->
[1] GB/T 39608—2020 基础地理信息数字成果元数据

<!-- section_type=术语定义; knowledge_type=term_definition -->
[2] CHT 1007—2001 基础地理信息数字产品元数据
