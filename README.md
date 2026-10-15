 <div align="center">

# 🌐 PROXY SCRAPER

### *Collect. Validate. Measure. Export. ⚡*

A feature-rich Python proxy scraping and validation tool with a live terminal dashboard, concurrent testing, latency statistics, SQLite storage, and Discord webhook support.

[![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Interface](https://img.shields.io/badge/Interface-Rich%20TUI-7C3AED?style=for-the-badge)](https://github.com/Textualize/rich)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-555555?style=for-the-badge)](https://github.com/Hidden-Rhythm/proxy-scraper)

**[Explore the Repository](https://github.com/Hidden-Rhythm/proxy-scraper) · [Report a Bug](https://github.com/Hidden-Rhythm/proxy-scraper/issues)**

</div>

---

## 📖 About

**Proxy Scraper** is a menu-driven Python application that collects public proxy endpoints from multiple online sources, tests candidates against a configurable website, measures response latency, and organizes successful results.

The application uses the [Rich](https://github.com/Textualize/rich) library to create a colorful terminal interface with a live main menu, progress indicators, validation statistics, and a continuously updated dashboard.

It also supports exporting results to multiple formats, storing validation records in SQLite, and sending results to a Discord channel through a webhook.

## ✨ Features

| Feature | Details |
|---|---|
| 🌍 Multiple Sources | Collects proxy candidates from GitHub-hosted lists, proxy APIs, and public proxy-list websites. |
| 🔎 Proxy Scraping | Extracts IPv4 address and port combinations from retrieved source content. |
| ⚡ Concurrent Validation | Tests multiple candidates using `ThreadPoolExecutor`. |
| 📊 Live Dashboard | Displays progress, working and failed counts, success rate, elapsed time, and recent successful results. |
| ⏱️ Latency Measurement | Measures response time and ranks successful results from fastest to slowest. |
| 🎛️ Interactive Settings | Configure the proxy limit, test URL, timeout, worker count, and Discord webhook. |
| 💾 Multiple Export Formats | Saves results as TXT, CSV, and JSON files. |
| 🗄️ SQLite Database | Stores validated proxy addresses, ports, latency, and test timestamps. |
| 💬 Discord Integration | Sends a results summary and a text file through a Discord webhook. |
| 🤖 Full Auto Mode | Runs the scraping, validation, and saving workflow, with optional Discord delivery. |
| 🔄 Source Checker | Checks configured sources for HTTP availability. |
| 🎨 Terminal UI | Uses Rich panels, tables, progress bars, colors, and an ASCII-art title. |

## 🖥️ Terminal Interface

The application includes a live main menu and a separate validation dashboard.

### Main menu

```text
                   PROXY SCRAPER
               Discord · GitHub

╭──────────────────────────────────────────────────────────╮
│ ACTIVE            TIME             SCRAPED         VALID │
├──────────────────────────────────────────────────────────┤
│                       MAIN MENU                          │
│                                                          │
│  [1]  Scrape Proxies                                     │
│  [2]  Validate Proxies                                   │
│  [3]  View Results                                       │
│  [4]  Save Proxies                                       │
│  [5]  Send to Discord                                    │
│  [6]  Settings                                           │
│  [7]  Full Auto Mode                                     │
│  [8]  Update Sources                                     │
│  [9]  View Database                                      │
│  [0]  Exit                                               │
╰──────────────────────────────────────────────────────────╯
```

*Illustrative representation of the actual menu options; exact rendering depends on terminal size.*

### Live validation dashboard

During validation, the application displays:

- Progress percentage and number of proxies tested.
- Number of working and failed candidates.
- Success rate and elapsed time.
- Average latency and a speed indicator.
- Recently validated proxies and their response times.
- The configured test URL, worker count, and timeout.

## ⚙️ Configuration

On startup, the application presents an interactive setup screen. The defaults defined in the source code are:

| Setting | Default | Purpose |
|---|---|---|
| Maximum proxies | `1000` | Maximum number of candidates to collect or test. |
| Worker threads | `50` | Maximum concurrent validation workers. |
| Timeout | `8` seconds | Timeout for each proxy validation request. |
| Test URL | `https://www.youtube.com/` | Website used to test proxy connectivity. |
| Results directory | `proxy_results` | Directory used for exported results. |
| Discord webhook | Empty | Optional webhook URL for sending results. |
| Auto-send | `False` | Enables automatic Discord delivery in Full Auto Mode. |

Use the numbered setup options to change the available settings, save the configuration for the current run, or reset the settings to their defaults.

**Note:** The settings are held in memory by the application; the current code does not persist the configuration between launches.

## 🚀 Getting Started

### Prerequisites

- Python 3 installed.
- An internet connection.
- A terminal that supports interactive input and Rich formatting.

### 1. Clone the repository

```bash
git clone https://github.com/Hidden-Rhythm/proxy-scraper.git
```

### 2. Enter the project directory

```bash
cd proxy-scraper
```

### 3. Install the dependencies

The script attempts to install missing third-party dependencies automatically when it starts. You can install them manually beforehand:

```bash
python -m pip install requests colorama rich pyfiglet fake-useragent
```

### 4. Run the application

**Use the actual filename, including the hyphen:**

```bash
python proxy-scraper.py
```

On Windows, you can also run:

```bash
py proxy-scraper.py
```

Follow the interactive prompts to configure the application and select an action from the main menu.

## 🎮 Menu Guide

| Option | Action |
|---|---|
| `1` | Scrape proxy candidates from the configured sources. |
| `2` | Validate collected candidates and measure response latency. |
| `3` | Display successful results, ordered by speed. |
| `4` | Export validated results to TXT, CSV, and JSON. |
| `5` | Send validated results to Discord using a webhook. |
| `6` | Open the configuration screen. |
| `7` | Run the full scraping, validation, and saving workflow. |
| `8` | Check the availability of configured sources. |
| `9` | View database statistics and the ten fastest stored entries. |
| `0` | Exit the application. |

## 📁 Output Files

The application creates its results directory automatically and initializes a SQLite database.

```text
proxy-scraper/
├── proxy-scraper.py
├── README.md
├── proxies.db
└── proxy_results/
    ├── proxies_fastest_<timestamp>.txt
    ├── proxies_<timestamp>.csv
    └── proxies_<timestamp>.json
```

The database and results directory are generated when the application runs; they are not part of the two-file repository listing shown above.

### Export formats

- **TXT:** Proxy addresses sorted by latency, with timing information.
- **CSV:** Ranked results with IP address, port, and latency in milliseconds.
- **JSON:** Generated metadata and the validated proxy records.

Exported filenames include a timestamp so that separate saves can be kept apart.

## 🗄️ Database

Validation records are stored in `proxies.db` using SQLite.

The `valid_proxies` table contains:

| Field | Description |
|---|---|
| `ip` | Proxy IP address. |
| `port` | Proxy port. |
| `latency` | Measured response time in seconds. |
| `tested_at` | Time recorded for the validation result. |

The database view displays the number of stored records, average recorded latency, database size, and up to ten of the fastest stored entries.

## 💬 Discord Webhook

You can configure a Discord webhook through the settings menu or when choosing the Discord action.

When results are available, the application sends a summary containing the number of working proxies and the fastest and slowest recorded response times, along with a text file of the results.

Full Auto Mode can send the results automatically when Auto-send is enabled and a webhook URL is configured.

**Keep your webhook URL private.** Anyone who obtains it may be able to post messages to its channel.

## 🧰 Built With

| Technology | Purpose |
|---|---|
| Python | Application logic and networking. |
| Requests | Retrieving source lists and testing proxy connectivity. |
| Rich | Terminal dashboard, tables, panels, progress bars, and live rendering. |
| Colorama | Terminal color initialization. |
| PyFiglet | ASCII-art application title. |
| Fake UserAgent | User-Agent selection for requests. |
| ThreadPoolExecutor | Concurrent proxy validation. |
| SQLite | Persistent storage of validation records. |

The application also uses Python's standard library for JSON, CSV, regular expressions, threading, timing, and file management.

## ⚠️ Important Notes

- Public proxies may be unreliable, slow, misconfigured, or operated by untrusted parties.
- A successful test only indicates that a proxy passed the application's configured response checks at that moment.
- Validation is performed using HTTP proxy settings in Requests; collecting an endpoint from a SOCKS-labelled source does not by itself mean the application supports SOCKS protocol validation.
- The current script uses a configurable test URL and accepts selected HTTP response codes as successful validation results.
- Source availability can change over time, and some endpoints may stop working without notice.
- Avoid sending credentials or sensitive information through untrusted proxies.
- Use the tool responsibly and follow applicable laws and the terms of service of the services you access.

## 🤝 Contributing

Suggestions, bug reports, and improvements are welcome.

1. Fork the repository.
2. Create a branch for your changes.
3. Make and test your changes.
4. Open a pull request describing the improvement.

## 🔗 Links

- **Repository:** https://github.com/Hidden-Rhythm/proxy-scraper
- **Source code:** https://github.com/Hidden-Rhythm/proxy-scraper/blob/main/proxy-scraper.py
- **Issues:** https://github.com/Hidden-Rhythm/proxy-scraper/issues
- **Author:** https://github.com/Hidden-Rhythm

---

<div align="center">

### 💜 Built by Hidden-Rhythm

*Collect smarter. Validate faster. Keep your results organized.*

</div>
