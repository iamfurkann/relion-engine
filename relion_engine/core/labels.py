"""
Labels and classification for analysis results.
Maps numeric scores to human-readable Turkish labels and severity levels.
"""

def get_soh_label(soh: float) -> str:
    """Classify State of Health into a Turkish label."""
    if soh >= 90:
        return "Mükemmel"
    elif soh >= 80:
        return "İyi"
    elif soh >= 70:
        return "Orta"
    elif soh >= 60:
        return "Zayıf"
    else:
        return "Kritik"

def get_rul_label(rul: float) -> str:
    """Classify Remaining Useful Life into a Turkish label."""
    if rul >= 3000:
        return "Uzun Ömür"
    elif rul >= 1500:
        return "Yeterli Ömür"
    elif rul >= 500:
        return "Sınırlı Ömür"
    elif rul > 0:
        return "Düşük Ömür"
    else:
        return "Ömrünü Tamamlamış"

def get_tus_label(tus: float) -> str:
    """Classify Technical Suitability Score into a Turkish label."""
    if tus >= 80:
        return "Çok Uygun"
    elif tus >= 60:
        return "Uygun"
    elif tus >= 40:
        return "Şartlı Uygun"
    elif tus >= 20:
        return "Riskli"
    else:
        return "Uygun Değil"

def get_eus_label(eus: float) -> str:
    """Classify Economic Suitability Score into a Turkish label."""
    if eus >= 80:
        return "Çok Kârlı"
    elif eus >= 60:
        return "Kârlı"
    elif eus >= 40:
        return "Marjinal"
    elif eus >= 20:
        return "Düşük Getiri"
    else:
        return "Ekonomik Değil"

def get_score_label(score: float) -> str:
    """Classify General Score into a Turkish label."""
    if score >= 80:
        return "Çok Uygun"
    elif score >= 60:
        return "Uygun"
    elif score >= 40:
        return "Şartlı Uygun"
    elif score >= 20:
        return "Riskli"
    else:
        return "Uygun Değil"

def get_score_color(score: float) -> str:
    """Return a CSS-friendly hex color for dashboard gauges."""
    if score >= 80:
        return "#22c55e"  # green
    elif score >= 60:
        return "#3b82f6"  # blue
    elif score >= 40:
        return "#f59e0b"  # amber
    elif score >= 20:
        return "#f97316"  # orange
    else:
        return "#ef4444"  # red
