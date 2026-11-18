# Ride-Hailing Platform Database Design — G6

Read the [English report](report_en.pdf) or its corresponding [Chinese report](report_zh.pdf). Both use the same five main chapters, schema, sample data, diagrams and verified results. The cover title and all six member names remain in English in both versions; the sixth member is **Jin Conghao**.

本仓库提供同步的中英文报告、LaTeX 源码、编译程序、完整 SQL、合成数据生成程序、四类可编辑图及执行验证结果。正文按需求、概念设计、关系映射与规范化、实现验证、数据使用与讨论五章组织；附录包含数据字典、参考材料与复现说明，以及成员职责草稿。中文版完整解释最新的范式推导；SQL、表名和图中标识符保持英文，以便逐项核对。

## Quick start

```sh
git clone https://github.com/Charlie0768/Ride-Hailing-Platform-Database-Design.git
cd Ride-Hailing-Platform-Database-Design
# Open report_en.pdf or report_zh.pdf directly; no installation is needed to read them.
make reports                       # requires Python 3 and XeLaTeX / TeX Live
make verify MYSQL_HOME=/path/to/mysql  # requires a MySQL 8.4 installation
```

To regenerate previews, diagrams or the ZIP, also install the optional Python dependencies:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements-dev.txt
make qa
make package                       # after reviewing the rendered pages
```

## Repository contents

| Path | Contents |
| --- | --- |
| [report_en.pdf](report_en.pdf), [report_zh.pdf](report_zh.pdf) | Compiled English and Chinese reports |
| [source/](source/) | Both generated, directly compilable LaTeX files |
| [sql/](sql/) | Schema, routines, 200-trip seed, warehouse, queries, application role and demonstrations |
| [scripts/](scripts/) | Data generation, MySQL verification, report generation, compilation and packaging |
| [figures/](figures/) | Four diagram sets in PDF, SVG, PNG and editable draw.io format |
| [results/](results/) | Actual TSV/JSON outputs, metadata, 32 checks and delivery checks |
| [Makefile](Makefile), [requirements-dev.txt](requirements-dev.txt) | Rebuild entry points and optional Python dependencies |
| [ride_hailing_complete.zip](ride_hailing_complete.zip) | Complete downloadable artifact bundle |
| [SHA256SUMS.txt](SHA256SUMS.txt) | SHA-256 checksums for packaged files (excluding the manifest itself and ZIP) |

The repository contains the project deliverables. Local course slides, the original Word reference, earlier drafts, MySQL binaries/data directories, Python environments, and disposable LaTeX logs/preview images are not part of the published bundle. The `.tex` sources and build scripts are included; auxiliary `.aux`, `.toc` and `.log` files are regenerated locally.

## Current revision

- The cover lists exactly six members and the supplied student IDs. The sixth name is **Jin Conghao**, as corrected by the user.
- Chapter 3 shows the initial relational schema S0, the 1NF check, the 2NF check and a separate ShiftWide counterexample, the Trip0 decomposition for 3NF, and a relation-by-relation BCNF check. It explains candidate keys, dependencies, lossless joins, dependency preservation and the treatment of unassigned trips.
- Trip0 is explicitly identified as a reconstructed design worksheet; ShiftWide is a separate illustrative 2NF counterexample. Neither is claimed to have been created in MySQL. The final operational schema remains unchanged.
- Lin Shuaiyu's confirmed responsibility runs from topic definition through requirements, ER/EER design, relational mapping and normalization. Sample-data preparation and later work are not allocated as confirmed duties. The other five members have TBD placeholders. No contribution percentages or peer-assessment scores are invented.
- The original Word document is unchanged. Earlier report versions are retained locally under `build/`, outside Git and the delivery ZIP.

## Diagrams and SQL evidence

Four diagram sets are in `figures/`: `01_frontend`, `02_backend`, `03_chen_eer`, `04_relational`. Each includes a vector PDF, SVG, PNG preview and editable `.drawio` file. Open `.drawio` files in diagrams.net / draw.io; these are not Visio `.vsdx` files. Shapes and line segments are editable, but segments are not automatically attached when shapes move.

The complete ER/EER and relational diagrams use A3 landscape pages; function diagrams use A4 landscape. Other report pages use A4 portrait. ER/EER notation follows LN3–LN4: rectangles, attribute ellipses, relationship diamonds, key underlines, weak entities, identifying relationships, endpoint cardinalities and partial overlapping/disjoint specializations.

The report contains the complete 11-table DDL, actual `SHOW TABLES` and `DESCRIBE` outputs, samples from all core tables, a joined result, insert/update/delete examples, and analytical SQL/results. `sql/07_report_demonstrations.sql` records the demonstration queries. `results/report_evidence.json`, `sample_*.tsv` and `crud_*.tsv` hold their actual outputs.

## Executed database verification

- MySQL 8.4.13, InnoDB, isolated Unix socket, TCP networking disabled.
- 11 operational tables, 2 views, 4 lifecycle procedures, 3 guard triggers and 1 application role.
- Analytical snapshot: 3 dimensions and 1 completed-trip fact table.
- 200 synthetic trips: 130 completed, 30 cancelled, 20 assigned, 10 in progress, 10 requested.
- 32/32 database checks passed, including rollback, concurrent completion and application privileges.
- Completed-trip total fare: 7,853.92 simulated currency units.
- Lectures 2–10 were available. Lecture 1 was not supplied.

The release was rebuilt and checked using a fresh, isolated MySQL instance before upload. Both PDFs are compiled from the same saved execution outputs. The report compilation and archive integrity checks are separate from the 32 database checks.

## Reproduce from an empty isolated instance

Requirements: MySQL 8.4 server/client programs and Python 3. SQL generation, loading and verification use the Python standard library.

```sh
bash scripts/reproduce.sh /absolute/path/to/mysql-installation
```

The installation must contain `bin/mysqld`, `bin/mysql` and `bin/mysqladmin`. The script initializes a new temporary data directory, disables TCP and MySQL X Protocol, runs the project, collects evidence and shuts down its instance. It does not use or erase an existing database. Temporary logs/data remain in the printed directory. No permanent service is installed. A restricted sandbox may require permission for MySQL initialization and socket access.

The verified run used Oracle's official macOS ARM64 MySQL 8.4.13 archive; the runtime is not bundled. Download: https://dev.mysql.com/downloads/mysql/8.4.html .

For an independently managed **disposable** server, run these scripts in order:

1. `sql/01_schema.sql`
2. `sql/02_logic.sql`
3. `sql/03_seed.sql`
4. `sql/04_warehouse.sql`
5. `sql/06_application_role.sql`

Set `MYSQL_BIN` and `MYSQL_SOCKET`, then run `python3 scripts/run_validation.py` and `python3 scripts/collect_report_evidence.py`. Schema/role creation deliberately fails on existing names. Verification creates and removes a temporary `rh_validation@localhost` account and needs administrative privileges. Do not use a production server.

`sql/05_queries.sql` contains analytical queries. All sample identities, contact values, licenses and vehicle identifiers are fictitious; `example.invalid` is a non-deliverable domain. The temporary CRUD user is deleted after its demonstration.

## Rebuild both reports

Use XeLaTeX and TeX Live packages `ctex`, `fontspec`, `tikz`, `tabularx`, `longtable`, `booktabs`, `listings`, `xurl`, `titlesec`, `fancyhdr`, `pdfpages` and `tocloft`, with the Fandol, Latin Modern and TeX Gyre fonts. No system font is required for member names; they are romanized.

```sh
python3 scripts/compile_reports.py
```

This generates `source/report_en.tex` and `source/report_zh.tex`, compiles each twice, checks for overfull boxes/missing glyphs, and writes both PDFs. The build fails if any paired report paragraph lacks a translation. The section organization, new normalization derivation and team details are in `scripts/structured_report.py`; reusable content is in `scripts/build_reports.py` and `scripts/revision_content.py`. For direct LaTeX edits, compile the `.tex` file twice from this directory without regenerating it.

The supplied figure PDFs suffice for compilation. To regenerate all diagram formats, install PyMuPDF and run `python3 scripts/draw_diagrams.py`. This overwrites exported figure files, so preserve any manual draw.io/SVG changes separately.

Visual QA uses PyMuPDF and Pillow: `python3 scripts/render_qa.py`. After inspecting the rendered pages, run `python3 scripts/package_delivery.py` to update the checks, SHA-256 manifest and ZIP. `build/`, `.git/`, virtual environments and Python caches are excluded from the archive. Git tracks the compiled PDFs and project ZIP so that the reports can be downloaded without a local TeX installation.

## Design boundaries

Trip records its assigned vehicle; the driver is derived through fixed vehicle ownership. Dispatch checks both driver and vehicle inputs. Changing ownership over time requires a different historical-assignment design. Pending/active requests use Trip states; only cancellations have CancelledTrip rows.

MySQL-specific features include `DELIMITER`, procedures/triggers, `SIGNAL`, roles, `DATE_ADD`, `WITH ROLLUP`, and engine/character-set declarations. The complete implementation is not portable unchanged to Oracle or SQLite.

Lifecycle procedures own their transactions; call them outside an existing transaction. The application role cannot directly write statuses/outcome details. Administrative direct writes can bypass application invariants. This service role does not implement customer authentication or row-level authorization. Shift conflicts, cross-trip driver availability and active insurance at dispatch are discussed but not automatically enforced. Payments, settlement, GPS and route planning are outside scope.
