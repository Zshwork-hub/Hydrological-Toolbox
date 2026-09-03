# ArcMap 基准案例

`case01_yuzhong.json` 记录案例一的输入、处理参数和参考输出。原始 ArcMap 数据保存在项目目录中的 `arcgis案例/`，由于体量较大，不纳入 Git 仓库；清单中的相对路径默认从项目根目录解析。

当前基准流程为：裁剪 DEM -> Fill -> Flow Direction (D8, NORMAL) -> Flow Accumulation (FLOAT, D8) -> `FlowAcc >= 30000` 提取河网 -> Strahler 河流分级。

参考结果：

- 出水口：榆中站点图层；
- 流域边界：宛川河流域面；
- 河网：`rivernet3w.tif` 和 `rivernet3w.shp`；
- 统计：面积输出 `km2`，周长输出 `km`，默认使用 WGS84 测地线计算；
- ArcGIS 基准：ArcMap Desktop 10.8.2。

案例二暂不作为第一版精度基准。
