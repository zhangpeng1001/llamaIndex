# 实景三维质检大数据支撑库 时空数据规范 第4部分 标志性地物

> 来源：实景三维质检大数据支撑库 时空数据规范 第4部分 标志性地物.pdf（增强版提取，已去目录/页眉/页码噪声）


第 4 部分 标志性地物

（草案）

2025 年7 月

前 言

本文件按照GB/T 1.1—2020《标准化工作导则  第1部分：标准化文件的结构和起草规

则》的规定起草。

第1部分 数据分类与基本规定

第2部分 检测点

第3部分 检测线

第5部分 重要要素

第6部分 高精度栅格数据

第7部分 资源数据

请注意本文件的某些内容可能涉及专利。本文件的发布机构不承担识别专利的责任。

起草单位：

起草人员：

<!-- chapter_no=1; chapter_title=范围; section_type=范围; knowledge_type=scope_intro -->
# 1 范围

<!-- section_type=范围; knowledge_type=scope_intro -->
定义、选取规则、分类与代码、数据要求、入库流程。标志性地物成

<!-- section_type=范围; knowledge_type=scope_intro -->
果适用于二维与三维实景三维成果的数学精度、属性精度验收检验，

<!-- section_type=范围; knowledge_type=scope_intro -->
为实景三维成果质量检验提供标准化真值。

<!-- chapter_no=2; chapter_title=引用文件; section_type=范围; knowledge_type=scope_intro -->
# 2 引用文件

<!-- section_type=范围; knowledge_type=scope_intro -->
GB/T 13923-2006《基础地理信息要素分类与代码》

<!-- section_type=范围; knowledge_type=scope_intro -->
GB/T 18316-2008《数字测绘成果质量检查与验收》

<!-- section_type=范围; knowledge_type=scope_intro -->
GB/T 24356-2023《测绘成果质量检查与验收》

<!-- section_type=范围; knowledge_type=scope_intro -->
CH/T 9024-2014《三维地理信息模型数据产品质量检查与验收》

<!-- section_type=范围; knowledge_type=scope_intro -->
《实景三维中国建设技术大纲（2024）》

<!-- chapter_no=3; chapter_title=术语与定义; section_type=范围; knowledge_type=scope_intro -->
# 3 术语与定义

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物

<!-- section_type=范围; knowledge_type=scope_intro -->
空间上具有显著位置特征， 视觉上具有独特性， 能够长期稳定性

<!-- section_type=范围; knowledge_type=scope_intro -->
存在， 具有较高空间辨识度和典型代表性或承载一定的文化意义， 可

<!-- section_type=范围; knowledge_type=scope_intro -->
作为实景三维成果质量检验的参照的地理实体， 如大型桥梁、 标志性

<!-- section_type=范围; knowledge_type=scope_intro -->
建筑等。

<!-- chapter_no=4; chapter_title=选取原则; section_type=范围; knowledge_type=scope_intro -->
# 4 选取原则

<!-- section_type=范围; knowledge_type=scope_intro -->
（1）显著性及可识别性

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物应具有视觉独特性及空间位置特征显著性， 在遥感影

<!-- section_type=范围; knowledge_type=scope_intro -->
像或实地环境中应具有较高的空间辨识度。 二维数据应具有清晰边界

<!-- section_type=范围; knowledge_type=scope_intro -->
或点位特征，三维数据应具有立体特征。

<!-- section_type=范围; knowledge_type=scope_intro -->
（2）稳定性及典型性

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物应长期存在， 不易受自然或人为因素影响而改变形态

<!-- section_type=范围; knowledge_type=scope_intro -->
或位置， 应涵盖自然地理实体和人工地理实体， 确保质检大数据支撑

<!-- section_type=范围; knowledge_type=scope_intro -->
库对多场景实景三维成果的适用性。

<!-- section_type=范围; knowledge_type=scope_intro -->
（3）可靠性及高精度

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物应确保数学精度、 属性精度的准确可靠， 已确定的标

<!-- section_type=范围; knowledge_type=scope_intro -->
志性地物应优先选取高精度成果， 其数学精度应符合相应尺度的成果

<!-- section_type=范围; knowledge_type=scope_intro -->
规范要求， 保证比对检查的精度， 有利于实现多尺度实景三维成果质

<!-- section_type=范围; knowledge_type=scope_intro -->
量检验。

<!-- chapter_no=5; chapter_title=分类与代码; section_type=范围; knowledge_type=scope_intro -->
# 5 分类与代码

<!-- section_type=范围; knowledge_type=scope_intro -->
依据 《基础地理实体分类与代码》 及 《基础地理信息要素分类与

<!-- section_type=范围; knowledge_type=scope_intro -->
代码》 ， 确定标志性地物的基础地理实体、 基础地理信息要素及相应

<!-- section_type=范围; knowledge_type=scope_intro -->
代码，详见附录A。各地可结合实景三维成果质量检验的应用需求，

<!-- section_type=范围; knowledge_type=scope_intro -->
在附录A中选取标志性地物。

<!-- chapter_no=6; chapter_title=数据要求; section_type=范围; knowledge_type=scope_intro -->
# 6 数据要求

<!-- section_type=范围; knowledge_type=scope_intro -->
（1）时空基准

<!-- section_type=范围; knowledge_type=scope_intro -->
坐标系统： 2000国家大地坐标系（ China Geodetic Coordinate

<!-- section_type=范围; knowledge_type=scope_intro -->
System 2000，CGCS2000）。

<!-- section_type=范围; knowledge_type=scope_intro -->
高程基准：1985国家高程基准。

<!-- section_type=范围; knowledge_type=scope_intro -->
时间基准：公元纪年和北京时间。

<!-- section_type=范围; knowledge_type=scope_intro -->
地图投影与分带：高斯-克吕格3°分带投影，确有必要，也可采

<!-- section_type=范围; knowledge_type=scope_intro -->
用高斯-克吕格1.5°分带投影。

<!-- section_type=范围; knowledge_type=scope_intro -->
（2）数学精度

<!-- section_type=范围; knowledge_type=scope_intro -->
数学精度包括平面精度、 高程精度、 高度精度。 标志性地物具有

<!-- section_type=范围; knowledge_type=scope_intro -->
多尺度特征， 选取入库的标志性地物数学精度应符合相应尺度的成果

<!-- section_type=范围; knowledge_type=scope_intro -->
规范要求。

<!-- section_type=范围; knowledge_type=scope_intro -->
（3）属性精度

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物属性成果属性表结构、 属性项内容名称及值域等应符

<!-- section_type=范围; knowledge_type=scope_intro -->
合附录B要求，各地可结合实景三维成果质量检验的应用需求，增加

<!-- section_type=范围; knowledge_type=scope_intro -->
属性项。

<!-- section_type=范围; knowledge_type=scope_intro -->
（4）存储格式

<!-- section_type=范围; knowledge_type=scope_intro -->
二维标志性地物可采用ShapeFile、MDB、GDB数据格式。

<!-- section_type=范围; knowledge_type=scope_intro -->
三维标志性地物可采用OBJ数据格式。

<!-- section_type=范围; knowledge_type=scope_intro -->
地面照片、影像截图、纹理等可采用JPG、TIF数据格式

<!-- section_type=范围; knowledge_type=scope_intro -->
（5）成果构成

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物数据成果由空间数据 （点、 线、 面、 体） 、 属性数据、

<!-- section_type=范围; knowledge_type=scope_intro -->
地面照片、影像截图、纹理构成。

<!-- chapter_no=7; chapter_title=采集要求及数据结构; section_type=范围; knowledge_type=scope_intro -->
# 7 采集要求及数据结构

<!-- section_type=范围; knowledge_type=scope_intro -->
（1）数据源

<!-- section_type=范围; knowledge_type=scope_intro -->
基于多尺度数字线划图、 数字正射影像、 基础地理实体数据、城

<!-- section_type=范围; knowledge_type=scope_intro -->
市国土空间监测、实景 三维模型、Mesh三维模型及其他资料生产或

<!-- section_type=范围; knowledge_type=scope_intro -->
提取标志性地物成果，综合分析各数据源的情况，优先选取精度高、

<!-- section_type=范围; knowledge_type=scope_intro -->
现势性强成果作为主要数据源。 对于复杂地物， 可补充外业实测数据。

<!-- section_type=范围; knowledge_type=scope_intro -->
（2）采集要求

<!-- section_type=范围; knowledge_type=scope_intro -->
基于各数据源提取标志性地物， 其几何精度应与数据源精度一致，

<!-- section_type=范围; knowledge_type=scope_intro -->
其数据源的属性值中存在错误的， 应修改完善， 确保标志性地物准确

<!-- section_type=范围; knowledge_type=scope_intro -->
可靠。

<!-- section_type=范围; knowledge_type=scope_intro -->
基于各数据源采集标志性地物， 根据标志性地物用途及数据源的

<!-- section_type=范围; knowledge_type=scope_intro -->
实际情况，采集标志性地物 几何精度不低于来源影像或 Mesh三维模

<!-- section_type=范围; knowledge_type=scope_intro -->
型， 达到1:500、1:1000、1:2000、1:5000、1:10000数字线划图或LOD1.3、

<!-- section_type=范围; knowledge_type=scope_intro -->
LOD2.1、LOD2.2、LOD2.3、LOD3.1等三维模型数据几何精度。利用收

<!-- section_type=范围; knowledge_type=scope_intro -->
集权威专题资料，按照附录B要求填写标志性地物基本属性。

<!-- section_type=范围; knowledge_type=scope_intro -->
生产或提取标志性地物成果质量应符合《数字测绘成果质量检查

<!-- section_type=范围; knowledge_type=scope_intro -->
与验收》《测绘成果质量检查与验收》 《实景三维中国建设技术大纲

<!-- section_type=范围; knowledge_type=scope_intro -->
（2024）》相关要求。

<!-- section_type=范围; knowledge_type=scope_intro -->
（3）数据结构

<!-- section_type=范围; knowledge_type=scope_intro -->
二维标志性地物以点、线、面图层形式存储，文件命名为BZXDW。

<!-- section_type=范围; knowledge_type=scope_intro -->
数据结构如表1。

<!-- section_type=范围; knowledge_type=scope_intro -->
表1 标志性地物子库数据结构

<!-- section_type=范围; knowledge_type=scope_intro -->
编号 数据层名 类型 要素类中文名称

<!-- chapter_no=1; chapter_title=BZXDW_P 点层 点状标志性地物; section_type=范围; knowledge_type=scope_intro -->
# 1 BZXDW_P 点层 点状标志性地物

<!-- chapter_no=2; chapter_title=BZXDW_L 线层 线状标志性地物; section_type=范围; knowledge_type=scope_intro -->
# 2 BZXDW_L 线层 线状标志性地物

<!-- chapter_no=3; chapter_title=BZXDW_A 面层 面状标志性地物; section_type=范围; knowledge_type=scope_intro -->
# 3 BZXDW_A 面层 面状标志性地物

<!-- section_type=范围; knowledge_type=scope_intro -->
三维标志性地物以体形式存储，三维模型数据文件（.obj）结构

<!-- section_type=范围; knowledge_type=scope_intro -->
按照《实景三维中国建设城市三维模型（LOD1.3级）快速构建技术规

<!-- section_type=范围; knowledge_type=scope_intro -->
定》要求执行，数据文件名为“该建筑三维模型代码”-bz。

<!-- section_type=范围; knowledge_type=scope_intro -->
纹理数据命名按照《实景三维中国建设城市三维模型（ LOD1.3

<!-- section_type=范围; knowledge_type=scope_intro -->
级）快速构建技术规定》要求，采用18位字符，命名为“建（构）筑

<!-- section_type=范围; knowledge_type=scope_intro -->
物所在街道的行政区划代码”“建（构）筑物序号” -“建（构）筑

<!-- section_type=范围; knowledge_type=scope_intro -->
物纹理的位置标识”“纹理序号（两位）”。

<!-- section_type=范围; knowledge_type=scope_intro -->
地面照片命名为“空间身份编码”-dmzp。

<!-- section_type=范围; knowledge_type=scope_intro -->
影像截图命名为“空间身份编码”-yxjt。

<!-- chapter_no=8; chapter_title=入库流程; section_type=范围; knowledge_type=scope_intro -->
# 8 入库流程

<!-- section_type=范围; knowledge_type=scope_intro -->
基于多尺度数字线划图、数字正射影像、三维模型及其他资料，

<!-- section_type=范围; knowledge_type=scope_intro -->
生产或提取标志性地物成果。 经格式转换、 坐标转换等预处理后， 对

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物成果进行入库前质量检查， 合格成果入实景三维质检大数

<!-- section_type=范围; knowledge_type=scope_intro -->
据支撑库。 入库完成后检查标志性地物成果质量， 经验收合格后， 形

<!-- section_type=范围; knowledge_type=scope_intro -->
C。

<!-- chapter_no=9; chapter_title=数据应用; section_type=范围; knowledge_type=scope_intro -->
# 9 数据应用

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物因其具有“空间显著性、视觉独特性，承载文化性”

<!-- section_type=范围; knowledge_type=scope_intro -->
的特征， 在基础地理实体数据成果及传统测绘成果质量检验中具有重

<!-- section_type=范围; knowledge_type=scope_intro -->
要意义。 在传统测绘成果质量检验中， 标志性地物可作为检查几何精

<!-- section_type=范围; knowledge_type=scope_intro -->
度、属性精度、完整性检查提供高精度、高可靠性的参考数据。在基

<!-- section_type=范围; knowledge_type=scope_intro -->
础地理实体数据成果质量检验中， 标志性地物因具有高度特征和纹理

<!-- section_type=范围; knowledge_type=scope_intro -->
信息，可作为检查基础地理实体几何精度、属性精度、完整性、逻辑

<!-- section_type=范围; knowledge_type=scope_intro -->
一致性、 场景效果的参考数据， 实现基础地理实体质量检查从规范符

<!-- section_type=范围; knowledge_type=scope_intro -->
合性向场景适用性转变。

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物子库应用方式主要有人工套合比对和软件自动比对

<!-- section_type=范围; knowledge_type=scope_intro -->
两种应用路径，两种应用路径的主要内容和方式如下：

<!-- section_type=范围; knowledge_type=scope_intro -->
（1）人工套合检查

<!-- section_type=范围; knowledge_type=scope_intro -->
人工套合检查方式主要是质检人员在检查时， 将标志性地物子库

<!-- section_type=范围; knowledge_type=scope_intro -->
数据加载到相应的地理信息软件中， 与待检成果开展比对分析， 检查

<!-- section_type=范围; knowledge_type=scope_intro -->
待检成果更新的完整性、正确性。

<!-- section_type=范围; knowledge_type=scope_intro -->
（2）软件自动比对

<!-- section_type=范围; knowledge_type=scope_intro -->
软件自动比对方式主要是利用自动化检查软件， 将标志性地物子

<!-- section_type=范围; knowledge_type=scope_intro -->
库中的标志性地物作为参考数据， 对待检成果开展位置比对分析或属

<!-- section_type=范围; knowledge_type=scope_intro -->
性比对分析，以检查同名位置的实体的完整性及属性的正确性。

<!-- section_type=范围; knowledge_type=scope_intro -->
附录 A 标志性地物基础地理实体、基础地理信息要素及代码表

<!-- section_type=范围; knowledge_type=scope_intro -->
基础地理实体分类与代码 基础地理信息要素分类与代码

<!-- section_type=范围; knowledge_type=scope_intro -->
用途

<!-- section_type=范围; knowledge_type=scope_intro -->
一级类 二级类 分类代

<!-- section_type=范围; knowledge_type=scope_intro -->
码 三级类 实体

<!-- section_type=范围; knowledge_type=scope_intro -->
分类代码

<!-- section_type=范围; knowledge_type=scope_intro -->
要素

<!-- section_type=范围; knowledge_type=scope_intro -->
分类代码 要素名称

<!-- section_type=范围; knowledge_type=scope_intro -->
山体 其他山体相关实体 110800 独立石 110802 750103 独立石 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
水利 水利附属设施 210400

<!-- section_type=范围; knowledge_type=scope_intro -->
堤防 210401 270101 主要堤（含堤顶边线） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
坝 210403

<!-- section_type=范围; knowledge_type=scope_intro -->
270500 滚水坝（依比例） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
270600 半依比例、依比例拦水坝

<!-- section_type=范围; knowledge_type=scope_intro -->
（能通车的， 含依比例拦水坝坝顶线） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
270601 半依比例拦水坝（不能通车的） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
270700 防波堤、制水坝 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
交通 桥梁 220600

<!-- section_type=范围; knowledge_type=scope_intro -->
铁路桥 220601 450305 铁路桥（半依比例、依比例） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
公路桥 220602 450301 公路桥（半依比例、依比例） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
公铁两用桥 220603

<!-- section_type=范围; knowledge_type=scope_intro -->
450302 铁路、公路两用双层桥 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
450303 车行并行桥 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
人行桥 220606 450502 人行桥（依比例） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
450503 缆索桥 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
450504 级面桥、人行拱桥 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
450505 亭桥、廊桥 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
450506 溜索桥 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
450507 栈桥 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
建 （构）

<!-- section_type=范围; knowledge_type=scope_intro -->
筑物及

<!-- section_type=范围; knowledge_type=scope_intro -->
设施

<!-- section_type=范围; knowledge_type=scope_intro -->
房屋 230100 普通房屋 230101

<!-- section_type=范围; knowledge_type=scope_intro -->
310300 单幢房屋（依比例） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
310400 突出房屋(依比例) 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
310500 高层房屋(依比例) 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
310501 超高层房屋(依比例) 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
名胜古迹设施 230900

<!-- section_type=范围; knowledge_type=scope_intro -->
长城、古城墙 230901

<!-- section_type=范围; knowledge_type=scope_intro -->
380101

<!-- section_type=范围; knowledge_type=scope_intro -->
不依比例砖石城墙、长城 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
依比例砖石城墙、长城 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
380102

<!-- section_type=范围; knowledge_type=scope_intro -->
不依比例砖石城墙、长城(破坏) 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
依比例砖石城墙、长城(破坏) 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
烽火台、碉堡 230902 350101 烽火台 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
350102 旧碉堡、旧地堡 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
牌楼、 牌坊、 彩

<!-- section_type=范围; knowledge_type=scope_intro -->
门 230903 350203 彩门、牌坊、牌楼 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
钟鼓楼、城楼、

<!-- section_type=范围; knowledge_type=scope_intro -->
古关塞 230904

<!-- section_type=范围; knowledge_type=scope_intro -->
350204 钟楼、鼓楼、城楼、古关塞 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
311007 碉楼 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
碑、像 230905

<!-- section_type=范围; knowledge_type=scope_intro -->
350206 文物碑石 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
350208 纪念像、艺术塑像 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
350201 纪念碑、柱、墩 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
亭、坛 230906 350205 亭 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
观景塔、纪念

<!-- section_type=范围; knowledge_type=scope_intro -->
塔、标志塔 230907

<!-- section_type=范围; knowledge_type=scope_intro -->
321103 瞭望塔 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
360400 宝塔、经塔、纪念塔（纪念塔） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
遗址 230908 350100 古遗迹、遗址 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
宗教设施 231000 宝塔、经塔 231001 360400 宝塔、经塔、纪念塔（宝塔、经塔） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
院落 公共管理与公共服务 250200 机关团体新闻

<!-- section_type=范围; knowledge_type=scope_intro -->
出版 250201

<!-- section_type=范围; knowledge_type=scope_intro -->
311102 省级政府位置标识点 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
311103 地级政府位置标识点 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
311104 县级政府位置标识点 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
311105 乡级政府位置标识点 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
311106 村委会位置标识点 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
科教文卫 250202

<!-- section_type=范围; knowledge_type=scope_intro -->
340101 学校（大学） 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
340111 学校（中、小学、职业教育学校） 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
340103 馆（科技馆、博物馆、展览馆） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
340401 露天体育场 （依比例 TYPE： 球场除外） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
340403 体育馆 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
交通运输 250600

<!-- section_type=范围; knowledge_type=scope_intro -->
铁路场站 250601 410301 火车站 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
交通服务场站 250603 450103 长途汽车站 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
港口 250604 460101 水运港客运站 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
机场 250605 480100 飞机场 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
特殊场院 250700 宗教场院 250703

<!-- section_type=范围; knowledge_type=scope_intro -->
360100 庙宇 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
360200 清真寺 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
360300 教堂 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
殡葬场院 250706

<!-- section_type=范围; knowledge_type=scope_intro -->
340303 陵园 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
340701 公墓（依比例） 定位

<!-- section_type=范围; knowledge_type=scope_intro -->
340704 殡葬场所 定性

<!-- section_type=范围; knowledge_type=scope_intro -->
附录 B 标志性地物基本属性

<!-- section_type=范围; knowledge_type=scope_intro -->
序号 属性项名称 属性项中文简称 字段类型 约束条件 长度 值域或示例 备注

<!-- chapter_no=1; chapter_title=EntityName 实体名称 字符型 M 60  如果实体没有名称，填写null; section_type=范围; knowledge_type=scope_intro -->
# 1 EntityName 实体名称 字符型 M 60  如果实体没有名称，填写null

<!-- chapter_no=2; chapter_title=Alias 别名 字符型 C 50  当搜集到实体别名资料时，必填; section_type=范围; knowledge_type=scope_intro -->
# 2 Alias 别名 字符型 C 50  当搜集到实体别名资料时，必填

<!-- chapter_no=3; chapter_title=GB 要素分类代码 字符型 O 10  按照《基础地理信息要素分类与代码》; section_type=范围; knowledge_type=scope_intro -->
# 3 GB 要素分类代码 字符型 O 10  按照《基础地理信息要素分类与代码》

<!-- section_type=范围; knowledge_type=scope_intro -->
填写

<!-- chapter_no=4; chapter_title=DWMC 要素名称 字符型 O 50  按照《基础地理信息要素分类与代码》; section_type=范围; knowledge_type=scope_intro -->
# 4 DWMC 要素名称 字符型 O 50  按照《基础地理信息要素分类与代码》

<!-- section_type=范围; knowledge_type=scope_intro -->
填写

<!-- chapter_no=5; chapter_title=EntityID 空间身份编码 字符型 M 100; section_type=范围; knowledge_type=scope_intro -->
# 5 EntityID 空间身份编码 字符型 M 100

<!-- chapter_no=6; chapter_title=FormerID 历史空间身份编码 字符型 C 100  因实体变更产生新的编码时，必填; section_type=范围; knowledge_type=scope_intro -->
# 6 FormerID 历史空间身份编码 字符型 C 100  因实体变更产生新的编码时，必填

<!-- chapter_no=7; chapter_title=LocationID 位置码 字符型 O 50; section_type=范围; knowledge_type=scope_intro -->
# 7 LocationID 位置码 字符型 O 50

<!-- chapter_no=8; chapter_title=ClassID 实体分类代码 字符型 M 6; section_type=范围; knowledge_type=scope_intro -->
# 8 ClassID 实体分类代码 字符型 M 6

<!-- chapter_no=9; chapter_title=ClassName 分类名称 字符型 M 30; section_type=范围; knowledge_type=scope_intro -->
# 9 ClassName 分类名称 字符型 M 30

<!-- chapter_no=10; chapter_title=LoadTime 入库时间 日期型 M   格式“YYYY/MM/DD”; section_type=范围; knowledge_type=scope_intro -->
# 10 LoadTime 入库时间 日期型 M   格式“YYYY/MM/DD”

<!-- chapter_no=11; chapter_title=UpdateSts 更新状态 字符型 O 8 新增/修改/删除; section_type=范围; knowledge_type=scope_intro -->
# 11 UpdateSts 更新状态 字符型 O 8 新增/修改/删除

<!-- chapter_no=12; chapter_title=UpdateTime 更新时间 日期型 O   格式“YYYY/MM/DD”; section_type=范围; knowledge_type=scope_intro -->
# 12 UpdateTime 更新时间 日期型 O   格式“YYYY/MM/DD”

<!-- chapter_no=13; chapter_title=ModelID 建筑三维模型代码 字符型 C 20  三维建（构）筑物及设施标志性地物必; section_type=范围; knowledge_type=scope_intro -->
# 13 ModelID 建筑三维模型代码 字符型 C 20  三维建（构）筑物及设施标志性地物必

<!-- section_type=范围; knowledge_type=scope_intro -->
填

<!-- chapter_no=14; chapter_title=Function 功用类型 字符型 C 20; section_type=范围; knowledge_type=scope_intro -->
# 14 Function 功用类型 字符型 C 20

<!-- section_type=范围; knowledge_type=scope_intro -->
堤防：干堤/一般堤

<!-- section_type=范围; knowledge_type=scope_intro -->
坝：拦水坝/滚水坝/制水

<!-- section_type=范围; knowledge_type=scope_intro -->
坝

<!-- section_type=范围; knowledge_type=scope_intro -->
院落：学校/医院//庙宇/

<!-- section_type=范围; knowledge_type=scope_intro -->
清真寺/教堂/道观/长途

<!-- section_type=范围; knowledge_type=scope_intro -->
客运站

<!-- section_type=范围; knowledge_type=scope_intro -->
堤防、坝、学校、医院、/庙宇、清真

<!-- section_type=范围; knowledge_type=scope_intro -->
寺、教堂、道观、长途客运站必填

<!-- section_type=范围; knowledge_type=scope_intro -->
序号 属性项名称 属性项中文简称 字段类型 约束条件 长度 值域或示例 备注

<!-- chapter_no=15; chapter_title=SubsType 表质类型 字符型 O 20 坝：砼/石 坝填写; section_type=范围; knowledge_type=scope_intro -->
# 15 SubsType 表质类型 字符型 O 20 坝：砼/石 坝填写

<!-- chapter_no=16; chapter_title=Transit 通行性 字符型 C 10 通车/不通车/不能走人 坝必填; section_type=范围; knowledge_type=scope_intro -->
# 16 Transit 通行性 字符型 C 10 通车/不通车/不能走人 坝必填

<!-- chapter_no=17; chapter_title=UseState 使用状态 字符型 O 10 利用/废弃/破坏 堤防、坝、桥梁填写; section_type=范围; knowledge_type=scope_intro -->
# 17 UseState 使用状态 字符型 O 10 利用/废弃/破坏 堤防、坝、桥梁填写

<!-- chapter_no=18; chapter_title=LoadCap 载重量 浮点型 C 10  桥梁必填写; section_type=范围; knowledge_type=scope_intro -->
# 18 LoadCap 载重量 浮点型 C 10  桥梁必填写

<!-- chapter_no=19; chapter_title=MaxHeight 限高 浮点型 O 10  桥梁填写; section_type=范围; knowledge_type=scope_intro -->
# 19 MaxHeight 限高 浮点型 O 10  桥梁填写

<!-- chapter_no=20; chapter_title=Length 长度 浮点型 O 10  桥梁填写; section_type=范围; knowledge_type=scope_intro -->
# 20 Length 长度 浮点型 O 10  桥梁填写

<!-- chapter_no=21; chapter_title=ConstSts 建设状态 字符型 O 10 建筑中/建成 桥梁、普通房屋填写; section_type=范围; knowledge_type=scope_intro -->
# 21 ConstSts 建设状态 字符型 O 10 建筑中/建成 桥梁、普通房屋填写

<!-- chapter_no=22; chapter_title=OpenYear 通车年份 日期型 O   桥梁填写; section_type=范围; knowledge_type=scope_intro -->
# 22 OpenYear 通车年份 日期型 O   桥梁填写

<!-- chapter_no=23; chapter_title=FloorNum 房屋层数 整数型 C 6  普通房屋城市级成果必填; section_type=范围; knowledge_type=scope_intro -->
# 23 FloorNum 房屋层数 整数型 C 6  普通房屋城市级成果必填

<!-- chapter_no=24; chapter_title=FloorNumUn 地下房屋层数 整数型 O 6  普通房屋城市级成果填写; section_type=范围; knowledge_type=scope_intro -->
# 24 FloorNumUn 地下房屋层数 整数型 O 6  普通房屋城市级成果填写

<!-- chapter_no=25; chapter_title=StrucType 结构类型 字符型 C 20 钢/ 钢筋混凝土 /混合 结; section_type=范围; knowledge_type=scope_intro -->
# 25 StrucType 结构类型 字符型 C 20 钢/ 钢筋混凝土 /混合 结

<!-- section_type=范围; knowledge_type=scope_intro -->
构/砖（石）木 普通房屋城市级成果必填

<!-- chapter_no=26; chapter_title=ConstArea 建筑面积 浮点型 C 10  普通房屋城市级成果必填; section_type=范围; knowledge_type=scope_intro -->
# 26 ConstArea 建筑面积 浮点型 C 10  普通房屋城市级成果必填

<!-- chapter_no=27; chapter_title=BaseArea 基底面积 浮点型 C 10  普通房屋城市级成果必填; section_type=范围; knowledge_type=scope_intro -->
# 27 BaseArea 基底面积 浮点型 C 10  普通房屋城市级成果必填

<!-- chapter_no=28; chapter_title=CpltAge 竣工年代 日期型 O   普通房屋填写; section_type=范围; knowledge_type=scope_intro -->
# 28 CpltAge 竣工年代 日期型 O   普通房屋填写

<!-- chapter_no=29; chapter_title=Address 地址 字符型 O 100  普通房屋填写; section_type=范围; knowledge_type=scope_intro -->
# 29 Address 地址 字符型 O 100  普通房屋填写

<!-- chapter_no=30; chapter_title=Function 功用类型 字符型 O 20 普通房屋：普通/突出/高; section_type=范围; knowledge_type=scope_intro -->
# 30 Function 功用类型 字符型 O 20 普通房屋：普通/突出/高

<!-- section_type=范围; knowledge_type=scope_intro -->
层 普通房屋填写

<!-- chapter_no=31; chapter_title=AdminRegion 所属行政区域 字符型 M 50  格式“**省**市***县***乡**村”; section_type=范围; knowledge_type=scope_intro -->
# 31 AdminRegion 所属行政区域 字符型 M 50  格式“**省**市***县***乡**村”

<!-- chapter_no=32; chapter_title=Scale 比例尺 字符型 C 10 1:500 二维标志性地物必填; section_type=范围; knowledge_type=scope_intro -->
# 32 Scale 比例尺 字符型 C 10 1:500 二维标志性地物必填

<!-- section_type=范围; knowledge_type=scope_intro -->
33 LOD 三维模型LOD 层级 字符型 C 4 LOD1.3 三维标志性地物必填

<!-- chapter_no=34; chapter_title=DataPhase 数据时相 整数型 M 10  格式“YYYY”; section_type=范围; knowledge_type=scope_intro -->
# 34 DataPhase 数据时相 整数型 M 10  格式“YYYY”

<!-- chapter_no=35; chapter_title=Use 用途 字符型 M 4 定位/定性; section_type=范围; knowledge_type=scope_intro -->
# 35 Use 用途 字符型 M 4 定位/定性

<!-- section_type=范围; knowledge_type=scope_intro -->
注 1：表中约束条件“M”为必选项，“C”为条件必选项，“O”为可选项。

<!-- section_type=范围; knowledge_type=scope_intro -->
序号 属性项名称 属性项中文简称 字段类型 约束条件 长度 值域或示例 备注

<!-- section_type=范围; knowledge_type=scope_intro -->
注 2：对于浮点型字段，除特殊情况外，保留小数点后2 位。

<!-- section_type=范围; knowledge_type=scope_intro -->
附录 C 标志性地物选取入库流程图

<!-- section_type=范围; knowledge_type=scope_intro -->
数据预处理

<!-- section_type=范围; knowledge_type=scope_intro -->
入库前质量检查 问题数据修改N

<!-- section_type=范围; knowledge_type=scope_intro -->
提取

<!-- section_type=范围; knowledge_type=scope_intro -->
多尺度数字线划图 数字正射影像 三维模型 其他资料

<!-- section_type=范围; knowledge_type=scope_intro -->
标志性地物成果

<!-- section_type=范围; knowledge_type=scope_intro -->
生产

<!-- section_type=范围; knowledge_type=scope_intro -->
数据库验收

<!-- section_type=范围; knowledge_type=scope_intro -->
合格数据

<!-- section_type=范围; knowledge_type=scope_intro -->
入库后质量检查

<!-- section_type=范围; knowledge_type=scope_intro -->
Y

<!-- section_type=范围; knowledge_type=scope_intro -->
数据库更新

<!-- section_type=范围; knowledge_type=scope_intro -->
管理系统运维
