# rel_db_learning

**Interactive Algorithm Library Development via Jupyter Notebooks and pgModeler for Relational Database Learning**

An interactive course for learning relational databases made of Jupyter notebooks backed by a small Python library.

The course is written for university students with little programming background. It follows a **visualization first, code second** approach: 
every concept is shown as a diagram or a table before any notation or SQL appears and [pgModeler](https://pgmodeler.io/) is the main visual tool. 
Throughout the course you build your own database, a **Library management system**, starting from a simple design and improving it step by step.

| Folder | Topic | Notebooks |
|---|---|---|
| `00_setup` | Environment setup | 1 |
| `01_introduction` | Databases, relations, the Chinook sample database | 3 |
| `02_er_pgmodeler` | Entity-relationship design with pgModeler | 6 |
| `03_relational_algebra_and_calculus` | Relational algebra and tuple calculus | 6 |
| `04_sql_with_pgmodeler` | SQL with PostgreSQL and pgModeler | 14 |
| `05_normalization` | Normalization (1NF, 2NF, 3NF, BCNF) | 5 |

The modules are meant to be followed **in order**.

---

## What you need

| **Python 3.8 or newer** (developed and tested with Python 3.14) | Runs the library and Jupyter |
| **PostgreSQL** (developed with version 16) | The database server used by every notebook |
| **pgModeler**| Visual database design |
| **Jupyter** | Runs the notebooks |

Everything runs on your own computer. No Docker or cloud account is needed.

---

## Installation

The instructions are written for **Windows**.

### Step 1. Install PostgreSQL

1. Download the installer from <https://www.postgresql.org/download/> and run it with the default options. The default port is **5432**.
2. The installer asks for a password for the `postgres` user. **Write it down**, you will need it in step 7.
3. **Add PostgreSQL to your PATH.** The setup notebook looks for the `psql` command and the Windows installer does not make it available automatically.
   - Open the Start menu and search for **"Edit environment variables for your account"**.
   - Select **Path**, click **Edit**, then **New** and add the PostgreSQL `bin` folder, for example `C:\Program Files\PostgreSQL\16\bin`.
   - Click **OK** and open a **new** PowerShell window.
4. Check that it works:

   ```powershell
   psql --version
   ```

You do not need to create any databases yourself the setup notebook does that. The Windows installer also includes **pgAdmin** which the setup notebook offers as a manual fallback.

### Step 2. Install pgModeler

Download pgModeler from <https://pgmodeler.io/download>. Ready made installers are offered on the official site the source code is free and can also be compiled yourself.

### Step 3. Install Python

Download Python from <https://www.python.org/downloads/>. In the first screen of the installer tick **"Add python.exe to PATH"**.

Check it in a new PowerShell window:

```powershell
py --version
```

### Step 4. Download this project

Click the green **Code** button on this page, then **Download ZIP** and extract it to a folder of your choice.

If you use git you can clone the repository instead:

```
git clone https://github.com/mtsouris/rel_db_learning.git
```

### Step 5. Create a virtual environment and install the library

Open PowerShell **inside the project folder** (the folder that contains `setup.cfg`) and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install .
```

After the second command your prompt starts with `(.venv)`. The third command installs the library together with Jupyter and all other dependencies which can take a few minutes.

If PowerShell says that running scripts is disabled, run this once and try again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```


### Step 6. Start Jupyter

With the virtual environment active run:

```powershell
jupyter notebook
```

Your browser opens with the project folder. Each time you return to the course open PowerShell in the project folder, activate the environment with `.\.venv\Scripts\Activate.ps1`, and run `jupyter notebook` again.

You can also use **VS Code** with the Jupyter extension: open the project folder and select the `.venv` environment as the kernel.

### Step 7. Run the setup notebook

Open `notebooks/00_setup/00_environment_check.ipynb` and run the cells in order.

---

## Where your work goes

- **chinook** is a ready-made sample database of a digital music store. You only read from it.
- **my_project** is your own Library database. It grows as you move through notebooks
- **`student_work/my_project/`** is the folder for the pgModeler design files (`.dbm`) you create during the course.

---

## License

This project is released under the **MIT License** (see `LICENSE.txt`).

The normalization module includes a small part of **dbis-functional-dependencies** (RWTH Aachen University, Apache License 2.0, version 1.0.4). Its `LICENSE` and `NOTICE` files are kept in `src/rel_db_learning/normalization/_vendor/`.

The **Chinook** sample database is used under its open license. **PostgreSQL** and **pgModeler** are separate applications and are not distributed with this project.

---

## About

Developed as part of a diploma thesis at the School of Electrical and Computer Engineering, Technical University of Crete.
