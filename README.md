# Mousam Windows · 现代天气应用 (Modern Weather App)

[中文版 (Chinese)](#中文) | [English](#english)

---

<a id="中文"></a>
## 🌟 中文说明

基于知名 Linux 开源天气应用 [Mousam (amit9838/mousam)](https://github.com/amit9838/mousam) 深度重构的 **Windows 11 Fluent 原生天气桌面应用**。

### 🚀 下载与安装 (普通用户)
如果您只想使用该软件，无需配置代码环境：
1. 前往本仓库的 **[Releases](https://github.com/YOUR_USERNAME/mousam-win/releases)** 页面。
2. 下载最新版本的 `MousamWeather.exe`。
3. 双击直接运行即可，无需安装！

### ✨ 核心特色
- **🎨 现代 Windows 11 Fluent 视觉**：支持 Mica / Acrylic 磨砂材质卡片、圆角控件与平滑过渡动效，并提供浅色/深色/跟随系统主题自适应，支持动态修改字体大小。
- **🌤️ 100% 还原 Mousam 数据层**：完全采用 Mousam 的 Open-Meteo 接口设计，精准获取气温、体感、湿度、降水量、紫外线、气压与风速风向。
- **📈 24 小时逐小时趋势图**：横向平滑滚动卡片，直观展示未来 24 小时气温、降雨概率与天气图标。
- **📅 未来 10 天天气预报**：带有平滑温标渐变条的 10 日预报。单击任意一天，即可在上方查看该日详细的 24 小时预报！
- **🌿 核心环境指标**：空气质量 (AQI)、紫外线指数 (UV)、风速风向、湿度露点、标准气压、日出日落。
- **🔍 城市面板与快捷管理**：内置全球城市检索，收藏城市直接在**左侧边栏**生成独立标签。支持右键点击侧边栏城市快速删除。
- **📐 200+ 高清 SVG 矢量天气图标**：完整复用 upstream 资源，在高分屏上清晰无瑕疵。

### 🛠️ 编译与开发 (开发者)

#### 1. 安装依赖
```bash
pip install -r requirements.txt
```

#### 2. 启动源码
```bash
python run.py
```

#### 3. 打包为 `.exe`
本项目提供了一个 `.spec` 配置文件。运行以下命令即可打包出独立的 `.exe` 程序：
```bash
pip install pyinstaller
pyinstaller MousamWeather.spec --clean -y
```
打包完成后即可在 `dist/MousamWeather.exe` 中找到独立程序。

---

<a id="english"></a>
## 🌟 English Description

A **Windows 11 Fluent Design weather application** deeply reconstructed based on the popular Linux open-source weather app [Mousam (amit9838/mousam)](https://github.com/amit9838/mousam).

### 🚀 Download & Install (For Users)
If you just want to use the app without touching any code:
1. Go to the **[Releases](https://github.com/YOUR_USERNAME/mousam-win/releases)** page of this repository.
2. Download the latest `MousamWeather.exe`.
3. Double click to run directly. No installation required!

### ✨ Key Features
- **🎨 Modern Windows 11 Fluent UI**: Supports Mica / Acrylic frosted glass effects, rounded corners, smooth animations, and intelligent light/dark mode switching with dynamic font scaling.
- **🌤️ High Accuracy Data Layer**: Uses Open-Meteo API to fetch temperature, real-feel, humidity, precipitation, UV, pressure, and wind metrics.
- **📈 Hourly Forecast**: Horizontally scrollable 24-hour forecast cards showing temperature, rain probability, and weather icons.
- **📅 10-Day Forecast**: Features a smooth temperature range gradient bar. **Click on any future day** to instantly switch the hourly forecast above to that specific day!
- **🌿 Comprehensive Environmental Metrics**: Air Quality (AQI), UV Index, Wind Direction/Speed, Humidity/Dew Point, Sea-Level Pressure, and Sunrise/Sunset.
- **🔍 City Dashboard**: Built-in global city search. Saved cities are dynamically pinned to the **left sidebar** as individual tabs. Right-click any city in the sidebar to delete it quickly.
- **📐 200+ HD SVG Icons**: Reuses the beautiful `@basmilius` high-resolution vector icons from the original Mousam project.

### 🛠️ Build & Development (For Developers)

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Run from Source
```bash
python run.py
```

#### 3. Build `.exe` Executable
This project includes a pre-configured `.spec` file. Run the following to build your own standalone `.exe`:
```bash
pip install pyinstaller
pyinstaller MousamWeather.spec --clean -y
```
The compiled executable will be available at `dist/MousamWeather.exe`.
