#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
StackTraceViewer.py
A small GUI tool to parse stack traces from a log file and resolve symbols
via llvm-symbolizer using a user-provided library directory.
"""

import os
import re
import sys
import shutil
import subprocess
from collections import defaultdict

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QPlainTextEdit,
    QLabel,
)
from PyQt5.QtCore import QSettings


STACK_RE = re.compile(
    r"^\s*(?:#(?P<frame1>\d+)|(?P<frame2>\d+)>)[ \t]+"
    r"(?P<lib_path>\S+)[ \t]+\+(?P<addr>0x[0-9a-fA-F]+)"
)


class StackTraceViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stack Trace Viewer")
        self.setGeometry(100, 100, 1200, 800)

        self.log_file = ""
        self.lib_dir = ""
        self.context_lines = 2

        self.init_ui()

        settings = QSettings("StackTraceViewer", "PathPlan")
        self.lib_dir = settings.value("lib_path", "")
        if self.lib_dir:
            self.set_lib_path_btn.setToolTip(f"Current: {self.lib_dir}")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()

        self.select_log_btn = QPushButton("Select Log File")
        self.select_log_btn.clicked.connect(self.select_log_file)
        button_layout.addWidget(self.select_log_btn)

        self.set_lib_path_btn = QPushButton("Select Libs Directory")
        self.set_lib_path_btn.clicked.connect(self.select_lib_dir)
        button_layout.addWidget(self.set_lib_path_btn)

        main_layout.addLayout(button_layout)

        self.status_label = QLabel("No log file selected.")
        main_layout.addWidget(self.status_label)

        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        main_layout.addWidget(self.output_text)

    def select_log_file(self):
        settings = QSettings("StackTraceViewer", "PathPlan")
        last_path = settings.value("last_log_directory", "")

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Log File", last_path, "Log Files (*)"
        )
        if not file_path:
            return

        settings.setValue("last_log_directory", os.path.dirname(file_path))
        self.log_file = file_path
        self.status_label.setText(f"Log: {self.log_file}")
        self.try_parse()

    def select_lib_dir(self):
        settings = QSettings("StackTraceViewer", "PathPlan")
        current_path = self.lib_dir if self.lib_dir else settings.value("last_log_directory", "")

        directory = QFileDialog.getExistingDirectory(
            self, "Select Library Directory", current_path
        )
        if not directory:
            return

        self.lib_dir = directory
        settings.setValue("lib_path", directory)
        self.set_lib_path_btn.setToolTip(f"Current: {self.lib_dir}")
        self.try_parse()

    def try_parse(self):
        if not self.log_file:
            return

        self.output_text.setPlainText("Parsing log...\n")
        output_lines = self.parse_log_file(self.log_file)
        self.output_text.clear()
        chunk_size = 200
        for i in range(0, len(output_lines), chunk_size):
            chunk_text = "\n".join(output_lines[i:i + chunk_size])
            if i == 0:
                self.output_text.setPlainText(chunk_text)
            else:
                self.output_text.appendPlainText(chunk_text)
            QApplication.processEvents()

    def parse_log_file(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = [line.rstrip("\n") for line in f]
        except Exception as exc:
            return [f"Failed to read log file: {exc}"]

        blocks = []
        pending_symbols = defaultdict(set)
        current_block = None
        last_frame_no = None
        last_line_idx = None

        for idx, line in enumerate(lines):
            match = STACK_RE.match(line)
            if not match:
                continue

            lib_path = match.group("lib_path")
            addr = match.group("addr")
            frame_no = int(match.group("frame1") or match.group("frame2"))
            pending_symbols[lib_path].add(addr)

            if (
                current_block
                and last_line_idx is not None
                and idx == last_line_idx + 1
                and last_frame_no is not None
                and frame_no == last_frame_no + 1
            ):
                current_block["end_idx"] = idx
            else:
                current_block = {
                    "start_idx": idx,
                    "end_idx": idx,
                    "frames": [],
                }
                blocks.append(current_block)

            current_block["frames"].append(
                {
                    "line_index": idx,
                    "line": line,
                    "lib_path": lib_path,
                    "addr": addr,
                    "frame_no": frame_no,
                }
            )
            last_frame_no = frame_no
            last_line_idx = idx

        symbol_cache, warnings = self.resolve_symbols(pending_symbols)

        if not blocks:
            return ["No stack trace lines found."]

        output_lines = []
        total_frames = sum(len(block["frames"]) for block in blocks)
        output_lines.append(
            f"Found {len(blocks)} stack trace blocks ({total_frames} frames).\n"
        )

        for i, block in enumerate(blocks, start=1):
            start_idx = block["start_idx"]
            end_idx = block["end_idx"]
            start_line_no = start_idx + 1
            end_line_no = end_idx + 1
            before_start = max(0, start_idx - self.context_lines)
            after_end = min(len(lines), end_idx + self.context_lines + 1)

            output_lines.append(
                f"=== Block {i} (lines {start_line_no}-{end_line_no}) ==="
            )
            output_lines.append("Context before:")
            if before_start < start_idx:
                for ctx_idx, ctx_line in enumerate(
                    lines[before_start:start_idx], start=before_start + 1
                ):
                    output_lines.append(f"  {ctx_idx}: {ctx_line}")
            else:
                output_lines.append("  (none)")

            output_lines.append("Frames:")
            for frame in block["frames"]:
                line_no = frame["line_index"] + 1
                lib_path = frame["lib_path"]
                addr = frame["addr"]
                func_name = symbol_cache.get((lib_path, addr), "??")
                output_lines.append(
                    f"  {line_no}: {frame['line']} => {func_name}"
                )

            output_lines.append("Context after:")
            if end_idx + 1 < after_end:
                for ctx_idx, ctx_line in enumerate(
                    lines[end_idx + 1:after_end], start=end_idx + 2
                ):
                    output_lines.append(f"  {ctx_idx}: {ctx_line}")
            else:
                output_lines.append("  (none)")
            output_lines.append("")

        if warnings:
            output_lines.append("Warnings:")
            output_lines.extend(warnings)

        return output_lines

    def resolve_symbols(self, pending_symbols):
        symbol_cache = {}
        warnings = []

        if not pending_symbols:
            return symbol_cache, warnings

        if not self.lib_dir:
            warnings.append("No libs directory set; symbols not resolved.")
            return symbol_cache, warnings

        symbolizer_path = shutil.which("llvm-symbolizer")
        if not symbolizer_path:
            warnings.append("llvm-symbolizer not found in PATH; symbols not resolved.")
            return symbol_cache, warnings

        for lib_full_path, addrs in pending_symbols.items():
            relative_path = lib_full_path.lstrip("/")
            lib_file_path = os.path.join(self.lib_dir, relative_path)
            if not os.path.exists(lib_file_path):
                lib_file_path = os.path.join(self.lib_dir, os.path.basename(lib_full_path))

            if not os.path.exists(lib_file_path):
                warnings.append(f"Library not found: {lib_file_path}")
                continue

            symbolizer_cmd = [symbolizer_path, "--obj", lib_file_path, "--inlining=false"]
            sorted_addrs = sorted(list(addrs))

            try:
                process = subprocess.Popen(
                    symbolizer_cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                stdout, stderr = process.communicate(input="\n".join(sorted_addrs))

                if process.returncode != 0:
                    warnings.append(f"llvm-symbolizer failed for {lib_full_path}: {stderr.strip()}")
                    continue

                lines = [l for l in stdout.strip().split("\n") if l.strip()]
                expected = len(sorted_addrs) * 2
                if len(lines) != expected:
                    warnings.append(
                        f"llvm-symbolizer output mismatch for {lib_full_path}: expected {expected}, got {len(lines)}"
                    )
                    continue

                for i, addr in enumerate(sorted_addrs):
                    func_name = lines[i * 2]
                    symbol_cache[(lib_full_path, addr)] = func_name

            except Exception as exc:
                warnings.append(f"Error resolving symbols for {lib_full_path}: {exc}")

        return symbol_cache, warnings


def main():
    app = QApplication(sys.argv)
    viewer = StackTraceViewer()
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
