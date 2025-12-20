# core/logger.py
LOG_BUFFER = []


def log(message: str):
    """Zapisuje wiadomość w buforze i wypisuje w terminalu."""
    print(f"[SERVER LOG] {message}")
    LOG_BUFFER.append(message)

    # Trzymaj tylko ostatnie 1000 logów, żeby nie zapchać pamięci
    if len(LOG_BUFFER) > 1000:
        LOG_BUFFER.pop(0)


def get_logs():
    """Zwraca i czyści bufor."""
    global LOG_BUFFER
    logs_to_send = list(LOG_BUFFER)
    LOG_BUFFER.clear()
    return logs_to_send