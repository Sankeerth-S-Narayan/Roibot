# 🤖 Roibot - Warehouse Robot Simulation

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![WebSocket](https://img.shields.io/badge/WebSocket-SocketIO-orange.svg)](https://flask-socketio.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎬 Demo

![Roibot Warehouse Simulation](simulation.gif)

*A real-time demonstration of the Roibot warehouse robot simulation showing bidirectional snake path navigation, order processing, and live analytics.*

---

A sophisticated real-time simulation of an e-commerce warehouse robot system using bidirectional snake path navigation. This project demonstrates advanced warehouse automation concepts with a web-based visualization interface.

## 🎯 Project Overview

Roibot simulates a single Autonomous Mobile Robot (AMR) operating in a 25x20 warehouse grid using optimized bidirectional snake path navigation. The system generates high-fidelity data for algorithm testing and operational improvements in warehouse automation.

### 🌟 Key Features

- **Real-time 60 FPS simulation** with smooth robot movement
- **Bidirectional snake path navigation** with direction optimization
- **Automatic order generation** every 20 seconds (max 4 items per order)
- **500 inventory locations** with real-time stock tracking
- **Web-based visualization** with HTML5 Canvas and WebSocket integration
- **Live analytics dashboard** with real-time KPIs and performance metrics
- **Interactive controls** for pause/resume and simulation management

## 🏗️ System Architecture

### Core Components

- **Simulation Engine**: Asyncio-based event loop with 60 FPS performance
- **Warehouse Layout**: 25x20 grid with snake pattern navigation
- **Robot Controller**: State machine with smooth movement physics
- **Order Management**: Auto-generation with FIFO queue management
- **Inventory System**: 500 unique items with real-time tracking
- **Analytics Engine**: Real-time KPIs and data export capabilities
- **Web Interface**: Real-time visualization with interactive controls

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Python 3.8+ | Simulation logic & state management |
| **Web Framework** | Flask + SocketIO | Real-time web server |
| **Frontend** | HTML5 Canvas + JavaScript | Real-time visualization |
| **State Management** | Python Dictionaries | In-memory state management |
| **Configuration** | JSON | Layout and parameters |
| **Data Export** | CSV/JSON | KPI and performance metrics |
| **Testing** | pytest | Comprehensive test suite |

## 📊 Warehouse Layout

```
25 Aisles × 20 Racks = 500 Storage Locations
┌─────────────────────────────────────────┐
│ Base/Packout Zone (Aisle 0, Rack 0)   │
├─────────────────────────────────────────┤
│ Aisle 1: Left → Right (Snake Pattern) │
│ Aisle 2: Right → Left                 │
│ Aisle 3: Left → Right                 │
│ ...                                    │
│ Aisle 25: Snake Pattern Navigation    │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8 or higher**
- **Windows 10/11** (optimized for Windows systems)
- **Modern web browser** (Chrome/Edge recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/roibot.git
   cd roibot
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv roibot
   roibot\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-socketio psutil pytest pytest-asyncio black flake8 mypy
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Open your browser**
   Navigate to: **http://localhost:5000**

## 🎮 How to Use

### Web Interface

Once you access `http://localhost:5000`, you'll see:

- **Warehouse Grid**: 25x20 grid showing robot position and movement
- **Robot Visualization**: Real-time robot movement with state indicators
- **Order Queue**: Live order status and assignment tracking
- **KPI Dashboard**: Real-time performance metrics
- **Control Panel**: Pause/resume and simulation controls

### Simulation Features

- **Automatic Order Generation**: New orders every 20 seconds
- **Bidirectional Navigation**: Optimized snake path with direction switching
- **Real-time Analytics**: Live KPIs and performance tracking
- **Smooth Animation**: 60 FPS robot movement with interpolation
- **Inventory Management**: 500 unique items with stock tracking

## 📁 Project Structure

```
roibot/
├── core/                    # Core simulation engine
│   ├── engine.py           # Main simulation engine
│   ├── layout/             # Warehouse layout components
│   ├── inventory/          # Inventory management
│   └── analytics/          # Analytics and performance tracking
├── web_interface/          # Web visualization interface
│   ├── server/             # Flask server and WebSocket handlers
│   ├── static/             # CSS, JavaScript, and assets
│   └── templates/          # HTML templates
├── entities/               # Business logic entities
├── utils/                  # Utility functions and tools
├── tests/                  # Comprehensive test suite
├── tasks/                  # Project management and documentation
├── docs/                   # API and system documentation
└── config/                 # Configuration files
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_engine.py -v
python -m pytest tests/test_web_interface.py -v
```

## 📈 Performance Metrics

The system tracks various KPIs in real-time:

- **Robot Efficiency**: Movement optimization and path savings
- **Order Processing**: Completion times and throughput
- **Inventory Turnover**: Stock movement and utilization
- **System Performance**: 60 FPS rendering and response times

## 🔧 Configuration

The system uses JSON-based configuration for easy customization:

- **Simulation Speed**: Adjustable time acceleration
- **Order Generation**: Configurable intervals and item limits
- **Robot Movement**: Customizable speed and physics
- **Warehouse Layout**: Flexible grid dimensions

## 🛠️ Development

### Code Quality

The project follows strict coding standards:

```bash
# Code formatting
black .

# Linting
flake8 .

# Type checking
mypy .
```

### Phase-Based Development

The project is organized into 11 development phases:

- ✅ **Phase 1-8**: Completed (Foundation through Web Visualization)
- 🔄 **Phase 9**: Order Dashboard & KPI Interface (In Progress)
- ⏳ **Phase 10-11**: Integration & Advanced Features (Planned)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Warehouse Automation Concepts**: Based on real-world AMR navigation strategies
- **Bidirectional Navigation**: Optimized snake path algorithms for efficiency
- **Real-time Visualization**: Modern web technologies for live monitoring
- **Modular Architecture**: Clean, extensible design for future enhancements

## 📞 Support

For questions, issues, or contributions:

- **Issues**: [GitHub Issues](https://github.com/yourusername/roibot/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/roibot/discussions)
- **Documentation**: See the `docs/` folder for detailed guides

---

**Built with ❤️ for warehouse automation research and education**

*Last updated: January 2025* 