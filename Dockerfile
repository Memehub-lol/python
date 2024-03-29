FROM python:3.10.5-buster
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1 
ENV TERM=xterm 
RUN --mount=type=cache,target=/var/cache/apt \
	--mount=type=cache,target=/var/lib/apt \
	apt-get update && apt-get install -qq -y \
	apt-transport-https ca-certificates curl gnupg \
	build-essential libpq-dev tesseract-ocr sqlite3 libsqlite3-dev python3-setuptools tree \
	--no-install-recommends && rm -rf /var/lib/apt/lists/*
RUN curl -sLf --retry 3 --tlsv1.2 --proto "=https" 'https://packages.doppler.com/public/cli/gpg.DE2A7741A397C129.key' | apt-key add - && \
	echo "deb https://packages.doppler.com/public/cli/deb/debian any-version main" | tee /etc/apt/sources.list.d/doppler-cli.list && \
	apt-get update && \
	apt-get -y install doppler
WORKDIR /app
USER root
RUN --mount=type=cache,target=/root/.cache/pip pip install torch===1.12.0+cpu \
	torchvision===0.13.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt
ADD start.flask.sh /
RUN chmod +x /start.flask.sh