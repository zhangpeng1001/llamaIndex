# 实景三维质检大数据支撑库 时空数据规范 第3部分 检测线

> 来源：实景三维质检大数据支撑库 时空数据规范 第3部分 检测线.pdf（增强版提取，已去目录/页眉/页码噪声）


第 3 部分 检测线

（草案）

2025 年7 月

前 言

本文件按照GB/T 1.1—2020《标准化工作导则  第1部分：标准化文件的结构和起草规

则》的规定起草。

第1部分 数据分类和基本规定

第2部分 检测点

第4部分 标志性地物

第5部分 重要要素

第6部分 高精度栅格数据

第7部分 资源数据

请注意本文件的某些内容可能涉及专利。本文件的发布机构不承担识别专利的责任。

起草单位：

起草人员：

II

引 言

为满足实景三维中国建设项目成果质量检验的快速响应需求， 同时适应大数

据、 人工智能等新技术的飞速发展对高可靠、 高更新频次质检参考数据的要求，

探索构建基于车载激光扫描技术或机载航摄技术采集的检测线数据库，规范检

测线数据的结构和内容，同时充分利用已有时空信息数据，探索数据收集、整

理、质检、建库应用于更新体系化建设，实现实景三维质检工作效率和成果质

量的提高，开展质检大数据支撑库检测线子库建设，建设方案如下。

<!-- chapter_no=1; chapter_title=范围; section_type=范围; knowledge_type=scope_intro -->
# 1 范围

<!-- section_type=范围; knowledge_type=scope_intro -->
入库流程、数据更新、共享应用、成果提交等。

<!-- chapter_no=2; chapter_title=技术依据; knowledge_type=chapter_title -->
# 2 技术依据

<!-- chapter_no=3; chapter_title=术语和定义; section_type=术语定义; knowledge_type=term_definition -->
# 3 术语和定义

<!-- section_type=术语定义; knowledge_type=term_definition -->
下列术语和定义适用于本文件。

<!-- chapter_no=3; chapter_title=1; knowledge_type=chapter_title -->
# 3 1

检测线

为进行实景三维空间地理信息成果位置精度检测，基于 车载激光扫描技术

或机载航摄技术采集的线状特征，包括：建筑物水平特征检测线、建筑物垂直

特征检测线、杆状物检测线、路面漆检测线、路边线检测网。

<!-- chapter_no=3; chapter_title=2; knowledge_type=chapter_title -->
# 3 2

建筑物水平特征检测线

沿着建筑物水平方向采集的线状特征，包括：建筑物外轮廓水平特征线、

建筑物门窗水平特征线、围墙水平特征线。

<!-- chapter_no=3; chapter_title=3; knowledge_type=chapter_title -->
# 3 3

建筑物垂直特征检测线

沿着建筑物水垂直向采集的线状特征，包括：建筑物外轮廓垂直特征线、

建筑物门窗垂直特征线、围墙垂直特征线。

<!-- chapter_no=3; chapter_title=4; knowledge_type=chapter_title -->
# 3 4

杆状物检测线

基于车载激光扫描技术采集的路边杆状物垂直特征， 包括： 路灯、电杆、 标

识牌等。

<!-- chapter_no=3; chapter_title=5; knowledge_type=chapter_title -->
# 3 5

路面漆检测线

基于车载激光扫描技术或机载航摄技术采集的路面漆范围线。

<!-- chapter_no=3; chapter_title=6; knowledge_type=chapter_title -->
# 3 6

路边线检测网

基于车载激光扫描技术或机载航摄技术采集的路边线，高密度时构成检测

网。

<!-- chapter_no=4; chapter_title=入库前数据要求; knowledge_type=chapter_title -->
# 4 入库前数据要求

<!-- chapter_no=4.1; chapter_title=空间参考; knowledge_type=chapter_title -->
## 4.1 空间参考

检测线数据应采用国家规定的、 统一的地理空间参考系， 应满足下列要求：

a) 大地基准为 2000 国家大地坐标系，或采用依法批准的独立坐标系。

b) 高程基准为 1985 国家高程基准。

c) 投影采用高斯-克吕格投影，3°分带，加带号。

<!-- chapter_no=4.2; chapter_title=时间参考; knowledge_type=chapter_title -->
## 4.2 时间参考

日期应采用公历纪元，时间应采用北京时间。

<!-- chapter_no=4.3; chapter_title=数学精度; knowledge_type=chapter_title -->
## 4.3 数学精度

检测线的平面位置精度应达到 1:1000 地形图平面精度要求， 高程精度应达

到1:2000 地形图平地丘陵地高程精度要求。

<!-- chapter_no=4.4; chapter_title=属性精度; knowledge_type=chapter_title -->
## 4.4 属性精度

检测线数据属性表结构、 属性项内容名称及值域等应符合表1 至表 6 填写要

求，各地可结合实景三维成果质量检验要求，扩展属性项。

<!-- chapter_no=4.5; chapter_title=存储格式; knowledge_type=chapter_title -->
## 4.5 存储格式

检测线文件以*.shap 或*.mdb 文件方式存储， 检测数据按特征类别命名文件

夹， 建筑物水平特征检测线、 建筑物垂直特征检测线、 电杆检测线、 路灯检测线、

路面漆检测线、路边线检测网数据。

实地照片数据可采用 JPG、TIF 数据格式。

<!-- chapter_no=5; chapter_title=检测线数据库结构; knowledge_type=chapter_title -->
# 5 检测线数据库结构

质检大数据支撑库检测线子库数据以*.gdb 格式存储， 检测数据按特征类别

划分不同图层， 包括： 建筑物水平特征检测线、 建筑物垂直特征检测线、 电杆检

测线、 路灯检测线、 路面漆检测线、 路边线检测网。 各图层数据结构见表1 至表

6。

表1 建筑物水平特征检测线属性结构表

建筑物水平特征检测线属性结构表

序

号

字段名

称 字段代码 字段类型 字段

长度

小数

位数 值域 约束/条

件 备注

<!-- chapter_no=1; chapter_title=检测线; knowledge_type=chapter_title -->
# 1 检测线

编号 jiancexianbianhao 字符型 20 — — M 见注2

<!-- chapter_no=2; chapter_title=端点纬; knowledge_type=chapter_title -->
# 2 端点纬

度值 duandian_B 双精度型 — 9 DD.DDDDD

DDDD M 见注3

<!-- chapter_no=3; chapter_title=端点经; knowledge_type=chapter_title -->
# 3 端点经

度值 duandian_L 双精度型 — 9 DDD.DDDD

DDDDD M 见注4

<!-- chapter_no=4; chapter_title=端点大; knowledge_type=chapter_title -->
# 4 端点大

地高 duandian_H 双精度型 — 3 — M 见注5

<!-- chapter_no=5; chapter_title=结点纬; knowledge_type=chapter_title -->
# 5 结点纬

度值 jiedian_B 双精度型 — 9 DD.DDDDD

DDDD M 见注3

6 结点经 jiedian_L 双精度型 — 9 DDD.DDDD M 见注4

度值 DDDDD

<!-- chapter_no=7; chapter_title=结点大; knowledge_type=chapter_title -->
# 7 结点大

地高 jiedian_H 双精度型 — 3 — M 见注5

<!-- chapter_no=8; chapter_title=端点北; knowledge_type=chapter_title -->
# 8 端点北

坐标 duandian_X 双精度型 — 3 ≥0 M 见注6

<!-- chapter_no=9; chapter_title=端点东; knowledge_type=chapter_title -->
# 9 端点东

坐标 duandian_Y 双精度型 — 3 ≥0 M 见注7

<!-- chapter_no=10; chapter_title=端点高; knowledge_type=chapter_title -->
# 10 端点高

程 duandian_H85 双精度型 — 3 — M 见注8

<!-- chapter_no=11; chapter_title=结点北; knowledge_type=chapter_title -->
# 11 结点北

坐标 jiedian_X 双精度型 — 3 ≥0 M 见注6

<!-- chapter_no=12; chapter_title=结点东; knowledge_type=chapter_title -->
# 12 结点东

坐标 jiedian_Y 双精度型 — 3 ≥0 M 见注7

<!-- chapter_no=13; chapter_title=结点高; knowledge_type=chapter_title -->
# 13 结点高

程 jiedian_H85 双精度型 — 3 — M 见注8

<!-- chapter_no=14; chapter_title=85 高高; knowledge_type=chapter_title -->
# 14 85 高高

程均值 junzhi_H85 双精度型 — 3 — M 见注8

<!-- chapter_no=15; chapter_title=中央子; knowledge_type=chapter_title -->
# 15 中央子

午线 ZYZWX 双精度型 — — ≥0 M 见注 10

<!-- chapter_no=16; chapter_title=投影面; knowledge_type=chapter_title -->
# 16 投影面

高程 h0 双精度型 — 3 — O 见注 11

<!-- chapter_no=17; chapter_title=地物代; knowledge_type=chapter_title -->
# 17 地物代

码 DWDM 字符型 15 —

JZWWLK_S

PTZX、

JZWMC_SP

TZX、

WQ_SPTZX

M 见注 12

<!-- chapter_no=18; chapter_title=地物名; knowledge_type=chapter_title -->
# 18 地物名

称 DWMC 字符型 30 —

建筑物外

轮廓水平

特征线、

建筑物门

窗水平特

征线、围

墙水平特

征线

M 见注 13

<!-- chapter_no=19; chapter_title=高程精; knowledge_type=chapter_title -->
# 19 高程精

度水平 GCJDSP 双精度型 — 2 ≥0 M 见注 14

<!-- chapter_no=20; chapter_title=采集方; knowledge_type=chapter_title -->
# 20 采集方

式 CJFS 字符型 20 —

车载激光

雷达实

测、机载

激光雷达

实测、

MESH 模型

内业采集

M 见注 15

表2 建筑物垂直特征检测线属性结构表

<!-- chapter_no=21; chapter_title=实地照; knowledge_type=chapter_title -->
# 21 实地照

片 ZP 字符型 254 — — O 见注 16

<!-- chapter_no=22; chapter_title=采集日; knowledge_type=chapter_title -->
# 22 采集日

期 RQ 日期型 — — YYYY/MM/

DD M 见注 17

<!-- chapter_no=23; chapter_title=行政区; knowledge_type=chapter_title -->
# 23 行政区

代码 XZQDM 整型 10 — — M 见注 18

<!-- chapter_no=24; chapter_title=是否可; knowledge_type=chapter_title -->
# 24 是否可

用 SFKY 字符型 254 — — O 见注 19

<!-- chapter_no=25; chapter_title=备注 BZ 字符型 254 — — O; knowledge_type=chapter_title -->
# 25 备注 BZ 字符型 254 — — O

注 1：约束/条件：“M”为必选项，即必须填写的信息；“C”为条件必选项，即满足某一条件或要求时

必须填写的信息；“O”为可选项，可根据实际情况选择填写。

注 2：进行全库统一编码。

注 3：检测线端点、结点纬度地理坐标，单位为“度”，小数点后保留有效位数 9 位。

注 4：检测线端点、结点纬度地理坐标，单位为“度”，小数点后保留有效位数 9 位。

注 5：检测线端点、结点的大地高，单位：米，保留 3 位小数。

注 6：检测线端点、结点北坐标（投影平面 x 坐标），单位：米，保留 3 位小数。

注 7：检测线端点、结点东坐标（投影平面 y 坐标），单位：米，保留 3 位小数。

注 8：检测线端点、结点的 85 高程，单位：米，保留 3 位小数。

注 9：检测线端点与结点的平均 85 高程，单位：米，保留 3 位小数。

注 10：中央子午线，根据检测线实际的中央子午线填写。

注 11：投影面高程，根据检测线实际的投影面高程填写。

注 12：检测地物代码，以 3 位代码表示，取值见附录 B.1。

注 13：地物名称，采集地物的名称，取值见附录 B.1。

注 14： 经评估的高程精度水平， 该检测线能用来进行高精度检测的最高高程中误差水平， 单位： 米。 如：

0.15 米、0.25 米、0.5 米、1 米等。

注 15：车载激光雷达实测、机载激光雷达实测、MESH 模型内业采集等。

注 16：存储实地照片文件所在的物理路径及文件名，当文件名不存在时此项为空。

注 17：属性值域为“YYYY/MM/DD”表示日期，其中“Y”表示年份，“M”表示月份，“D”表示日，不

足位的用 0 补足，例如“2024/03/06”。

注 18：填写该检测点所属县级行政区代码。

注 19：记录检测点是否可用状态，如当检测点对应地物发生变化时，说明变化状态。

建筑物垂直特征检测线属性结构表

序

号 字段名称 字段代码 字段

类型

字段

长度

小数

位数 值域 约束/

条件 备注

<!-- chapter_no=1; chapter_title=检测线编; knowledge_type=chapter_title -->
# 1 检测线编

号

jiancexianbian

hao

字符

型 20 — — M 见注2

<!-- chapter_no=2; chapter_title=端点纬度; knowledge_type=chapter_title -->
# 2 端点纬度

值 duandian_B 双精

度型 — 9 DD.DDDDDDD

DD M 见注3

<!-- chapter_no=3; chapter_title=端点经度; knowledge_type=chapter_title -->
# 3 端点经度

值 duandian_L 双精

度型 — 9 DDD.DDDDDD

DDD M 见注4

<!-- chapter_no=4; chapter_title=端点大地; knowledge_type=chapter_title -->
# 4 端点大地

高 duandian_H 双精

度型 — 3 — M 见注5

<!-- chapter_no=5; chapter_title=结点纬度; knowledge_type=chapter_title -->
# 5 结点纬度

值 jiedian_B 双精

度型 — 9 DD.DDDDDDD

DD M 见注3

<!-- chapter_no=6; chapter_title=结点经度; knowledge_type=chapter_title -->
# 6 结点经度

值 jiedian_L 双精

度型 — 9 DDD.DDDDDD

DDD M 见注4

<!-- chapter_no=7; chapter_title=结点大地; knowledge_type=chapter_title -->
# 7 结点大地

高 jiedian_H 双精

度型 — 3 — M 见注5

<!-- chapter_no=8; chapter_title=端点北坐; knowledge_type=chapter_title -->
# 8 端点北坐

标 duandian_X 双精

度型 — 3 ≥0 M 见注6

<!-- chapter_no=9; chapter_title=端点东坐; knowledge_type=chapter_title -->
# 9 端点东坐

标 duandian_Y 双精

度型 — 3 ≥0 M 见注7

<!-- chapter_no=10; chapter_title=端点高程 duandian_H85 双精; knowledge_type=chapter_title -->
# 10 端点高程 duandian_H85 双精

度型 — 3 — M 见注8

<!-- chapter_no=11; chapter_title=结点北坐; knowledge_type=chapter_title -->
# 11 结点北坐

标 jiedian_X 双精

度型 — 3 ≥0 M 见注6

<!-- chapter_no=12; chapter_title=结点东坐; knowledge_type=chapter_title -->
# 12 结点东坐

标 jiedian_Y 双精

度型 — 3 ≥0 M 见注7

<!-- chapter_no=13; chapter_title=结点高程 jiedian_H85 双精; knowledge_type=chapter_title -->
# 13 结点高程 jiedian_H85 双精

度型 — 3 — M 见注8

<!-- chapter_no=14; chapter_title=检测线北; knowledge_type=chapter_title -->
# 14 检测线北

坐标均值 junzhi_X 双精

度型 — 3 — M 见注9

<!-- chapter_no=15; chapter_title=检测线东; knowledge_type=chapter_title -->
# 15 检测线东

坐标均值 junzhi_Y 双精

度型 — 3 — M 见注9

<!-- chapter_no=16; chapter_title=中央子午; knowledge_type=chapter_title -->
# 16 中央子午

线 ZYZWX 双精

度型 — — ≥0 M 见注10

<!-- chapter_no=17; chapter_title=投影面高; knowledge_type=chapter_title -->
# 17 投影面高

程 h0 双精

度型 — 3 — O 见注11

<!-- chapter_no=18; chapter_title=地物代码 DWDM 字符; knowledge_type=chapter_title -->
# 18 地物代码 DWDM 字符

型 15 —

JZWWLK_CZT

ZX、

JZWMC_CZTZ

X、WQ_CZTZX

M 见注12

<!-- chapter_no=19; chapter_title=地物名称 DWMC 字符; knowledge_type=chapter_title -->
# 19 地物名称 DWMC 字符

型 30 —

建筑物外轮

廓垂直特征

线、建筑物

门窗垂直特

征线、围墙

垂直特征线

M 见注13

<!-- chapter_no=20; chapter_title=平面位置; knowledge_type=chapter_title -->
# 20 平面位置

精度水平 GCJDSP 双精

度型 — 2 ≥0 M 见注14

<!-- chapter_no=21; chapter_title=采集方式 CJFS 字符; knowledge_type=chapter_title -->
# 21 采集方式 CJFS 字符

型 20 —

车载激光雷

达实测、机

载激光雷达

实测、MESH

模型内业采

集

M 见注15

<!-- chapter_no=22; chapter_title=实地照片 ZP 字符; knowledge_type=chapter_title -->
# 22 实地照片 ZP 字符

型 254 — — O 见注16

<!-- chapter_no=23; chapter_title=采集日期 RQ 日期; knowledge_type=chapter_title -->
# 23 采集日期 RQ 日期

型 — — YYYY/MM/DD M 见注17

<!-- chapter_no=24; chapter_title=行政区代; knowledge_type=chapter_title -->
# 24 行政区代

码 XZQDM 整型 10 — — M 见注18

<!-- chapter_no=25; chapter_title=是否可用 SFKY 字符; knowledge_type=chapter_title -->
# 25 是否可用 SFKY 字符

型 254 — — O 见注19

<!-- chapter_no=26; chapter_title=备注 BZ 字符; knowledge_type=chapter_title -->
# 26 备注 BZ 字符

型 254 — — O

注 1：约束/条件：“M”为必选项，即必须填写的信息；“C”为条件必选项，即满足某一条件或要求

时必须填写的信息；“O”为可选项，可根据实际情况选择填写。

注 2：进行全库统一编码。

注 3：检测线端点、结点纬度地理坐标，单位为“度”，小数点后保留有效位数9 位。端点指该检测线

高程值最低的点，结点指该检测线高程值最高的点。

注 4：检测线端点、结点纬度地理坐标，单位为“度”，小数点后保留有效位数 9 位。

注 5：检测线端点、结点的大地高，单位：米，保留 3 位小数。

注 6：检测线端点、结点北坐标（投影平面 x 坐标），单位：米，保留 3 位小数。

注 7：检测线端点、结点东坐标（投影平面 y 坐标），单位：米，保留 3 位小数。

注 8：检测线端点、结点的 85 高程，单位：米，保留 3 位小数。

注 9：检测线端点与结点的北坐标平均值及东坐标平均值，单位：米，保留 3 位小数。

注 10：中央子午线，根据检测线实际的中央子午线填写。

注 11：投影面高程，根据检测线实际的投影面高程填写。

注 12：检测地物代码，取值见附录 B.1。

注 13：地物名称，采集地物的名称，取值见附录 B.1。

注 14：经评估的平面位置精度水平，该检测线能用来进行高精度检测的最高平面位置中误差水平，单

位：米。如：0.25 米、0.30 米、0.5 米、1.2 米等。

注 15：车载激光雷达实测、机载激光雷达实测、MESH 模型内业采集等。

注 16：存储实地照片文件所在的物理路径及文件名，当文件名不存在时此项为空。

注 17：属性值域为“YYYY/MM/DD”表示日期，其中“Y”表示年份，“M”表示月份，“D”表示日，不

足位的用 0 补足，例如“2024/03/06”。

注 18：填写该检测点所属县级行政区代码。

注 19：记录检测点是否可用状态，如当检测点对应地物发生变化时，说明变化状态。

表3 电杆检测线属性结构表

电杆检测线属性结构表

序

号 字段名称 字段代码 字段

类型

字段

长度

小数

位数 值域 约束/条

件 备注

<!-- chapter_no=1; chapter_title=检测线编; knowledge_type=chapter_title -->
# 1 检测线编

号 jiancexianbianhao 字符

型 20 — — M 见注2

<!-- chapter_no=2; chapter_title=端点纬度; knowledge_type=chapter_title -->
# 2 端点纬度

值 duandian_B 双精

度型 — 9 DD.DDDDDDDD

D M 见注3

<!-- chapter_no=3; chapter_title=端点经度; knowledge_type=chapter_title -->
# 3 端点经度

值 duandian_L 双精

度型 — 9 DDD.DDDDDDD

DD M 见注4

<!-- chapter_no=4; chapter_title=端点大地; knowledge_type=chapter_title -->
# 4 端点大地

高 duandian_H 双精

度型 — 3 — M 见注5

<!-- chapter_no=5; chapter_title=结点纬度; knowledge_type=chapter_title -->
# 5 结点纬度

值 jiedian_B 双精

度型 — 9 DD.DDDDDDDD

D M 见注3

<!-- chapter_no=6; chapter_title=结点经度; knowledge_type=chapter_title -->
# 6 结点经度

值 jiedian_L 双精

度型 — 9 DDD.DDDDDDD

DD M 见注4

<!-- chapter_no=7; chapter_title=结点大地; knowledge_type=chapter_title -->
# 7 结点大地

高 jiedian_H 双精

度型 — 3 — M 见注5

<!-- chapter_no=8; chapter_title=端点北坐; knowledge_type=chapter_title -->
# 8 端点北坐

标 duandian_X 双精

度型 — 3 ≥0 M 见注6

<!-- chapter_no=9; chapter_title=端点东坐; knowledge_type=chapter_title -->
# 9 端点东坐

标 duandian_Y 双精

度型 — 3 ≥0 M 见注7

<!-- chapter_no=10; chapter_title=端点高程 duandian_H85 双精; knowledge_type=chapter_title -->
# 10 端点高程 duandian_H85 双精

度型 — 3 — M 见注8

<!-- chapter_no=11; chapter_title=结点北坐; knowledge_type=chapter_title -->
# 11 结点北坐

标 jiedian_X 双精

度型 — 3 ≥0 M 见注6

<!-- chapter_no=12; chapter_title=结点东坐; knowledge_type=chapter_title -->
# 12 结点东坐

标 jiedian_Y 双精

度型 — 3 ≥0 M 见注7

<!-- chapter_no=13; chapter_title=结点高程 jiedian_H85 双精; knowledge_type=chapter_title -->
# 13 结点高程 jiedian_H85 双精

度型 — 3 — M 见注8

<!-- chapter_no=14; chapter_title=检测线北; knowledge_type=chapter_title -->
# 14 检测线北

坐标均值 junzhi_X 双精

度型 — 3 — M 见注9

<!-- chapter_no=15; chapter_title=检测线东; knowledge_type=chapter_title -->
# 15 检测线东

坐标均值 junzhi_Y 双精

度型 — 3 — M 见注9

<!-- chapter_no=16; chapter_title=中央子午; knowledge_type=chapter_title -->
# 16 中央子午

线 ZYZWX 双精

度型 — — ≥0 M 见注10

<!-- chapter_no=17; chapter_title=投影面高; knowledge_type=chapter_title -->
# 17 投影面高

程 h0 双精

度型 — 3 — O 见注11

<!-- chapter_no=18; chapter_title=地物代码 DWDM 字符; knowledge_type=chapter_title -->
# 18 地物代码 DWDM 字符

型 15 — DG_CZTZX M 见注12

<!-- chapter_no=19; chapter_title=地物名称 DWMC 字符; knowledge_type=chapter_title -->
# 19 地物名称 DWMC 字符

型 30 — 电杆垂直特

征线 M 见注13

<!-- chapter_no=20; chapter_title=平面位置; knowledge_type=chapter_title -->
# 20 平面位置

精度水平 GCJDSP 双精

度型 — 2 ≥0 M 见注14

<!-- chapter_no=21; chapter_title=采集方式 CJFS 字符; knowledge_type=chapter_title -->
# 21 采集方式 CJFS 字符

型 20 —

车载激光雷

达实测、 机载

激光雷达实

测、MESH 模型

内业采集

M 见注15

<!-- chapter_no=22; chapter_title=实地照片 ZP 字符; knowledge_type=chapter_title -->
# 22 实地照片 ZP 字符

型 254 — — O 见注16

<!-- chapter_no=23; chapter_title=采集日期 RQ 日期; knowledge_type=chapter_title -->
# 23 采集日期 RQ 日期

型 — — YYYY/MM/DD M 见注17

<!-- chapter_no=24; chapter_title=行政区代; knowledge_type=chapter_title -->
# 24 行政区代

码 XZQDM 整型 10 — — M 见注18

<!-- chapter_no=25; chapter_title=是否可用 SFKY 字符; knowledge_type=chapter_title -->
# 25 是否可用 SFKY 字符

型 254 — — O 见注19

<!-- chapter_no=26; chapter_title=备注 BZ 字符; knowledge_type=chapter_title -->
# 26 备注 BZ 字符

型 254 — — O

注 1：约束/条件：“M”为必选项，即必须填写的信息；“C”为条件必选项，即满足某一条件或要求时

必须填写的信息；“O”为可选项，可根据实际情况选择填写。

注 2：进行全库统一编码。

注 3：检测线端点、结点纬度地理坐标，单位为“度”，小数点后保留有效位数9 位。端点指该检测线高

程值最低的点，结点指该检测线高程值最高的点。

注 4：检测线端点、结点纬度地理坐标，单位为“度”，小数点后保留有效位数 9 位。

注 5：检测线端点、结点的大地高，单位：米，保留 3 位小数。

注 6：检测线端点、结点北坐标（投影平面 x 坐标），单位：米，保留 3 位小数。

注 7：检测线端点、结点东坐标（投影平面 y 坐标），单位：米，保留 3 位小数。

注 8：检测线端点、结点的 85 高程，单位：米，保留 3 位小数。

注 9：检测线端点与结点的北坐标平均值及东坐标平均值，单位：米，保留 3 位小数。

注 10：中央子午线，根据检测线实际的中央子午线填写。

注 11：投影面高程，根据检测线实际的投影面高程填写。

注 12：检测地物代码，取值见附录 B.1。

注 13：地物名称，采集地物的名称，取值见附录 B.1。

注 14： 经评估的平面位置精度水平， 该检测线能用来进行高精度检测的最高平面位置中误差水平， 单位：

米。如：0.25 米、0.30 米、0.5 米、1.2 米等。

注 15：车载激光雷达实测、机载激光雷达实测、MESH 模型内业采集等。

注 16：存储实地照片文件所在的物理路径及文件名，当文件名不存在时此项为空。

注 17：属性值域为“YYYY/MM/DD”表示日期，其中“Y”表示年份，“M”表示月份，“D”表示日，不足

位的用 0 补足，例如“2024/03/06”。

注 18：填写该检测点所属县级行政区代码。

注 19：记录检测点是否可用状态，如当检测点对应地物发生变化时，说明变化状态。

表4 路灯检测线属性结构表

路灯检测线属性结构表

序

号 字段名称 字段代码 字段

类型

字段

长度

小数

位数 值域 约束/

条件 备注

<!-- chapter_no=1; chapter_title=检测线编; knowledge_type=chapter_title -->
# 1 检测线编

号 jiancexianbianhao 字符

型 20 — — M 见注2

<!-- chapter_no=2; chapter_title=端点纬度; knowledge_type=chapter_title -->
# 2 端点纬度

值 duandian_B 双精

度型 — 9 DD.DDDDDDDDD M 见注3

<!-- chapter_no=3; chapter_title=端点经度; knowledge_type=chapter_title -->
# 3 端点经度

值 duandian_L 双精

度型 — 9 DDD.DDDDDDDD

D M 见注4

<!-- chapter_no=4; chapter_title=端点大地; knowledge_type=chapter_title -->
# 4 端点大地

高 duandian_H 双精

度型 — 3 — M 见注5

<!-- chapter_no=5; chapter_title=结点纬度; knowledge_type=chapter_title -->
# 5 结点纬度

值 jiedian_B 双精

度型 — 9 DD.DDDDDDDDD M 见注3

<!-- chapter_no=6; chapter_title=结点经度; knowledge_type=chapter_title -->
# 6 结点经度

值 jiedian_L 双精

度型 — 9 DDD.DDDDDDDD

D M 见注4

<!-- chapter_no=7; chapter_title=结点大地; knowledge_type=chapter_title -->
# 7 结点大地

高 jiedian_H 双精

度型 — 3 — M 见注5

<!-- chapter_no=8; chapter_title=端点北坐; knowledge_type=chapter_title -->
# 8 端点北坐

标 duandian_X 双精

度型 — 3 ≥0 M 见注6

<!-- chapter_no=9; chapter_title=端点东坐; knowledge_type=chapter_title -->
# 9 端点东坐

标 duandian_Y 双精

度型 — 3 ≥0 M 见注7

<!-- chapter_no=10; chapter_title=端点高程 duandian_H85 双精; knowledge_type=chapter_title -->
# 10 端点高程 duandian_H85 双精

度型 — 3 — M 见注8

<!-- chapter_no=11; chapter_title=结点北坐; knowledge_type=chapter_title -->
# 11 结点北坐

标 jiedian_X 双精

度型 — 3 ≥0 M 见注6

<!-- chapter_no=12; chapter_title=结点东坐; knowledge_type=chapter_title -->
# 12 结点东坐

标 jiedian_Y 双精

度型 — 3 ≥0 M 见注7

<!-- chapter_no=13; chapter_title=结点高程 jiedian_H85 双精; knowledge_type=chapter_title -->
# 13 结点高程 jiedian_H85 双精

度型 — 3 — M 见注8

<!-- chapter_no=14; chapter_title=检测线北; knowledge_type=chapter_title -->
# 14 检测线北

坐标均值 junzhi_X 双精

度型 — 3 — M 见注9

<!-- chapter_no=15; chapter_title=检测线东; knowledge_type=chapter_title -->
# 15 检测线东

坐标均值 junzhi_Y 双精

度型 — 3 — M 见注9

<!-- chapter_no=16; chapter_title=中央子午; knowledge_type=chapter_title -->
# 16 中央子午

线 ZYZWX 双精

度型 — — ≥0 M 见注10

<!-- chapter_no=17; chapter_title=投影面高; knowledge_type=chapter_title -->
# 17 投影面高

程 h0 双精

度型 — 3 — O 见注11

<!-- chapter_no=18; chapter_title=地物代码 DWDM 字符; knowledge_type=chapter_title -->
# 18 地物代码 DWDM 字符

型 15 — LD_CZTZX M 见注12

<!-- chapter_no=19; chapter_title=地物名称 DWMC 字符; knowledge_type=chapter_title -->
# 19 地物名称 DWMC 字符

型 30 — 路灯垂直特征

线 M 见注13

<!-- chapter_no=20; chapter_title=平面位置; knowledge_type=chapter_title -->
# 20 平面位置

精度水平 GCJDSP 双精

度型 — 2 ≥0 M 见注14

<!-- chapter_no=21; chapter_title=采集方式 CJFS 字符; knowledge_type=chapter_title -->
# 21 采集方式 CJFS 字符

型 20 —

车载激光雷达

实测、机载激

光雷达实测、

MESH 模型内业

采集

M 见注15

<!-- chapter_no=22; chapter_title=实地照片 ZP 字符; knowledge_type=chapter_title -->
# 22 实地照片 ZP 字符

型 254 — — O 见注16

<!-- chapter_no=23; chapter_title=采集日期 RQ 日期; knowledge_type=chapter_title -->
# 23 采集日期 RQ 日期

型 — — YYYY/MM/DD M 见注17

<!-- chapter_no=24; chapter_title=行政区代; knowledge_type=chapter_title -->
# 24 行政区代

码 XZQDM 整型 10 — — M 见注18

<!-- chapter_no=25; chapter_title=是否可用 SFKY 字符; knowledge_type=chapter_title -->
# 25 是否可用 SFKY 字符

型 254 — — O 见注19

<!-- chapter_no=26; chapter_title=备注 BZ 字符; knowledge_type=chapter_title -->
# 26 备注 BZ 字符

型 254 — — O

注 1：约束/条件：“M”为必选项，即必须填写的信息；“C”为条件必选项，即满足某一条件或要求时

必须填写的信息；“O”为可选项，可根据实际情况选择填写。

注 2：进行全库统一编码。

注 3：检测线端点、结点纬度地理坐标，单位为“度”，小数点后保留有效位数 9 位。端点指该检测线

高程值最低的点，结点指该检测线高程值最高的点。

注 4：检测线端点、结点纬度地理坐标，单位为“度”，小数点后保留有效位数 9 位。

注 5：检测线端点、结点的大地高，单位：米，保留 3 位小数。

注 6：检测线端点、结点北坐标（投影平面 x 坐标），单位：米，保留 3 位小数。

注 7：检测线端点、结点东坐标（投影平面 y 坐标），单位：米，保留 3 位小数。

注 8：检测线端点、结点的 85 高程，单位：米，保留 3 位小数。

注 9：检测线端点与结点的北坐标平均值及东坐标平均值，单位：米，保留 3 位小数。

注 10：中央子午线，根据检测线实际的中央子午线填写。

注 11：投影面高程，根据检测线实际的投影面高程填写。

注 12：检测地物代码，取值见附录 B.1。

注 13：地物名称，采集地物的名称，取值见附录 B.1。

注 14： 经评估的平面位置精度水平， 该检测线能用来进行高精度检测的最高平面位置中误差水平， 单位：

米。如：0.25 米、0.30 米、0.5 米、1.2 米等。

注 15：车载激光雷达实测、机载激光雷达实测、MESH 模型内业采集等。

注 16：存储实地照片文件所在的物理路径及文件名，当文件名不存在时此项为空。

注 17：属性值域为“YYYY/MM/DD”表示日期，其中“Y”表示年份，“M”表示月份，“D”表示日，不

足位的用 0 补足，例如“2024/03/06”。

注 18：填写该检测点所属县级行政区代码。

表5 路面漆检测线属性结构表

注 19：记录检测点是否可用状态，如当检测点对应地物发生变化时，说明变化状态。

路面漆检测线属性结构表

序号 字段名

称 字段代码 字段

类型

字段

长度

小数

位数 值域 约束/

条件 备注

<!-- chapter_no=1; chapter_title=检测线; knowledge_type=chapter_title -->
# 1 检测线

编号 jiancexianbianhao 字符

型 20 — — M 见注2

<!-- chapter_no=2; chapter_title=中央子; knowledge_type=chapter_title -->
# 2 中央子

午线 ZYZWX 双精

度型 — — ≥0 M 见注3

<!-- chapter_no=3; chapter_title=投影面; knowledge_type=chapter_title -->
# 3 投影面

高程 h0 双精

度型 — 3 — O 见注4

<!-- chapter_no=4; chapter_title=地物代; knowledge_type=chapter_title -->
# 4 地物代

码 DWDM 字符

型 15 — LMQ_LKX M 见注5

<!-- chapter_no=5; chapter_title=地物名; knowledge_type=chapter_title -->
# 5 地物名

称 DWMC 字符

型 30 — 路面漆轮廓线 M 见注6

平面位

置精度

水平

GCJDSP 双精

度型 — 2 ≥0 M 见注7

表6 路边线检测网属性结构表

<!-- chapter_no=7; chapter_title=采集方; knowledge_type=chapter_title -->
# 7 采集方

式 CJFS 字符

型 20 —

车载激光雷达

实测、机载激

光雷达实测、

MESH 模型内业

采集

M 见注8

<!-- chapter_no=8; chapter_title=实地照; knowledge_type=chapter_title -->
# 8 实地照

片 ZP 字符

型 254 — — O 见注9

<!-- chapter_no=9; chapter_title=采集日; knowledge_type=chapter_title -->
# 9 采集日

期 RQ 日期

型 — — YYYY/MM/DD M 见注10

<!-- chapter_no=10; chapter_title=行政区; knowledge_type=chapter_title -->
# 10 行政区

代码 XZQDM 整型 10 — — M 见注11

<!-- chapter_no=11; chapter_title=是否可; knowledge_type=chapter_title -->
# 11 是否可

用 SFKY 字符

型 254 — — O 见注12

<!-- chapter_no=12; chapter_title=备注 BZ 字符; knowledge_type=chapter_title -->
# 12 备注 BZ 字符

型 254 — — O

注 1：约束/条件：“M”为必选项，即必须填写的信息；“C”为条件必选项，即满足某一条件或要求时

必须填写的信息；“O”为可选项，可根据实际情况选择填写。

注 2：进行全库统一编码。

注 3：中央子午线，根据检测线实际的中央子午线填写。

注 4：投影面高程，根据检测线实际的投影面高程填写。

注 5：检测地物代码，取值见附录 B.1。

注 6：地物名称，采集地物的名称，取值见附录 B.1。

注 7：经评估的平面位置精度水平，该检测线能用来进行高精度检测的最高平面位置中误差水平，单位：

米。如：0.25 米、0.30 米、0.5 米、1.2 米等。

注 8：车载激光雷达实测、机载激光雷达实测、MESH 模型内业采集等。

注 9：存储实地照片文件所在的物理路径及文件名，当文件名不存在时此项为空。

注 10：属性值域为“YYYY/MM/DD”表示日期，其中“Y”表示年份，“M”表示月份，“D”表示日，不足

位的用 0 补足，例如“2024/03/06”。

注 11：填写该检测点所属县级行政区代码。

注 12：记录检测点是否可用状态，如当检测点对应地物发生变化时，说明变化状态。

路边线检测网属性结构表

序

号 字段名称 字段代码 字段类型 字段长

度

小数位

数 值域 约束/

条件 备注

<!-- chapter_no=1; chapter_title=检测线编; knowledge_type=chapter_title -->
# 1 检测线编

号

jiancexianb

ianhao 字符型 20 — — M 见注2

<!-- chapter_no=2; chapter_title=中央子午; knowledge_type=chapter_title -->
# 2 中央子午

线 ZYZWX 双精度型 — — ≥0 M 见注3

<!-- chapter_no=3; chapter_title=投影面高; knowledge_type=chapter_title -->
# 3 投影面高

程 h0 双精度型 — 3 — O 见注4

<!-- chapter_no=4; chapter_title=地物代码 DWDM 字符型 15 — LBX M 见注5; knowledge_type=chapter_title -->
# 4 地物代码 DWDM 字符型 15 — LBX M 见注5

<!-- chapter_no=5; chapter_title=地物名称 DWMC 字符型 30 — 路边线 M 见注6; knowledge_type=chapter_title -->
# 5 地物名称 DWMC 字符型 30 — 路边线 M 见注6

<!-- chapter_no=6; chapter_title=平面位置; knowledge_type=chapter_title -->
# 6 平面位置

精度水平 GCJDSP 双精度型 — 2 ≥0 M 见注7

<!-- chapter_no=7; chapter_title=采集方式 CJFS 字符型 20 —; knowledge_type=chapter_title -->
# 7 采集方式 CJFS 字符型 20 —

车载激光雷达

实测、机载激光

雷达实测、MESH

模型内业采集

M 见注8

<!-- chapter_no=8; chapter_title=实地照片 ZP 字符型 254 — — O 见注9; knowledge_type=chapter_title -->
# 8 实地照片 ZP 字符型 254 — — O 见注9

<!-- chapter_no=9; chapter_title=采集日期 RQ 日期型 — — YYYY/MM/DD M 见注10; knowledge_type=chapter_title -->
# 9 采集日期 RQ 日期型 — — YYYY/MM/DD M 见注10

<!-- chapter_no=10; chapter_title=行政区代; knowledge_type=chapter_title -->
# 10 行政区代

码 XZQDM 整型 10 — — M 见注11

<!-- chapter_no=11; chapter_title=是否可用 SFKY 字符型 254 — — O 见注12; knowledge_type=chapter_title -->
# 11 是否可用 SFKY 字符型 254 — — O 见注12

<!-- chapter_no=12; chapter_title=备注 BZ 字符型 254 — — O; knowledge_type=chapter_title -->
# 12 备注 BZ 字符型 254 — — O

注 1：约束/条件：“M”为必选项，即必须填写的信息；“C”为条件必选项，即满足某一条件或要求时

必须填写的信息；“O”为可选项，可根据实际情况选择填写。

注 2：进行全库统一编码。

注 3：中央子午线，根据检测线实际的中央子午线填写。

注 4：投影面高程，根据检测线实际的投影面高程填写。

注 5：检测地物代码，取值见附录 B.1。

注 6：地物名称，采集地物的名称，取值见附录 B.1。

注 7：经评估的平面位置精度水平，该检测线能用来进行高精度检测的最高平面位置中误差水平，单位：

米。如：0.25 米、0.30 米、0.5 米、1.2 米等。

注 8：车载激光雷达实测、机载激光雷达实测、MESH 模型内业采集等。

注 9：存储实地照片文件所在的物理路径及文件名，当文件名不存在时此项为空。

注 10：属性值域为“YYYY/MM/DD”表示日期，其中“Y”表示年份，“M”表示月份，“D”表示日，不足

位的用 0 补足，例如“2024/03/06”。

注 11：填写该检测点所属县级行政区代码。

注 12：记录检测点是否可用状态，如当检测点对应地物发生变化时，说明变化状态。

<!-- chapter_no=6; chapter_title=入库流程; section_type=数据库; knowledge_type=data_spec -->
# 6 入库流程

<!-- chapter_no=6.1; chapter_title=数据收集及分类; section_type=数据库; knowledge_type=data_spec -->
## 6.1 数据收集及分类

<!-- section_type=数据库; knowledge_type=data_spec -->
检测线数据源包含：

<!-- section_type=数据库; knowledge_type=data_spec -->
（1）车载激光扫描测量点云数据，采用人工或自动的方式从点云数据中提

<!-- section_type=数据库; knowledge_type=data_spec -->
取的检测线数据；

<!-- section_type=数据库; knowledge_type=data_spec -->
（2） 无人机航空摄影测量建立MESH 模型后， 采用人工或自动的方式在模型

<!-- section_type=数据库; knowledge_type=data_spec -->
上采集的检测线数据。

<!-- section_type=数据库; knowledge_type=data_spec -->
将历年采集的检测数据汇集，并按照数据源的不同进行分类。

<!-- chapter_no=6.2; chapter_title=入库数据预处理; section_type=数据库; knowledge_type=data_spec -->
## 6.2 入库数据预处理

<!-- section_type=数据库; knowledge_type=data_spec -->
入库数据预处理工作包括：

<!-- chapter_no=1; chapter_title=采用人机交互的方式，对自动提取的检测线数据进行可靠性判别，剔除; knowledge_type=chapter_title -->
# 1 采用人机交互的方式，对自动提取的检测线数据进行可靠性判别，剔除

提取错误的检测线数据。

<!-- chapter_no=2; chapter_title=按照质检大数据库设计要求，将可靠的检测线数据进行格式转换、坐标; knowledge_type=chapter_title -->
# 2 按照质检大数据库设计要求，将可靠的检测线数据进行格式转换、坐标

转换、分层，并根据表 1 至表 6 录入属性值。

<!-- chapter_no=6.3; chapter_title=质量检查; knowledge_type=chapter_title -->
## 6.3 质量检查

质量检查主要检查预处理后的数学基础、 属性精度、 数据结构和完整性。 发

现数据要素或属性缺失的， 需结合补充数据进行修正和完善， 确保数据的现势性

满足使用需求。

<!-- chapter_no=6.4; chapter_title=数据入库; knowledge_type=chapter_title -->
## 6.4 数据入库

根据检测线数据库图层及属性结构设计要求构建检测线数据库库体； 利用统

一的工具将完成预处理的数据映射入库， 并对入库数据进行检查复核。 检测线数

据入库后进行统一编码。

<!-- chapter_no=7; chapter_title=数据更新; section_type=数据整理; knowledge_type=data_spec -->
# 7 数据更新

<!-- section_type=数据整理; knowledge_type=data_spec -->
暂未编写……

<!-- chapter_no=8; chapter_title=共享应用; knowledge_type=chapter_title -->
# 8 共享应用

验各类型数字测绘成果精度检测、 重要要素的快速检查， 以节省外业工作， 提升

质检工作的效率。 检测线数据应用方式主要以人工套合比对和软件自动检查方式。

<!-- chapter_no=9; chapter_title=成果提交; knowledge_type=chapter_title -->
# 9 成果提交

质检大数据支撑库检测点子库建设项目提交的成果清单如下：

（1）检测线数据库.gdb；

（2）实景照片数据集；

（3）技术设计方案.pdf；

（4）质量检查报告.docx；

（5）地物代码表.xlsx；

（6）入库脚本或工具。

附录A

（资料性）

图层、地物、地物代码关系表见表A.1。

表A.1 图层、地物、地物代码关系表

图层、地物、地物代码关系表

图层名称 地物名称 地物代码

建筑物水平特征检测线

建筑物外轮廓水平特征线 JZWWLK_SPTZX

建筑物门窗水平特征线 JZWMC_SPTZX

围墙水平特征线 WQ_SPTZX

建筑物垂直特征检测线

建筑物外轮廓垂直特征线 JZWWLK_CZTZX

建筑物门窗垂直特征线 JZWMC_CZTZX

围墙垂直特征线 WQ_CZTZX

电杆检测线 电杆垂直特征线 DG_CZTZX

路灯检测线 路灯垂直特征线 LD_CZTZX

路面漆检测线 路面漆轮廓线 LMQ_LKX

路边线检测网 路边线 LBX

参 考 文 献

[1] GB/T 2260 《中华人民共和国行政区划代码》；

[2] GB/T 18521《地名分类与类别代码编制规则》；

[3] GB/T 23705《数字城市地理信息公共平台地名/地址编码规则》；

[4] GB/T 33176 《国家基本比例尺地图1：500 1：1000 1：2000 地形图》；

[5] GB/T 33453《基础地理信息数据库建设规范》；

[6] GB/T 39616 《卫星导航定位基准站网络实时动态测量（RTK）规范》；

[7] GB/T****《地理实体空间身份编码规则》；

[8] CH/T 1020 《1：500、1：1000、1：2000 地形图质量检验技术规程》；

[9] CH/T 2009 《全球定位系统实时动态测量（RTK）技术规范》；

[10] CH/T 3003 《低空数字航空摄影测量内业规范》；

[11] CH/T 3004 《低空数字航空摄影测量外业规范》；

[12] CH/T 3005 《低空数字航空摄影规范》；

[13] CH/T 6003 《车载移动测量数据规范》；

[14] CH/T 6004 《车载移动测量技术规程》；

[15] CH/T 8023 《机载激光雷达数据处理技术规范》；

[16] CH/T 8024 《机载激光雷达数据获取技术规范》；

[17] CH/T****《基础地理实体分类、粒度及精度基本要求》；

[18] CH/T****《基础地理实体数据元数据》。
