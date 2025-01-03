# Systemd Unit Files for LM-Studio and Xvfb

This repository contains a set of systemd unit files and an environment file designed to facilitate the setup and execution of LM-Studio, along with the necessary dependencies such as the Xvfb virtual framebuffer. The files are designed to be run as a user service using `systemctl --user`.

## Files

### 1. `test.service`
This is a systemd unit file created for testing purposes. It is designed to run as a user service. The purpose of this file is to serve as a template or a basic example of how to configure a systemd service for running user-level applications. It may be modified for various use cases as needed.

**Key Features:**
- Runs as a user service.
- Intended for testing purposes.

### 2. `xvfb-user.service`
This systemd unit file is used to start the Xvfb (X virtual framebuffer) server for a specific user. Xvfb is required to simulate an X11 server, which is useful for applications that require graphical display output but do not need to be run on a physical monitor.

- This unit depends on the environment file `lmstudio.env`, which is described below.
- It must be executed using the `systemctl --user` command, running in the context of the specific user.

**Key Features:**
- Starts a virtual X11 server using Xvfb.
- Dependent on `lmstudio.env` for configuration.
- Can be started as a user service (`systemctl --user`).

### 3. `lmstudio-user.service`
This systemd unit file starts the LM-Studio suite, a software package that requires both graphical and environment configurations. The unit depends on the `xvfb-user.service` (which brings up Xvfb), and it uses the `lmstudio.env` environment file for additional configuration.

**Key Features:**
- Starts the LM-Studio suite after Xvfb is running.
- Depends on `xvfb-user.service` to ensure the virtual framebuffer is active.
- Uses `lmstudio.env` for configuring the LM-Studio package and setting the `DISPLAY` variable.

**Command Usage:**
- The unit should be executed with the `systemctl --user` command.

### 4. `lmstudio.env`
This is an environment file that provides necessary variables for both the `xvfb-user.service` and `lmstudio-user.service` systemd units. The file contains the following important settings:

- `DISPLAY`: Specifies the display number used by Xvfb.
- `LM_STUDIO`: Defines the name to the LM-Studio AppImage file that should be used by `lmstudio-user.service`.

**Key Features:**
- Sets the `DISPLAY` environment variable, which is shared by both `xvfb-user.service` and `lmstudio-user.service`.
- Defines the `LM_STUDIO` variable for the LM-Studio AppImage file name.

---

## Usage

To use these services, you need to execute the commands under the context of the user. Here are the steps for usage:

1. **Start the Xvfb virtual framebuffer:**
   ```bash
   systemctl --user start xvfb-user.service
   ```

2. **Start the LM-Studio suite:**
   ```bash
   systemctl --user start lmstudio-user.service
   ```

Both of these services depend on the `lmstudio.env` file for correct environment variables to be set. Make sure this environment file is properly configured before starting the services.

## Conclusion
These systemd unit files help automate the setup and running of LM-Studio in a virtual X environment. The `xvfb-user.service` ensures graphical output is available, while `lmstudio-user.service` manages the actual LM-Studio execution. The environment file `lmstudio.env` ties everything together by setting essential variables like `DISPLAY` and the name of the LM-Studio AppImage.
