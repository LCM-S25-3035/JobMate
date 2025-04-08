# 🚀 Job Scraping Pipeline with Airflow (Docker Edition)

This project sets up a full job data scraping and enrichment pipeline using **Apache Airflow** and  **Docker** , suitable for Windows development environments.

---

## 📁 Project Structure

```
project/
├── airflow-docker/           # Docker + Airflow setup
├── dags/                     # Airflow DAGs
│   └── job_pipeline_dag.py
├── src/data_gathering/       # Python scraping + processing scripts
│   ├── GlassdoorDataGathering.py
│   ├── JobSpy.py
│   └── ...
```

---

## 🧱 Setup Instructions

### 1. Clone or Create Docker Folder

If using the official Apache Airflow repo:

```bash
cd C:\metricsPipeline\project
git clone https://github.com/apache/airflow.git airflow-docker
```

Or create it manually:

```bash
mkdir airflow-docker
cd airflow-docker
```

### 2. Create `docker-compose.yml`

Inside `airflow-docker/`, create a file `docker-compose.yml`:

```yaml

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
      AIRFLOW__WEBSERVER__SECRET_KEY: my_super_secret_key
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data

  webserver:
    build: .
    image: custom-airflow:latest
    restart: always
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CORE__FERNET_KEY: ''
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__WEBSERVER__SECRET_KEY: qv3p3v9Iw3YT6KvlXzq2KiZEq0PSoA9kQff8Pym4pQM=
      _PIP_ADDITIONAL_REQUIREMENTS: -r /requirements.txt
    volumes:
      - ../dags:/opt/airflow/dags
      - ../src:/opt/airflow/src
      - ../requirements.txt:/requirements.txt
    ports:
      - "8080:8080"
    command:  >
      bash -c "
        pip install -r /requirements.txt &&
        airflow webserver
      "

  scheduler:
    build: .
    image: custom-airflow:latest
    restart: always
    depends_on:
      - webserver
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__WEBSERVER__SECRET_KEY: qv3p3v9Iw3YT6KvlXzq2KiZEq0PSoA9kQff8Pym4pQM=
      _PIP_ADDITIONAL_REQUIREMENTS: -r /requirements.txt
    volumes:
      - ../dags:/opt/airflow/dags
      - ../src:/opt/airflow/src
      - ../requirements.txt:/requirements.txt
    command: >
      bash -c "
        pip install -r /requirements.txt &&
        airflow scheduler
      "

  airflow-init:
    build: .
    image: custom-airflow:latest
    depends_on:
      - postgres
    environment:
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__CORE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__WEBSERVER__SECRET_KEY: qv3p3v9Iw3YT6KvlXzq2KiZEq0PSoA9kQff8Pym4pQM=
    volumes:
      - ../dags:/opt/airflow/dags
      - ../src:/opt/airflow/src
    entrypoint: >
      bash -c "
        airflow db init &&
        airflow users create --username airflow --password airflow --firstname Admin --lastname User --role Admin --email admin@example.com
      "
volumes:
  postgres-db-volume:

```

---

### 3. Initialize Airflow Database

```bash
cd airflow-docker
I want to delete previous volumen
docker-compose down -v
docker-compose up --build -d


docker build --no-cache -t custom-airflow .

docker-compose up airflow-init
```

✅ This will:

* Initialize Airflow DB
* Create the admin user (airflow / airflow)

---

### 4. Start Airflow Services

```bash
docker-compose up -d
```

### Key Differences:

* **Rebuild Behavior** :
* `docker-compose up --build`: Forces a rebuild of the Docker images before starting the containers.
* `docker-compose up -d`: Starts the containers using the already built images, without rebuilding them.
* **Running Mode** :
* `docker-compose up --build`: Runs in the foreground by default, showing the logs in the terminal (unless `-d` is added).

### When to Use Each:

* **Use `docker-compose up --build`** if you’ve made changes to the Dockerfile or any files that affect the image, and you need to ensure that the new changes are included when the containers are started.
* **Use `docker-compose up -d`** if the images have already been built and you just want to start the containers in the background without rebuilding them.

Then open your browser:

```
http://localhost:8080
```

Login with:

* **Username:** airflow
* **Password:** airflow

---

### in thedocker file

# Use your base Airflow image

FROM apache/airflow:2.7.2-python3.10

USER root

# Install dependencies for Chrome

RUN apt-get update && apt-get install -y
    wget
    curl
    unzip
    gnupg
    fonts-liberation
    libatk-bridge2.0-0
    libnspr4
    libnss3
    libxss1
    libasound2
    xdg-utils
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome stable

RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - &&
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list &&
    apt-get update && apt-get install -y google-chrome-stable &&
    rm -rf /var/lib/apt/lists/*

# Set Chrome path for Selenium

ENV CHROME_BIN=/usr/bin/google-chrome
ENV PATH="$PATH:/usr/bin/google-chrome"

USER airflow

# Copy Python dependencies

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

### 5. Trigger Your DAG

* Locate your DAG in the UI (`job_pipeline_dag`)
* Toggle it ON
* Click ▶️ to run it
* View task status, logs, and Gantt chart

---

## 🧠 What This Does

This pipeline:

* Scrapes jobs from Glassdoor and JobSpy
* Cleans and deduplicates data
* Translates French descriptions
* Uses a local LLM to extract skills and contract types
* Loads the final data into MongoDB

---

## ✅ You're Production Ready!

Your Airflow pipeline is now:

* 🕓 Schedulable (e.g., daily)
* 🔁 Retryable on failure
* 📊 Trackable via Airflow UI

Want to go further?

* 📈 Add Prometheus + Grafana monitoring
* ☁️ Deploy to cloud with Render, Railway, or EC2
* 📬 Add Slack or Email alerts

Let me know if you want to keep building! 💡

## 📈 Bonus: Add Metrics Later (Optional)

Once you're comfortable with this:

* Add Prometheus exporter to Airflow
* Or use Airflow's built-in task duration + success metrics
* Export logs for each task from the UI or store in a database for monitoring

# 🐳 Docker Cheat Sheet for Airflow Projects

---

## 🔧 Docker Build & Compose

| Command                            | Description                                          |
| ---------------------------------- | ---------------------------------------------------- |
| `docker build -t <image_name> .` | Build a Docker image from a Dockerfile               |
| `docker-compose up`              | Start all services defined in `docker-compose.yml` |
| `docker-compose up -d`           | Start services in detached mode                      |
| `docker-compose down`            | Stop and remove containers, networks, and volumes    |
| `docker-compose up --build`      | Rebuild images and start services                    |
| `docker-compose ps`              | List running services in the compose setup           |

---

## 🧱 Container Management

| Command                             | Description                               |
| ----------------------------------- | ----------------------------------------- |
| `docker ps`                       | List running containers                   |
| `docker ps -a`                    | List all containers (running and stopped) |
| `docker stop <container_name>`    | Stop a container                          |
| `docker start <container_name>`   | Start a stopped container                 |
| `docker restart <container_name>` | Restart a container                       |
| `docker rm <container_name>`      | Remove a container                        |
| `docker rmi <image_name>`         | Remove an image                           |

---

## 🖥️ Accessing Containers

| Command                                    | Description                                   |
| ------------------------------------------ | --------------------------------------------- |
| `docker exec -it <container_name> bash`  | Start an interactive shell inside a container |
| `docker exec <container_name> <command>` | Run a command inside a running container      |
| `exit`                                   | Exit the container shell                      |
| `docker logs <container_name>`           | View logs from a container                    |

---

## 🧼 Volumes & Cleanups

| Command                            | Description                                                                 |
| ---------------------------------- | --------------------------------------------------------------------------- |
| `docker volume ls`               | List Docker volumes                                                         |
| `docker volume rm <volume_name>` | Remove a specific volume                                                    |
| `docker system prune -a`         | Remove all stopped containers, unused networks/images (**dangerous**) |
| `docker network ls`              | List Docker networks                                                        |

---

## 📁 Useful Paths in Airflow Containers

| Path                  | Description                                           |
| --------------------- | ----------------------------------------------------- |
| `/opt/airflow/dags` | Location for DAG files                                |
| `/opt/airflow/src`  | Custom scripts (e.g. job scrapers)                    |
| `/requirements.txt` | Path to the Python requirements file inside container |

---

## ✅ Commands You've Used So Far

| Command                                             | Purpose                                      |
| --------------------------------------------------- | -------------------------------------------- |
| `docker exec -it airflow-docker-webserver-1 bash` | Open shell inside webserver container        |
| `pip install -r /requirements.txt`                | Install Python packages inside the container |
| `pip list`                                        | See installed Python packages                |
| `exit`                                            | Exit container terminal                      |
| `docker-compose up --build`                       | Rebuild and start services                   |
| `docker-compose down`                             | Stop and clean up all containers             |



### ✅ STEP 1: Create `prometheus.yml`

Create a file named `prometheus.yml` in the same directory as your `docker-compose.yml`.

Paste this config inside:

<pre class="overflow-visible!" data-start="438" data-end="582"><div class="contain-inline-size rounded-md border-[0.5px] border-token-border-medium relative bg-token-sidebar-surface-primary"><div class="flex items-center text-token-text-secondary px-4 py-2 text-xs font-sans justify-between h-9 bg-token-sidebar-surface-primary dark:bg-token-main-surface-secondary select-none rounded-t-[5px]">yaml</div><div class="sticky top-9"><div class="absolute right-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-sidebar-surface-primary text-token-text-secondary dark:bg-token-main-surface-secondary flex items-center rounded-sm px-2 font-sans text-xs"><span class="" data-state="closed"><button class="flex gap-1 items-center select-none px-4 py-1" aria-label="Copy"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path fill-rule="evenodd" clip-rule="evenodd" d="M7 5C7 3.34315 8.34315 2 10 2H19C20.6569 2 22 3.34315 22 5V14C22 15.6569 20.6569 17 19 17H17V19C17 20.6569 15.6569 22 14 22H5C3.34315 22 2 20.6569 2 19V10C2 8.34315 3.34315 7 5 7H7V5ZM9 7H14C15.6569 7 17 8.34315 17 10V15H19C19.5523 15 20 14.5523 20 14V5C20 4.44772 19.5523 4 19 4H10C9.44772 4 9 4.44772 9 5V7ZM5 9C4.44772 9 4 9.44772 4 10V19C4 19.5523 4.44772 20 5 20H14C14.5523 20 15 19.5523 15 19V10C15 9.44772 14.5523 9 14 9H5Z" fill="currentColor"></path></svg>Copy</button></span><span class="" data-state="closed"><button class="flex items-center gap-1 px-4 py-1 select-none"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path d="M2.5 5.5C4.3 5.2 5.2 4 5.5 2.5C5.8 4 6.7 5.2 8.5 5.5C6.7 5.8 5.8 7 5.5 8.5C5.2 7 4.3 5.8 2.5 5.5Z" fill="currentColor" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"></path><path d="M5.66282 16.5231L5.18413 19.3952C5.12203 19.7678 5.09098 19.9541 5.14876 20.0888C5.19933 20.2067 5.29328 20.3007 5.41118 20.3512C5.54589 20.409 5.73218 20.378 6.10476 20.3159L8.97693 19.8372C9.72813 19.712 10.1037 19.6494 10.4542 19.521C10.7652 19.407 11.0608 19.2549 11.3343 19.068C11.6425 18.8575 11.9118 18.5882 12.4503 18.0497L20 10.5C21.3807 9.11929 21.3807 6.88071 20 5.5C18.6193 4.11929 16.3807 4.11929 15 5.5L7.45026 13.0497C6.91175 13.5882 6.6425 13.8575 6.43197 14.1657C6.24513 14.4392 6.09299 14.7348 5.97903 15.0458C5.85062 15.3963 5.78802 15.7719 5.66282 16.5231Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M14.5 7L18.5 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>Edit</button></span></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-yaml"><span><span>global:</span><span>
  </span><span>scrape_interval:</span><span></span><span>15s</span><span>

</span><span>scrape_configs:</span><span>
  </span><span>-</span><span></span><span>job_name:</span><span></span><span>'statsd-exporter'</span><span>
    </span><span>static_configs:</span><span>
      </span><span>-</span><span></span><span>targets:</span><span> [</span><span>'statsd:9102'</span><span>]
</span></span></code></div></div></pre>

This tells Prometheus to scrape metrics from the `statsd` container.

---

### ✅ STEP 2: Start Everything

Run from your project root:

<pre class="overflow-visible!" data-start="720" data-end="757"><div class="contain-inline-size rounded-md border-[0.5px] border-token-border-medium relative bg-token-sidebar-surface-primary"><div class="flex items-center text-token-text-secondary px-4 py-2 text-xs font-sans justify-between h-9 bg-token-sidebar-surface-primary dark:bg-token-main-surface-secondary select-none rounded-t-[5px]">bash</div><div class="sticky top-9"><div class="absolute right-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-sidebar-surface-primary text-token-text-secondary dark:bg-token-main-surface-secondary flex items-center rounded-sm px-2 font-sans text-xs"><span class="" data-state="closed"><button class="flex gap-1 items-center select-none px-4 py-1" aria-label="Copy"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path fill-rule="evenodd" clip-rule="evenodd" d="M7 5C7 3.34315 8.34315 2 10 2H19C20.6569 2 22 3.34315 22 5V14C22 15.6569 20.6569 17 19 17H17V19C17 20.6569 15.6569 22 14 22H5C3.34315 22 2 20.6569 2 19V10C2 8.34315 3.34315 7 5 7H7V5ZM9 7H14C15.6569 7 17 8.34315 17 10V15H19C19.5523 15 20 14.5523 20 14V5C20 4.44772 19.5523 4 19 4H10C9.44772 4 9 4.44772 9 5V7ZM5 9C4.44772 9 4 9.44772 4 10V19C4 19.5523 4.44772 20 5 20H14C14.5523 20 15 19.5523 15 19V10C15 9.44772 14.5523 9 14 9H5Z" fill="currentColor"></path></svg>Copy</button></span><span class="" data-state="closed"><button class="flex items-center gap-1 px-4 py-1 select-none"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" class="icon-xs"><path d="M2.5 5.5C4.3 5.2 5.2 4 5.5 2.5C5.8 4 6.7 5.2 8.5 5.5C6.7 5.8 5.8 7 5.5 8.5C5.2 7 4.3 5.8 2.5 5.5Z" fill="currentColor" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"></path><path d="M5.66282 16.5231L5.18413 19.3952C5.12203 19.7678 5.09098 19.9541 5.14876 20.0888C5.19933 20.2067 5.29328 20.3007 5.41118 20.3512C5.54589 20.409 5.73218 20.378 6.10476 20.3159L8.97693 19.8372C9.72813 19.712 10.1037 19.6494 10.4542 19.521C10.7652 19.407 11.0608 19.2549 11.3343 19.068C11.6425 18.8575 11.9118 18.5882 12.4503 18.0497L20 10.5C21.3807 9.11929 21.3807 6.88071 20 5.5C18.6193 4.11929 16.3807 4.11929 15 5.5L7.45026 13.0497C6.91175 13.5882 6.6425 13.8575 6.43197 14.1657C6.24513 14.4392 6.09299 14.7348 5.97903 15.0458C5.85062 15.3963 5.78802 15.7719 5.66282 16.5231Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><path d="M14.5 7L18.5 11" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path></svg>Edit</button></span></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose up --build
</span></span></code></div></div></pre>

---

### ✅ STEP 3: Verify Services Are Running

* Airflow UI: [http://localhost:8080](http://localhost:8080)
* Prometheus UI: [http://localhost:9090](http://localhost:9090)
* Grafana UI: [http://localhost:3000]()

---

### ✅ STEP 4: Set Up Grafana

1. Go to [http://localhost:3000]()
2. Login:
   * **Username** : `admin`
   * **Password** : `admin`
3. Add a new  **Data Source** :
   * Type: **Prometheus**
   * URL: `http://prometheus:9090`
   * Click **Save & Test**

---

### ✅ STEP 5: Import Airflow Dashboard

Grafana dashboards are available in the community. Use a popular one:

* Click **“+” → Import**
* Paste **Dashboard ID `14674`**
* Click **Load**
* Choose **Prometheus** as the data source
* Click **Import**

---

Once this is done, you'll have beautiful metrics like:

* DAG Success / Failure rates
* Task durations
* Scheduler health
* And more!


---
