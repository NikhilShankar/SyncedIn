# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Install system dependencies for LaTeX and font handling
# Corrected command - Use this if we need the whole latex environment
RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-luatex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-latex-extra \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# ADD THIS OPTIMIZED BLOCK INSTEAD

## 1. Install prerequisites for TinyTeX and font management
#RUN apt-get update && apt-get install -y --no-install-recommends \
#    wget \
#    perl \
#    fontconfig \
#    && rm -rf /var/lib/apt/lists/*
#
## 2. Download and install TinyTeX, a minimal LaTeX distribution
#RUN wget -qO- "https://yihui.org/tinytex/install-bin-unix.sh" | sh -s - --admin --no-path \
#    && mv /root/bin/* /usr/local/bin/ \
#    && rmdir /root/bin
#
## 3. Use TinyTeX's manager (tlmgr) to install only the necessary packages
#RUN tlmgr update --self \
#    && tlmgr install \
#    luatex \
#    luaotfload \
#    fontspec \
#    latex-base \
#    latex-recommended \
#    titlesec \
#    lm-math \
#    && tlmgr path add

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY *.tex ./
COPY resume_data_enhanced.json ./
COPY llm_config.json ./

# Copy font files to both locations
# 1. Keep in app directory for LaTeX to find by filename
COPY fonts/ ./fonts/
# 2. Also copy individual font files to working directory for direct access
COPY fonts/*.ttf ./

# Install custom fonts system-wide for fontconfig
RUN mkdir -p /usr/share/fonts/truetype/lato && \
    cp fonts/*.ttf /usr/share/fonts/truetype/lato/ && \
    fc-cache -f -v

# Create necessary directories with proper permissions
RUN mkdir -p generated output resume_backups && \
    chmod 777 generated output resume_backups && \
    touch applications_tracking.json && \
    echo "[]" > applications_tracking.json && \
    chmod 666 applications_tracking.json

# Expose custom port (8765 instead of default 8501)
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8765/_stcore/health')" || exit 1

# Run Streamlit app on port 8765
CMD ["streamlit", "run", "main_app.py", "--server.port=8765", "--server.address=0.0.0.0", "--server.headless=true"]