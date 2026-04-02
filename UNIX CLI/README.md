# Simple Shell Interface (SSI)

A lightweight, custom Unix-like shell implemented in C. This project demonstrates foundational operating system concepts, including process creation, signal handling, and background job management. 

## Features

* **Process Execution** - Executes standard Unix commands using `fork()` and `execvp()`.
* **Built-in Commands** -
    * `cd` - Changes the current working directory. Supports `~` to navigate to the user's home directory.
    * `bg` - Executes a given command in the background.
    * `bglist` - Lists all currently active background jobs alongside their Process IDs (PIDs).
* **Background Job Management** - Continuously tracks and reaps background processes non-blockingly using `waitpid` with the `WNOHANG` flag.
* **Interactive Prompt** - Displays a dynamically updated prompt featuring the current username, hostname, and working directory.
* **Readline Integration** - Utilizes the GNU `readline` library for robust command history and line editing capabilities.
* **Signal Handling** - Custom `SIGINT` (Ctrl-C) handling prevents the shell itself from terminating unexpectedly while allowing foreground child processes to be correctly interrupted.

---

## Prerequisites

To build and run this project, you will need a C compiler (GCC) and the `readline` development library installed on your system. 

For Debian or Ubuntu-based systems, you can install the required library using -

```bash
sudo apt-get update
sudo apt-get install build-essential libreadline-dev
```

For macOS using Homebrew -

```bash
brew install readline
```

---

## Building and Running

A `makefile` is included for straightforward compilation.

1. Clone the repository and navigate to the project directory.
2. Compile the shell using `make` -
```bash
make
```
3. Run the executable -
```bash
./ssi
```
4. To clean up the compiled object files and the executable, run -
```bash
make clean
```

---

## Technical Details

* **Language** - C (C99 standard)
* **Core Libraries** - standard C libraries, POSIX operating system API (`<unistd.h>`, `<sys/wait.h>`, `<signal.h>`), GNU Readline (`<readline/readline.h>`).
* **Architecture** - The shell operates on an infinite read-eval-print loop (REPL). It tokenizes user input into arrays, forks child processes for external commands, and executes built-in commands directly within the parent process context. Data structures include a fixed-size array to track active background jobs and their execution states.
