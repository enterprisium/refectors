# Builder stage
FROM python:3.10.0 as builder

# Create a non-root user
RUN useradd -ms /bin/bash admin

# Set the working directory
WORKDIR /srv

# Copy requirements file first to leverage caching
COPY --chown=admin requirements.txt .


# Install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  wget ffmpeg curl aria2 \
  fonts-liberation \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libatspi2.0-0 \
  libcups2 \
  libdrm2 \
  libgbm1 \
  libgtk-3-0 \
  libnspr4 \
  libnss3 \
  libu2f-udev \
  libvulkan1 \
  libxcomposite1 \
  libxdamage1 \
  mesa-vulkan-drivers \
  libxfixes3 \
  libasound2 \
  libxkbcommon0 \
  libxrandr2 \
  xdg-utils \
  software-properties-common \
  npm

# Install youtubeuploader
ADD https://github.com/porjo/youtubeuploader/releases/download/23.06/youtubeuploader_23.06_Linux_x86_64.tar.gz youtubeuploader.tar.gz
RUN mkdir -p /srv/youtube && \
  tar -zxvf youtubeuploader.tar.gz -C /srv/youtube && \
  rm youtubeuploader.tar.gz && \
  chmod +x /srv/youtube/youtubeuploader

# Install latest npm and node
RUN npm install npm@latest -g && \
  npm install n -g && \
  n latest

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install unsilence
RUN pipx ensurepath && \
  pipx install unsilence

# Copy the application code
COPY --chown=admin . /srv




# Command to run the application
# CMD python -m uvicorn App.app:app --host 0.0.0.0 --port 7860 &  python -m celery -A App.Worker.celery worker -c 5  --max-tasks-per-child=1  --without-heartbeat 

# Give read and write permissions to the admin user

RUN chown -R admin:admin /srv
RUN chmod 755 /srv
USER admin
CMD python -m uvicorn App.app:app --workers 4 --host 0.0.0.0 --port 7860 

# Expose port
EXPOSE 7860