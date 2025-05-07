# _Gotcha!_

*Gotcha!* (alias `gotcha-system`) is a proof of concept of an anomaly detection system.

This project was created mainly as a submission for the *Ingegneria della Conoscenza* (Knowledge Engineering) course, part of the Bachelor's programme in *Informatica* (Computer Science) at *Università di Bari Aldo Moro*.

## Installation

### Install dependencies

Firstly, make sure you have installed

- python3
- python-venv 
- Prolog interpreter, such as [SWI-Prolog](https://www.swi-prolog.org/Download.html)

Process will depend on your operating system.

---

Next, assuming you have already cloned the repository and opened it with your favorite IDE or Editor:

1. open a **terminal**
2. **create** a python **virtual enviroment (venv)** in the root directory:


```shell
python3 -m venv .venv # '.venv' will be its name
```

3. **enter the venv** with

```shell
source .venv/bin/activate
```

or (for Windows users):

```shell
.venv\Scripts\activate.bat
```

To exit the venv, just run `deactivate` in the terminal.

4. **install required packages** with

```shell
pip install -r requirements.txt
```

5. you are ready to go!

## Usage

Make sure you entered the virtual environment you have created earlier with the required packages installed.

Now:

1. Generate fake data by executing

```python
python -m scripts.genlog
```

2. Run the main script

```python
python -m app.main
```

3. Unfortunately, that is all there is to see for now!


## Other docs

- [Architecture overview](./docs/architecture.md)
- [Use cases](./docs/use-cases.md)
- [Planned features](./docs/todo.md)
