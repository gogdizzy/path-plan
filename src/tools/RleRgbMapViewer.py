import sys
from dataclasses import dataclass


@dataclass
class RleRgbMap:
    stx: int
    sty: int
    edx: int
    edy: int
    width: int
    height: int
    buffer: bytearray
    decoded_pixels: int


def _parse_header(line: str):
    parts = line.strip().split()
    if len(parts) != 4:
        raise ValueError("Header must be: StX StY EdX EdY")
    stx, sty, edx, edy = map(int, parts)
    width = edx - stx + 1
    height = edy - sty + 1
    if width <= 0 or height <= 0:
        raise ValueError("Invalid range in header")
    return stx, sty, edx, edy, width, height


def _fill_buffer(buf: bytearray, pos: int, count: int, rgb: bytes) -> int:
    if count <= 0:
        return pos
    remaining = min(count * 3, len(buf) - pos)
    if remaining <= 0:
        return pos
    pixels_per_chunk = 4096
    chunk = rgb * pixels_per_chunk
    while remaining > 0:
        step = min(remaining, len(chunk))
        buf[pos:pos + step] = chunk[:step]
        pos += step
        remaining -= step
    return pos


def decode_rle_rgb(path: str) -> RleRgbMap:
    with open(path, "rb") as file_obj:
        header = file_obj.readline()
        if not header:
            raise ValueError("Empty file")
        stx, sty, edx, edy, width, height = _parse_header(header.decode("ascii", "strict"))
        data = file_obj.read()

    buf = bytearray(width * height * 3)
    idx = 0
    write_pos = 0

    while idx < len(data) and write_pos < len(buf):
        if idx + 3 > len(data):
            break
        r = data[idx]
        g = data[idx + 1]
        b = data[idx + 2]
        idx += 3

        while idx < len(data) and data[idx] in b" \t\r\n":
            idx += 1
        if idx >= len(data):
            break

        start = idx
        while idx < len(data) and data[idx] not in b" \t\r\n":
            idx += 1
        if start == idx:
            break

        try:
            count = int(data[start:idx].decode("ascii"))
        except ValueError:
            break

        write_pos = _fill_buffer(buf, write_pos, count, bytes((r, g, b)))

        while idx < len(data) and data[idx] in b" \t\r\n":
            idx += 1

    decoded_pixels = write_pos // 3
    return RleRgbMap(stx, sty, edx, edy, width, height, buf, decoded_pixels)


def run_viewer(file_path: str):
    from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QScrollArea
    from PyQt5.QtGui import QImage, QPixmap
    from PyQt5.QtCore import Qt

    rgb_map = decode_rle_rgb(file_path)
    image = QImage(rgb_map.buffer, rgb_map.width, rgb_map.height, rgb_map.width * 3, QImage.Format_RGB888)
    pixmap = QPixmap.fromImage(image)

    window = QMainWindow()
    window.setWindowTitle("RLE RGB Map Viewer")

    container = QWidget()
    layout = QVBoxLayout(container)

    info = (
        f"Range: [{rgb_map.stx} {rgb_map.sty} {rgb_map.edx} {rgb_map.edy}]  "
        f"Size: {rgb_map.width}x{rgb_map.height}  "
        f"Decoded: {rgb_map.decoded_pixels}/{rgb_map.width * rgb_map.height}"
    )
    info_label = QLabel(info)
    info_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

    image_label = QLabel()
    image_label.setPixmap(pixmap)
    image_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)

    scroll_area = QScrollArea()
    scroll_area.setWidget(image_label)
    scroll_area.setWidgetResizable(True)

    layout.addWidget(info_label)
    layout.addWidget(scroll_area)

    window.setCentralWidget(container)
    window.showMaximized()

    window._img_buf = rgb_map.buffer
    window._image = image
    window._pixmap = pixmap
    return window


def main():
    from PyQt5.QtWidgets import QApplication
    from src.modules import FileOpener

    app = QApplication(sys.argv)
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_opener = FileOpener(None, "RleRgbMapViewer")
        file_path = file_opener.getPath()
    window = run_viewer(file_path)
    app._main_window = window
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
