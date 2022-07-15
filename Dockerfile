FROM python:3.10.5-buster
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1 
ENV TERM=xterm 
ENV IS_DOCKER=1
RUN --mount=type=cache,target=/var/cache/apt \
	--mount=type=cache,target=/var/lib/apt \
	apt-get update && apt-get install -qq -y \
	build-essential libpq-dev tesseract-ocr sqlite3 libsqlite3-dev python3-setuptools tree \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*
WORKDIR /app
USER root
RUN --mount=type=cache,target=/root/.cache/pip pip install torch===1.12.0+cpu \
	torchvision===0.13.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
ADD start.flask.sh /
RUN chmod +x /start.flask.sh