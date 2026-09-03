# 流域提取工具

这是一个面向 Windows 的 Python 3 流域提取与水文预处理工具，第一版以接近 ArcMap 水文分析结果为目标。

## 第一版范围

- DEM 预处理、洼地填充、D8 流向和汇流累积；
- 按汇流累积阈值提取河网；
- 点图层、表格和地图交互选取出水口；
- 单个和批量完整上游流域提取；
- 后续支持互不重叠的分区子流域；
- 输出流域栅格、矢量边界、河网和统计表。

## 当前状态

当前版本完成项目骨架、案例清单和非破坏性路径检查。水文计算引擎尚未接入。

## 本地检查

建议使用 Python 3.10 或更新版本创建项目环境，然后安装项目依赖：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

检查案例一文件是否齐全：

```powershell
python -m basin_tool validate-case benchmarks/case01_yuzhong.json
```

查看案例元数据和栅格/矢量摘要：

```powershell
python -m basin_tool inspect-case benchmarks/case01_yuzhong.json --json
```

原始案例文件不会由项目自动修改，也不应直接提交到 Git；`arcgis案例/` 已加入忽略规则。
