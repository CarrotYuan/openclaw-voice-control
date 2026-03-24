from __future__ import annotations

import argparse
import ctypes
import json
import math
import sys
from pathlib import Path

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, QTimer, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient, QTextDocument, QTextOption
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QScrollArea, QSizePolicy, QVBoxLayout, QWidget

from .config import load_config
from .state import OverlayStateManager


if sys.platform == "darwin":
    try:
        import objc
        from AppKit import (
            NSApp,
            NSApplication,
            NSApplicationActivationPolicyAccessory,
            NSRunningApplication,
            NSScreenSaverWindowLevel,
            NSStatusWindowLevel,
            NSWindowCollectionBehaviorCanJoinAllApplications,
            NSWindowCollectionBehaviorCanJoinAllSpaces,
            NSWindowCollectionBehaviorFullScreenAuxiliary,
        )
    except ImportError:
        objc = None
        NSApp = None
        NSApplication = None
        NSApplicationActivationPolicyAccessory = None
        NSRunningApplication = None
        NSScreenSaverWindowLevel = None
        NSStatusWindowLevel = None
        NSWindowCollectionBehaviorCanJoinAllApplications = 0
        NSWindowCollectionBehaviorCanJoinAllSpaces = 0
        NSWindowCollectionBehaviorFullScreenAuxiliary = 0
else:
    objc = None
    NSApp = None
    NSApplication = None
    NSApplicationActivationPolicyAccessory = None
    NSRunningApplication = None
    NSScreenSaverWindowLevel = None
    NSStatusWindowLevel = None
    NSWindowCollectionBehaviorCanJoinAllApplications = 0
    NSWindowCollectionBehaviorCanJoinAllSpaces = 0
    NSWindowCollectionBehaviorFullScreenAuxiliary = 0


WINDOW_LEVEL_MODE = "screensaver"
WINDOW_WIDTH = 520
WINDOW_MIN_HEIGHT = 168
WINDOW_MAX_HEIGHT = 560
REPLY_SCROLL_MAX_HEIGHT = 330
COMPACT_WINDOW_WIDTH = 520
COMPACT_WINDOW_HEIGHT = 168
PILL_WIDTH = 34
PILL_HEIGHT = 88
PILL_EDGE_MARGIN = 8
PILL_BOTTOM_MARGIN = 120
CONTENT_MARGIN_LEFT = 22
CONTENT_MARGIN_TOP = 12
CONTENT_MARGIN_RIGHT = 12
CONTENT_MARGIN_BOTTOM = 22
REPLY_LABEL_HPAD = 4
REPLY_LABEL_VPAD = 10
REPLY_WIDTH_RESERVED = 10
REPLY_MIN_VISIBLE_HEIGHT = 72

TITLE_MAP = {
    "wake": "我在",
    "listening": "正在聆听...",
    "recognized": "识别完成",
    "thinking": "正在思考...",
    "reply": "这是我的回答",
    "no_speech": "没有听清",
    "idle": "",
}


def activate_accessory_app() -> None:
    if sys.platform != "darwin" or objc is None:
        return
    try:
        app = NSApp
        if app is None and NSApplication is not None:
            app = NSApplication.sharedApplication()
        if NSRunningApplication is not None:
            current_app = NSRunningApplication.currentApplication()
            if current_app is not None:
                current_app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        if app is not None:
            app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
    except Exception:
        pass


def configure_native_window(widget: QWidget) -> None:
    if sys.platform != "darwin" or objc is None:
        return

    try:
        wid = int(widget.winId())
        ns_view = objc.objc_object(c_void_p=ctypes.c_void_p(wid))
        ns_window = ns_view.window()
        if ns_window is None:
            return

        behavior = (
            NSWindowCollectionBehaviorCanJoinAllSpaces
            | NSWindowCollectionBehaviorFullScreenAuxiliary
            | NSWindowCollectionBehaviorCanJoinAllApplications
        )
        ns_window.setCollectionBehavior_(behavior)

        if WINDOW_LEVEL_MODE == "screensaver":
            ns_window.setLevel_(NSScreenSaverWindowLevel)
        else:
            ns_window.setLevel_(NSStatusWindowLevel)

        if ns_window.respondsToSelector_("setHidesOnDeactivate:"):
            ns_window.setHidesOnDeactivate_(False)
        if ns_window.respondsToSelector_("setOpaque:"):
            ns_window.setOpaque_(False)
        if ns_window.respondsToSelector_("setBackgroundColor:"):
            ns_window.setBackgroundColor_(objc.nil)
    except Exception:
        pass


class SiriCardWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(2, 2, -2, -2)
        radius = 28

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        painter.save()
        painter.setClipPath(path)

        base_gradient = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
        base_gradient.setColorAt(0.00, QColor(124, 210, 255, 38))
        base_gradient.setColorAt(0.28, QColor(132, 118, 255, 30))
        base_gradient.setColorAt(0.64, QColor(206, 135, 255, 24))
        base_gradient.setColorAt(1.00, QColor(255, 181, 110, 18))
        painter.fillRect(rect, base_gradient)

        painter.fillRect(rect, QColor(248, 249, 253, 228))

        glow_tl = QRadialGradient(rect.left() + 78, rect.top() + 62, 180)
        glow_tl.setColorAt(0.0, QColor(110, 210, 255, 52))
        glow_tl.setColorAt(0.36, QColor(110, 210, 255, 18))
        glow_tl.setColorAt(1.0, QColor(110, 210, 255, 0))
        painter.fillRect(rect, glow_tl)

        glow_tr = QRadialGradient(rect.right() - 58, rect.top() + 58, 170)
        glow_tr.setColorAt(0.0, QColor(170, 128, 255, 44))
        glow_tr.setColorAt(0.40, QColor(170, 128, 255, 14))
        glow_tr.setColorAt(1.0, QColor(170, 128, 255, 0))
        painter.fillRect(rect, glow_tr)

        glow_bottom = QRadialGradient(rect.center().x(), rect.bottom() - 10, 230)
        glow_bottom.setColorAt(0.0, QColor(255, 184, 120, 22))
        glow_bottom.setColorAt(0.34, QColor(255, 184, 120, 10))
        glow_bottom.setColorAt(1.0, QColor(255, 184, 120, 0))
        painter.fillRect(rect, glow_bottom)

        top_highlight = QLinearGradient(rect.topLeft(), rect.bottomLeft())
        top_highlight.setColorAt(0.0, QColor(255, 255, 255, 112))
        top_highlight.setColorAt(0.18, QColor(255, 255, 255, 34))
        top_highlight.setColorAt(0.42, QColor(255, 255, 255, 0))
        painter.fillRect(rect, top_highlight)

        left_inner = QLinearGradient(rect.left(), rect.center().y(), rect.left() + 90, rect.center().y())
        left_inner.setColorAt(0.0, QColor(255, 255, 255, 48))
        left_inner.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, left_inner)

        right_inner = QLinearGradient(rect.right(), rect.center().y(), rect.right() - 90, rect.center().y())
        right_inner.setColorAt(0.0, QColor(255, 255, 255, 28))
        right_inner.setColorAt(1.0, QColor(255, 255, 255, 0))
        painter.fillRect(rect, right_inner)

        painter.restore()
        painter.setPen(QPen(QColor(255, 255, 255, 168), 1))
        painter.drawPath(path)

        inner_rect = rect.adjusted(1, 1, -1, -1)
        inner_path = QPainterPath()
        inner_path.addRoundedRect(inner_rect, radius - 1, radius - 1)
        painter.setPen(QPen(QColor(255, 255, 255, 78), 1))
        painter.drawPath(inner_path)


class SiriOrb(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.status = "idle"
        self.setFixedSize(14, 14)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def set_status(self, status: str):
        self.status = status
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), self.height())
        if self.status == "listening":
            gradient.setColorAt(0.0, QColor(52, 199, 89, 230))
            gradient.setColorAt(1.0, QColor(90, 200, 250, 210))
        elif self.status == "thinking":
            gradient.setColorAt(0.0, QColor(94, 92, 230, 230))
            gradient.setColorAt(1.0, QColor(191, 90, 242, 210))
        elif self.status == "reply":
            gradient.setColorAt(0.0, QColor(0, 122, 255, 230))
            gradient.setColorAt(1.0, QColor(90, 200, 250, 210))
        elif self.status == "no_speech":
            gradient.setColorAt(0.0, QColor(255, 69, 58, 220))
            gradient.setColorAt(1.0, QColor(255, 159, 10, 210))
        else:
            gradient.setColorAt(0.0, QColor(90, 200, 250, 220))
            gradient.setColorAt(1.0, QColor(191, 90, 242, 210))

        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(1, 1, 12, 12)
        painter.setBrush(QColor(255, 255, 255, 105))
        painter.drawEllipse(3, 3, 3, 3)


class CircleGlyphButton(QWidget):
    def __init__(
        self,
        glyph: str,
        bg_color: QColor,
        glyph_color: QColor,
        glyph_font_size: int,
        glyph_offset: tuple[int, int] = (0, 0),
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.glyph = glyph
        self.bg_color = bg_color
        self.glyph_color = glyph_color
        self.glyph_font_size = glyph_font_size
        self.glyph_offset = glyph_offset
        self.hovered = False
        self.pressed = False
        self.setFixedSize(14, 14)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)

    def enterEvent(self, event):
        self.hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.pressed = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        inside = self.rect().contains(event.pos())
        was_pressed = self.pressed
        self.pressed = False
        self.update()
        if was_pressed and inside and event.button() == Qt.LeftButton:
            self.clicked()
        super().mouseReleaseEvent(event)

    def clicked(self):
        pass

    def _current_bg(self) -> QColor:
        color = QColor(self.bg_color)
        if self.pressed:
            return color.darker(112)
        if self.hovered:
            return color.lighter(105)
        return color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._current_bg())
        painter.drawEllipse(rect)

        painter.setPen(self.glyph_color)
        font = QFont("SF Pro Display", self.glyph_font_size, QFont.DemiBold)
        painter.setFont(font)
        draw_rect = QRect(rect)
        dx, dy = self.glyph_offset
        draw_rect.translate(dx, dy)
        painter.drawText(draw_rect, Qt.AlignCenter, self.glyph)


class ReplyScrollArea(QScrollArea):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 6px;
                margin: 6px 2px 6px 0;
            }
            QScrollBar::handle:vertical {
                background: rgba(60, 60, 67, 88);
                border-radius: 3px;
                min-height: 24px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
                height: 0px;
            }
            """
        )
        self.viewport().setAttribute(Qt.WA_TranslucentBackground, True)
        self.viewport().setAutoFillBackground(False)
        self.viewport().setStyleSheet("background: transparent;")

    def set_scrollbar_visible(self, visible: bool):
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded if visible else Qt.ScrollBarAlwaysOff)

    def reset_to_top(self):
        self.verticalScrollBar().setValue(0)


class RestorePillWindow(QWidget):
    def __init__(self, owner: "OverlayWindow"):
        super().__init__(None)
        self.owner = owner
        self.status = "reply"

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.setFixedSize(PILL_WIDTH, PILL_HEIGHT)
        self.hide()

        QTimer.singleShot(0, lambda: configure_native_window(self))

    def set_status(self, status: str):
        self.status = status
        self.update()

    def target_pos(self) -> QPoint:
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.x() + screen.width() - self.width() - PILL_EDGE_MARGIN
        y = screen.y() + screen.height() - self.height() - PILL_BOTTOM_MARGIN
        return QPoint(x, y)

    def show_pill(self):
        self.move(self.target_pos())
        self.show()
        self.update()

    def hide_pill(self):
        self.hide()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.owner.restore_minimized_overlay()
        elif event.button() == Qt.RightButton:
            self.owner.on_force_stop_clicked()
        super().mouseReleaseEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 17, 17)

        painter.save()
        painter.setClipPath(path)

        bg = QLinearGradient(rect.left(), rect.top(), rect.right(), rect.bottom())
        bg.setColorAt(0.0, QColor(248, 249, 253, 232))
        bg.setColorAt(1.0, QColor(236, 239, 247, 226))
        painter.fillRect(rect, bg)

        glow = QRadialGradient(rect.center().x(), rect.top() + 22, 34)
        glow.setColorAt(0.0, QColor(130, 180, 255, 56))
        glow.setColorAt(1.0, QColor(130, 180, 255, 0))
        painter.fillRect(rect, glow)

        painter.restore()
        painter.setPen(QPen(QColor(255, 255, 255, 165), 1))
        painter.drawPath(path)

        orb_rect = QRect((self.width() - 14) // 2, 12, 14, 14)
        gradient = QLinearGradient(orb_rect.topLeft(), orb_rect.bottomRight())
        if self.status == "listening":
            gradient.setColorAt(0.0, QColor(52, 199, 89, 230))
            gradient.setColorAt(1.0, QColor(90, 200, 250, 210))
        elif self.status == "thinking":
            gradient.setColorAt(0.0, QColor(94, 92, 230, 230))
            gradient.setColorAt(1.0, QColor(191, 90, 242, 210))
        elif self.status == "reply":
            gradient.setColorAt(0.0, QColor(0, 122, 255, 230))
            gradient.setColorAt(1.0, QColor(90, 200, 250, 210))
        elif self.status == "no_speech":
            gradient.setColorAt(0.0, QColor(255, 69, 58, 220))
            gradient.setColorAt(1.0, QColor(255, 159, 10, 210))
        else:
            gradient.setColorAt(0.0, QColor(90, 200, 250, 220))
            gradient.setColorAt(1.0, QColor(191, 90, 242, 210))

        painter.setPen(Qt.NoPen)
        painter.setBrush(gradient)
        painter.drawEllipse(orb_rect)
        painter.setBrush(QColor(255, 255, 255, 110))
        painter.drawEllipse(orb_rect.adjusted(2, 2, -8, -8))

        painter.setPen(QPen(QColor(68, 68, 78, 220), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        cx = self.width() / 2 + 1.0
        cy = 54.0
        width = 7.0
        height = 10.0
        chevron = QPainterPath()
        chevron.moveTo(cx + width / 2, cy - height / 2)
        chevron.lineTo(cx - width / 2, cy)
        chevron.lineTo(cx + width / 2, cy + height / 2)
        painter.drawPath(chevron)


class OverlayWindow(QWidget):
    def __init__(self, state: OverlayStateManager, poll_interval_ms: int):
        super().__init__(None)
        self.state = state
        self.last_payload: dict | None = None
        self.last_mtime = 0.0
        self.current_status = "idle"
        self.is_minimized = False
        self.last_non_idle_payload: dict | None = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, True)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow, True)
        self.setAttribute(Qt.WA_NativeWindow, True)
        self.resize(COMPACT_WINDOW_WIDTH, COMPACT_WINDOW_HEIGHT)
        self.setMinimumHeight(WINDOW_MIN_HEIGHT)
        self.setMaximumHeight(WINDOW_MAX_HEIGHT)

        self.card = SiriCardWidget(self)
        self.orb = SiriOrb()

        self.status_label = QLabel(TITLE_MAP["reply"])
        self.status_label.setFont(QFont("SF Pro Display", 14, QFont.DemiBold))
        self.status_label.setStyleSheet("color: rgba(68,68,78,0.88); background: transparent;")

        self.minimize_button = CircleGlyphButton(
            glyph="-",
            bg_color=QColor(52, 199, 89, 245),
            glyph_color=QColor(40, 40, 46, 235),
            glyph_font_size=10,
            glyph_offset=(0, -1),
            parent=self,
        )
        self.minimize_button.clicked = self.minimize_current
        self.minimize_button.setVisible(False)

        self.stop_tts_button = CircleGlyphButton(
            glyph="x",
            bg_color=QColor(255, 59, 48, 245),
            glyph_color=QColor(40, 40, 46, 235),
            glyph_font_size=9,
            glyph_offset=(0, -1),
            parent=self,
        )
        self.stop_tts_button.clicked = self.on_force_stop_clicked
        self.stop_tts_button.setVisible(False)

        self.user_label = QLabel("")
        self.user_label.setFont(QFont("PingFang SC", 13))
        self.user_label.setWordWrap(False)
        self.user_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.user_label.setStyleSheet("color: rgba(112,112,122,0.88); background: transparent;")

        self.reply_label = QLabel("")
        self.reply_label.setFont(QFont("PingFang SC", 16))
        self.reply_label.setWordWrap(True)
        self.reply_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.reply_label.setTextFormat(Qt.PlainText)
        self.reply_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.reply_label.setStyleSheet(
            """
            color: rgba(18,18,22,0.96);
            background: transparent;
            padding: 4px 2px 6px 2px;
            line-height: 1.28;
            """
        )

        self.reply_container = QWidget()
        self.reply_container.setAttribute(Qt.WA_TranslucentBackground, True)
        self.reply_container.setAutoFillBackground(False)
        self.reply_container.setStyleSheet("background: transparent;")

        reply_layout = QVBoxLayout(self.reply_container)
        reply_layout.setContentsMargins(0, 0, 0, 0)
        reply_layout.setSpacing(0)
        reply_layout.addWidget(self.reply_label)

        self.reply_scroll = ReplyScrollArea()
        self.reply_scroll.setMaximumHeight(REPLY_SCROLL_MAX_HEIGHT)
        self.reply_scroll.setMinimumHeight(0)
        self.reply_scroll.setWidget(self.reply_container)

        self.meta_label = QLabel("")
        self.meta_label.setFont(QFont("PingFang SC", 11))
        self.meta_label.setStyleSheet("color: rgba(120,120,128,0.66); background: transparent;")

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(6)
        top_row.addWidget(self.orb, 0, Qt.AlignVCenter)
        top_row.addWidget(self.status_label, 1, Qt.AlignVCenter)
        top_row.addWidget(self.minimize_button, 0, Qt.AlignTop)
        top_row.addWidget(self.stop_tts_button, 0, Qt.AlignTop)

        content = QVBoxLayout()
        content.setContentsMargins(CONTENT_MARGIN_LEFT, CONTENT_MARGIN_TOP, CONTENT_MARGIN_RIGHT, CONTENT_MARGIN_BOTTOM)
        content.setSpacing(12)
        content.addLayout(top_row)
        content.addWidget(self.user_label)
        content.addWidget(self.reply_scroll)
        content.addWidget(self.meta_label)
        self.card.setLayout(content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.card)

        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(220)
        self.fade_anim.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_anim.finished.connect(self._on_fade_finished)

        self.pos_anim = QPropertyAnimation(self, b"pos")
        self.pos_anim.setDuration(260)
        self.pos_anim.setEasingCurve(QEasingCurve.OutCubic)

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)

        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.check_state_file)
        self.poll_timer.start(poll_interval_ms)

        self.target_pos = QPoint(0, 0)
        self.restore_pill = RestorePillWindow(self)
        self.setWindowOpacity(0.0)
        self.hide()

        QTimer.singleShot(0, lambda: configure_native_window(self))

    def _on_fade_finished(self):
        if self.windowOpacity() <= 0.01:
            self.hide()

    def _show_restore_pill(self):
        payload = self.last_non_idle_payload or {}
        status = payload.get("status", "reply")
        if self.is_minimized and payload and status != "idle":
            self.restore_pill.set_status(status)
            self.restore_pill.show_pill()
        else:
            self.restore_pill.hide_pill()

    def on_force_stop_clicked(self):
        self.state.request_stop()
        self.is_minimized = False
        self.last_non_idle_payload = None
        self.hide_timer.stop()
        self.meta_label.setText("已中断")
        self.meta_label.setVisible(True)
        self.restore_pill.hide_pill()
        self.fade_out()

    def minimize_current(self):
        if self.current_status == "idle":
            return
        self.is_minimized = True
        self.hide_timer.stop()
        self.hide()
        self.setWindowOpacity(0.0)
        self._show_restore_pill()

    def restore_minimized_overlay(self):
        payload = self.last_non_idle_payload
        if not self.is_minimized or not payload:
            self._show_restore_pill()
            return

        self.is_minimized = False
        self.restore_pill.hide_pill()
        self.set_content(
            status=payload.get("status", "idle"),
            user_text=payload.get("user_text", ""),
            reply_text=payload.get("reply_text", ""),
            meta_text=payload.get("meta_text", ""),
            auto_hide_ms=0,
            from_restore=True,
        )

    def _calc_target_pos_for_size(self, width: int, height: int) -> QPoint:
        screen = QApplication.primaryScreen().availableGeometry()
        x = screen.x() + screen.width() - width - 16
        y = screen.y() + screen.height() - height - 24
        return QPoint(x, y)

    def _reply_text_width(self) -> int:
        width = WINDOW_WIDTH - CONTENT_MARGIN_LEFT - CONTENT_MARGIN_RIGHT - REPLY_WIDTH_RESERVED
        return max(360, width)

    def _measure_reply_text_height(self, text: str, text_width: int) -> int:
        doc = QTextDocument()
        doc.setDocumentMargin(0)
        doc.setDefaultFont(self.reply_label.font())
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        doc.setDefaultTextOption(option)
        doc.setPlainText(text or "")
        doc.setTextWidth(max(1, text_width - REPLY_LABEL_HPAD))
        text_height = math.ceil(doc.size().height())
        return text_height + REPLY_LABEL_VPAD

    def _apply_compact_window_size(self):
        self.reply_scroll.setVisible(False)
        self.reply_label.clear()
        self.reply_label.setFixedWidth(self._reply_text_width())
        self.reply_container.setFixedWidth(self._reply_text_width())
        self.reply_scroll.setMinimumHeight(0)
        self.reply_scroll.setMaximumHeight(REPLY_SCROLL_MAX_HEIGHT)
        self.reply_scroll.set_scrollbar_visible(False)
        self.reply_scroll.reset_to_top()
        self.resize(COMPACT_WINDOW_WIDTH, COMPACT_WINDOW_HEIGHT)

    def _apply_reply_window_size(self, reply_text: str):
        text_width = self._reply_text_width()
        measured_height = self._measure_reply_text_height(reply_text, text_width)
        need_scroll = measured_height > REPLY_SCROLL_MAX_HEIGHT
        target_height = REPLY_SCROLL_MAX_HEIGHT if need_scroll else max(REPLY_MIN_VISIBLE_HEIGHT, measured_height)

        self.reply_label.setFixedWidth(text_width)
        self.reply_container.setFixedWidth(text_width)
        self.reply_label.setMinimumHeight(measured_height)
        self.reply_label.adjustSize()
        self.reply_scroll.setMinimumHeight(target_height)
        self.reply_scroll.setMaximumHeight(target_height)
        self.reply_scroll.set_scrollbar_visible(need_scroll)
        self.reply_scroll.reset_to_top()
        self.reply_scroll.setVisible(True)

        self.card.layout().activate()
        self.adjustSize()
        target_window_height = max(WINDOW_MIN_HEIGHT, min(self.sizeHint().height(), WINDOW_MAX_HEIGHT))
        self.resize(WINDOW_WIDTH, target_window_height)

    def show_overlay(self):
        width = self.width()
        height = self.height()
        self.target_pos = self._calc_target_pos_for_size(width, height)
        start_pos = QPoint(self.target_pos.x(), self.target_pos.y() + 10)

        self.move(start_pos)
        self.show()

        self.fade_anim.stop()
        self.fade_anim.setStartValue(self.windowOpacity())
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

        self.pos_anim.stop()
        self.pos_anim.setStartValue(start_pos)
        self.pos_anim.setEndValue(self.target_pos)
        self.pos_anim.start()

    def fade_out(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(self.windowOpacity())
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.start()

    def set_content(
        self,
        status: str,
        user_text: str = "",
        reply_text: str = "",
        meta_text: str = "",
        auto_hide_ms: int = 4000,
        from_restore: bool = False,
    ):
        self.current_status = status
        self.orb.set_status(status)

        self.status_label.setText(TITLE_MAP.get(status, "Jarvis"))
        self.status_label.setVisible(status != "idle")

        if user_text:
            elided = user_text if len(user_text) <= 24 else user_text[:24] + "…"
            self.user_label.setText(f"你说：{elided}")
            self.user_label.setVisible(True)
        else:
            self.user_label.setVisible(False)
            self.user_label.setText("")

        has_reply = bool(reply_text and reply_text.strip())
        self.minimize_button.setVisible(status != "idle")
        self.stop_tts_button.setVisible(status != "idle")

        if status != "idle":
            self.last_non_idle_payload = {
                "status": status,
                "user_text": user_text,
                "reply_text": reply_text,
                "meta_text": meta_text,
                "auto_hide_ms": auto_hide_ms,
            }
        else:
            self.last_non_idle_payload = None
            self.is_minimized = False

        if has_reply:
            self.reply_label.setText(reply_text)
            self._apply_reply_window_size(reply_text)
        else:
            self._apply_compact_window_size()

        self.meta_label.setText(meta_text or "")
        self.meta_label.setVisible(bool(meta_text))

        self._show_restore_pill()
        if status == "idle":
            self.fade_out()
            return

        if self.is_minimized and not from_restore:
            return

        self.show_overlay()

        if auto_hide_ms and status in {"wake", "recognized", "reply", "no_speech"}:
            self.hide_timer.start(auto_hide_ms)
        else:
            self.hide_timer.stop()

    def check_state_file(self):
        state_path: Path = self.state.config.state_file
        if not state_path.exists():
            return

        try:
            mtime = state_path.stat().st_mtime
            if mtime == self.last_mtime:
                return
            self.last_mtime = mtime

            payload = json.loads(state_path.read_text(encoding="utf-8"))
            if payload == self.last_payload:
                return
            self.last_payload = payload

            self.set_content(
                status=payload.get("status", "idle"),
                user_text=payload.get("user_text", ""),
                reply_text=payload.get("reply_text", ""),
                meta_text=payload.get("meta_text", ""),
                auto_hide_ms=int(payload.get("auto_hide_ms", 4000)),
            )
        except Exception:
            pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the OpenClaw overlay UI.")
    parser.add_argument("--config", help="Path to config YAML file.")
    parser.add_argument("--env-file", help="Optional .env file to load before config expansion.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    config = load_config(config_path=args.config, env_path=args.env_file)
    state = OverlayStateManager(config.overlay)
    state.ensure_idle_state(reset=True)

    activate_accessory_app()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    activate_accessory_app()
    QTimer.singleShot(0, activate_accessory_app)
    QTimer.singleShot(250, activate_accessory_app)

    window = OverlayWindow(state, config.overlay.poll_interval_ms)
    window.show()
    window.hide()
    QTimer.singleShot(500, activate_accessory_app)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
