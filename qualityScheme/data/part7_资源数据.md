# 实景三维质检大数据支撑库 时空数据规范 第7部分 资源数据

> 来源：实景三维质检大数据支撑库 时空数据规范 第7部分 资源数据.pdf

<!-- 第 1 页 -->

部省共建项目
实景三维质检大数据支撑库 时空数据规范
第 7 部分 资源数据
（草案）

2025 年 7 月
<!-- 第 2 页 -->

<!-- 第 3 页 -->

I

目  次
前 言 .......................................................................... II
1 范围 ............................................................................... 1
2 规范性引用文件 ..................................................................... 1
3 术语和定义 ......................................................................... 1
4 数据内容 ........................................................................... 1
5 数据体范围文件 ..................................................................... 1
6 元数据表结构 ....................................................................... 1
参考文献  ..................................................................... 13

<!-- 第 4 页 -->
II

前 言
本文件按照GB/T 1.1—2020《标准化工作导则  第1部分：标准化文件的结构和起草规则》的规定
起草。
本文件是实景三维质检大数据支撑库 时空数据规范 第7部分。其他部分还包括：
第1部分 数据分类与基本规定
第2部分 检测点
第3部分 检测线
第4部分 标志性地物
第5部分 重要要素
第6部分 高精度栅格数据
请注意本文件的某些内容可能涉及专利。本文件的发布机构不承担识别专利的责任。
起草单位：
起草人员：
<!-- 第 5 页 -->

1 范围
本规程给出了质检大数据支撑库中资源库的数据的一般规定， 规定了资源库数据的数据类型、字段
名称、数据项以及数据组织形式。
本规程适用于质检大数据支撑库资源库数据获取、处理、整合、建库、更新和服务。
2 规范性引用文件
下列文件对于本文件的应用是必不可少的。 凡是注日期的引用文件， 仅所注日期的版本适用于本文
件。凡是不注日期的引用文件，其最新版本（包括所有的修改单）适用于本文件。
3 术语和定义
3.1 资源数据库
用于存储、管理和分析大规模、多类型数据的数据库，数据类型包括矢量、栅格、三维数据、二维
实体、三维实体、原始影像以及航飞照片等数据。
4 数据内容
资源数据由数据体及元数据组成。
——数据体。数据体是作为资源进行管理的时空大数据，按文件进行存储和管理。
——元数据是数据的说明文件，采用空间元数据形式进行存储和管理，以矢量面表示数据集范围，
以属性信息记录数据集的来源、质量、管理等信息。
5 数据范围文件
数据体范围文件采用shape files格式的面文件，面的范围即为数据体的范围，面文件的命名与数
据体命名一致。
6 元数据表结构
——各属性项约束条件中，“ M”为必选项；“ O”为可选项。
——每个元素表对应一个空间索引的多边形文件。
表1 矢量数据元数据表
序号 字段名称 数据项 字段类型 约束条件 备注
1  ID 数据 id 字符型 M
2  Datum_Geodetic 大地基准 字符型 M
<!-- 第 6 页 -->

序号 字段名称 数据项 字段类型 约束条件 备注
3  Datum_ele 高程基准 字符型 M
4  Projection 空间投影 字符型 M
5  Accuracy 比例尺 长整型 M
6  AdminRegion 所属行政区划 字符型 M
7  SheetNumber 分幅号 字符型 M
8  Bbox 四至范围 字符型 M
9  Program 所属项目 字符型 M 数据所属项目名
称
10  Userid 上传者 整型 M
11  Collecttime 生产时间 日期型 M
12  Manufacturer 数据生产单位 字符型 O
13  Metadata Files 元数据文件 字符型 O
14  Datatype 数据类型 字符型 O DEM\DLG\DOM…
15  Dataformat 数据格式 字符型 O Shp\GDB\TIFF..
.
16  Accy_H 高程精度 双精度浮点型 M
17  Accy_V 平面精度 双精度浮点型 M
18  ClassSTD 分类标准 字符型 O
19  LayerName 图层名称 字符型 O
20  LayerStructure 图层结构 字符型 O
21  FileName 所属文件 字符型 O
22  FilePath 文件路径/存
储地址 字符型 M
23  File 文件大小 字符型 O
24  Notes 备注 字符型 O

表2 栅格数据元数据表
序号 字段名称 数据项 字段类型 约束
条件 备注
1  ID 数据 id 字符型 M
2  Datum_Geodetic 大地基准 字符型 M
<!-- 第 7 页 -->

序号 字段名称 数据项 字段类型 约束
条件 备注
3  Datum_ele 高程基准 字符型 M
4  Projection 空间投影 字符型 M
5  Accuracy 比例尺 长整型 M
6  AdminRegion 所属行政区划 字符型 M
7  SheetNumber 分幅号 字符型 M
8  Program 所属项目 字符型 M
9  Userid 上传者 整型 M
10  Accy_H 高程精度 双精度浮点型 M
11  Accy_V 平面精度 双精度浮点型 M
12  FilePath 文件路径/存储地址 字符型 M
13  Notes 备注 字符型 O
14  DOM\DEM
15  ImageType 影像类型 DOM\DEM\... M
16  Frequency 周期频次 整型 O
17  ImageResolution 影像分辨率像素 浮点型 M
18  ImageSource 影像来源类型 字符型 O
19  ImageEPSGID 影像 EPSG 代码 字符型 O
20  TransformCoef 变换系数 字符型 O
21  BandsNum 波段数 整型 O
22  PixelWidth 像元宽度 浮点型 O
23  PixelHeight 像元高度 浮点型 O
24  DepthType 位深类型 字符型 O
25  RowsNum 行总数 整型 O
26  ColumnsNum 列总数 整型 O
27  InvalidValue 无效值 整型 O
<!-- 第 8 页 -->

序号 字段名称 数据项 字段类型 约束
条件 备注
28  EffectiveArea 有效面积 双精度浮点型 O
29  LeftUpper x 四至左上角 x 坐标 双精度浮点型 O
30  LeftUpper y 四至左上角 y 坐标 双精度浮点型 O
31  LowerRight x 四至右下角 x 坐标 双精度浮点型 O
32  LowerRight y 四至右下角 y 坐标 双精度浮点型 O
33  CenterPoi lon 中心点经度 双精度浮点型 O
34  CenterPoi lat 中心点纬度 双精度浮点型 O
35  ThumbnailName 缩略图名称 字符型 O
36  UsageLabel 用途标记 字符型 O
37  MetadataName 影像元数据名称 字符型 O

表3 三维数据元数据表
序号 字段名称 数据项 字段类型 约束条件 备注
1  ID 数据 id 字符型 M
2  Datum_Geodetic 大地基准 字符型 M
3  Datum_ele 高程基准 字符型 M
4  Projection 空间投影 字符型 M
5  Accuracy 比例尺 长整型 M
6  AdminRegion 所属行政区划 字符型 M
7  SheetNumber 分幅号 字符型 M
8  Program 所属项目 字符型 M
9  Userid 上传者 整型 M
10  Collecttime 生产时间 日期型 M
11  Datatype 数据类型 字符型 M Shp\GDB\T
IFF...
12  Dataformat 数据格式 字符型 M
13  Accy_H 高程精度 双精度浮点型 M
<!-- 第 9 页 -->

序号 字段名称 数据项 字段类型 约束条件 备注
14  Accy_V 平面精度 双精度浮点型 M
15  FilePath 文件路径/存储地址 字符型 M
16  CenterPoi lon 中心点经度 双精度浮点型 O
17  CenterPoi lat 中心点纬度 双精度浮点型 O
18  ModelResolution 影像分辨率像素 浮点型 O
19  ImageEPSGID 影像 EPSG 代码 字符型 O
20  MetadataName 模型元数据文件 字符型 O
21  mesh 三维
22  SpatialRef 空间参考 字符型 M
23  Projection 空间投影 字符型 M
24  Resolution 空间分辨率 字符型 M
25  SensorType 传感器类型 字符型 M
26  AcquisitionTime 获取时间 日期 M
27  TriNetNum 三角网数量 双精度浮点型 O
28  TexturesNum 纹理数量 双精度浮点型 O
29  TextureSize 纹理尺寸 双精度浮点型 O
30  Lidar
31  Datum_Geodetic 大地基准 字符型 M
32  Datum_ele 高程基准 字符型 M
33  Projection 空间投影 字符型 M
34  Reslution  空间分辨率 字符型 M
35  SensorType 传感器类型 字符型 O
36  Density 点云密度 双精度浮点型 O
37  PointNum 点云数量 双精度浮点型 O
38  Classify 是否分类 布尔型 O
39  Notes 备注 字符型 O
<!-- 第 10 页 -->

表4 二维实体元数据表
序号 字段名称 数据项 字段类型 约束条件 备注
1  ID 数据 id 字符型 M
2  Datum_Geodetic 大地基准 字符型 M
3  Datum_Ele 高程基准 字符型 M
4  Projection 空间投影 字符型 M
5  Accuracy 比例尺 长整型 M
6  AdminRegion 所属行政区划 字符型 M
7  AdminRegionNum 所属行政区划代码 字符型 M
8  SheetNumber 分幅号 字符型 M
9  Program 所属项目 字符型 M
10  UserId 上传者 整型 M
11  CollectTime 生产时间 日期型 M DEM\DLG\DOM…
12  DataType 数据类型 字符型 M Shp\GDB\TIFF.
..
13  DataFormat 数据格式 字符型 M
14  Accy_H 高程精度 双精度浮点型 M
15  Accy_V 平面精度 双精度浮点型 M
16  LayerName 图层名称 字符型 O
17  EntityName 实体名称 字符型 O
18  FilePath 文件路径/存储地
址 字符型 M
19  Notes 备注 字符型 O

表5 三维实体（LOD）元数据表
序号 字段名称 数据项 字段类型 约束条件 备注
1  ID 数据 id 字符型 M
2  Datum_Geodetic 大地基准 字符型 M
3  Datum_Ele 高程基准 字符型 M
4  Projection 空间投影 字符型 M
<!-- 第 11 页 -->

序号 字段名称 数据项 字段类型 约束条件 备注
5  Accuracy 比例尺 长整型 M
6  AdminRegion 所属行政区划 字符型 M
7  SheetNumber 分幅号 字符型 M
8  Program 所属项目 字符型 M
9  UserId 上传者 整型 M
10  CollectTime 生产时间 日期型 M
11  DataType 数据类型 字符型 M
12  DataFormat 数据格式 字符型 M
13  Accy_H 高程精度 双精度浮点型 M
14  Accy_V 平面精度 双精度浮点型 M
15  EntityName                                                                                                                   实体名称 字符型 O
16  MinLon 数据范围最小经度值 双精度浮点型 O
17  MaxLon 数据范围最大经度值 双精度浮点型 O
18  MinLat 数据范围最小纬度值 双精度浮点型 O
19  MaxLat 数据范围最小纬度值 双精度浮点型 O
20  Inspection1srt 一级检查结论 字符型 O
21  Manufacture 生产单位 字符型 O
22  FilePath 文件路径/存储地址 字符型 M
23  Notes 备注 字符型 O

表6 卫星影像元数据表
序号 字段名称 数据项 字段类型 约束条件 备注
1  ID 数据id 字符型 M
2  Datum_Geodetic 大地基准 字符型 M
3  Datum_Ele 高程基准 字符型 M
4  Projection 空间投影 字符型 M
5  Accuracy 比例尺 长整型 M
6  AdminRegion 所属行政区划 字符型 M
<!-- 第 12 页 -->

序号 字段名称 数据项 字段类型 约束条件 备注
7  SheetNumber 分幅号 字符型 M
8  Program 所属项目 字符型 M
9  UserId 上传者 字符型 M
10  CollectTime 生产时间 日期型 M DEM\DLG\DOM…
11  DataType 数据类型 字符型 M Shp\GDB\TIFF.
..
12  DataFormat 数据格式 字符型 M
13  Accy_H 高程精度 双精度浮
点型
M
14  Accy_V 平面精度 双精度浮
点型
M
15  SatelliteID 卫星ID 字符型 O
16  SatelliteSeries 卫星系列 字符型 O
17  Unique 数据采集记录
唯一值 字符型 O

18  SpectralType 波谱类型 字符型 O
19  ImageFormat 影像格式 字符型 O
20  ControlPoiRef 控制点空间参
考 字符型 O

21  SatelliteCollectTim
e 卫星采集时间 日期型 O

22  PyramidLevel 金字塔级别 双精度浮
点型
O

23  ControlPoiNum 控制点个数 整型 O
24  ControlPoiCor 控制点坐标 双精度浮
点型
O

25  Resolution 卫星分辨率 浮点型 O
26  CompressionType 压缩类型 字符型 O
27  SensorType 传感器类型 字符型 O

28  ProductID 产品号 字符型 O
29  TrackNum 轨道号 字符型 O
30  CloudCov 云覆盖量 浮点型 O
31  SnowCov 雪覆盖量 浮点型 O
<!-- 第 13 页 -->

序号 字段名称 数据项 字段类型 约束条件 备注
32  ProductLevel 产品级别 整型 O
33  ConsecutiveSceneNum 连续景数 整型 O
34  ShootDirection 拍摄方向 字符型 O
35  ReceivingStation 接收站 字符型 O
Same origin and same
scene
identification
同源同景标识 字符型
O

37  AttachedRPC 附属 RPC 文件
名称 字符型 O

38  AttachedThumbnail 附属缩略图文
件名称 字符型 O

39  AttachedThumbName 附属拇指 图文
件名称 字符型 O

40  DetectFileName 检测 文件的
shp 数据名称 字符型 O

41  FileSize 文件大小 双精度浮
点型
O

42  CloudCovFile 云 覆盖量的
shp 数据名称 字符型 O

43  FilePath 文件路径 字符型 M
44  Notes 备注 字符型 O

表7 航摄成果元数据表
序号 字段名称 数据项 字段类型 约束条件 备注
1  ID 数据 id 字符型 M
2  DatumGeodetic 大地基准 字符型 M
3  DatumEle 高程基准 字符型 M
4  Projection 空间投影 字符型 M
5  Accuracy 比例尺 长整型 M
6  AdminRegion 所属行政区划 字符型 M
7  SubdivisionNum 分幅号 字符型 M
<!-- 第 14 页 -->

序号 字段名称 数据项 字段类型 约束条件 备注
8  Program 所属项目 字符型 M
9  Userid 上传者 字符型 M
10  Collecttime 采集时间 日期型 M DEM\DLG\DOM
…
11  Datatype 数据类型 字符型 M Shp\GDB\TIFF
…
12  Dataformat 数据格式 字符型 M
13  Accy_H 高程精度 双精度浮点型 M
14  Accy_V 平面精度 双精度浮点型 M
15  AttachmentName 附件名称 字符型 O
16  AttachmentAddr
ess 附件地址 字符型
O

17  AttachmentSour
ceEquipment 附件来源设备 字符型
O

18  AttachmentType 附件类型 字符型 O
19  TakeOffLon 起飞点经度 双精度浮点型 O
20  TakeOffLat 起飞点纬度 双精度浮点型 O
21  TakeOff 起飞点相对地面高
度 双精度浮点型
O

22  TakeOff 起飞点地面海拔 双精度浮点型 O
23  Time 拍摄时间 日期型 O
24  Angle 拍摄角度 双精度浮点型 O
25  PitchAngle 拍摄俯仰角 双精度浮点型 O
26  Elevation 拍摄点地面海拔 双精度浮点型 O
27  ShootingPositi
onLon 拍摄位置经度 双精度浮点型
O

28  ShootingPositi
onLat 拍摄位置纬度 双精度浮点型
O

29  ShootingPositi
onX 拍摄位置 X 双精度浮点型
O

30  ShootingPositi
onY 拍摄位置 Y 双精度浮点型
O

31  Metadata 元数据 字符型 O
<!-- 第 15 页 -->

序号 字段名称 数据项 字段类型 约束条件 备注
32  FilePath 文件路径/存储地址 字符型 M
33  Notes 备注 字符型 O
表8 成果包元数据表
序号 字段名称 数据项 字段类型 约束条件 备注
1  ID 数据 id 字符型 M

2  Datum_Geodetic 大地基准 字符型 M
3  Datum_ele 高程基准 字符型 M
4  Projection 空间投影 字符型 M
5  Accuracy 比例尺 长整型 M
6  AdminRegion 所属行政区划 字符型 M
7  SubdivisionNum 分幅号 字符型 M
8  Program 所属项目 字符型 M
9  Userid 上传者 整型 M
10  Collecttime 采集时间 日期型 M DEM\DLG\D
OM…
11  Datatype 数据类型 字符型 M Shp\GDB\T
IFF...
12  Dataformat 数据格式 字符型 M
13  Accy_H 高程精度 双精度浮点型 M
14  Accy_V 平面精度 双精度浮点型 M
15  PackageName 文件包名称 字符型 O
16  PackageSize 文件包大小 双精度浮点型 O
17  SubdirectoriesNum 子目录数 整型 O
18  FileNum 文件数 整型 O
19  FolderDepth 文件夹深度 整型 O
20  FilePath 文件路径/存储地址 字符型 M
21  MetadataFiles 元数据文件 字符型 O
22  Manufacture 数据生产单位 字符型 O
23  BornTime 数据生产日期 日期型 O
<!-- 第 16 页 -->

序号 字段名称 数据项 字段类型 约束条件 备注
24  InspectionUnit 数据质检单位 字符型 O
25  InspectionTime 数据质检日期 日期型 O
26  PublishUnit 数据发布单位 字符型 O
27  PublishTime 数据发布日期 日期型 O
28  Notes 备注 字符型 O

<!-- 第 17 页 -->

参考文献

[1] 实景三维数据库建库技术规范。
