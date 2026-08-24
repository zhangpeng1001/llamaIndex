# 实景三维质检大数据支撑库 时空数据规范 第7部分 资源数据

> 来源：实景三维质检大数据支撑库 时空数据规范 第7部分 资源数据.pdf（增强版提取，已去目录/页眉/页码噪声）


第 7 部分 资源数据

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

第4部分 标志性地物

第5部分 重要要素

第6部分 高精度栅格数据

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

<!-- chapter_no=3.1; chapter_title=资源数据库; section_type=术语定义; knowledge_type=term_definition -->
## 3.1 资源数据库

<!-- section_type=术语定义; knowledge_type=term_definition -->
用于存储、管理和分析大规模、多类型数据的数据库，数据类型包括矢量、栅格、三维数据、二维

<!-- section_type=术语定义; knowledge_type=term_definition -->
实体、三维实体、原始影像以及航飞照片等数据。

<!-- chapter_no=4; chapter_title=数据内容; section_type=术语定义; knowledge_type=term_definition -->
# 4 数据内容

<!-- section_type=术语定义; knowledge_type=term_definition -->
资源数据由数据体及元数据组成。

<!-- section_type=术语定义; knowledge_type=term_definition -->
——数据体。数据体是作为资源进行管理的时空大数据，按文件进行存储和管理。

<!-- section_type=术语定义; knowledge_type=term_definition -->
——元数据是数据的说明文件，采用空间元数据形式进行存储和管理，以矢量面表示数据集范围，

<!-- section_type=术语定义; knowledge_type=term_definition -->
以属性信息记录数据集的来源、质量、管理等信息。

<!-- chapter_no=5; chapter_title=数据范围文件; section_type=术语定义; knowledge_type=term_definition -->
# 5 数据范围文件

<!-- section_type=术语定义; knowledge_type=term_definition -->
数据体范围文件采用shape files格式的面文件，面的范围即为数据体的范围，面文件的命名与数

<!-- section_type=术语定义; knowledge_type=term_definition -->
据体命名一致。

<!-- chapter_no=6; chapter_title=元数据表结构; section_type=术语定义; knowledge_type=term_definition -->
# 6 元数据表结构

<!-- section_type=术语定义; knowledge_type=term_definition -->
——各属性项约束条件中，“ M”为必选项；“ O”为可选项。

<!-- section_type=术语定义; knowledge_type=term_definition -->
——每个元素表对应一个空间索引的多边形文件。

<!-- section_type=术语定义; knowledge_type=term_definition -->
表1 矢量数据元数据表

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=ID 数据 id 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据 id 字符型 M

<!-- chapter_no=2; chapter_title=Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 2 Datum_Geodetic 大地基准 字符型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=3; chapter_title=Datum_ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 Datum_ele 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- chapter_no=5; chapter_title=Accuracy 比例尺 长整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 Accuracy 比例尺 长整型 M

<!-- chapter_no=6; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 6 AdminRegion 所属行政区划 字符型 M

<!-- chapter_no=7; chapter_title=SheetNumber 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 7 SheetNumber 分幅号 字符型 M

<!-- chapter_no=8; chapter_title=Bbox 四至范围 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 8 Bbox 四至范围 字符型 M

<!-- chapter_no=9; chapter_title=Program 所属项目 字符型 M 数据所属项目名; section_type=术语定义; knowledge_type=term_definition -->
# 9 Program 所属项目 字符型 M 数据所属项目名

<!-- section_type=术语定义; knowledge_type=term_definition -->
称

<!-- chapter_no=10; chapter_title=Userid 上传者 整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 10 Userid 上传者 整型 M

<!-- chapter_no=11; chapter_title=Collecttime 生产时间 日期型 M; section_type=术语定义; knowledge_type=term_definition -->
# 11 Collecttime 生产时间 日期型 M

<!-- chapter_no=12; chapter_title=Manufacturer 数据生产单位 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 12 Manufacturer 数据生产单位 字符型 O

<!-- chapter_no=13; chapter_title=Metadata Files 元数据文件 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 13 Metadata Files 元数据文件 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
14  Datatype 数据类型 字符型 O DEM\DLG\DOM…

<!-- section_type=术语定义; knowledge_type=term_definition -->
15  Dataformat 数据格式 字符型 O Shp\GDB\TIFF..

<!-- section_type=术语定义; knowledge_type=term_definition -->
.

<!-- chapter_no=16; chapter_title=Accy_H 高程精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 16 Accy_H 高程精度 双精度浮点型 M

<!-- chapter_no=17; chapter_title=Accy_V 平面精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 17 Accy_V 平面精度 双精度浮点型 M

<!-- chapter_no=18; chapter_title=ClassSTD 分类标准 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 18 ClassSTD 分类标准 字符型 O

<!-- chapter_no=19; chapter_title=LayerName 图层名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 LayerName 图层名称 字符型 O

<!-- chapter_no=20; chapter_title=LayerStructure 图层结构 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 20 LayerStructure 图层结构 字符型 O

<!-- chapter_no=21; chapter_title=FileName 所属文件 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 21 FileName 所属文件 字符型 O

<!-- chapter_no=22; chapter_title=FilePath 文件路径/存; section_type=术语定义; knowledge_type=term_definition -->
# 22 FilePath 文件路径/存

<!-- section_type=术语定义; knowledge_type=term_definition -->
储地址 字符型 M

<!-- chapter_no=23; chapter_title=File 文件大小 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 23 File 文件大小 字符型 O

<!-- chapter_no=24; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 24 Notes 备注 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
表2 栅格数据元数据表

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束

<!-- section_type=术语定义; knowledge_type=term_definition -->
条件 备注

<!-- chapter_no=1; chapter_title=ID 数据 id 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据 id 字符型 M

<!-- chapter_no=2; chapter_title=Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 2 Datum_Geodetic 大地基准 字符型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束

<!-- section_type=术语定义; knowledge_type=term_definition -->
条件 备注

<!-- chapter_no=3; chapter_title=Datum_ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 Datum_ele 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- chapter_no=5; chapter_title=Accuracy 比例尺 长整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 Accuracy 比例尺 长整型 M

<!-- chapter_no=6; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 6 AdminRegion 所属行政区划 字符型 M

<!-- chapter_no=7; chapter_title=SheetNumber 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 7 SheetNumber 分幅号 字符型 M

<!-- chapter_no=8; chapter_title=Program 所属项目 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 8 Program 所属项目 字符型 M

<!-- chapter_no=9; chapter_title=Userid 上传者 整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 9 Userid 上传者 整型 M

<!-- chapter_no=10; chapter_title=Accy_H 高程精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 10 Accy_H 高程精度 双精度浮点型 M

<!-- chapter_no=11; chapter_title=Accy_V 平面精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 11 Accy_V 平面精度 双精度浮点型 M

<!-- chapter_no=12; chapter_title=FilePath 文件路径/存储地址 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 12 FilePath 文件路径/存储地址 字符型 M

<!-- chapter_no=13; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 13 Notes 备注 字符型 O

<!-- chapter_no=14; chapter_title=DOM\DEM; section_type=术语定义; knowledge_type=term_definition -->
# 14 DOM\DEM

<!-- section_type=术语定义; knowledge_type=term_definition -->
15  ImageType 影像类型 DOM\DEM\... M

<!-- chapter_no=16; chapter_title=Frequency 周期频次 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 16 Frequency 周期频次 整型 O

<!-- chapter_no=17; chapter_title=ImageResolution 影像分辨率像素 浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 17 ImageResolution 影像分辨率像素 浮点型 M

<!-- chapter_no=18; chapter_title=ImageSource 影像来源类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 18 ImageSource 影像来源类型 字符型 O

<!-- chapter_no=19; chapter_title=ImageEPSGID 影像 EPSG 代码 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 ImageEPSGID 影像 EPSG 代码 字符型 O

<!-- chapter_no=20; chapter_title=TransformCoef 变换系数 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 20 TransformCoef 变换系数 字符型 O

<!-- chapter_no=21; chapter_title=BandsNum 波段数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 21 BandsNum 波段数 整型 O

<!-- chapter_no=22; chapter_title=PixelWidth 像元宽度 浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 22 PixelWidth 像元宽度 浮点型 O

<!-- chapter_no=23; chapter_title=PixelHeight 像元高度 浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 23 PixelHeight 像元高度 浮点型 O

<!-- chapter_no=24; chapter_title=DepthType 位深类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 24 DepthType 位深类型 字符型 O

<!-- chapter_no=25; chapter_title=RowsNum 行总数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 25 RowsNum 行总数 整型 O

<!-- chapter_no=26; chapter_title=ColumnsNum 列总数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 26 ColumnsNum 列总数 整型 O

<!-- chapter_no=27; chapter_title=InvalidValue 无效值 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 27 InvalidValue 无效值 整型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束

<!-- section_type=术语定义; knowledge_type=term_definition -->
条件 备注

<!-- chapter_no=28; chapter_title=EffectiveArea 有效面积 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 28 EffectiveArea 有效面积 双精度浮点型 O

<!-- chapter_no=29; chapter_title=LeftUpper x 四至左上角 x 坐标 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 29 LeftUpper x 四至左上角 x 坐标 双精度浮点型 O

<!-- chapter_no=30; chapter_title=LeftUpper y 四至左上角 y 坐标 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 30 LeftUpper y 四至左上角 y 坐标 双精度浮点型 O

<!-- chapter_no=31; chapter_title=LowerRight x 四至右下角 x 坐标 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 31 LowerRight x 四至右下角 x 坐标 双精度浮点型 O

<!-- chapter_no=32; chapter_title=LowerRight y 四至右下角 y 坐标 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 32 LowerRight y 四至右下角 y 坐标 双精度浮点型 O

<!-- chapter_no=33; chapter_title=CenterPoi lon 中心点经度 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 33 CenterPoi lon 中心点经度 双精度浮点型 O

<!-- chapter_no=34; chapter_title=CenterPoi lat 中心点纬度 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 34 CenterPoi lat 中心点纬度 双精度浮点型 O

<!-- chapter_no=35; chapter_title=ThumbnailName 缩略图名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 35 ThumbnailName 缩略图名称 字符型 O

<!-- chapter_no=36; chapter_title=UsageLabel 用途标记 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 36 UsageLabel 用途标记 字符型 O

<!-- chapter_no=37; chapter_title=MetadataName 影像元数据名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 37 MetadataName 影像元数据名称 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
表3 三维数据元数据表

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=ID 数据 id 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据 id 字符型 M

<!-- chapter_no=2; chapter_title=Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 2 Datum_Geodetic 大地基准 字符型 M

<!-- chapter_no=3; chapter_title=Datum_ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 Datum_ele 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- chapter_no=5; chapter_title=Accuracy 比例尺 长整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 Accuracy 比例尺 长整型 M

<!-- chapter_no=6; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 6 AdminRegion 所属行政区划 字符型 M

<!-- chapter_no=7; chapter_title=SheetNumber 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 7 SheetNumber 分幅号 字符型 M

<!-- chapter_no=8; chapter_title=Program 所属项目 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 8 Program 所属项目 字符型 M

<!-- chapter_no=9; chapter_title=Userid 上传者 整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 9 Userid 上传者 整型 M

<!-- chapter_no=10; chapter_title=Collecttime 生产时间 日期型 M; section_type=术语定义; knowledge_type=term_definition -->
# 10 Collecttime 生产时间 日期型 M

<!-- chapter_no=11; chapter_title=Datatype 数据类型 字符型 M Shp\GDB\T; section_type=术语定义; knowledge_type=term_definition -->
# 11 Datatype 数据类型 字符型 M Shp\GDB\T

<!-- section_type=术语定义; knowledge_type=term_definition -->
IFF...

<!-- chapter_no=12; chapter_title=Dataformat 数据格式 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 12 Dataformat 数据格式 字符型 M

<!-- chapter_no=13; chapter_title=Accy_H 高程精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 13 Accy_H 高程精度 双精度浮点型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=14; chapter_title=Accy_V 平面精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 14 Accy_V 平面精度 双精度浮点型 M

<!-- chapter_no=15; chapter_title=FilePath 文件路径/存储地址 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 15 FilePath 文件路径/存储地址 字符型 M

<!-- chapter_no=16; chapter_title=CenterPoi lon 中心点经度 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 16 CenterPoi lon 中心点经度 双精度浮点型 O

<!-- chapter_no=17; chapter_title=CenterPoi lat 中心点纬度 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 17 CenterPoi lat 中心点纬度 双精度浮点型 O

<!-- chapter_no=18; chapter_title=ModelResolution 影像分辨率像素 浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 18 ModelResolution 影像分辨率像素 浮点型 O

<!-- chapter_no=19; chapter_title=ImageEPSGID 影像 EPSG 代码 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 ImageEPSGID 影像 EPSG 代码 字符型 O

<!-- chapter_no=20; chapter_title=MetadataName 模型元数据文件 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 20 MetadataName 模型元数据文件 字符型 O

<!-- chapter_no=21; chapter_title=mesh 三维; section_type=术语定义; knowledge_type=term_definition -->
# 21 mesh 三维

<!-- chapter_no=22; chapter_title=SpatialRef 空间参考 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 22 SpatialRef 空间参考 字符型 M

<!-- chapter_no=23; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 23 Projection 空间投影 字符型 M

<!-- chapter_no=24; chapter_title=Resolution 空间分辨率 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 24 Resolution 空间分辨率 字符型 M

<!-- chapter_no=25; chapter_title=SensorType 传感器类型 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 25 SensorType 传感器类型 字符型 M

<!-- chapter_no=26; chapter_title=AcquisitionTime 获取时间 日期 M; section_type=术语定义; knowledge_type=term_definition -->
# 26 AcquisitionTime 获取时间 日期 M

<!-- chapter_no=27; chapter_title=TriNetNum 三角网数量 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 27 TriNetNum 三角网数量 双精度浮点型 O

<!-- chapter_no=28; chapter_title=TexturesNum 纹理数量 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 28 TexturesNum 纹理数量 双精度浮点型 O

<!-- chapter_no=29; chapter_title=TextureSize 纹理尺寸 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 29 TextureSize 纹理尺寸 双精度浮点型 O

<!-- chapter_no=30; chapter_title=Lidar; section_type=术语定义; knowledge_type=term_definition -->
# 30 Lidar

<!-- chapter_no=31; chapter_title=Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 31 Datum_Geodetic 大地基准 字符型 M

<!-- chapter_no=32; chapter_title=Datum_ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 32 Datum_ele 高程基准 字符型 M

<!-- chapter_no=33; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 33 Projection 空间投影 字符型 M

<!-- chapter_no=34; chapter_title=Reslution  空间分辨率 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 34 Reslution  空间分辨率 字符型 M

<!-- chapter_no=35; chapter_title=SensorType 传感器类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 35 SensorType 传感器类型 字符型 O

<!-- chapter_no=36; chapter_title=Density 点云密度 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 36 Density 点云密度 双精度浮点型 O

<!-- chapter_no=37; chapter_title=PointNum 点云数量 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 37 PointNum 点云数量 双精度浮点型 O

<!-- chapter_no=38; chapter_title=Classify 是否分类 布尔型 O; section_type=术语定义; knowledge_type=term_definition -->
# 38 Classify 是否分类 布尔型 O

<!-- chapter_no=39; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 39 Notes 备注 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
表4 二维实体元数据表

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=ID 数据 id 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据 id 字符型 M

<!-- chapter_no=2; chapter_title=Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 2 Datum_Geodetic 大地基准 字符型 M

<!-- chapter_no=3; chapter_title=Datum_Ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 Datum_Ele 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- chapter_no=5; chapter_title=Accuracy 比例尺 长整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 Accuracy 比例尺 长整型 M

<!-- chapter_no=6; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 6 AdminRegion 所属行政区划 字符型 M

<!-- chapter_no=7; chapter_title=AdminRegionNum 所属行政区划代码 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 7 AdminRegionNum 所属行政区划代码 字符型 M

<!-- chapter_no=8; chapter_title=SheetNumber 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 8 SheetNumber 分幅号 字符型 M

<!-- chapter_no=9; chapter_title=Program 所属项目 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 9 Program 所属项目 字符型 M

<!-- chapter_no=10; chapter_title=UserId 上传者 整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 10 UserId 上传者 整型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
11  CollectTime 生产时间 日期型 M DEM\DLG\DOM…

<!-- section_type=术语定义; knowledge_type=term_definition -->
12  DataType 数据类型 字符型 M Shp\GDB\TIFF.

<!-- section_type=术语定义; knowledge_type=term_definition -->
..

<!-- chapter_no=13; chapter_title=DataFormat 数据格式 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 13 DataFormat 数据格式 字符型 M

<!-- chapter_no=14; chapter_title=Accy_H 高程精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 14 Accy_H 高程精度 双精度浮点型 M

<!-- chapter_no=15; chapter_title=Accy_V 平面精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 15 Accy_V 平面精度 双精度浮点型 M

<!-- chapter_no=16; chapter_title=LayerName 图层名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 16 LayerName 图层名称 字符型 O

<!-- chapter_no=17; chapter_title=EntityName 实体名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 17 EntityName 实体名称 字符型 O

<!-- chapter_no=18; chapter_title=FilePath 文件路径/存储地; section_type=术语定义; knowledge_type=term_definition -->
# 18 FilePath 文件路径/存储地

<!-- section_type=术语定义; knowledge_type=term_definition -->
址 字符型 M

<!-- chapter_no=19; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 Notes 备注 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
表5 三维实体（LOD）元数据表

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=ID 数据 id 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据 id 字符型 M

<!-- chapter_no=2; chapter_title=Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 2 Datum_Geodetic 大地基准 字符型 M

<!-- chapter_no=3; chapter_title=Datum_Ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 Datum_Ele 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=5; chapter_title=Accuracy 比例尺 长整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 Accuracy 比例尺 长整型 M

<!-- chapter_no=6; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 6 AdminRegion 所属行政区划 字符型 M

<!-- chapter_no=7; chapter_title=SheetNumber 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 7 SheetNumber 分幅号 字符型 M

<!-- chapter_no=8; chapter_title=Program 所属项目 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 8 Program 所属项目 字符型 M

<!-- chapter_no=9; chapter_title=UserId 上传者 整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 9 UserId 上传者 整型 M

<!-- chapter_no=10; chapter_title=CollectTime 生产时间 日期型 M; section_type=术语定义; knowledge_type=term_definition -->
# 10 CollectTime 生产时间 日期型 M

<!-- chapter_no=11; chapter_title=DataType 数据类型 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 11 DataType 数据类型 字符型 M

<!-- chapter_no=12; chapter_title=DataFormat 数据格式 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 12 DataFormat 数据格式 字符型 M

<!-- chapter_no=13; chapter_title=Accy_H 高程精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 13 Accy_H 高程精度 双精度浮点型 M

<!-- chapter_no=14; chapter_title=Accy_V 平面精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 14 Accy_V 平面精度 双精度浮点型 M

<!-- chapter_no=15; chapter_title=EntityName                                                                                                                   实体名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 15 EntityName                                                                                                                   实体名称 字符型 O

<!-- chapter_no=16; chapter_title=MinLon 数据范围最小经度值 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 16 MinLon 数据范围最小经度值 双精度浮点型 O

<!-- chapter_no=17; chapter_title=MaxLon 数据范围最大经度值 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 17 MaxLon 数据范围最大经度值 双精度浮点型 O

<!-- chapter_no=18; chapter_title=MinLat 数据范围最小纬度值 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 18 MinLat 数据范围最小纬度值 双精度浮点型 O

<!-- chapter_no=19; chapter_title=MaxLat 数据范围最小纬度值 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 MaxLat 数据范围最小纬度值 双精度浮点型 O

<!-- chapter_no=20; chapter_title=Inspection1srt 一级检查结论 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 20 Inspection1srt 一级检查结论 字符型 O

<!-- chapter_no=21; chapter_title=Manufacture 生产单位 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 21 Manufacture 生产单位 字符型 O

<!-- chapter_no=22; chapter_title=FilePath 文件路径/存储地址 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 22 FilePath 文件路径/存储地址 字符型 M

<!-- chapter_no=23; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 23 Notes 备注 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
表6 卫星影像元数据表

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=ID 数据id 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据id 字符型 M

<!-- chapter_no=2; chapter_title=Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 2 Datum_Geodetic 大地基准 字符型 M

<!-- chapter_no=3; chapter_title=Datum_Ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 Datum_Ele 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- chapter_no=5; chapter_title=Accuracy 比例尺 长整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 Accuracy 比例尺 长整型 M

<!-- chapter_no=6; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 6 AdminRegion 所属行政区划 字符型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=7; chapter_title=SheetNumber 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 7 SheetNumber 分幅号 字符型 M

<!-- chapter_no=8; chapter_title=Program 所属项目 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 8 Program 所属项目 字符型 M

<!-- chapter_no=9; chapter_title=UserId 上传者 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 9 UserId 上传者 字符型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
10  CollectTime 生产时间 日期型 M DEM\DLG\DOM…

<!-- section_type=术语定义; knowledge_type=term_definition -->
11  DataType 数据类型 字符型 M Shp\GDB\TIFF.

<!-- section_type=术语定义; knowledge_type=term_definition -->
..

<!-- chapter_no=12; chapter_title=DataFormat 数据格式 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 12 DataFormat 数据格式 字符型 M

<!-- chapter_no=13; chapter_title=Accy_H 高程精度 双精度浮; section_type=术语定义; knowledge_type=term_definition -->
# 13 Accy_H 高程精度 双精度浮

<!-- section_type=术语定义; knowledge_type=term_definition -->
点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
M

<!-- chapter_no=14; chapter_title=Accy_V 平面精度 双精度浮; section_type=术语定义; knowledge_type=term_definition -->
# 14 Accy_V 平面精度 双精度浮

<!-- section_type=术语定义; knowledge_type=term_definition -->
点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
M

<!-- chapter_no=15; chapter_title=SatelliteID 卫星ID 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 15 SatelliteID 卫星ID 字符型 O

<!-- chapter_no=16; chapter_title=SatelliteSeries 卫星系列 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 16 SatelliteSeries 卫星系列 字符型 O

<!-- chapter_no=17; chapter_title=Unique 数据采集记录; section_type=术语定义; knowledge_type=term_definition -->
# 17 Unique 数据采集记录

<!-- section_type=术语定义; knowledge_type=term_definition -->
唯一值 字符型 O

<!-- chapter_no=18; chapter_title=SpectralType 波谱类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 18 SpectralType 波谱类型 字符型 O

<!-- chapter_no=19; chapter_title=ImageFormat 影像格式 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 ImageFormat 影像格式 字符型 O

<!-- chapter_no=20; chapter_title=ControlPoiRef 控制点空间参; section_type=术语定义; knowledge_type=term_definition -->
# 20 ControlPoiRef 控制点空间参

<!-- section_type=术语定义; knowledge_type=term_definition -->
考 字符型 O

<!-- chapter_no=21; chapter_title=SatelliteCollectTim; section_type=术语定义; knowledge_type=term_definition -->
# 21 SatelliteCollectTim

<!-- section_type=术语定义; knowledge_type=term_definition -->
e 卫星采集时间 日期型 O

<!-- chapter_no=22; chapter_title=PyramidLevel 金字塔级别 双精度浮; section_type=术语定义; knowledge_type=term_definition -->
# 22 PyramidLevel 金字塔级别 双精度浮

<!-- section_type=术语定义; knowledge_type=term_definition -->
点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=23; chapter_title=ControlPoiNum 控制点个数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 23 ControlPoiNum 控制点个数 整型 O

<!-- chapter_no=24; chapter_title=ControlPoiCor 控制点坐标 双精度浮; section_type=术语定义; knowledge_type=term_definition -->
# 24 ControlPoiCor 控制点坐标 双精度浮

<!-- section_type=术语定义; knowledge_type=term_definition -->
点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=25; chapter_title=Resolution 卫星分辨率 浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 25 Resolution 卫星分辨率 浮点型 O

<!-- chapter_no=26; chapter_title=CompressionType 压缩类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 26 CompressionType 压缩类型 字符型 O

<!-- chapter_no=27; chapter_title=SensorType 传感器类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 27 SensorType 传感器类型 字符型 O

<!-- chapter_no=28; chapter_title=ProductID 产品号 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 28 ProductID 产品号 字符型 O

<!-- chapter_no=29; chapter_title=TrackNum 轨道号 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 29 TrackNum 轨道号 字符型 O

<!-- chapter_no=30; chapter_title=CloudCov 云覆盖量 浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 30 CloudCov 云覆盖量 浮点型 O

<!-- chapter_no=31; chapter_title=SnowCov 雪覆盖量 浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 31 SnowCov 雪覆盖量 浮点型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=32; chapter_title=ProductLevel 产品级别 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 32 ProductLevel 产品级别 整型 O

<!-- chapter_no=33; chapter_title=ConsecutiveSceneNum 连续景数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 33 ConsecutiveSceneNum 连续景数 整型 O

<!-- chapter_no=34; chapter_title=ShootDirection 拍摄方向 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 34 ShootDirection 拍摄方向 字符型 O

<!-- chapter_no=35; chapter_title=ReceivingStation 接收站 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 35 ReceivingStation 接收站 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
Same origin and same

<!-- section_type=术语定义; knowledge_type=term_definition -->
scene

<!-- section_type=术语定义; knowledge_type=term_definition -->
identification

<!-- section_type=术语定义; knowledge_type=term_definition -->
同源同景标识 字符型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=37; chapter_title=AttachedRPC 附属 RPC 文件; section_type=术语定义; knowledge_type=term_definition -->
# 37 AttachedRPC 附属 RPC 文件

<!-- section_type=术语定义; knowledge_type=term_definition -->
名称 字符型 O

<!-- chapter_no=38; chapter_title=AttachedThumbnail 附属缩略图文; section_type=术语定义; knowledge_type=term_definition -->
# 38 AttachedThumbnail 附属缩略图文

<!-- section_type=术语定义; knowledge_type=term_definition -->
件名称 字符型 O

<!-- chapter_no=39; chapter_title=AttachedThumbName 附属拇指 图文; section_type=术语定义; knowledge_type=term_definition -->
# 39 AttachedThumbName 附属拇指 图文

<!-- section_type=术语定义; knowledge_type=term_definition -->
件名称 字符型 O

<!-- chapter_no=40; chapter_title=DetectFileName 检测 文件的; section_type=术语定义; knowledge_type=term_definition -->
# 40 DetectFileName 检测 文件的

<!-- section_type=术语定义; knowledge_type=term_definition -->
shp 数据名称 字符型 O

<!-- chapter_no=41; chapter_title=FileSize 文件大小 双精度浮; section_type=术语定义; knowledge_type=term_definition -->
# 41 FileSize 文件大小 双精度浮

<!-- section_type=术语定义; knowledge_type=term_definition -->
点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=42; chapter_title=CloudCovFile 云 覆盖量的; section_type=术语定义; knowledge_type=term_definition -->
# 42 CloudCovFile 云 覆盖量的

<!-- section_type=术语定义; knowledge_type=term_definition -->
shp 数据名称 字符型 O

<!-- chapter_no=43; chapter_title=FilePath 文件路径 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 43 FilePath 文件路径 字符型 M

<!-- chapter_no=44; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 44 Notes 备注 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
表7 航摄成果元数据表

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=ID 数据 id 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据 id 字符型 M

<!-- chapter_no=2; chapter_title=DatumGeodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 2 DatumGeodetic 大地基准 字符型 M

<!-- chapter_no=3; chapter_title=DatumEle 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 DatumEle 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- chapter_no=5; chapter_title=Accuracy 比例尺 长整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 Accuracy 比例尺 长整型 M

<!-- chapter_no=6; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 6 AdminRegion 所属行政区划 字符型 M

<!-- chapter_no=7; chapter_title=SubdivisionNum 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 7 SubdivisionNum 分幅号 字符型 M

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=8; chapter_title=Program 所属项目 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 8 Program 所属项目 字符型 M

<!-- chapter_no=9; chapter_title=Userid 上传者 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 9 Userid 上传者 字符型 M

<!-- chapter_no=10; chapter_title=Collecttime 采集时间 日期型 M DEM\DLG\DOM; section_type=术语定义; knowledge_type=term_definition -->
# 10 Collecttime 采集时间 日期型 M DEM\DLG\DOM

<!-- section_type=术语定义; knowledge_type=term_definition -->
…

<!-- chapter_no=11; chapter_title=Datatype 数据类型 字符型 M Shp\GDB\TIFF; section_type=术语定义; knowledge_type=term_definition -->
# 11 Datatype 数据类型 字符型 M Shp\GDB\TIFF

<!-- section_type=术语定义; knowledge_type=term_definition -->
…

<!-- chapter_no=12; chapter_title=Dataformat 数据格式 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 12 Dataformat 数据格式 字符型 M

<!-- chapter_no=13; chapter_title=Accy_H 高程精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 13 Accy_H 高程精度 双精度浮点型 M

<!-- chapter_no=14; chapter_title=Accy_V 平面精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 14 Accy_V 平面精度 双精度浮点型 M

<!-- chapter_no=15; chapter_title=AttachmentName 附件名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 15 AttachmentName 附件名称 字符型 O

<!-- chapter_no=16; chapter_title=AttachmentAddr; section_type=术语定义; knowledge_type=term_definition -->
# 16 AttachmentAddr

<!-- section_type=术语定义; knowledge_type=term_definition -->
ess 附件地址 字符型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=17; chapter_title=AttachmentSour; section_type=术语定义; knowledge_type=term_definition -->
# 17 AttachmentSour

<!-- section_type=术语定义; knowledge_type=term_definition -->
ceEquipment 附件来源设备 字符型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=18; chapter_title=AttachmentType 附件类型 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 18 AttachmentType 附件类型 字符型 O

<!-- chapter_no=19; chapter_title=TakeOffLon 起飞点经度 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 TakeOffLon 起飞点经度 双精度浮点型 O

<!-- chapter_no=20; chapter_title=TakeOffLat 起飞点纬度 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 20 TakeOffLat 起飞点纬度 双精度浮点型 O

<!-- chapter_no=21; chapter_title=TakeOff 起飞点相对地面高; section_type=术语定义; knowledge_type=term_definition -->
# 21 TakeOff 起飞点相对地面高

<!-- section_type=术语定义; knowledge_type=term_definition -->
度 双精度浮点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=22; chapter_title=TakeOff 起飞点地面海拔 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 22 TakeOff 起飞点地面海拔 双精度浮点型 O

<!-- chapter_no=23; chapter_title=Time 拍摄时间 日期型 O; section_type=术语定义; knowledge_type=term_definition -->
# 23 Time 拍摄时间 日期型 O

<!-- chapter_no=24; chapter_title=Angle 拍摄角度 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 24 Angle 拍摄角度 双精度浮点型 O

<!-- chapter_no=25; chapter_title=PitchAngle 拍摄俯仰角 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 25 PitchAngle 拍摄俯仰角 双精度浮点型 O

<!-- chapter_no=26; chapter_title=Elevation 拍摄点地面海拔 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 26 Elevation 拍摄点地面海拔 双精度浮点型 O

<!-- chapter_no=27; chapter_title=ShootingPositi; section_type=术语定义; knowledge_type=term_definition -->
# 27 ShootingPositi

<!-- section_type=术语定义; knowledge_type=term_definition -->
onLon 拍摄位置经度 双精度浮点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=28; chapter_title=ShootingPositi; section_type=术语定义; knowledge_type=term_definition -->
# 28 ShootingPositi

<!-- section_type=术语定义; knowledge_type=term_definition -->
onLat 拍摄位置纬度 双精度浮点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=29; chapter_title=ShootingPositi; section_type=术语定义; knowledge_type=term_definition -->
# 29 ShootingPositi

<!-- section_type=术语定义; knowledge_type=term_definition -->
onX 拍摄位置 X 双精度浮点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=30; chapter_title=ShootingPositi; section_type=术语定义; knowledge_type=term_definition -->
# 30 ShootingPositi

<!-- section_type=术语定义; knowledge_type=term_definition -->
onY 拍摄位置 Y 双精度浮点型

<!-- section_type=术语定义; knowledge_type=term_definition -->
O

<!-- chapter_no=31; chapter_title=Metadata 元数据 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 31 Metadata 元数据 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=32; chapter_title=FilePath 文件路径/存储地址 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 32 FilePath 文件路径/存储地址 字符型 M

<!-- chapter_no=33; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 33 Notes 备注 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
表8 成果包元数据表

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=1; chapter_title=ID 数据 id 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 1 ID 数据 id 字符型 M

<!-- chapter_no=2; chapter_title=Datum_Geodetic 大地基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 2 Datum_Geodetic 大地基准 字符型 M

<!-- chapter_no=3; chapter_title=Datum_ele 高程基准 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 3 Datum_ele 高程基准 字符型 M

<!-- chapter_no=4; chapter_title=Projection 空间投影 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 4 Projection 空间投影 字符型 M

<!-- chapter_no=5; chapter_title=Accuracy 比例尺 长整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 5 Accuracy 比例尺 长整型 M

<!-- chapter_no=6; chapter_title=AdminRegion 所属行政区划 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 6 AdminRegion 所属行政区划 字符型 M

<!-- chapter_no=7; chapter_title=SubdivisionNum 分幅号 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 7 SubdivisionNum 分幅号 字符型 M

<!-- chapter_no=8; chapter_title=Program 所属项目 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 8 Program 所属项目 字符型 M

<!-- chapter_no=9; chapter_title=Userid 上传者 整型 M; section_type=术语定义; knowledge_type=term_definition -->
# 9 Userid 上传者 整型 M

<!-- chapter_no=10; chapter_title=Collecttime 采集时间 日期型 M DEM\DLG\D; section_type=术语定义; knowledge_type=term_definition -->
# 10 Collecttime 采集时间 日期型 M DEM\DLG\D

<!-- section_type=术语定义; knowledge_type=term_definition -->
OM…

<!-- chapter_no=11; chapter_title=Datatype 数据类型 字符型 M Shp\GDB\T; section_type=术语定义; knowledge_type=term_definition -->
# 11 Datatype 数据类型 字符型 M Shp\GDB\T

<!-- section_type=术语定义; knowledge_type=term_definition -->
IFF...

<!-- chapter_no=12; chapter_title=Dataformat 数据格式 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 12 Dataformat 数据格式 字符型 M

<!-- chapter_no=13; chapter_title=Accy_H 高程精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 13 Accy_H 高程精度 双精度浮点型 M

<!-- chapter_no=14; chapter_title=Accy_V 平面精度 双精度浮点型 M; section_type=术语定义; knowledge_type=term_definition -->
# 14 Accy_V 平面精度 双精度浮点型 M

<!-- chapter_no=15; chapter_title=PackageName 文件包名称 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 15 PackageName 文件包名称 字符型 O

<!-- chapter_no=16; chapter_title=PackageSize 文件包大小 双精度浮点型 O; section_type=术语定义; knowledge_type=term_definition -->
# 16 PackageSize 文件包大小 双精度浮点型 O

<!-- chapter_no=17; chapter_title=SubdirectoriesNum 子目录数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 17 SubdirectoriesNum 子目录数 整型 O

<!-- chapter_no=18; chapter_title=FileNum 文件数 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 18 FileNum 文件数 整型 O

<!-- chapter_no=19; chapter_title=FolderDepth 文件夹深度 整型 O; section_type=术语定义; knowledge_type=term_definition -->
# 19 FolderDepth 文件夹深度 整型 O

<!-- chapter_no=20; chapter_title=FilePath 文件路径/存储地址 字符型 M; section_type=术语定义; knowledge_type=term_definition -->
# 20 FilePath 文件路径/存储地址 字符型 M

<!-- chapter_no=21; chapter_title=MetadataFiles 元数据文件 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 21 MetadataFiles 元数据文件 字符型 O

<!-- chapter_no=22; chapter_title=Manufacture 数据生产单位 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 22 Manufacture 数据生产单位 字符型 O

<!-- chapter_no=23; chapter_title=BornTime 数据生产日期 日期型 O; section_type=术语定义; knowledge_type=term_definition -->
# 23 BornTime 数据生产日期 日期型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
序号 字段名称 数据项 字段类型 约束条件 备注

<!-- chapter_no=24; chapter_title=InspectionUnit 数据质检单位 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 24 InspectionUnit 数据质检单位 字符型 O

<!-- chapter_no=25; chapter_title=InspectionTime 数据质检日期 日期型 O; section_type=术语定义; knowledge_type=term_definition -->
# 25 InspectionTime 数据质检日期 日期型 O

<!-- chapter_no=26; chapter_title=PublishUnit 数据发布单位 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 26 PublishUnit 数据发布单位 字符型 O

<!-- chapter_no=27; chapter_title=PublishTime 数据发布日期 日期型 O; section_type=术语定义; knowledge_type=term_definition -->
# 27 PublishTime 数据发布日期 日期型 O

<!-- chapter_no=28; chapter_title=Notes 备注 字符型 O; section_type=术语定义; knowledge_type=term_definition -->
# 28 Notes 备注 字符型 O

<!-- section_type=术语定义; knowledge_type=term_definition -->
参考文献

<!-- section_type=术语定义; knowledge_type=term_definition -->
[1] 实景三维数据库建库技术规范。
