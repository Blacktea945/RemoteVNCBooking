# PySide6 6.5.3, Python 3.8.19
import re
from PySide6.QtCore import QRegularExpression, Qt, QSettings
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLineEdit, QCheckBox
from Login_ui import Ui_Dialog
import RemoteVNCBooking_rc


class Login:
    ORG = "RemoteVNCBooking"
    APP = "Login"

    def __init__(self, parent=None):
        self.dlg = QDialog(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self.dlg)

        self.edit_name: QLineEdit = self.ui.lineEdit_Name
        self.edit_wwid: QLineEdit = self.ui.lineEdit_Wwid
        self.chk_remember: QCheckBox = self.ui.checkBox_remember
        self.button_box: QDialogButtonBox = self.ui.buttonBox_Start

        self.btn_ok = self.button_box.button(QDialogButtonBox.Ok)
        if self.btn_ok:
            self.btn_ok.setEnabled(False)
            self.btn_ok.setDefault(True)

        self.edit_name.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^[A-Za-z]{0,50}$"), self.dlg)
        )
        self.edit_wwid.setValidator(
            QRegularExpressionValidator(QRegularExpression(r"^\d{0,8}$"), self.dlg)
        )

        self.edit_name.textChanged.connect(self._update_ok_state)
        self.edit_wwid.textChanged.connect(self._update_ok_state)
        self.button_box.accepted.connect(self._on_accept)

        self._settings = QSettings(self.ORG, self.APP)
        self._load_settings()

        self._update_ok_state()
        self.edit_name.setFocus(Qt.FocusReason.ActiveWindowFocusReason)

    def _load_settings(self):
        remember = self._settings.value("remember", False, type=bool)
        name = self._settings.value("display_name", "", type=str) or ""
        wwid = self._settings.value("wwid", "", type=str) or ""
        self.chk_remember.setChecked(bool(remember and (name or wwid)))
        if remember:
            if name:
                self.edit_name.setText(name)
            if wwid:
                self.edit_wwid.setText(wwid)

    def _save_settings(self):
        """只保留最後一次；未勾選則清除。"""
        if self.chk_remember.isChecked() and self._is_valid():
            self._settings.setValue("remember", True)
            self._settings.setValue("display_name", self.edit_name.text().strip())
            self._settings.setValue("wwid", self.edit_wwid.text().strip())
        else:
            self._settings.setValue("remember", False)
            self._settings.remove("display_name")
            self._settings.remove("wwid")

    def _is_valid(self) -> bool:
        name = (self.edit_name.text() or "").strip()
        wwid = (self.edit_wwid.text() or "").strip()
        ok_name = bool(re.fullmatch(r"[A-Za-z]+", name))
        ok_wwid = bool(re.fullmatch(r"\d{8}", wwid))
        return ok_name and ok_wwid

    def _update_ok_state(self):
        if self.btn_ok:
            self.btn_ok.setEnabled(self._is_valid())

    def _on_accept(self):
        self._save_settings()

    def exec(self):
        code = self.dlg.exec()
        if code == QDialog.Accepted and self._is_valid():
            return self.edit_name.text().strip(), self.edit_wwid.text().strip()
        return None
