import os
import sys
import json
import time
import subprocess
import importlib
from datetime import datetime
from typing import List, Set, Dict, Optional
import warnings
warnings.filterwarnings('ignore')

# Auto-install
def install():
    packages = {
        'requests': 'requests',
        'colorama': 'colorama',
        'rich': 'rich',
        'pyfiglet': 'pyfiglet',
        'fake-useragent': 'fake_useragent',
    }
    for pkg, mod in packages.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg],
                                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass

install()

from colorama import init, Fore, Style
from rich.console import Console, Group
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich import box
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
from rich.rule import Rule
from rich.text import Text
import pyfiglet
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import re
import csv
import random
import sqlite3
import shutil
import threading

init(autoreset=True)
console = Console()

# AUTHOR
AUTHOR_DISCORD = "hidden_rhythm"
AUTHOR_GITHUB = "https://github.com/Hidden-Rhythm"

# Sources
SOURCE_LIST_1 = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/https.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks4.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/socks5.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    "https://raw.githubusercontent.com/UserR3X/proxy-list/main/online/http.txt",
    "https://raw.githubusercontent.com/mmpx12/proxy-list/master/http.txt",
    "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    "https://raw.githubusercontent.com/rdavydov/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/zevtyardt/proxy-list/main/http.txt",
]

SOURCE_LIST_2 = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all",
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://www.proxy-list.download/api/v1/get?type=socks4",
    "https://www.proxy-list.download/api/v1/get?type=socks5",
    "https://api.openproxy.space/lists/http",
    "https://api.openproxy.space/lists/socks4",
    "https://api.openproxy.space/lists/socks5",
]

SOURCE_LIST_3 = [
    "https://free-proxy-list.net/",
    "https://www.sslproxies.org/",
    "https://www.us-proxy.org/",
    "https://www.socks-proxy.net/",
    "https://hidemy.name/en/proxy-list/",
]


class ProxyManager:
    def __init__(self):
        self.proxies = set()
        self.valid_proxies = []
        self.ua = UserAgent()
        self.settings = {
            'max_proxies': 1000,
            'workers': 50,
            'timeout': 8,
            'test_url': 'https://www.youtube.com/',
            'save_dir': 'proxy_results',
            'discord_webhook': '',
            'auto_send': False,
        }
        self.setup_db()
        os.makedirs(self.settings['save_dir'], exist_ok=True)
        self._clock_stop = threading.Event()
        self._start_clock_thread()

    # Terminal size / window title
    def _term_size(self):
        """Accurate terminal (cols, rows). Uses Windows API on Windows."""
        try:
            if os.name == 'nt':
                import ctypes, struct
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
                csbi = ctypes.create_string_buffer(22)
                if kernel32.GetConsoleScreenBufferInfo(handle, csbi):
                    size = struct.unpack("hhhhHhhhhhh", csbi.raw)
                    left, top, right, bottom = size[5:9]
                    cols = right - left + 1
                    rows = bottom - top + 1
                    if cols > 0 and rows > 0:
                        return cols, rows
        except Exception:
            pass
        try:
            s = shutil.get_terminal_size()
            return s.columns, s.lines
        except Exception:
            return 100, 30

    def _term_width(self):
        return self._term_size()[0]

    def _refresh_console(self):
        """Force Rich to adopt the real current terminal size."""
        cols, rows = self._term_size()
        try:
            console.width = cols
            console.height = rows
        except Exception:
            pass

    def _start_clock_thread(self):
        """Background thread: keeps the terminal title in sync (secondary)."""
        def tick():
            while not self._clock_stop.is_set():
                try:
                    now = datetime.now().strftime('%H:%M:%S')
                    title = (
                        f'Proxy Scraper  |  {now}'
                        f'  |  Scraped: {len(self.proxies)}'
                        f'  |  Valid: {len(self.valid_proxies)}'
                    )
                    console.set_window_title(title)
                except Exception:
                    pass
                self._clock_stop.wait(1)

        threading.Thread(target=tick, daemon=True).start()

    def _stop_clock_thread(self):
        try:
            self._clock_stop.set()
        except Exception:
            pass

    def setup_db(self):
        self.conn = sqlite3.connect('proxies.db', check_same_thread=False)
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS valid_proxies 
                         (ip TEXT, port INTEGER, latency REAL, tested_at TEXT, UNIQUE(ip, port))''')
        self.conn.commit()

    def clear(self):
        self._refresh_console()
        os.system('cls' if os.name == 'nt' else 'clear')

    def _build_logo(self, term_width):
        logo = pyfiglet.figlet_format("PROXY SCRAPER", font="slant")
        lines = [line.rstrip() for line in logo.splitlines() if line.strip()]
        txt = Text(justify="center")
        colors = ["cyan", "bright_blue", "magenta", "cyan"]
        for i, line in enumerate(lines):
            if len(line) > term_width - 4:
                continue
            txt.append(line + "\n", style=colors[i % len(colors)])
        return txt

    def _build_credit(self):
        """Professional two-tone credit line, no duplicate name."""
        txt = Text(justify="center")
        txt.append("discord ", style="grey50")
        txt.append(AUTHOR_DISCORD, style="bold #5865F2")   # Discord blurple
        txt.append("   ·   ", style="grey37")
        txt.append("github ", style="grey50")
        txt.append(AUTHOR_GITHUB, style="bold #a371f7")    # GitHub purple
        txt.append("\n")
        return txt

    def show_logo(self):
        """Non-live version (used by non-Live screens)."""
        self._refresh_console()
        w = self._term_width()
        console.print(self._build_logo(w))
        console.print(self._build_credit())
        console.print()

    # Non-blocking key read 
    def _read_key_nonblocking(self):
        if os.name == 'nt':
            import msvcrt
            if msvcrt.kbhit():
                try:
                    ch = msvcrt.getch().decode('utf-8', errors='ignore')
                    return ch
                except Exception:
                    return None
            return None
        else:
            import select, tty, termios
            dr, _, _ = select.select([sys.stdin], [], [], 0)
            if not dr:
                return None
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)
            return ch

    # Initial setup
    def initial_setup(self):
        while True:
            self.clear()
            self.show_logo()
            console.print(Rule(style="bold magenta"))
            console.print(Align.center("[bold yellow]⚙️  CONFIGURATION SETUP[/bold yellow]"))
            console.print(Rule(style="bold magenta"))
            console.print()

            settings_table = Table(
                show_header=True, header_style="bold yellow", border_style="magenta",
                box=box.ROUNDED, title="[bold cyan]CURRENT SETTINGS[/bold cyan]",
                title_justify="center", padding=(1, 2), expand=True,
            )
            settings_table.add_column("Option", style="bold yellow", ratio=1, justify="center", no_wrap=True)
            settings_table.add_column("Setting", style="bold cyan", ratio=3, no_wrap=True)
            settings_table.add_column("Current Value", style="bold green", ratio=4)
            settings_table.add_column("Description", style="white", ratio=4)
            settings_table.add_row("[1]", "Max Proxies", str(self.settings['max_proxies']), "Number of proxies to test")
            settings_table.add_row("[2]", "Test URL", self.settings['test_url'], "Website to test proxies")
            settings_table.add_row("[3]", "Timeout", f"{self.settings['timeout']}s", "Wait time per proxy")
            settings_table.add_row("[4]", "Threads", str(self.settings['workers']), "Concurrent tests")
            settings_table.add_row("[5]", "Discord", "Set" if self.settings['discord_webhook'] else "Not set", "Webhook URL")
            settings_table.add_row("[6]", "Auto-Send", "ON" if self.settings['auto_send'] else "OFF", "Auto send to Discord")
            console.print(settings_table)
            console.print()

            console.print(Panel(
                "[bold green][8] Save & Continue[/bold green]     [bold yellow][9] Reset[/bold yellow]     [bold red][0] Back[/bold red]",
                border_style="cyan", box=box.ROUNDED, padding=(1, 1), expand=True,
            ))
            console.print()

            choice = Prompt.ask("[bold yellow]Select option[/bold yellow]",
                                choices=["0", "1", "2", "3", "4", "5", "6", "8", "9"])

            if choice == "0":
                return
            elif choice == "1":
                self.settings['max_proxies'] = IntPrompt.ask("[bold yellow]Max proxies[/bold yellow]",
                                                             default=self.settings['max_proxies'])
                console.print(f"[green]✓ Saved: {self.settings['max_proxies']} proxies[/green]")
                time.sleep(0.4)
            elif choice == "2":
                self.settings['test_url'] = Prompt.ask("[bold yellow]Test URL[/bold yellow]",
                                                       default=self.settings['test_url'])
                console.print(f"[green]✓ Saved: {self.settings['test_url']}[/green]")
                time.sleep(0.4)
            elif choice == "3":
                self.settings['timeout'] = IntPrompt.ask("[bold yellow]Timeout (seconds)[/bold yellow]",
                                                         default=self.settings['timeout'])
                console.print(f"[green]✓ Saved: {self.settings['timeout']}s[/green]")
                time.sleep(0.4)
            elif choice == "4":
                self.settings['workers'] = IntPrompt.ask("[bold yellow]Threads[/bold yellow]",
                                                         default=self.settings['workers'])
                console.print(f"[green]✓ Saved: {self.settings['workers']} threads[/green]")
                time.sleep(0.4)
            elif choice == "5":
                webhook = Prompt.ask("[bold yellow]Webhook URL[/bold yellow]",
                                     default=self.settings['discord_webhook'])
                self.settings['discord_webhook'] = webhook
                if webhook:
                    self.settings['auto_send'] = Confirm.ask("[bold yellow]Auto-send?[/bold yellow]", default=True)
                    console.print("[green]✓ Discord configured![/green]")
                else:
                    self.settings['auto_send'] = False
                    console.print("[yellow]Discord skipped[/yellow]")
                time.sleep(0.4)
            elif choice == "6":
                self.settings['auto_send'] = not self.settings['auto_send']
                console.print(f"[green]✓ Auto-send: {'ON' if self.settings['auto_send'] else 'OFF'}[/green]")
                time.sleep(0.4)
            elif choice == "8":
                console.print("[green]✅ Configuration saved![/green]")
                time.sleep(0.8)
                return
            elif choice == "9":
                self.settings = {
                    'max_proxies': 1000, 'workers': 50, 'timeout': 8,
                    'test_url': 'https://www.youtube.com/', 'save_dir': 'proxy_results',
                    'discord_webhook': '', 'auto_send': False,
                }
                console.print("[green]✓ Reset to defaults![/green]")
                time.sleep(0.4)

    # ---------- Live menu (real-time clock IN the console) ----------
    def _build_menu_renderable(self):
        w = self._term_width()
        now = datetime.now().strftime('%H:%M:%S')

        logo = self._build_logo(w)
        credit = self._build_credit()

        stats = Table.grid(expand=True, padding=(0, 2))
        for _ in range(4):
            stats.add_column(justify="center")
        stats.add_row(
            "[bold green]● ACTIVE[/bold green]",
            f"[cyan]TIME[/cyan] [white]{now}[/white]",
            f"[yellow]SCRAPED[/yellow] [white]{len(self.proxies)}[/white]",
            f"[green]VALID[/green] [white]{len(self.valid_proxies)}[/white]",
        )
        header = Panel(stats, border_style="cyan", box=box.ROUNDED, padding=(0, 1), expand=True)

        menu = Table(
            title="[bold cyan]◆ MAIN MENU ◆[/bold cyan]",
            box=box.ROUNDED, border_style="cyan",
            show_header=False, expand=True, padding=(0, 2),
        )
        menu.add_column("Key", style="bold yellow", width=6, justify="center")
        menu.add_column("Action", style="bold white")
        menu.add_column("Description", style="dim")
        items = [
            ("1", "🔍  Scrape Proxies", "Collect proxy endpoints from configured sources"),
            ("2", "✓   Validate Proxies", "Test collected proxies and measure latency"),
            ("3", "▣   View Results", "Browse working proxies, fastest first"),
            ("4", "▤   Save Proxies", "Export TXT, CSV and JSON results"),
            ("5", "↗   Send to Discord", "Upload current results through webhook"),
            ("6", "⚙   Settings", "Configure limits, timeout and workers"),
            ("7", "⚡  Full Auto Mode  [bold green]★ RECOMMENDED[/bold green]", "Scrape → validate → save automatically"),
            ("8", "↻   Update Sources", "Check configured sources for availability"),
            ("9", "▦   View Database", "Inspect stored validation results"),
            ("0", "⏻   Exit", "Close Proxy Scraper"),
        ]
        for key, action, desc in items:
            menu.add_row(f"[{key}]", action, desc)

        settings = (
            f"[cyan]MAX[/cyan] {self.settings['max_proxies']}   "
            f"[cyan]TIMEOUT[/cyan] {self.settings['timeout']}s   "
            f"[cyan]THREADS[/cyan] {self.settings['workers']}   "
            f"[cyan]AUTO-SEND[/cyan] {'ON' if self.settings['auto_send'] else 'OFF'}"
        )
        footer = Panel(Align.center(settings), border_style="magenta", box=box.ROUNDED, padding=(0, 1), expand=True)

        prompt = Text()
        prompt.append("\n  Choose ", style="bold yellow")
        prompt.append("[0-9]", style="bold white")
        prompt.append("  :  ", style="bold yellow")

        return Group(logo, credit, header, menu, footer, prompt)

    def show_menu(self):
        """Live main menu — returns the chosen digit."""
        self._refresh_console()
        with Live(console=console, refresh_per_second=4, screen=True,
                  vertical_overflow="visible") as live:
            while True:
                live.update(self._build_menu_renderable())
                ch = self._read_key_nonblocking()
                if ch and ch in "0123456789":
                    return ch
                time.sleep(0.08)

    # Simple non-live header for action screens 
    def print_header(self):
        self.clear()
        self.show_logo()
        now = datetime.now().strftime('%H:%M:%S')
        stats = Table.grid(expand=True, padding=(0, 2))
        for _ in range(4):
            stats.add_column(justify="center")
        stats.add_row(
            "[bold green]● ACTIVE[/bold green]",
            f"[cyan]TIME[/cyan] [white]{now}[/white]",
            f"[yellow]SCRAPED[/yellow] [white]{len(self.proxies)}[/white]",
            f"[green]VALID[/green] [white]{len(self.valid_proxies)}[/white]",
        )
        console.print(Panel(stats, border_style="cyan", box=box.ROUNDED, padding=(0, 1), expand=True))

    # Actions 
    def scrape_proxies(self):
        self.print_header()
        console.print(Align.center("[bold cyan]🔍 SCRAPING PROXIES[/bold cyan]"))
        print()
        all_proxies = set()
        for source_list, label in ((SOURCE_LIST_1, "Collecting..."),
                                   (SOURCE_LIST_2, "More sources..."),
                                   (SOURCE_LIST_3, "Websites...")):
            if len(all_proxies) >= self.settings['max_proxies']:
                break
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(bar_width=40, style="cyan"),
                TaskProgressColumn(),
                TextColumn("[yellow]{task.fields[found]}[/yellow]"),
                TimeElapsedColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(f"[cyan]{label}[/cyan]", total=len(source_list),
                                         found=f"{len(all_proxies)}")
                for url in source_list:
                    if len(all_proxies) >= self.settings['max_proxies']:
                        break
                    try:
                        headers = {'User-Agent': self.ua.random}
                        response = requests.get(url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            pattern = r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}\b'
                            all_proxies.update(re.findall(pattern, response.text))
                    except Exception:
                        pass
                    progress.update(task, advance=1, found=f"{len(all_proxies)}")

        if len(all_proxies) > self.settings['max_proxies']:
            all_proxies = set(random.sample(list(all_proxies), self.settings['max_proxies']))
        self.proxies = all_proxies

        self.print_header()
        console.print(Panel(
            f"[bold green]✅ SCRAPING COMPLETE![/bold green]\n\n  Found: [bold yellow]{len(self.proxies)}[/bold yellow] proxies\n\n  [green][1] Validate[/green]  │  [cyan][0] Back[/cyan]",
            border_style="green", box=box.ROUNDED, title="[bold]RESULT[/bold]",
            title_align="center", padding=(1, 2), expand=True,
        ))
        choice = Prompt.ask("Choose", choices=["0", "1"])
        if choice == "1":
            self.validate_proxies()

    def validate_proxies(self):
        if not self.proxies:
            self.print_header()
            console.print(Panel("[bold red]No proxies![/bold red]\n\n[0] Back",
                                border_style="red", box=box.ROUNDED, expand=True))
            input()
            return

        proxies_to_test = list(self.proxies)[:self.settings['max_proxies']]
        total = len(proxies_to_test)
        valid = []
        tested = 0
        start_time = time.time()

        def test_proxy(proxy):
            try:
                ip, port = proxy.split(':')
                proxies_dict = {'http': f'http://{ip}:{port}', 'https': f'http://{ip}:{port}'}
                headers = {'User-Agent': self.ua.random}
                t0 = time.time()
                r = requests.get(self.settings['test_url'], proxies=proxies_dict,
                                 timeout=self.settings['timeout'], headers=headers,
                                 allow_redirects=True)
                lat = time.time() - t0
                if r.status_code in (200, 301, 302, 303, 307, 308, 403):
                    return {'ip': ip, 'port': port, 'latency': lat,
                            'tested_at': datetime.now().strftime('%H:%M:%S')}
            except Exception:
                pass
            return None

        with Live(console=console, refresh_per_second=10, screen=True) as live:
            with ThreadPoolExecutor(max_workers=self.settings['workers']) as ex:
                futures = {ex.submit(test_proxy, p): p for p in proxies_to_test}
                for fut in as_completed(futures):
                    tested += 1
                    res = fut.result()
                    if res:
                        valid.append(res)
                        cur = self.conn.cursor()
                        cur.execute('INSERT OR REPLACE INTO valid_proxies (ip, port, latency, tested_at) VALUES (?, ?, ?, ?)',
                                    (res['ip'], res['port'], res['latency'], res['tested_at']))
                        self.conn.commit()

                    succ = (len(valid) / tested * 100) if tested else 0
                    avg = sum(p['latency'] for p in valid) / len(valid) if valid else 0
                    elapsed = time.time() - start_time
                    pct = (tested / total) * 100 if total else 0

                    if avg < 1:
                        se, sl, ss = "⚡⚡⚡", "VERY FAST", "bold green"
                    elif avg < 2:
                        se, sl, ss = "⚡⚡", "FAST", "bold cyan"
                    elif avg < 3:
                        se, sl, ss = "⚡", "MEDIUM", "bold yellow"
                    else:
                        se, sl, ss = "🐌", "SLOW", "bold red"

                    dash = Table.grid(expand=True, padding=(0, 1))
                    dash.add_column(ratio=1, min_width=34)
                    dash.add_column(ratio=1, min_width=34)

                    pt = Table.grid(expand=True)
                    pt.add_column(); pt.add_column(justify="right")
                    bw = 26
                    fill = int(bw * pct / 100)
                    bar = "━" * fill + "─" * (bw - fill)
                    pt.add_row("[bold white]Progress[/bold white]", f"[bold cyan]{pct:5.1f}%[/bold cyan]")
                    pt.add_row(f"[cyan]{bar}[/cyan]", f"[white]{tested}/{total}[/white]")
                    pt.add_row("[dim]Target[/dim]", f"[dim]{self.settings['test_url']}[/dim]")
                    pp = Panel(pt, title="[bold yellow]PROGRESS[/bold yellow]",
                               border_style="cyan", box=box.ROUNDED, padding=(0, 1), expand=True)

                    st = Table.grid(expand=True)
                    st.add_column(); st.add_column(justify="right")
                    st.add_row("[green]✓ Working[/green]", f"[bold green]{len(valid):>5}[/bold green]")
                    st.add_row("[red]✗ Failed[/red]", f"[bold red]{tested - len(valid):>5}[/bold red]")
                    st.add_row("[yellow]◆ Success[/yellow]", f"[bold yellow]{succ:>5.1f}%[/bold yellow]")
                    st.add_row("[cyan]◷ Elapsed[/cyan]", f"[white]{elapsed:>5.1f}s[/white]")
                    sp = Panel(st, title="[bold yellow]STATISTICS[/bold yellow]",
                               border_style="green", box=box.ROUNDED, padding=(0, 1), expand=True)

                    speed_panel = Panel(
                        Align.center(f"[{ss}]{se} {avg*1000:6.0f} ms  {sl}[/{ss}]\n[dim]Average latency[/dim]"),
                        title="[bold cyan]SPEED[/bold cyan]", border_style="magenta",
                        box=box.ROUNDED, padding=(0, 1), expand=True,
                    )

                    rt = Table.grid(expand=True)
                    rt.add_column(width=3, justify="right", style="dim")
                    rt.add_column(style="green")
                    rt.add_column(justify="right", style="dim")
                    recent = valid[-6:]
                    if recent:
                        for i, pr in enumerate(reversed(recent), 1):
                            rt.add_row(str(i), f"✓ {pr['ip']}:{pr['port']}", f"{pr['latency']*1000:.0f}ms")
                    else:
                        rt.add_row("", "[dim]Waiting for working proxies...[/dim]", "")
                    rp = Panel(rt, title="[bold cyan]LATEST WORKING[/bold cyan]",
                               border_style="yellow", box=box.ROUNDED, padding=(0, 1), expand=True)

                    dash.add_row(pp, sp)
                    dash.add_row(speed_panel, rp)

                    hdr = Panel(Align.center("[bold yellow]⚡ LIVE VALIDATION DASHBOARD[/bold yellow]\n"
                                             f"[dim]Testing against: {self.settings['test_url']}[/dim]"),
                                border_style="cyan", box=box.DOUBLE, padding=(0, 1), expand=True)
                    ftr = Align.center(
                        f"[dim]Threads: {self.settings['workers']}  │  Timeout: {self.settings['timeout']}s  │  Testing: {tested}/{total}[/dim]"
                    )
                    outer = Table.grid(expand=True)
                    outer.add_row(hdr); outer.add_row(dash); outer.add_row(ftr)
                    live.update(Panel(outer, border_style="cyan", box=box.ROUNDED, padding=(0, 1), expand=True))

        valid.sort(key=lambda x: x['latency'])
        self.valid_proxies = valid
        self.print_header()

        rt = Table(title="✅ VALIDATION COMPLETE", show_header=True, header_style="bold cyan",
                   border_style="green", box=box.ROUNDED, padding=(0, 3), expand=True)
        rt.add_column("Detail", style="cyan", ratio=1)
        rt.add_column("Value", style="green", ratio=2)
        rt.add_row("Total Tested", str(total))
        rt.add_row("Working", str(len(valid)))
        rt.add_row("Failed", str(total - len(valid)))
        if total > 0:
            rt.add_row("Success Rate", f"{len(valid)/total*100:.1f}%")
        if valid:
            rt.add_row("Fastest", f"{valid[0]['latency']*1000:.0f}ms")
            rt.add_row("Slowest", f"{valid[-1]['latency']*1000:.0f}ms")
            rt.add_row("Average", f"{sum(p['latency'] for p in valid)/len(valid)*1000:.0f}ms")
        console.print(rt)

        if valid:
            console.print("\n[bold cyan]TOP 10 FASTEST:[/bold cyan]")
            for i, p in enumerate(valid[:10], 1):
                ms = p['latency'] * 1000
                if ms < 1000:   col, s = "green",  "Very Fast"
                elif ms < 2000: col, s = "cyan",   "Fast"
                elif ms < 3000: col, s = "yellow", "Medium"
                else:           col, s = "red",    "Slow"
                console.print(f"  [{col}]{i:>2}. {p['ip']}:{p['port']} - {ms:6.0f}ms ({s})[/{col}]")

        console.print()
        console.print("[green][1] Save[/green]  │  [cyan][2] Discord[/cyan]  │  [yellow][0] Back[/yellow]")
        choice = Prompt.ask("  Choose", choices=["0", "1", "2"])
        if choice == "1":
            self.save_proxies()
        elif choice == "2":
            self.send_discord()

    def save_proxies(self):
        if not self.valid_proxies:
            self.print_header()
            console.print(Panel("[bold red]No valid proxies![/bold red]\n\n[0] Back",
                                border_style="red", box=box.ROUNDED, expand=True))
            input()
            return
        sp = sorted(self.valid_proxies, key=lambda x: x['latency'])
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_file = f"{self.settings['save_dir']}/proxies_fastest_{ts}.txt"
        with open(txt_file, 'w') as f:
            f.write("# Working proxies sorted by speed\n")
            f.write(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# discord: {AUTHOR_DISCORD}  ·  github: {AUTHOR_GITHUB}\n\n")
            for p in sp:
                f.write(f"{p['ip']}:{p['port']}  # {p['latency']*1000:.0f}ms\n")
        csv_file = f"{self.settings['save_dir']}/proxies_{ts}.csv"
        with open(csv_file, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['Rank', 'IP', 'Port', 'Latency(ms)'])
            for i, p in enumerate(sp, 1):
                w.writerow([i, p['ip'], p['port'], f"{p['latency']*1000:.0f}"])
        json_file = f"{self.settings['save_dir']}/proxies_{ts}.json"
        with open(json_file, 'w') as f:
            json.dump({
                'discord': AUTHOR_DISCORD,
                'github': AUTHOR_GITHUB,
                'generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'proxies': sp,
            }, f, indent=2)

        self.print_header()
        console.print(Panel(
            f"[bold green]✅ SAVED {len(sp)} PROXIES![/bold green]\n\n  📄 {txt_file}\n  📄 {csv_file}\n  📄 {json_file}\n\n  [0] Back",
            border_style="green", box=box.ROUNDED, title="[bold]FILES SAVED[/bold]",
            title_align="center", padding=(1, 2), expand=True,
        ))
        input()

    def send_discord(self):
        if not self.settings['discord_webhook']:
            self.print_header()
            webhook = Prompt.ask("Discord webhook URL (0 to cancel)")
            if webhook == "0":
                return
            self.settings['discord_webhook'] = webhook
        if not self.valid_proxies:
            self.print_header()
            console.print(Panel("[bold red]No valid proxies![/bold red]\n\n[0] Back",
                                border_style="red", box=box.ROUNDED, expand=True))
            input()
            return
        sp = sorted(self.valid_proxies, key=lambda x: x['latency'])
        fc = "# Working proxies sorted by speed\n"
        fc += f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        fc += f"# discord: {AUTHOR_DISCORD}  ·  github: {AUTHOR_GITHUB}\n\n"
        for p in sp:
            fc += f"{p['ip']}:{p['port']}  # {p['latency']*1000:.0f}ms\n"
        content = (f"**Proxy Validation Results**\nWorking: {len(sp)}\n"
                   f"Fastest: {sp[0]['latency']*1000:.0f}ms\nSlowest: {sp[-1]['latency']*1000:.0f}ms")
        files = {'file': ('proxies_fastest.txt', fc.encode('utf-8'), 'text/plain')}
        try:
            r = requests.post(self.settings['discord_webhook'], data={'content': content}, files=files)
            self.print_header()
            if r.status_code in (200, 204):
                console.print(Panel("[bold green]✅ Sent to Discord![/bold green]\n\n[0] Back",
                                    border_style="green", box=box.ROUNDED, expand=True))
            else:
                console.print(Panel(f"[bold red]❌ Error: {r.status_code}[/bold red]\n\n[0] Back",
                                    border_style="red", box=box.ROUNDED, expand=True))
            input()
        except Exception as e:
            self.print_header()
            console.print(Panel(f"[bold red]❌ Error: {e}[/bold red]\n\n[0] Back",
                                border_style="red", box=box.ROUNDED, expand=True))
            input()

    def full_auto(self):
        self.scrape_proxies()
        time.sleep(1)
        if not self.proxies:
            return
        self.validate_proxies()
        time.sleep(1)
        if self.valid_proxies:
            self.save_proxies()
            if self.settings['auto_send'] and self.settings['discord_webhook']:
                self.send_discord()

    def update_sources(self):
        global SOURCE_LIST_1, SOURCE_LIST_2, SOURCE_LIST_3
        self.print_header()
        console.print(Align.center("[bold cyan]🔄 UPDATING SOURCES[/bold cyan]"))
        print()
        all_sources = SOURCE_LIST_1 + SOURCE_LIST_2 + SOURCE_LIST_3
        working = []
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      BarColumn(bar_width=40, style="cyan"), TaskProgressColumn(), console=console) as progress:
            task = progress.add_task("[cyan]Checking...[/cyan]", total=len(all_sources))
            for url in all_sources:
                try:
                    r = requests.get(url, headers={'User-Agent': self.ua.random}, timeout=5)
                    if r.status_code == 200:
                        working.append(url)
                except Exception:
                    pass
                progress.update(task, advance=1)
        SOURCE_LIST_1 = [s for s in working if 'raw.' in s or 'github' in s]
        SOURCE_LIST_2 = [s for s in working if 'api' in s or 'proxy-list' in s]
        SOURCE_LIST_3 = [s for s in working if s not in SOURCE_LIST_1 and s not in SOURCE_LIST_2]
        self.print_header()
        console.print(Panel(
            f"[bold green]✅ SOURCES UPDATED![/bold green]\n\n  Working: [green]{len(working)}[/green]\n  Removed: [red]{len(all_sources)-len(working)}[/red]\n\n  [0] Back",
            border_style="green", box=box.ROUNDED, expand=True,
        ))
        input()

    def view_database(self):
        self.print_header()
        cur = self.conn.cursor()
        cur.execute('SELECT COUNT(*) FROM valid_proxies')
        total = cur.fetchone()[0]
        cur.execute('SELECT AVG(latency) FROM valid_proxies')
        avg = cur.fetchone()[0] or 0
        cur.execute('SELECT ip, port, latency FROM valid_proxies ORDER BY latency LIMIT 10')
        top = cur.fetchall()
        console.print(Panel(
            f"[bold cyan]🗄️ DATABASE[/bold cyan]\n\n  Total: [green]{total}[/green]\n  Avg Speed: [yellow]{avg*1000:.0f}ms[/yellow]\n  Size: [cyan]{os.path.getsize('proxies.db')/1024:.1f} KB[/cyan]",
            border_style="cyan", box=box.ROUNDED, title="[bold]DATABASE[/bold]",
            title_align="center", padding=(1, 2), expand=True,
        ))
        if top:
            console.print("\n[bold cyan]TOP 10 FASTEST:[/bold cyan]")
            for i, (ip, port, lat) in enumerate(top, 1):
                console.print(f"  [green]{i}. {ip}:{port} - {lat*1000:.0f}ms[/green]")
        console.print()
        input("  [0] Back")

    # ---------- Run loop ----------
    def run(self):
        self.initial_setup()
        while True:
            choice = self.show_menu()
            if choice == "0":
                self._stop_clock_thread()
                self.clear()
                self.show_logo()
                console.print(Panel("[bold green]👋 Goodbye![/bold green]",
                                    border_style="green", box=box.ROUNDED, expand=True))
                time.sleep(1)
                break
            elif choice == "1":
                self.scrape_proxies()
            elif choice == "2":
                self.validate_proxies()
            elif choice == "3":
                self.print_header()
                if self.valid_proxies:
                    sp = sorted(self.valid_proxies, key=lambda x: x['latency'])
                    console.print("[bold cyan]WORKING PROXIES (FASTEST FIRST):[/bold cyan]")
                    console.print("[yellow]" + "═" * 60 + "[/yellow]")
                    for i, p in enumerate(sp[:30], 1):
                        ms = p['latency'] * 1000
                        col = "green" if ms < 1000 else "cyan" if ms < 2000 else "yellow" if ms < 3000 else "red"
                        console.print(f"  [{col}]{i:>2}. {p['ip']}:{p['port']} - {ms:6.0f}ms[/{col}]")
                else:
                    console.print("[red]  No results yet.[/red]")
                console.print("[yellow]" + "═" * 60 + "[/yellow]")
                input("  [0] Back")
            elif choice == "4":
                self.save_proxies()
            elif choice == "5":
                self.send_discord()
            elif choice == "6":
                self.initial_setup()
            elif choice == "7":
                self.full_auto()
            elif choice == "8":
                self.update_sources()
            elif choice == "9":
                self.view_database()


if __name__ == "__main__":
    try:
        manager = ProxyManager()
        manager.run()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nInterrupted" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\nError: {e}" + Style.RESET_ALL)
        input("Press Enter to exit...")
