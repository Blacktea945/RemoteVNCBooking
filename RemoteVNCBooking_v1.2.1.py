# RemoteVNCBooking_v1.2.1py — PySide6 6.5.3 / Python 3.8.19
import os, tempfile, re, sys, shutil
import pymysql
from pathlib import Path
from typing import Optional, Dict, Set, Tuple, List
from pymysql.cursors import DictCursor
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, Slot, QDate, QTime, Qt, QSize, QTimer, QDateTime, QTimeZone
from PySide6.QtGui import QFont, QColor
from PySide6.QtWidgets import (
    QApplication, QListWidget, QAbstractButton, QDateEdit, QPushButton,
    QLabel, QHBoxLayout, QListWidgetItem, QWidget, QMessageBox, QToolButton,
    QScrollArea, QVBoxLayout, QGridLayout, QFrame, QSizePolicy, QInputDialog
)

def resource_path(rel: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)

UI_FILE = Path(resource_path("ui/RemoteVNCBooking.ui"))

BLUE     = "#1e90ff"
LED_BLUE = "#0000cd"
GREEN    = "#10b981"
RED      = "#dc143c"
GRAY     = "#B6B6B6"
FG       = "#ffffff"

APP_FONT_PT     = 12
BUTTON_FONT_PT  = 12
DETAIL_FONT_PT  = 12

_TZ = QTimeZone(b"Asia/Taipei")
def tz_now():
    return QDateTime.currentDateTimeUtc().toTimeZone(_TZ)
def tz_today():
    return tz_now().date()
def tz_time():
    return tz_now().time()
def tz_hour():
    return tz_now().time().hour()

def ymd(qdate: QDate) -> str:
    return qdate.toString("yyyy-MM-dd")

def paint(btn: QAbstractButton, bg: str, border: Optional[str] = None):
    border = border or bg
    btn.setStyleSheet(
        "QPushButton {"
        f"background-color: {bg};"
        f"color: {FG};"
        f"border: 2px solid {border};"
        "border-radius: 6px;"
        "padding: 6px 12px;"
        "}"
    )

def slot_canon(s: str) -> str:
    m = re.match(r"\s*(\d{1,2})", (s or ""))
    return m.group(1) if m else (s or "").strip()

# MySQL
from DB_Config_sample import DB

def fmt_mysql_error(e):
    code = e.args[0] if getattr(e, "args", None) else None
    host = DB.get("host", "?"); port = DB.get("port", 3306)
    db   = DB.get("database", "")
    if code == 2003:
        return f"Unable to connect to database {host}:{port}\nPlease check the network is connect or MySQL service is started。"
    if code == 1045:
        return "Database account or password is incorrect。"
    if code == 1049:
        return f"Repository not found：{db}。"
    return f"Database error [{code}]"

class Repo:
    def __init__(self):
        self._db = DB

    def conn(self):
        return pymysql.connect(cursorclass=DictCursor, autocommit=False, **self._db)

    # machines
    def list_machines(self) -> List[dict]:
        sql = """
            SELECT id, sn, owner, host_name, host_account_password, windows_account, windows_password, note, state,
                   data_create_at, data_update_at
            FROM machines
            ORDER BY sn
        """
        with self.conn() as cx, cx.cursor() as cur:
            cur.execute(sql)
            return list(cur.fetchall())

    def get_machine_by_sn(self, sn: str) -> Optional[dict]:
        with self.conn() as cx, cx.cursor() as cur:
            cur.execute("SELECT * FROM machines WHERE sn=%s", (sn,))
            return cur.fetchone()

    # bookings
    def bookings_of(self, machine_id: Optional[int] = None,
                    date_s: Optional[str] = None) -> List[dict]:
        where, params = [], []
        if machine_id is not None:
            where.append("b.machine_id=%s"); params.append(machine_id)
        if date_s is not None:
            where.append("b.date=%s"); params.append(date_s)
        sql = "SELECT b.* FROM bookings b"
        if where:
            sql += " WHERE " + " AND ".join(where)
        with self.conn() as cx, cx.cursor() as cur:
            cur.execute(sql, params)
            return list(cur.fetchall())

    def insert_booking(self, machine_id: int, date_s: str, slot_i: int,
                       display_name: str, wwid: str) -> bool:
        sql = """INSERT INTO bookings(machine_id,date,slot,display_name,wwid)
                 VALUES(%s,%s,%s,%s,%s)"""
        with self.conn() as cx, cx.cursor() as cur:
            try:
                cur.execute(sql, (machine_id, date_s, slot_i, display_name, wwid))
                cx.commit()
                return True
            except pymysql.err.IntegrityError:
                cx.rollback()
                return False

    def delete_bookings(self, machine_id: int, date_s: str, slots: List[int]) -> int:
        if not slots:
            return 0
        fmt = ",".join(["%s"] * len(slots))
        sql = f"DELETE FROM bookings WHERE machine_id=%s AND date=%s AND slot IN ({fmt})"
        with self.conn() as cx, cx.cursor() as cur:
            cur.execute(sql, [machine_id, date_s, *slots])
            cx.commit()
            return cur.rowcount

# MachineButton LED
class MachineButton(QPushButton):
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self._led = QLabel(self)
        self._led.setFixedSize(12, 12)
        self._led.setAttribute(Qt.WA_TransparentForMouseEvents)
        self._set_led(LED_BLUE)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        m = 4
        self._led.move(self.width() - self._led.width() - m, m)

    def _set_led(self, color: str):
        self._led.setStyleSheet(f"background:{color}; border-radius:6px;")

    def set_led_red(self):
        self._set_led(RED)

    def set_led_blue(self):
        self._set_led(LED_BLUE)

class Controller:
    def _as_url(self, v: str) -> str:
        s = (v or "").strip()
        if not s:
            return ""
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", s):
            return s
        return f"http://{s}"

    def __init__(self, ui: QWidget, display_name: str = "", wwid: str = ""):
        self.ui = ui
        self.display_name = display_name or ""
        self.wwid = wwid or ""
        self.repo = Repo()

        self.listw = ui.findChild(QListWidget, "listWidget")
        self.date_edit = ui.findChild(QDateEdit, "DateEdit")
        self.btn_prev = ui.findChild(QPushButton, "DateButton_Left")
        self.btn_next = ui.findChild(QPushButton, "DateButton_Right")
        self.btn_connect = ui.findChild(QAbstractButton, "Button_Connect")
        if self.btn_connect:
            self.btn_connect.clicked.connect(self.on_connect_clicked)

        self.btn_booking = (
            self.ui.findChild(QAbstractButton, "Button_Booking")
            or self.ui.findChild(QAbstractButton, "booking")
        )
        self.btn_delete = (
            self.ui.findChild(QAbstractButton, "Button_Cancel")
            or self.ui.findChild(QAbstractButton, "delete")
        )
        if self.btn_booking: self.btn_booking.clicked.connect(self.on_booking_clicked)
        if self.btn_delete:  self.btn_delete.clicked.connect(self.on_delete_clicked)

        self.current_machine: Optional[str] = None     
        self.sn_to_id: Dict[str, int] = {}           
        self.machine_btns: Dict[str, MachineButton] = {}
        self.selected: Set[int] = set()             

        today = tz_today()
        if self.date_edit:
            self.date_edit.setCalendarPopup(True)
            self.date_edit.setDate(today)
            self.date_edit.setMinimumDate(today)
            self.date_edit.setMaximumDate(today.addDays(14))
            self.date_edit.dateChanged.connect(self.on_date_changed)
        if self.btn_prev: self.btn_prev.clicked.connect(lambda: self.shift_date(-1))
        if self.btn_next: self.btn_next.clicked.connect(lambda: self.shift_date(1))

        # AM/PM
        self._init_time_buttons()
        self._ampm_auto = False  

        self._apply_code_fonts()

        # Machine list
        self.section_area = (
            self.ui.findChild(QScrollArea, "machinesScroll")
            or self.ui.findChild(QScrollArea, "scrollArea_Section")
            or self.ui.findChild(QScrollArea)
        )
        self.build_section_ui()
        if self.section_area:
            self.section_area.setWidgetResizable(True)
            self.section_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            self.section_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Periodic refresh
        self._timer = QTimer(self.ui)
        self._timer.setInterval(5000)
        self._timer.timeout.connect(self._tick)
        self._timer.start()

        self.refresh_slot_colors()
        self.refresh_machine_colors()
        self.refresh_machine_leds()
        self.update_action_buttons()
        self.update_date_nav_state()

    def _init_time_buttons(self):
        self.btn_ampm: Optional[QAbstractButton] = self.ui.findChild(QAbstractButton, "DataButton_Pm")
        self.is_pm: bool = False
        self.time_btns: List[Tuple[int, QAbstractButton]] = []

        for i in range(1, 13):
            b = self.ui.findChild(QAbstractButton, f"Time_{i}")
            if not b:
                continue
            base = i - 1
            b.setCheckable(True)
            b.toggled.connect(lambda checked, base=base: self.on_base_slot_toggled(base, checked))
            self.time_btns.append((base, b))

        if self.btn_ampm:
            self.btn_ampm.setText("AM")
            self.btn_ampm.clicked.connect(self.toggle_am_pm)

        self.relabel_time_buttons()

    def _offset(self) -> int:
        return 12 if self.is_pm else 0

    def relabel_time_buttons(self):
        if self.btn_ampm:
            self.btn_ampm.setText("PM" if self.is_pm else "AM")
        off = self._offset()
        for base, btn in self.time_btns:
            btn.setText(str(base + off))

    @Slot()
    def toggle_am_pm(self):
        self.is_pm = not self.is_pm
        self.relabel_time_buttons()
        self.refresh_slot_colors()
        self.update_action_buttons()

    def _apply_code_fonts(self):
        app = QApplication.instance()
        if app:
            f_app = QFont(app.font()); f_app.setPointSize(APP_FONT_PT); app.setFont(f_app)
        f_btn = QFont();    f_btn.setPointSize(BUTTON_FONT_PT)
        f_detail = QFont(); f_detail.setPointSize(DETAIL_FONT_PT)
        if self.listw: self.listw.setFont(f_detail)
        for w in (self.date_edit, self.btn_prev, self.btn_next, self.btn_booking, self.btn_delete, getattr(self, "btn_ampm", None)):
            if w: w.setFont(f_btn)
        for _, btn in getattr(self, "time_btns", []):
            btn.setFont(f_btn)
        for btn in self.machine_btns.values(): btn.setFont(f_btn)

    def _tick(self):
        self.refresh_slot_colors()
        self.refresh_machine_leds()
        if self.current_machine:
            self.show_machine_details(self.current_machine)
        self.update_action_buttons()

    def on_connect_clicked(self):
        if not self.current_machine:
            QMessageBox.warning(self.ui, "Connect", "Please select the machine first"); return

        rec = self._current_booking_record_now(self.current_machine)
        if rec:
            booked_name = (rec.get("display_name") or "").strip()
            booked_wwid = (rec.get("wwid") or "").strip()
            my_wwid     = (self.wwid or "").strip()
            if booked_wwid and booked_wwid != my_wwid:
                tip = (
                    f"This period is for {booked_name} reserved。\n"
                    f"Please contact {booked_name}, or enter the {booked_name} WWID。"
                )
                ww, ok = QInputDialog.getText(self.ui, "Already booked", tip)
                if not ok:
                    return
                if ww.strip() != booked_wwid:
                    QMessageBox.warning(self.ui, "Connection Rejected", "WWID does not match, Unable to connect。")
                    return

        if not self._has_vnc_viewer():
            QMessageBox.warning(self.ui, "RealVNC not installed", "Not found RealVNC Viewer，Please install first and then connect。")
            return

        row = self.repo.get_machine_by_sn(self.current_machine)
        if not row:
            QMessageBox.warning(self.ui, "Connect", "Database cannot find the machine"); return

        host = (row.get("host_name") or "").strip()
        user = (row.get("windows_account") or "").strip()
        pwd  = (row.get("32-bit_password") or row.get("windows_password") or "").strip()
        if not host:
            QMessageBox.warning(self.ui, "Connect", "host_name 為空"); return
        try:
            self._launch_vnc_with(host, user, pwd, self.current_machine)
        except Exception as e:
            QMessageBox.critical(self.ui, "Connect 失敗", str(e))

    def _launch_vnc_with(self, host: str, user: str, pwd: str, sn: str):
        tpl = Path(resource_path("VNC/MyHost.vnc"))
        if not tpl.exists():
            raise FileNotFoundError(f"Template not found：{tpl}")
        txt = tpl.read_text(encoding="utf-8", errors="ignore")

        def set_kv(s: str, key: str, val: str) -> str:
            pat = re.compile(rf'(?mi)^{re.escape(key)}\s*=.*$')
            return pat.sub(f"{key}={val}", s) if pat.search(s) else s + f"\n{key}={val}\n"

        txt = set_kv(txt, "Host", host)
        if user: txt = set_kv(txt, "Username", user)
        if pwd:  txt = set_kv(txt, "Password", pwd)

        tmp = Path(tempfile.gettempdir()) / f"MyHost_{sn}.vnc"
        tmp.write_text(txt, encoding="utf-8")
        os.startfile(str(tmp))

    def _current_booking_record_now(self, sn: str):
        """回傳『今天此小時檔期』的預約資料 dict；找不到回 None。"""
        mid = self.sn_to_id.get(sn)
        if mid is None:
            return None
        date_s = tz_today().toString("yyyy-MM-dd")
        hour  = tz_time().hour()
        rows = self.repo.bookings_of(machine_id=mid, date_s=date_s)
        for r in rows:
            try:
                if int(r.get("slot", -1)) == int(hour):
                    return r
            except Exception:
                pass
        return None

    def _has_vnc_viewer(self) -> bool:
        """是否可找到 RealVNC Viewer 執行檔。"""
        if shutil.which("vncviewer") or shutil.which("vncviewer.exe"):
            return True
        candidates = [
            Path(os.environ.get("ProgramFiles", "")) / "RealVNC" / "VNC Viewer" / "vncviewer.exe",
            Path(os.environ.get("ProgramFiles(x86)", "")) / "RealVNC" / "VNC Viewer" / "vncviewer.exe",
        ]
        return any(p.exists() for p in candidates)

    def shift_date(self, days: int):
        if not self.date_edit: return
        d = self.date_edit.date().addDays(days)
        if d < self.date_edit.minimumDate(): d = self.date_edit.minimumDate()
        if d > self.date_edit.maximumDate(): d = self.date_edit.maximumDate()
        self.date_edit.setDate(d)
        self.update_date_nav_state()

    def update_date_nav_state(self):
        if not self.date_edit: return
        cur = self.date_edit.date()
        if self.btn_prev: self.btn_prev.setEnabled(cur > self.date_edit.minimumDate())
        if self.btn_next: self.btn_next.setEnabled(cur < self.date_edit.maximumDate())

    def _fetch_machines(self):
        rows = self.repo.list_machines()
        self.sn_to_id = {r["sn"]: r["id"] for r in rows}
        return rows

    def machines_by_section(self) -> Dict[str, List[str]]:
        groups: Dict[str, List[str]] = {}
        for r in self._fetch_machines():
            sn = (r["sn"] or "").strip()
            sec = sn.split("_", 1)[0] if "_" in sn else "OTHER"
            groups.setdefault(sec, []).append(sn)
        for k in list(groups.keys()):
            groups[k] = sorted(set(groups[k]))
        return groups

    def _make_section_block(self, title: str, machines: List[str], cols: int = 3) -> QWidget:
        block = QWidget()
        v = QVBoxLayout(block); v.setContentsMargins(4,4,4,4); v.setSpacing(4)

        lab = QLabel(title)
        lab.setStyleSheet("QLabel {border:1px solid #ddd; padding:2px 6px; border-radius:8px; font-weight:600;}")
        v.addWidget(lab)

        frame = QFrame(); frame.setFrameShape(QFrame.StyledPanel)
        frame.setStyleSheet("QFrame {border:1px solid #ddd; border-radius:12px;}")
        grid = QGridLayout(frame); grid.setContentsMargins(6,6,6,6); grid.setSpacing(6)
        v.addWidget(frame)

        for c in range(cols): grid.setColumnStretch(c, 1)

        for i, sn in enumerate(machines):
            btn = MachineButton(sn)
            btn.setObjectName(sn)
            paint(btn, BLUE)
            btn.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
            btn.setMinimumWidth(0)
            btn.setToolTip(sn)
            btn.clicked.connect(lambda _=False, m=sn: self.on_machine_clicked(m))
            self.machine_btns[sn] = btn
            r, c = divmod(i, cols)
            grid.addWidget(btn, r, c)
        return block

    def build_section_ui(self):
        self.machine_btns.clear()
        if not self.section_area: return
        self.section_area.setWidgetResizable(True)
        content = QWidget()
        lay = QVBoxLayout(content); lay.setContentsMargins(2,2,2,2); lay.setSpacing(6)

        groups = self.machines_by_section()
        for sec in sorted(groups.keys()):
            lay.addWidget(self._make_section_block(sec, groups[sec], cols=3))
        lay.addStretch(1)
        self.section_area.setWidget(content)

        self._apply_code_fonts()
        self.refresh_machine_colors()
        self.refresh_machine_leds()

    def show_machine_details(self, sn: str):
        if not self.listw: return
        self.listw.clear()
        row = self.repo.get_machine_by_sn(sn)
        if not row:
            self.listw.addItem(sn + " : not found")
            return
        def add(k, v): self._add_kv_item(k, v if v is not None else "")
        add("sn", row.get("sn",""))
        add("owner", row.get("owner",""))
        add("host_name", row.get("host_name",""))
        add("host_account_password", row.get("host_account_password",""))
        add("windows_account", row.get("windows_account",""))
        add("windows_password", row.get("windows_password",""))
        add("note", row.get("note",""))
        add("state", row.get("state",""))
        add("ipkvm", str(row.get("ipkvm")))
        add("account/password", str(row.get("account/password")))
        add("data_update_at", str(row.get("data_update_at")))
        info = self._current_booker_now(sn)
        if info:
            name, wwid = info
            self._add_kv_item("Current User", name, value_color=RED)
            self._add_kv_item("WWID", wwid, value_color=RED)

    def _add_kv_item(self, key: str, value: str, value_color: Optional[str] = None):
        item = QListWidgetItem(self.listw)
        item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
        row = QWidget(self.listw)
        lay = QHBoxLayout(row); lay.setContentsMargins(6, 0, 6, 0); lay.setSpacing(8)
        base = QFont(); base.setPointSize(DETAIL_FONT_PT)
        lab_key = QLabel(f"{key}:", parent=row); lab_val = QLabel(value, parent=row)
        bold = QFont(base); bold.setBold(True); lab_key.setFont(bold)
        lab_key.setStyleSheet(f"color:{BLUE};")
        lab_val.setFont(base)
        if value_color: lab_val.setStyleSheet(f"color:{value_color};")
        lab_key.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        if (key or "").strip().lower() == "ipkvm" and (value or "").strip():
            url = self._as_url(value)
            lab_val.setText(f'<a href="{url}">{url}</a>')
            lab_val.setTextFormat(Qt.RichText)
            lab_val.setOpenExternalLinks(True)
            lab_val.setTextInteractionFlags(Qt.TextBrowserInteraction)
        else:
            lab_val.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)

        lay.addWidget(lab_key); lay.addWidget(lab_val, 1)
        item.setSizeHint(row.sizeHint()); self.listw.addItem(item); self.listw.setItemWidget(item, row)

    @Slot()
    def on_machine_clicked(self, sn: str):
        if self.current_machine == sn:
            self.current_machine = None
            self.selected.clear()
            if self.listw: self.listw.clear()
        else:
            self.current_machine = sn
            self.selected.clear()
            self.show_machine_details(sn)
            self.current_machine = sn
            if not getattr(self, "_ampm_auto", False):
                self.is_pm = tz_hour() >= 12
                self.relabel_time_buttons()
                self._ampm_auto = True
        self.refresh_machine_colors()
        self.refresh_slot_colors()
        self.update_action_buttons()

    @Slot()
    def on_date_changed(self, _):
        self.selected.clear()
        self.refresh_slot_colors()
        self.update_action_buttons()
        self.update_date_nav_state()

    @Slot()
    def on_base_slot_toggled(self, base_i: int, checked: bool):
        if not self.current_machine or not self.date_edit:
            for b_base, b in self.time_btns:
                if b_base == base_i:
                    b.blockSignals(True); b.setChecked(False); b.blockSignals(False)
                    break
            return
        hour_i = base_i + self._offset()
        if checked: self.selected.add(hour_i)
        else:       self.selected.discard(hour_i)
        self.refresh_slot_colors()
        self.update_action_buttons()

    @Slot()
    def on_booking_clicked(self):
        if not (self.current_machine and self.date_edit and self.selected):
            return
        date_s = ymd(self.date_edit.date())
        mid = self.sn_to_id.get(self.current_machine)
        if mid is None:
            QMessageBox.warning(self.ui, "Error", "Machine number not found")
            return
        committed = []
        for slot_i in sorted(self.selected):
            ok = self.repo.insert_booking(mid, date_s, int(slot_i), self.display_name, self.wwid)
            if ok: committed.append(slot_i)
        if committed:
            slots = ", ".join(str(s) for s in committed)
            QMessageBox.information(
                self.ui, "Booking Successful",
                f"Time zone use : GMT+8\nMachine： {self.current_machine}\nDate： {date_s}\nTime： {slots}"
            )
        self.selected.difference_update(committed)
        self.refresh_slot_colors()
        self.refresh_machine_leds()
        self.update_action_buttons()

    @Slot()
    def on_delete_clicked(self):
        if not (self.current_machine and self.date_edit and self.selected):
            return
        date_s = ymd(self.date_edit.date())
        mid = self.sn_to_id.get(self.current_machine)
        if mid is None:
            return
        n = self.repo.delete_bookings(mid, date_s, sorted(int(x) for x in self.selected))
        if n > 0:
            QMessageBox.information(
                self.ui, "Cancel Successful",
                f"Machine： {self.current_machine}\nDate： {date_s}\nCancel： {n} time period"
            )
            self.selected.clear()
        self.refresh_slot_colors()
        self.refresh_machine_leds()
        self.update_action_buttons()

    def _current_booker_now(self, sn: str) -> Optional[Tuple[str, str]]:
        mid = self.sn_to_id.get(sn)
        if mid is None:
            return None
        date_s = ymd(tz_today())
        now_h = tz_hour()
        rows = self.repo.bookings_of(machine_id=mid, date_s=date_s)
        for r in rows:
            try:
                if int(r.get("slot", -1)) == int(now_h):
                    return (r.get("display_name",""), r.get("wwid",""))
            except Exception:
                pass
        return None

    def refresh_machine_colors(self):
        for sn, btn in self.machine_btns.items():
            if self.current_machine == sn: paint(btn, GREEN)
            else: paint(btn, BLUE)

    def refresh_machine_leds(self):
        date_s = ymd(tz_today())
        now_slot = tz_hour()
        for sn, btn in self.machine_btns.items():
            mid = self.sn_to_id.get(sn)
            led_red = False
            if mid is not None:
                for r in self.repo.bookings_of(machine_id=mid, date_s=date_s):
                    try:
                        if int(r.get("slot", -1)) == now_slot:
                            led_red = True; break
                    except Exception:
                        pass
            if led_red: btn.set_led_red()
            else: btn.set_led_blue()

    def refresh_slot_colors(self):
        if not self.time_btns:
            return
        off = self._offset()
        for _, btn in self.time_btns:
            btn.blockSignals(True)
            btn.setEnabled(True)
            btn.setChecked(False)
            btn.blockSignals(False)
            paint(btn, GRAY)

        if not self.current_machine or not self.date_edit:
            self.relabel_time_buttons()
            return

        date_s = ymd(self.date_edit.date())
        booked_rows = self._booking_rows_for(self.current_machine, date_s)
        booked_map = {int(r["slot"]): (r.get("display_name") or "") for r in booked_rows}

        is_today = self.date_edit.date() == tz_today()
        now_t = tz_time()

        for base, btn in self.time_btns:
            start_h = base + off
            end_h = min(23, start_h + 1)

            if is_today and now_t >= QTime(end_h, 0):
                btn.setEnabled(False); paint(btn, GRAY)
                btn.setText(str(start_h))
                continue

            is_booked = start_h in booked_map
            is_selected = start_h in self.selected

            btn.setEnabled(True)
            btn.blockSignals(True); btn.setChecked(is_selected); btn.blockSignals(False)

            label = str(start_h)
            if is_booked:
                nm = booked_map.get(start_h, '')
                if nm: label = f"{label} : {nm}"
            if len(label) > 15: label = label[:15]
            btn.setText(label)

            if is_selected: paint(btn, GREEN)
            elif is_booked: paint(btn, RED)
            else: paint(btn, BLUE)

    def update_action_buttons(self):
        if not (self.btn_booking or self.btn_delete): return
        if not (self.current_machine and self.date_edit and self.selected):
            if self.btn_booking: self.btn_booking.setEnabled(False)
            if self.btn_delete:  self.btn_delete.setEnabled(False)
            return

        date_s = ymd(self.date_edit.date())
        booked_rows = self._booking_rows_for(self.current_machine, date_s)
        booked_set = {int(r["slot"]) for r in booked_rows}
        sels = set(int(x) for x in self.selected)
        any_booked = any(s in booked_set for s in sels)
        any_free   = any(s not in booked_set for s in sels)

        if self.btn_booking: self.btn_booking.setEnabled(any_free and not any_booked)
        if self.btn_delete:  self.btn_delete.setEnabled(any_booked)

    def _booking_rows_for(self, sn: str, date_s: str) -> List[dict]:
        mid = self.sn_to_id.get(sn)
        if mid is None:
            return []
        return self.repo.bookings_of(machine_id=mid, date_s=date_s)

def main():
    app = QApplication(sys.argv)
    app.setFont(QFont(app.font().family(), APP_FONT_PT))

    # --- Login gate ---
    from Login import Login
    start = Login()
    result = start.exec()
    if not result: return
    display_name, wwid = result

    # --- Load main UI ---
    qf = QFile(str(UI_FILE)); qf.open(QFile.ReadOnly)
    ui = QUiLoader().load(qf); qf.close()
    ui.setFixedSize(ui.size())                  
    ui.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

    name_lab = ui.findChild(QLabel, "label_Name2")
    wwid_lab = ui.findChild(QLabel, "label_Wwid2")
    if name_lab: name_lab.setText(display_name)
    if wwid_lab: wwid_lab.setText(wwid)

    qbtn = ui.findChild(QToolButton, "toolButton_Qustion")
    if qbtn:
        def show_info():
            msg = QMessageBox(ui)
            msg.setWindowTitle("Info")
            msg.setIcon(QMessageBox.Information)
            msg.setText(
                "<span style='font-size:14pt; font-weight:bold'>Any Problem? Plase Message.</span><br>"
                "Name : 123, Test<br>"
                "WWID : ********<br>"
                "<span style='font-size:8pt'>Version 1.2.1</span>"
            )
            msg.setTextFormat(Qt.RichText)
            msg.setTextInteractionFlags(Qt.TextBrowserInteraction)
            msg.exec()
        qbtn.clicked.connect(show_info)

    Controller(ui, display_name=display_name, wwid=wwid)
    ui.show()
    app.exec()

if __name__ == "__main__":
    try:
        main()
    except pymysql.MySQLError as e:
        m = QMessageBox(QMessageBox.Critical, "Database error", fmt_mysql_error(e))
        m.setDetailedText(str(e))
        m.exec()
