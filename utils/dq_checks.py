def run_dq_checks(text: str):
    if not text or len(text.split()) < 10:
        return False, "Transcript too short or empty"
    return True, "OK"
