# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Docker (preferred)
```bash
docker-compose build
docker-compose up          # production via uWSGI on port 8080
docker-compose -f docker-compose.dev.yml up  # dev mode on port 5000
```

Inside the running container, for frontend hot-reload:
```bash
yarn babel:watch
yarn sass:watch
```

### Manual (unsupported)
```bash
pip3 install -r requirements.txt
yarn run install-depends        # production JS deps → functree/static/yarn_components/
yarn run install-devDepends     # dev JS/build tooling
yarn run bower install          # bower components
yarn run build                  # transpile ES6 + SCSS via Gulp
uwsgi --ini uwsgi.ini           # start app
```

### Development server (no uWSGI)
```bash
python3 run.py   # Flask dev server on port 5000 (requires MongoDB)
```

### Frontend build tasks
```bash
yarn babel          # one-shot Babel transpile
yarn sass           # one-shot SCSS compile
yarn build          # both
```

## Architecture

### Stack
- **Backend**: Python 3 / Flask 0.12 + uWSGI
- **Database**: MongoDB via MongoEngine (ODM) + flask-mongoengine
- **Frontend**: Vanilla JS (ES6 transpiled by Babel/Gulp), SCSS compiled to CSS, Vue 2, D3 v3, Highcharts
- **Auth**: HTTP Digest auth (flask-httpauth) for admin routes

### Python package layout (`functree/`)
| File | Purpose |
|------|---------|
| `__init__.py` | App factory — creates Flask app, wires MongoEngine, CSRF, cache, debug toolbar |
| `config.py` | Default config; override with `instance/config.py` |
| `models.py` | MongoEngine documents: `Tree`, `Definition`, `Profile`, `AnnotationMapping` |
| `views.py` | All Flask routes |
| `forms.py` | WTForms form classes (`MappingForm`, `ComparisonForm`, `DisplayForm`, `UploadForm`) |
| `tree.py` | Tree data structures and KEGG hierarchy download/parsing; `Node` dict subclass |
| `services.py` | `DefinitionService` helper |
| `filters.py` | Jinja2 template filters |
| `constants.py` | App-wide constants (e.g. `NO_MATCHED_HIERARCHIES`) |
| `analysis/` | Core computation modules |

### Analysis pipeline (`functree/analysis/`)
- `__init__.py` — `load_input()`, `map_external_annotations()`, `calc_abundances()`, `calc_distributed_abundances()` — shared logic used by the analysis modes below
- `basic_mapping.py` — maps omics data to the functional tree (mean/sum per node; optional module coverage); uses `multiprocessing` for parallel computation
- `comparison.py` — two-sample comparison mode
- `display.py` — display a pre-computed profile (JSON or TSV input)
- `module_coverage.py` — KEGG module completeness scoring (uses `crckm` submodule)

### Data flow (mapping mode)
1. User submits TSV (gene/ortholog × sample matrix) + selects a reference tree target
2. `views.route_analysis('mapping')` validates the form and calls `analysis.basic_mapping.from_table()`
3. External annotations (non-K-numbers for KEGG/FOAM/EnteropathWay targets) are mapped to KEGG K-numbers via the `AnnotationMapping` MongoDB collection
4. Abundances are aggregated up the hierarchy (mean/sum, optionally with incidence-based distribution) via parallel `multiprocessing.Process` jobs
5. Result is stored as a `Profile` document in MongoDB with a UUID; user is redirected to `/viewer/?profile_id=<uuid>`
6. Viewer fetches the profile via `/profile/<uuid>` and renders the D3 radial tree SVG (`functree.js`)

### Frontend (`functree/static/src/`)
- `js/functree.js` — `FuncTree` class, D3 v3 radial tree renderer; compiled to `functree/static/dist/`
- `js/charts.js` — Highcharts-based bar/pie charts for the charts view
- `js/pathways.js` — KEGG pathway overlay view
- `js/utils.js` — shared helpers
- `scss/*.scss` — per-page stylesheets

Templates live in `functree/templates/`; `layout.html` is the Jinja2 base template.

### MongoDB collections
| Collection | Model | Notes |
|-----------|-------|-------|
| `tree` | `Tree` | Hierarchical functional tree (KEGG BRITE or custom) stored as a nested dict |
| `definition` | `Definition` | KEGG Module definitions (for module coverage) |
| `profile` | `Profile` | Analysis results; auto-expires after `FUNCTREE_PROFILE_TTL_DAYS` (default 7) |
| `annotation_mapping` | `AnnotationMapping` | Maps external annotation IDs to KEGG K-numbers |

### Configuration
Override defaults by creating `instance/config.py` (same keys as `functree/config.py`). Key settings:
- `MONGODB_HOST` — defaults to `mongodb://db:27017/functree`
- `FUNCTREE_ADMIN_USERNAME` / `FUNCTREE_ADMIN_PASSWORD` — protect `/admin/` routes
- `SECRET_KEY` — must be changed before deployment

### Admin actions (require HTTP Digest auth)
- `/action/update_trees/` — fetches and stores the KEGG BRITE tree from the KEGG API
- `/action/update_definitions/` — fetches KEGG Module definitions (via `crckm` submodule)
- `/action/update_annotation_mapping/` — loads `external_annotation.map` into MongoDB
- `/action/init_profiles/` — seeds example profile from `static/data/example/profile.json`

### API endpoints (CSRF-exempt)
- `POST /api/mapping/` — programmatic mapping submission; returns `{"profile_id": "..."}`
- `POST /api/comparison/` — comparison submission
- `POST /api/display/` — display submission
- `GET /api/viewer/` — renders the viewer via headless Chrome (Selenium) and returns raw SVG

### SVG export
`POST /action/save_image/` converts SVG to PDF/PNG/PS using CairoSVG.
