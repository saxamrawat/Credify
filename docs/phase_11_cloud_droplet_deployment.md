# Phase 11 — Cloud Droplet Deployment

## Phase overview

- **Status:** Complete; Steps 11.1–11.12 complete.
- **Objective:** Deploy Credify so the analyst dashboard and scoring API are available at `credify.saxam.dev`.
- **Scope:** Prepare the application and Cloud Droplet, deploy the service, configure DNS and HTTPS, verify operation, and document basic maintenance and resource limits.
- **Outcome and evidence:** Deployed at [https://credify.saxam.dev](https://credify.saxam.dev) using FastAPI/Uvicorn under systemd, a dedicated `credify` account, and Nginx with a separate Let's Encrypt certificate. Public health checks pass, HTTP redirects to HTTPS, and the user reports the dashboard and all functionality work. A verified recovery bundle is stored off the Droplet.
- **Limitations:** The Droplet has 1 vCPU and 1 GiB RAM. The 30,000-row application cap is not a measured capacity guarantee; a maximum-size scoring request was not run on this host. The recovery process was documented but not exercised as a full restore. Authentify sign-in is a later feature update after Authentify is available as an API service. The application remains a prototype, not a production banking or credit-approval system.

## Contents

- [Phase handoff and working agreement](#phase-handoff-and-working-agreement)
- [Deployment context](#deployment-context)
- [Planned steps](#planned-steps)
- [Step 11.1 — Choose the deployment setup](#step-111--choose-the-deployment-setup)
- [Step 11.2 — Inspect the Droplet without changing it](#step-112--inspect-the-droplet-without-changing-it)
- [Step 11.3 — Choose the runtime and model-artifact compatibility plan](#step-113--choose-the-runtime-and-model-artifact-compatibility-plan)
- [Step 11.4 — Inspect existing Droplet services](#step-114--inspect-existing-droplet-services)
- [Step 11.5 — Choose how Credify shares the web server](#step-115--choose-how-credify-shares-the-web-server)
- [Step 11.6 — Inspect Nginx, Authentify, and DNS routing](#step-116--inspect-nginx-authentify-and-dns-routing)
- [Step 11.7 — Choose Credify's service account](#step-117--choose-credifys-service-account)
- [Step 11.8 — Prepare Credify's service account and directory](#step-118--prepare-credifys-service-account-and-directory)
- [Step 11.9 — Deploy and manage the application](#step-119--deploy-and-manage-the-application)
- [Step 11.10 — Configure hostname and HTTPS](#step-1110--configure-hostname-and-https)
- [Step 11.11 — Verify live behavior and operations](#step-1111--verify-live-behavior-and-operations)
- [Step 11.12 — Document deployment and close Phase 11](#step-1112--document-deployment-and-close-phase-11)
- [Phase closeout](#phase-closeout)

## Phase handoff and working agreement

This phase is carried out in this chat, one step at a time. Deployment decisions must be based on the project workspace and facts the user supplies; do not assume unobserved server state, provider settings, or capabilities. When an action must happen on the Droplet or in its control panel, the assistant will provide the commands or instructions for the user to run. The user will share command output or screenshots when a step needs verification, and the assistant will use that evidence to troubleshoot before moving on. The assistant will explain each step, present meaningful choices with pros and cons, and recommend an approach before implementation where a choice is needed.

The assistant does not need server credentials or direct access. Do not paste passwords, private keys, API tokens, or other secrets into chat. Any secret configuration should be entered directly on the user's server using the instructions provided for that step.

For each step, keep a detailed record of the goal, decision, exact actions or code, verification results, files changed, and limitations. Maintain this document as the active phase record; at closeout, make sure the final combined record preserves the complete ordered walkthrough.

## Deployment context

- **Server:** User's Cloud Droplet.
- **Current size:** 1 vCPU, 1 GB RAM, 25 GB disk (from the supplied configuration screenshot).
- **Application:** FastAPI serves the API and the custom HTML/CSS/JavaScript dashboard from the same application.
- **Python package:** `propensity_prediction`; the public product name is Credify.
- **Deployed hostname:** `credify.saxam.dev`.
- **External access:** User operates the server and domain/DNS provider; assistant supplies instructions and reviews results in chat.
- **Deferred work:** Authentify sign-in integration is outside this phase and depends on Authentify becoming an API service.

The 1 GB memory limit is a design constraint. We should favor a modest runtime footprint, measure actual use after deployment, and avoid assuming this prototype is sized for many concurrent users or production banking workloads.

## Planned steps

The order may be adjusted if an earlier decision changes what is needed later.

1. **11.1 — Choose the deployment setup.** Select the runtime and public traffic path before preparing configuration. **Complete:** Python virtual environment + systemd + Nginx.
2. **11.2 — Inspect the Droplet without changing it.** Collect OS, Python, memory, disk, and CPU details from the user's server before issuing installation commands or finalizing dependency compatibility. **Complete:** Ubuntu 24.04.5, Python 3.12.3, 1 CPU, 24 GB filesystem with 20 GB available, 321 MiB memory available at inspection, no swap.
3. **11.3 — Choose the runtime and model-artifact compatibility plan.** Decide how to install a lean app runtime on the observed OS/Python while handling the checked-in serialized model and its recorded package versions. **Complete:** the artifact-matched pins resolved for the Droplet's Python 3.12.3 in a dry run.
4. **11.4 — Inspect existing Droplet services.** Check current accounts, running services, listening ports, firewall tool/state, and whether Nginx is already installed before modifying a server that may host other services. **Complete:** Nginx serves on ports 80/443; Authentify's Gunicorn listens on 127.0.0.1:8000; PostgreSQL and Redis listen only on loopback; UFW is inactive.
5. **11.5 — Choose how Credify shares the web server.** Decide how Credify will be routed through the existing Nginx while preserving Authentify. **Complete:** use a separate `credify.saxam.dev` hostname and Nginx site.
6. **11.6 — Inspect Nginx, Authentify, and DNS routing.** Read the current virtual-host routing, Authentify service metadata, and DNS answers before proposing edits. **Complete:** Authentify has its own server block, both hostnames resolve to the same redacted address, and the existing certificate covers only Authentify.
7. **11.7 — Choose Credify's service account.** Decide whether Credify runs as a dedicated restricted account or shares the existing `saxam` account used by Authentify. **Complete:** dedicated restricted `credify` account selected.
8. **11.8 — Prepare Credify's service account and directory.** Check for existing account/path collisions, then create the selected restricted account and application directory if clear. **Complete:** the account home and application directory under `/home/credify` passed guarded ownership and permission checks.
9. **11.9 — Deploy and manage the application.** Choose a reproducible source transfer, install the agreed application version and model artifact, configure its systemd service, and verify startup, restart behavior, and local health checks. **Complete:** deployed commit `b6b253dc36cc47fcf2d7cbd263b12fdadbb7d711`; lean Python 3.12 environment; single-worker systemd service on loopback port 8001; restart and health checks passed.
10. **11.10 — Configure hostname and HTTPS.** Confirm wildcard DNS behavior and certificate coverage, configure the Credify Nginx site without disrupting Authentify, and verify secure browser access. **Complete:** existing Porkbun wildcard A record covers the host; Credify has a separate certificate, public HTTPS health passes, and HTTP redirects to HTTPS.
11. **11.11 — Verify live behavior and operations.** Check dashboard assets, API health and scoring, logs, restart/recovery, resource use, upload limits, and a practical backup/restore approach. **Complete:** browser workflow reported working; sanitized error count zero; Nginx body limit set to 16 MiB for Credify; verified recovery bundle copied off-host. Maximum-row workload and full restore were not run.
12. **11.12 — Document deployment and close Phase 11.** Record the final architecture, commands and configuration locations (without secrets), verification evidence, operational limits, and recovery steps; then update the README and consolidate the phase record. **Complete:** this detailed phase record and concise README entry were finalized.

## Step 11.1 — Choose the deployment setup

**Step status:** Complete · **Phase status:** In progress

### Goal

Choose how the existing single FastAPI application will run on the Cloud Droplet and how internet traffic will reach it. This choice guides the production configuration and server setup in later steps.

### Options considered

| Option | Setup | Pros | Cons |
|---|---|---|---|
| **A — Python virtual environment + systemd + Nginx** | Run FastAPI in a Python virtual environment; systemd supervises it; Nginx accepts public traffic and handles proxying and HTTPS. | Low overhead for a 1 GB server; fits the existing Python app; uses a standard service manager and reverse proxy. | Requires configuring and maintaining a systemd service and Nginx site. |
| **B — Docker Compose + Nginx** | Package the app in a container and use Compose to run it behind Nginx. | Reproducible app environment; deployment and rollback can be organized around image versions. | Adds container configuration and operational complexity; consumes additional disk and some memory on a small server. |
| **C — Direct public Uvicorn** | Expose the Uvicorn application server directly to the internet. | Fewest components and simplest initial setup. | Less suitable for handling TLS, proxy behavior, and public web traffic; leaves more operational responsibilities on the app process. |

### Recommendation

Option A is the recommended starting point. The application is already one FastAPI service that serves both its API and dashboard, and a Python environment plus systemd and Nginx should fit the Droplet's resource limit without introducing container operations. Option B remains reasonable if reproducible container deployment is more important to the user than minimizing setup and footprint.

### Decision

**Selected: Option A — Python virtual environment + systemd + Nginx.** The user selected this approach on 2026-10-19. It matches the existing single FastAPI application and is the recommended low-overhead fit for the supplied 1 vCPU / 1 GB RAM / 25 GB disk Droplet. The choice defines the deployment approach; it does not assume what operating system or packages are currently installed on the server.

### Verification

Reviewed the workspace's FastAPI application factory, which mounts the API router and dashboard static assets in one app, and confirmed `uvicorn` is declared as a project dependency. No server changes were made in this decision step.

## Step 11.2 — Inspect the Droplet without changing it

**Step status:** Complete · **Phase status:** In progress

### Goal

Collect the Droplet's actual operating system, installed Python, available memory and disk, and CPU count before choosing Python installation instructions or changing the server.

### Options

- **A — Run a read-only inventory command (recommended).** It provides OS and live resource/package facts directly from the server, without installing or changing anything.
- **B — Send a control-panel screenshot.** It can confirm the Droplet's configured size and perhaps OS image, but it does not show the server's currently installed Python or available disk/memory.

### Recommended command

Run this in your normal SSH session on the Droplet and paste the output here:

```bash
cat /etc/os-release; python3 --version; command -v python3; free -h; df -h /; nproc
```

This command only reads system information. Do not run it on your local computer; run it in the Droplet's terminal. No `sudo` is needed.

### Decision and verification

The user ran the read-only inventory command over SSH and supplied this result: Ubuntu 24.04.5 LTS; `/usr/bin/python3` at Python 3.12.3; 1 CPU; 961 MiB total memory with 321 MiB available at inspection; no swap; root filesystem 24 GB total with 20 GB available. No packages or configuration were changed during this inspection step.

## Step 11.3 — Choose the runtime and model-artifact compatibility plan

**Step status:** Complete · **Phase status:** In progress

### Goal

Choose how to install the app's Python runtime on the observed Ubuntu/Python environment while keeping the serialized model and its required package versions compatible.

### Workspace evidence

- `models/selected_default_risk_model.joblib` is the checked-in serialized model used by the API. Its metadata sidecar records Python 3.14.7, NumPy 2.5.3, pandas 3.0.5, scikit-learn 1.9.1, and joblib 1.6.0.
- `src/propensity_prediction/models/artifact.py` warns when the installed scikit-learn version differs from the version used to create the artifact and states that serialized models are not guaranteed compatible across versions.
- `pyproject.toml` uses version ranges and does not declare a supported Python version. It also includes Streamlit as a dependency, while the current dashboard is served as packaged static HTML, CSS, and JavaScript by FastAPI.
- `requirements.txt` pins the workstation's broad environment, including packages beyond the API/model runtime. Its pinned model-library versions match the artifact metadata.
- The Droplet currently reports Python 3.12.3. Its observed available memory was about 321 MiB, with no swap; package installation and application memory must be considered carefully.

### Options considered

| Option | Approach | Pros | Cons |
|---|---|---|---|
| **A — Install the current full pinned environment** | Use the existing `requirements.txt` on the Droplet and retain its exact model-library pins. | The model-related versions match the artifact metadata; uses the existing lock file. | Installs workstation, notebook, test, and Streamlit packages the deployed app does not need; may use more disk and installation resources on the small server. Python 3.12 compatibility of every pinned package has not yet been established from this workspace. |
| **B — Install directly from `pyproject.toml` ranges** | Install the project and let pip choose versions satisfying its declared ranges. | Uses the package's declared runtime dependencies and avoids the broad workstation freeze. | The ranges are not a deployment lock; they do not guarantee the scikit-learn version recorded with the serialized model. Streamlit remains a declared dependency despite the current static dashboard. |
| **C — Create a deployment-specific pinned runtime set** | Add a lean deployment dependency file using only required API/model packages, pin the direct dependencies, and validate package resolution for the Droplet's Python before installation. | Avoids development-only packages while preserving the model's recorded direct library versions. | Adds a second dependency file to maintain. Transitive dependencies still need to be resolved and then captured for the target Python; if the artifact-matching versions cannot be resolved there, we will need to choose a different runtime/artifact plan before changing the server. |

### Recommendation

Option C. It uses the package-version evidence already recorded beside the model without installing the workstation's entire frozen environment. First create the lean direct-pin file in the workspace, then use a temporary virtual environment and pip's dry-run mode on the Droplet to see whether those versions and their transitive requirements resolve for Python 3.12. A successful resolution will not, by itself, prove the serialized model loads; that is a later application verification. If package resolution fails, stop and revisit the runtime/artifact choice instead of silently accepting a different scikit-learn version.

### Decision

**Selected: Option C.** The user chose a lean deployment-specific runtime set on 2026-10-19. Added `requirements-deploy.txt` with the direct and transitive pins resolved for the observed Ubuntu 24.04 / Python 3.12 / x86_64 Droplet. Streamlit, tests, notebooks, and development tooling are excluded from this file. The project package will later be installed with `--no-deps` so `pyproject.toml` does not pull in its broader declared dependency set.

### What changed

`requirements-deploy.txt` now records the resolved packages for the observed target:

```text
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.15.1
click==8.5.0
cloudpickle==3.1.2
fastapi==0.143.0
h11==0.16.0
idna==3.20
joblib==1.6.0
narwhals==2.27.1
numpy==2.5.3
opentelemetry-api==1.45.1
pandas==3.0.5
pydantic==2.14.0
pydantic-core==2.50.0
python-dateutil==2.9.0.post0
scikit-learn==1.9.1
scipy==1.18.1
six==1.17.0
starlette==1.9.0
threadpoolctl==3.7.0
typing-inspection==0.4.4
typing-extensions==4.16.0
uvicorn==0.54.0
```

The NumPy, pandas, scikit-learn, and joblib pins match `models/selected_default_risk_model.json`. FastAPI, Pydantic, and Uvicorn use the versions recorded in the repository's existing environment requirements. The API imports the model/feature/data stack and serves static dashboard assets; it does not need Streamlit to render the current dashboard. The user's pip resolver output provides exact pins for transitive packages on the observed target Python/platform.

### Verification and next action

The user ran the compatibility check in a temporary Python 3.12 virtual environment. Pip resolved the seven direct dependencies and their transitive dependencies, including the artifact-matched NumPy 2.5.3, pandas 3.0.5, scikit-learn 1.9.1, and joblib 1.6.0 pins. It reported the packages as “Would install”; no packages were installed into the virtual environment. Pip did download package wheels and metadata and may have cached them. This confirms dependency resolution for the observed Python/platform but does not yet prove model deserialization or application startup.

The resolver's exact output was added to `requirements-deploy.txt`. `git diff --check` passes. Automated tests were not run because this step changes deployment dependency metadata and makes no application-code change.

```bash
cat > /tmp/credify-runtime-requirements.txt <<'EOF'
fastapi==0.143.0
joblib==1.6.0
numpy==2.5.3
pandas==3.0.5
pydantic==2.14.0
scikit-learn==1.9.1
uvicorn==0.54.0
EOF
python3 -m venv /tmp/credify-deps-check
/tmp/credify-deps-check/bin/python -m pip install --dry-run --report /tmp/credify-pip-report.json -r /tmp/credify-runtime-requirements.txt
```

The deployment lock reflects the user's supplied dry-run output. Do not install the application packages until the existing server services have been inspected and the install location/account are agreed.

## Step 11.4 — Inspect existing Droplet services

**Step status:** Complete · **Phase status:** In progress

### Goal

Review the Droplet's existing login accounts, running services, open listening ports, firewall status, and Nginx state before making changes. This avoids assuming the server is dedicated to Credify or overwriting an existing service configuration.

### Options

- **A — Run the read-only inventory command (recommended).** Shows current service and network state directly from the server.
- **B — Send a control-panel screenshot.** Useful for provider-level configuration, but it cannot show the services and ports currently running inside Ubuntu.

### Recommended command

Run this in the Droplet's SSH session and paste the output. These checks do not change configuration:

```bash
id; getent passwd | awk -F: '$3 >= 1000 && $3 < 60000 {print $1 ":" $3 ":" $6}'; systemctl --type=service --state=running --no-pager; ss -lntup; if command -v ufw >/dev/null 2>&1; then ufw status verbose; else echo 'ufw is not installed'; fi; if command -v nginx >/dev/null 2>&1; then nginx -v 2>&1; systemctl is-active nginx; else echo 'nginx is not installed'; fi
```

The output may include service names and ports. It should not include passwords or private keys. No installation or firewall changes should be made until the inventory is reviewed.

### Decision and verification

**Selected: Option A — Run the read-only inventory command.** The user supplied the output from the Droplet. It showed the `saxam` account (UID 1000), an active `authentify.service`, Nginx active on ports 80 and 443, Authentify's Gunicorn listener on `127.0.0.1:8000`, PostgreSQL on `127.0.0.1:5432`, Redis on `127.0.0.1:6379`, SSH on port 22, and UFW inactive. No separate Credify service account was listed. The provider-level firewall was not inspected. No server configuration was changed.

## Step 11.5 — Choose how Credify shares the web server

**Step status:** Complete · **Phase status:** In progress

### Goal

Select how public requests for Credify will reach its FastAPI app while the same Droplet already runs Authentify behind Nginx. Nginx currently owns public HTTP/HTTPS ports, and Authentify uses local port 8000.

### Options considered

| Option | Approach | Pros | Cons |
|---|---|---|---|
| **A — Separate Credify hostname and Nginx server block** | Route `credify.saxam.dev` through the existing Nginx to Credify on a different loopback port (for example, 127.0.0.1:8001). | Matches the requested hostname; keeps Authentify and Credify as separate sites; does not require another public listening port. | Adds a site configuration to a shared Nginx server and requires DNS and HTTPS setup. The active Nginx configuration must be inspected before writing it. |
| **B — Put Credify under an existing site's URL path** | Serve Credify below a path such as `/credify` on an existing hostname. | Could avoid creating a separate DNS name. | Couples the projects and may require the app/static routes to support a URL prefix; this does not match the planned `credify.saxam.dev` address. |
| **C — Expose Credify on a separate public port** | Publish Credify at a port other than 80/443. | Avoids adding a host-based Nginx route. | Creates a less familiar URL, still needs secure transport planning, and exposes another public port; it does not use the existing reverse proxy effectively. |

### Recommendation

Option A. It matches the agreed hostname and reuses the existing Nginx listener without replacing Authentify's site. The port 8001 is currently free in the supplied listening-port snapshot, but it must be rechecked immediately before the service is configured. Before editing any site file, inspect only the relevant current Nginx routing directives and Authentify's service metadata; preserve the existing configuration and validate Nginx before any reload.

### Decision

**Selected: Option A — Separate Credify hostname and Nginx server block.** The user chose this on 2026-10-19 and reported that their domain is on Porkbun and wildcard DNS is already used to host the app. The wildcard DNS record's current target, its resolution for `credify.saxam.dev`, and TLS certificate coverage have not yet been checked. No Nginx, DNS, firewall, or application service changes have been made.

## Step 11.6 — Inspect Nginx, Authentify, and DNS routing

**Step status:** Complete · **Phase status:** In progress

### Goal

Inspect the active Nginx site routing and Authentify service metadata, and check how the two relevant hostnames resolve. This will establish the current routing without exposing full Nginx files or changing the live site.

### Options

- **A — Run the filtered, read-only inspection command (recommended).** Prints only selected Nginx routing directives, Authentify service metadata, and DNS answers; it does not print environment variable values or private-key contents.
- **B — Manually copy relevant configuration details.** Gives you control over what is shared, but is easier to omit a server block or accidentally include sensitive configuration.

### Recommended command

Run this in the Droplet's SSH session and share the output:

```bash
systemctl show authentify.service -p User -p Group -p WorkingDirectory -p FragmentPath -p EnvironmentFiles; nginx -T 2>&1 | awk '/^# configuration file / {file=$0} /^[[:space:]]*(listen|server_name|root|proxy_pass|ssl_certificate)[[:space:]]/ {print file; print $0}'; getent ahostsv4 credify.saxam.dev auth.saxam.dev
```

This reads service metadata, filters Nginx's full configuration output down to routing and certificate-path directives, and queries DNS through the system resolver. It makes no configuration changes. It does not reveal the contents of `EnvironmentFiles` or certificate private keys. If `getent` returns no Credify address, share that result too; the wildcard setup may still need checking in Porkbun later.

### Decision and verification

**Selected: Option A — Run the filtered, read-only inspection command.** The user supplied the output. The Authentify systemd service runs with `User=saxam` and `Group=www-data` from `/home/saxam/projects/Authentify`, with its unit at `/etc/systemd/system/authentify.service`. The active Nginx configuration has an `auth.saxam.dev` server block, proxying to `http://127.0.0.1:8000`, and references `/etc/letsencrypt/live/auth.saxam.dev/fullchain.pem`. DNS lookup returned the same redacted address for `credify.saxam.dev` and `auth.saxam.dev`. The exact Porkbun wildcard record and certificate SAN coverage remain unverified. No server configuration was changed.

## Step 11.7 — Choose Credify's service account

**Step status:** Complete · **Phase status:** In progress

### Goal

Choose the Unix account that will own and run Credify's application files and systemd service. The existing `saxam` account already runs Authentify, so the choice determines how much filesystem access the two apps share.

### Options considered

| Option | Approach | Pros | Cons |
|---|---|---|---|
| **A — Create a dedicated restricted `credify` service account** | Run Credify under its own non-login account, with a separate application directory such as `/opt/credify`. | Separates Credify's files and process permissions from Authentify; follows least-privilege service operation. | Adds one account and a small amount of ownership/permission setup. |
| **B — Reuse the existing `saxam` account** | Store and run Credify alongside the account currently used by Authentify. | Matches the existing service pattern and avoids creating another account. | Both applications would run with access to the same user's files; a Credify process issue could affect Authentify's files and vice versa. |
| **C — Run Credify as root** | Use the current administrative account for the app service. | Simplest initial file permissions. | Gives the web application administrative access to the whole server; this is not appropriate for a publicly reachable service. |

### Recommendation

Option A. The Droplet hosts two related but separately deployed applications, so a dedicated restricted account gives Credify a clear filesystem and process boundary. Nginx communicates with the app over loopback and does not need to read the application files, so Credify does not need to join `www-data` merely for proxying.

### Decision

**Selected: Option A — Create a dedicated restricted `credify` service account.** The user chose this on 2026-10-19. The user later requested the app be placed under `/home/credify` rather than `/opt/credify`; keep the non-login account separate from `saxam`, which runs Authentify. Do not add Credify to `www-data` merely for Nginx proxying.

## Step 11.8 — Prepare Credify's service account and directory

**Step status:** Complete · **Phase status:** In progress

### Goal

The user completed the read-only collision check and created the dedicated service account and application directory. The earlier account listing excluded system UIDs, so it did not establish that the account was absent.

### Read-only preflight

**Preflight result:** The user reported `No credify account exists` and `/opt/credify does not exist`. This clears the known account and path collision check.

```bash
if getent passwd credify >/dev/null; then getent passwd credify; else echo 'No credify account exists'; fi; if [ -e /opt/credify ]; then stat -c '%A %U:%G %n' /opt/credify; else echo '/opt/credify does not exist'; fi
```

### Create and verify

Run these commands in the Droplet's SSH session as root. They create a system account with no interactive login, set a private home-directory mode, and create the application directory with the account as owner:

```bash
set -e
useradd --system --user-group --home-dir /opt/credify --create-home --shell /usr/sbin/nologin --comment 'Credify application service' credify
chmod 0750 /opt/credify
install -d -o credify -g credify -m 0750 /opt/credify/app
id credify
stat -c '%A %U:%G %n' /opt/credify /opt/credify/app
```

If any command reports an error, stop and share the error output rather than retrying with different flags. The expected final ownership is `credify:credify`; both directories should have mode `drwxr-x---` (`750`).

**User-reported verification:** `id credify` returned `uid=997(credify) gid=987(credify) groups=987(credify)`. `stat` confirmed `/opt/credify` and `/opt/credify/app` are both `credify:credify` with mode `drwxr-x---`. Step complete; no `www-data` membership was added.

### Requested path adjustment

The user asked to place the application under the service account's home. A `usermod --home /home/credify --move-home credify` attempt reported that `/opt/credify` did not exist or was inaccessible; its following `chown` also failed because `/home/credify` did not exist. The subsequent read-only inspection confirmed the passwd entry now names `/home/credify`, while `/opt/credify`, `/opt/credify/app`, and `/home/credify` are all absent. No application checkout has been made. Create the missing home and app directory for the existing account, then verify before continuing.

Run in the Droplet SSH session as root:

```bash
set -e
test "$(getent passwd credify | cut -d: -f6)" = /home/credify
test ! -e /home/credify
install -d -o credify -g credify -m 0750 /home/credify
install -d -o credify -g credify -m 0750 /home/credify/app
getent passwd credify
id credify
stat -c '%A %U:%G %n' /home/credify /home/credify/app
```

Expected: the account home is `/home/credify`, and both directories are owned by `credify:credify` with mode `drwxr-x---`. If a command fails, stop and share the output.

The user reported that the directory-creation commands were run, but the SSH session disconnected before output could be shared. The later guarded source-checkout command passed the account-home, directory ownership, permission, and empty-app-directory checks before cloning. This completes Step 11.8.

## Step 11.9 — Deploy and manage the application

**Step status:** Complete · **Phase status:** In progress

### Goal

Place a known version of the application and its selected model artifact under `/home/credify/app`, install the lean runtime in an isolated virtual environment, and prepare a systemd-managed local service. The server has 1 vCPU and about 1 GB RAM, so the deployment should avoid unnecessary build or container overhead. The deployment target should be a specific, reproducible source revision rather than an unspecified moving branch.

### Options considered

| Option | Transfer approach | Pros | Cons |
|---|---|---|---|
| **A — Clone the public GitHub repository at an exact commit** | Clone `https://github.com/saxamrawat/Credify.git` into the app directory, then check out a commit chosen for deployment. | Keeps source history and makes a later rollback or update explicit; avoids manually packaging source files; the workspace Git remote confirms this repository URL. | Requires the intended code to be pushed first and the Droplet to reach GitHub; a clone of the wrong commit could omit the required fixes. |
| **B — Download a GitHub source archive for an exact commit** | Download and extract a commit-pinned archive into the app directory. | Reproducible source snapshot without needing Git installed or keeping repository metadata on the server. | Rollback requires downloading and extracting another archive; must ensure the archive contains the checked-in model artifact and package files. |
| **C — Copy a prepared source bundle from the local machine** | Build an archive locally and transfer it to the Droplet with `scp`. | Uses the exact local workspace content, including changes not yet pushed; no server-side GitHub access needed. | More transfer steps; easy to omit files or copy uncommitted content unintentionally; rollback needs a separately preserved bundle. |

### Recommendation

Choose **Option A**, then deploy an exact commit that is present on GitHub. This suits the public repository and gives a clear version to record and roll back to. Before giving commands, confirm the desired commit exists remotely; do not deploy a guessed branch tip. If the desired workspace changes are not pushed, Option C can carry them, but it needs a careful manifest and archive verification first.

### Decision

**Selected: Option A — Clone the public GitHub repository at an exact commit.** The user chose this on 2026-10-19. The workspace `HEAD` is `b6b253dc36cc47fcf2d7cbd263b12fdadbb7d711` (`updated requirements.txt`), and a read-only remote check confirmed GitHub `HEAD` resolves to the same commit. This revision contains the package, dashboard assets, and selected model artifact. The local workspace has uncommitted README and phase-document changes plus an untracked `requirements-deploy.txt`; therefore the exact remote revision does not contain the deploy-only pin file. We will transfer/recreate that dependency manifest explicitly during runtime setup instead of assuming it is in the clone. No application files have yet been copied to the Droplet.

### Clone and verify source

Run in the Droplet SSH session as root. This verifies Git is installed and the app directory is still empty, then clones and checks out the confirmed commit under the restricted service account:

```bash
set -e
command -v git
test -z "$(find /home/credify/app -mindepth 1 -maxdepth 1 -print -quit)"
runuser -u credify -- git clone --no-checkout https://github.com/saxamrawat/Credify.git /home/credify/app
runuser -u credify -- git -C /home/credify/app checkout --detach b6b253dc36cc47fcf2d7cbd263b12fdadbb7d711
runuser -u credify -- git -C /home/credify/app rev-parse HEAD
stat -c '%A %U:%G %n' /home/credify/app
```

The checkout printed `HEAD is now at b6b253d updated requirements.txt`. The subsequent revision check initially ran as root and Git rejected access to the service account's repository as dubious ownership. No global `safe.directory` exception was added. The user reran the read-only revision check as `credify`; it returned the exact expected commit `b6b253dc36cc47fcf2d7cbd263b12fdadbb7d711`, and `stat` confirmed the checkout is owned by `credify:credify` with mode `drwxr-x---`. Source checkout is verified.

```bash
runuser -u credify -- git -C /home/credify/app rev-parse HEAD
stat -c '%A %U:%G %n' /home/credify/app
```

### Runtime installation

Create an isolated Python virtual environment under `/home/credify/venv` and install only the resolved deployment pins in `requirements-deploy.txt`. That file is a local workspace addition and is not in the pinned GitHub commit; reproduce its exact pins on the Droplet rather than installing the repository's broad development requirements. Install packages as `credify` and require binary wheels to avoid compiling large scientific packages on the 1-vCPU Droplet. Verify dependency consistency and imports before configuring systemd.

**User-reported verification:** The exact pinned packages installed successfully in `/home/credify/venv`; `pip check` reported no broken requirements; importing `propensity_prediction.api.main:app` through `/home/credify/app/src` succeeded and printed `Credit Risk Review Prioritization API`. Runtime setup is complete.

### Prepare the systemd service

The selected deployment layout uses systemd and a single Uvicorn worker to keep resource use appropriate for the 1-vCPU, 1-GB Droplet. Authentify already binds to `127.0.0.1:8000`, so use `127.0.0.1:8001` for Credify if the port is free. Before writing a unit, inspect that port and check whether a Credify unit already exists. No service unit has yet been created.

**User-reported preflight:** `ss` showed no listener on port 8001; `systemctl cat credify.service` confirmed there is no existing unit. Current memory was 961 MiB total, 300 MiB available, with no swap; `/home` is on the 24 GB root filesystem with 19 GB available.

**Decision:** The user selected a 1 GB swap file as a buffer for memory spikes before starting the model service. This uses little of the 19 GB available disk space; sustained pressure on swap will be slower than RAM. Before creating it, check for an existing `/swapfile`, fstab entry, active swap, and sufficient disk space.

Run in the Droplet SSH session as root. The script stops without changing anything if a collision exists or disk space is insufficient:

```bash
bash -euo pipefail <<'EOF'
if [ -e /swapfile ] || grep -Eq '^[[:space:]]*/swapfile([[:space:]]|$)' /etc/fstab; then
  echo 'An existing /swapfile or fstab entry was found; stop and share this output.'
  exit 1
fi
if [ -n "$(swapon --show --noheadings)" ]; then
  echo 'Active swap already exists; stop and share this output.'
  swapon --show
  exit 1
fi
available_kb=$(df -Pk / | awk 'NR == 2 {print $4}')
if [ "$available_kb" -lt 1048576 ]; then
  echo 'Less than 1 GiB is available on the root filesystem; stop.'
  df -h /
  exit 1
fi
fallocate -l 1G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
printf '%s\n' '/swapfile none swap sw 0 0' >> /etc/fstab
swapon --show
free -h
EOF
```

**User-reported verification:** `mkswap` created a 1,024 MiB swap area, `swapon --show` listed `/swapfile` active with 0 bytes used, and `free -h` reported 1.0 GiB swap available. The guarded script completed successfully, including the `/etc/fstab` persistence entry and mode-600 permission command.

### Create and start the systemd service

Use one Uvicorn worker on the preflight-confirmed free loopback port 8001. The service runs as the restricted `credify` account, reads code and the model from `/home/credify/app`, and uses the isolated `/home/credify/venv`. Systemd hardening keeps the service filesystem read-only and home files read-only; the app does not require persistent writes. The unit must not overwrite an existing service file.

Run this as root after confirming the swap and its persistent entry. It writes `/etc/systemd/system/credify.service`, reloads systemd, enables and starts the service, then checks its local health endpoint. If startup or health fails, it prints recent service logs:

```bash
bash -euo pipefail <<'EOF'
if [ -e /etc/systemd/system/credify.service ]; then
  echo 'A Credify service unit file already exists; stop and inspect it.'
  exit 1
fi
test "$(stat -c '%a' /swapfile)" = 600
grep -Fqx '/swapfile none swap sw 0 0' /etc/fstab
swapon --show=NAME --noheadings | grep -Fxq /swapfile
cat > /etc/systemd/system/credify.service <<'UNIT'
[Unit]
Description=Credify scoring API and analyst dashboard
After=network.target

[Service]
Type=simple
User=credify
Group=credify
WorkingDirectory=/home/credify/app
Environment=HOME=/home/credify
Environment=PYTHONPATH=/home/credify/app/src
Environment=PROPENSITY_MODEL_ARTIFACT_PATH=/home/credify/app/models/selected_default_risk_model.joblib
Environment=PYTHONDONTWRITEBYTECODE=1
Environment=PYTHONUNBUFFERED=1
ExecStart=/home/credify/venv/bin/uvicorn propensity_prediction.api.main:app --host 127.0.0.1 --port 8001 --workers 1
Restart=on-failure
RestartSec=5
TimeoutStopSec=30
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=read-only
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictSUIDSGID=true
LockPersonality=true
UMask=0077

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable credify.service
if systemctl start credify.service; then
  systemctl --no-pager --full status credify.service
  if runuser -u credify -- /home/credify/venv/bin/python -c 'import json; from urllib.request import urlopen; result=json.load(urlopen("http://127.0.0.1:8001/health", timeout=10)); print(json.dumps(result)); assert result.get("status") == "ok" and result.get("model_loaded") is True'; then
    :
  else
    journalctl -u credify.service -n 60 --no-pager
    exit 1
  fi
else
  journalctl -u credify.service -n 60 --no-pager
  exit 1
fi
EOF
```

**User-reported startup:** The unit was written and enabled. The first immediate request to `127.0.0.1:8001/health` received `ConnectionRefusedError` only 28 ms after service start. A later status and journal check confirmed the service remained active, application startup completed, and Uvicorn reported `http://127.0.0.1:8001`; memory use was about 137 MiB. The full unit content was then inspected; it matches the intended single-worker loopback configuration.

The initial `systemctl cat` call opened a pager. The user reran the inspection with `--no-pager` and supplied the results:

```bash
systemctl status credify.service --no-pager --full
systemctl cat --no-pager credify.service
ss -ltnp 'sport = :8001'
journalctl -u credify.service -n 80 --no-pager
free -h
```

The user subsequently confirmed port 8001 listens only on `127.0.0.1`, and the local readiness request returned `{"status": "ok", "model_loaded": true}`. At that time the system showed about 302 MiB available RAM and 115 MiB swap in use. The local health check is complete; a controlled restart remains to confirm service recovery.

Run this as root to restart the service, allow model loading to finish, and verify it returns healthy:

```bash
systemctl restart credify.service && sleep 10 && systemctl is-active credify.service && runuser -u credify -- /home/credify/venv/bin/python -c 'import json; from urllib.request import urlopen; result=json.load(urlopen("http://127.0.0.1:8001/health", timeout=10)); print(json.dumps(result)); assert result.get("status") == "ok" and result.get("model_loaded") is True'
```

If the restart or health request fails, share the output and recent journal before changing the unit.

**User-reported restart verification:** `systemctl is-active credify.service` returned `active`, and the health endpoint again returned `{"status": "ok", "model_loaded": true}`. Step 11.9 is complete. The selected model-backed API and dashboard service is running as `credify`, on loopback port 8001, with the isolated venv and 1 GB swap.

The runtime manifest contains these exact pins for Ubuntu 24.04, Python 3.12, and x86_64:

```text
annotated-doc==0.0.5
annotated-types==0.8.0
anyio==4.15.1
click==8.5.0
cloudpickle==3.1.2
fastapi==0.143.0
h11==0.16.0
idna==3.20
joblib==1.6.0
narwhals==2.27.1
numpy==2.5.3
opentelemetry-api==1.45.1
pandas==3.0.5
pydantic==2.14.0
pydantic-core==2.50.0
python-dateutil==2.9.0.post0
scikit-learn==1.9.1
scipy==1.18.1
six==1.17.0
starlette==1.9.0
threadpoolctl==3.7.0
typing-inspection==0.4.4
typing-extensions==4.16.0
uvicorn==0.54.0
```

## Step 11.10 — Configure hostname and HTTPS

**Step status:** Complete · **Phase status:** In progress

### Goal

Use the verified Porkbun wildcard DNS for `credify.saxam.dev`, then route it through a dedicated Nginx server block to the verified Credify service at `127.0.0.1:8001`, enable HTTPS, and keep the existing `auth.saxam.dev` configuration working. Preflight confirmed the current Authentify certificate covers only `auth.saxam.dev`, Certbot's Nginx plugin is available, and the existing Nginx configuration passes validation.

### DNS verification comes first

Before adding a DNS record, inspect the Porkbun DNS records for `saxam.dev`. Check for an explicit record with host `credify` and a wildcard record with host `*`; note each record's type and whether its target is the Droplet's public IPv4 address. The earlier server-side lookup proves that the hostname currently resolves, not which record supplies the answer. If a correct wildcard record already covers the name, no extra record is needed. If neither record routes it to this Droplet, create an A record for host `credify` pointing to the Droplet's public IPv4 address, then wait for DNS to resolve before requesting a certificate.

**User-reported DNS verification:** Porkbun has an A record for host `*.saxam.dev` pointing to the same redacted public IPv4 address previously observed for the Droplet, with TTL 600. It also has an A record for the apex `saxam.dev` to that address. The wildcard DNS record already covers `credify.saxam.dev`, so no additional DNS record is needed. No DNS record was changed. A wildcard DNS record does not itself provide TLS certificate coverage.

### Certificate options considered

| Option | Certificate plan | Pros | Cons |
|---|---|---|---|
| **A — Issue a separate certificate for `credify.saxam.dev`** | Give Credify its own Let's Encrypt certificate and renewal entry; Nginx serves it in the separate Credify site. | Keeps Authentify's existing certificate and renewal lifecycle independent; HTTP-01 can use the already public hostname if port 80 is reachable. | Adds a second certificate to renew and monitor; depends on the Certbot Nginx plugin or careful manual Nginx configuration. |
| **B — Expand the existing Authentify certificate to include Credify** | Add both hostnames to the existing certificate and use it from separate server blocks. | One certificate covers both current hostnames. | Couples the services' renewal and certificate lifecycle; a certificate change now affects the existing Authentify site. |
| **C — Use a wildcard certificate for `*.saxam.dev`** | Obtain a wildcard certificate using DNS-01 validation through Porkbun or another DNS workflow. | Covers Credify and future subdomains without another per-host certificate. | Requires DNS validation steps or API credential management and more setup; wildcard keys have wider impact if exposed. |

### Certificate recommendation

Use **Option A**, a separate `credify.saxam.dev` certificate. It preserves Authentify's current certificate lifecycle and matches the existing separate-hostname design. The certificate and Certbot preflight is complete; validate the new Credify HTTP site before asking Certbot to issue and install its certificate.

### Decision

**Selected: Option A — Issue a separate certificate for `credify.saxam.dev`.** The user chose this after confirming the Porkbun wildcard DNS record already routes the hostname to the Droplet. Preflight showed the existing Authentify certificate covers only `auth.saxam.dev` and is valid until 2026-12-12; Certbot 2.9.0 and its Nginx plugin are installed; `certbot certificates` lists only the Authentify certificate; and `nginx -t` succeeds. No DNS record, Nginx configuration, or certificate has been changed for Credify.

### Add and verify the Credify HTTP site

Create a separate Nginx site file for `credify.saxam.dev` that proxies to the verified local service on port 8001. Keep the existing Authentify site untouched. After linking the site, validate Nginx before reloading it. Then check the Credify health route through Nginx using the hostname as the HTTP Host header.

Run as root. These checks stop if either Credify site path already exists:

```bash
bash -euo pipefail <<'EOF'
test -d /etc/nginx/sites-available
if [ -e /etc/nginx/sites-available/credify ] || [ -e /etc/nginx/sites-enabled/credify ]; then
  echo 'A Credify Nginx site path already exists; stop and inspect it.'
  exit 1
fi
cat > /etc/nginx/sites-available/credify <<'NGINX'
server {
    listen 80;
    server_name credify.saxam.dev;

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX
ln -s /etc/nginx/sites-available/credify /etc/nginx/sites-enabled/credify
nginx -t
systemctl reload nginx
python3 -c 'import json; from urllib.request import Request, urlopen; request=Request("http://127.0.0.1/health", headers={"Host":"credify.saxam.dev"}); result=json.load(urlopen(request, timeout=10)); print(json.dumps(result)); assert result.get("status") == "ok" and result.get("model_loaded") is True'
EOF
```

**User-reported HTTP-site verification:** The separate `/etc/nginx/sites-available/credify` site was enabled, `nginx -t` passed, Nginx reloaded, and a request with `Host: credify.saxam.dev` returned `{"status": "ok", "model_loaded": true}` through the proxy. The Authentify site was not edited. HTTP routing is complete.

### Issue the separate certificate and enable HTTPS

Use Certbot's installed Nginx plugin to request a certificate only for `credify.saxam.dev` and configure HTTP-to-HTTPS redirection. This should keep the existing Authentify certificate separate. Run as root:

```bash
certbot --nginx --redirect -d credify.saxam.dev
```

If prompted to choose the HTTP-to-HTTPS redirect option, select the redirect. Certbot may need the existing account email or terms confirmation. Share its final result and any error output; do not rerun issuance blindly if it fails.

**Certificate issuance result:** The user ran the command successfully. Certbot saved the certificate at `/etc/letsencrypt/live/credify.saxam.dev/fullchain.pem`, deployed it to the Credify Nginx site, set up a scheduled renewal task, and reported expiry on 2027-01-17.

**Verification result:** The user confirmed `nginx -t` succeeds; Certbot lists distinct certificates for `auth.saxam.dev` and `credify.saxam.dev`; HTTP for Credify returns `301` to `https://credify.saxam.dev/`; and `https://credify.saxam.dev/health` returns `{"status":"ok","model_loaded":true}`. The HTTPS `HEAD` request to Authentify returned `405 Method Not Allowed` with `Allow: GET`; this is an unsupported request method at that route, while the HTTPS response confirms the hostname is reachable. No Authentify configuration or certificate was changed as part of Credify setup.

**Status:** Complete.

## Step 11.11 — Verify live behavior and operations

**Step status:** Complete · **Phase status:** In progress

### Goal

Verify that a user can load the deployed dashboard and assets, score a valid request through the public hostname, upload a small CSV through the browser, and recover the service after a controlled restart. Inspect request-size limits, logs, and resource use. Prepare a practical backup and restore procedure based on the fact that application source and the model artifact are versioned in Git while the systemd and Nginx configuration live under `/etc`.

### Decision

**Selected: Option B — Full operational checks.** The user chose this option on 2026-10-19. It includes the essential live checks plus the CSV upload boundary and backup/restore planning. Run the checks in stages; do not restart the service or create a backup archive until the user has reviewed the earlier live-check results.

### Workspace facts for the live check

- FastAPI serves the dashboard at `/`, `/styles.css`, and `/app.js`.
- `GET /health` returns model readiness; `GET /v1/dashboard-config` reports the active row limit and required CSV columns.
- `POST /v1/review-queue` accepts `customers` and `max_review_count`. Each customer has an integer `ID`, numeric limit/age/bill/payment features, integer `SEX`, `EDUCATION`, `MARRIAGE`, and integer `PAY_0`, `PAY_2`…`PAY_6`.
- The configured row maximum is 30,000. The browser parses CSV locally and sends JSON to the API, so Nginx's request-body limit must also permit a maximum-size portfolio request.
- The workspace includes `data/sample_customer_portfolio_10.csv` for the browser upload check.

**Status:** Complete.

**User-reported browser result:** The deployed website and all its functionality work. The user does not want to share raw logs because they may contain IP addresses; only aggregate error counts were shared. The public dashboard configuration reports a 30,000-row application cap. Compact JSON for the workspace's 10-row sample is 3,657 bytes; a linear estimate for 30,000 similar rows is about 11.0 MB (roughly 10.5 MiB).

### Request-size limit decision

| Option | Implementation | Pros | Cons |
|---|---|---|---|
| **A — Raise the Credify-only Nginx limit to 16 MiB** | Add `client_max_body_size 16m;` inside Credify's HTTPS server block, test and reload Nginx, then verify the effective setting. | Preserves the existing 30,000-row application cap for typical customer data; applies only to Credify's hostname; leaves Authentify unchanged. | Allows larger requests to consume more memory and processing on a 1 GB Droplet; the estimated maximum is typical-data based, not a guarantee for unusually long numeric values. |
| **B — Keep Nginx's 1 MiB default and lower the supported portfolio size** | Leave Nginx unchanged and revise the user-facing/API row cap to a value whose request fits below 1 MiB. | Avoids raising the web server's request allowance on a small Droplet. | Requires an application change and new deployment; limits the agreed 30,000-row workflow and still needs a safety margin for varied data. |

**Recommendation:** Option A, with the 16 MiB limit scoped to the Credify virtual host. It aligns Nginx with the existing dashboard/API contract while limiting the larger request allowance to this app. Do not deliberately send a 30,000-row request to the 1 GB production Droplet as part of this check; the API maximum is not a measured throughput guarantee.

**Decision and verification:** The user selected Option A. The `16m` directive was added only in Credify's HTTPS block. `nginx -t` succeeded, Nginx reloaded, the effective configuration showed `client_max_body_size 16m;`, and the public health check returned `{"status":"ok","model_loaded":true}`. Authentify was not modified.

The user inspected `/etc/nginx/sites-available/credify`. It has one HTTPS block proxying to `127.0.0.1:8001` and one HTTP block that redirects to HTTPS; the HTTPS block was the correct location for the site-specific body limit. The user backed up the site file to `/etc/nginx/sites-available/credify.before-body-limit.conf`, added `client_max_body_size 16m;` only to the HTTPS block, passed `nginx -t`, reloaded Nginx, confirmed the directive in the effective config, and verified public health `{"status":"ok","model_loaded":true}`. Authentify was not modified. The 30,000-row endpoint cap is aligned with the typical estimated request size, but a full-capacity production request was intentionally not sent to this 1 GB host.

### Backup and recovery decision

**Options considered:** (A) create a small root-only bundle of the Credify systemd unit, active Nginx site, and exact runtime dependency manifests; record the exact public Git commit for source and model recovery; verify the bundle and transfer it off-host; or (B) create a full Droplet snapshot through the provider. The user selected **Option A**. TLS private keys and raw logs were excluded.

**Backup verification:** Both `/tmp/credify-runtime-requirements.txt` and `/home/credify/requirements-deploy.txt` were present. The deployed checkout was clean at `b6b253dc36cc47fcf2d7cbd263b12fdadbb7d711`. The user created `/root/credify-recovery-20261019T184133Z.tar.gz` with mode `0600`, size 2,124 bytes, and the six expected entries, including the systemd unit, Nginx site and symlink, both manifests, and `RESTORE.md`. The archive was copied to `~/Downloads/`; its local SHA-256 matched `90b07fc154cc9e69fe88a0e2ac02efc568463d5783da80fcb00f4b4ef2448b6f`. The first SCP attempt using default SSH credentials failed; the user succeeded with their `res-dev` key. The archive is off-host. A full restore was not run against the live service.

**Operational verification:** The user reports the deployed dashboard and all functionality work. The public health endpoint passed after the Nginx change. Sanitized error-level log count was zero; service was active with zero restarts, about 170 MiB resident memory, 295 MiB RAM available, 114 MiB swap used, and 18 GB disk free. The controlled service restart and post-restart health check had already passed in Step 11.9, so it was not repeated. Typical 30,000-row request size is estimated at about 10.5 MiB, below the new 16 MiB Credify-only Nginx limit. A maximum-size portfolio was not sent to the 1 GB host; the cap is an application limit, not a measured throughput guarantee.

**Status:** Complete.

## Step 11.12 — Document deployment and close Phase 11

**Step status:** Complete · **Phase status:** Complete

### Goal

Finish the deployment record and update the README with a short, ordered summary of Phase 11. Keep operational commands, choices, evidence, and limitations in this complete phase document.

### Options considered

| Option | Documentation approach | Pros | Cons |
|---|---|---|---|
| **A — Concise README and complete phase record** | Add a brief Phase 11 summary and link in the README; put deployment details and the ordered walkthrough in this document. | Keeps the README scannable and operational instructions in one maintained reference. | A reader must follow the link for detailed deployment commands. |
| **B — Duplicate deployment details in the README** | Copy server commands, configuration, verification, and recovery details into both documents. | Makes the README more self-contained. | Duplicates operational instructions and creates a risk that the two copies drift. |

### Decision and completion record

**Selected: Option A.** The user chose the concise README approach. The README now marks Phase 11 complete, briefly describes the deployment and key operational limits, and links here for the ordered deployment decisions and command walkthrough. This phase document records the chosen service architecture, pinned deployed commit, DNS/certificate setup, site-specific Nginx request limit, operational evidence, and backup/recovery procedure.

### Final deployment reference

- **Public address:** `https://credify.saxam.dev`; HTTP redirects to HTTPS.
- **Application service:** `credify.service` runs as the restricted `credify` account from `/home/credify/app`, using `/home/credify/venv` and one Uvicorn worker bound to `127.0.0.1:8001`.
- **Model and source:** GitHub repository `https://github.com/saxamrawat/Credify.git`, deployed commit `b6b253dc36cc47fcf2d7cbd263b12fdadbb7d711`; the model artifact is in that commit.
- **Web routing:** `/etc/nginx/sites-available/credify`, enabled at `/etc/nginx/sites-enabled/credify`; the HTTPS server block sets `client_max_body_size 16m;`. Authentify retains its own Nginx site and certificate.
- **TLS:** Certbot issued a separate certificate for `credify.saxam.dev` and reported automatic renewal scheduling. The private key is not in the recovery bundle.
- **DNS:** The user's existing Porkbun wildcard A record already covered the hostname; no DNS change was needed.
- **Service checks:** `systemctl status credify.service`; `systemctl restart credify.service`; `curl -fsS https://credify.saxam.dev/health`; `nginx -t`. The health response was `{"status":"ok","model_loaded":true}`. A controlled restart passed during Step 11.9.
- **Logs and privacy:** Review `journalctl -u credify.service` locally. Raw logs may contain client IP addresses; do not paste them into chat. For a shareable check, provide only an aggregate error count or redact IPs.
- **Resource profile:** 1 vCPU, 1 GiB RAM, 25 GB disk, and 1 GiB swap. At the latest inspection the service used about 170 MiB resident memory; RAM available was 295 MiB, swap used 114 MiB, and disk free was 18 GB. These values are a point-in-time observation, not a concurrency or availability guarantee.
- **Portfolio limit:** The API and dashboard permit up to 30,000 rows. A typical request of that size is estimated at about 10.5 MiB, which fits under the Credify-only 16 MiB Nginx limit. The maximum workload was not run on the 1 GiB host, so production capacity at that cap is unmeasured.
- **Recovery bundle:** `~/Downloads/credify-recovery-20261019T184133Z.tar.gz` on the user's computer; SHA-256 `90b07fc154cc9e69fe88a0e2ac02efc568463d5783da80fcb00f4b4ef2448b6f`. It contains the service unit, Nginx site and symlink, both runtime dependency manifests, and `RESTORE.md`. It excludes logs, customer data, and TLS private keys. The archive checksum was verified after off-host transfer; a full restore was not exercised.
- **Deferred feature:** Authentify sign-in remains a later feature update after Authentify becomes an API service.

### Documentation verification

The README and phase document link to each other, list Phase 11 complete, and preserve the deployment walkthrough in order. `git diff --check` passed. Automated tests were not run because this closeout changes documentation only.

## Phase closeout

Phase 11 is complete. Credify is deployed at `https://credify.saxam.dev`; the public health check passes, HTTPS is enabled with a separate certificate, the user's browser checks confirmed the dashboard functionality, and the verified recovery bundle is stored off the Droplet. The operational limitations in this record remain part of the deployment handoff: the 30,000-row cap is not a measured maximum workload, and full restoration has not been rehearsed.
