def load_stylesheet(file_path="Resources/styles.qss"):
    with open(file_path, "r") as f:
        return f.read()

def emit_signal(signal_name):
    from Utils.signal_manager import signal_manager
    signal_manager.navigate.emit(signal_name)