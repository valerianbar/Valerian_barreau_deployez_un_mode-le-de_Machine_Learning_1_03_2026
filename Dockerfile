# Doc HF: https://huggingface.co/docs/hub/spaces-sdks-docker
FROM python:3.13-slim

# ── Dépendances système (gcc/g++ pour scikit-learn/xgboost, libgomp1 pour OpenMP) ──
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ── User non-root (obligatoire sur HF Spaces, bonne pratique sécurité) ──
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# ── Installation des dépendances Python ──
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ── Copie du code ──
COPY --chown=user . /app

# ── Port flexible : 7860 par défaut (HF Spaces), surchargeable via $PORT ──
EXPOSE 7860

CMD ["sh", "-c", "uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-7860}"]
