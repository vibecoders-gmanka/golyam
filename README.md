# Hello World GTK4/Libadwaita (C)

This is a simple "Hello World" application built using GTK4 and Libadwaita in C.

## Prerequisites

To build and run this application, you will need the following software:

*   A C compiler (e.g., GCC or Clang)
*   The Meson build system
*   Ninja (usually installed with Meson or as a separate package)
*   GTK4 development libraries
*   Libadwaita development libraries

**Installation on Ubuntu/Debian-based systems:**

```bash
sudo apt update
sudo apt install gcc meson libgtk-4-dev libadwaita-1-dev
```

**Installation on Fedora-based systems:**

```bash
sudo dnf install gcc meson gtk4-devel libadwaita-devel
```

## Building the Application

Follow these steps to build the application:

1.  **Navigate to the project root directory:**
    Open your terminal and change to the directory where you cloned or downloaded this project.

    ```bash
    cd path/to/hello-world
    ```

2.  **Create a build directory and setup Meson:**
    This command configures the build environment.

    ```bash
    meson setup build
    ```

3.  **Compile the project:**
    This command uses Ninja to compile the source code.

    ```bash
    ninja -C build
    ```

## Running the Application

After successfully building the application, you can run it using the following command from the project root directory:

```bash
./build/hello-world
```

This will launch the "Hello World" window.
