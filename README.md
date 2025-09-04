
## Requirements

- [ViGEmBus Driver](https://github.com/nefarius/ViGEmBus): Required for virtual gamepad emulation

## Installation

### 1. Install the ViGEmBus Driver

The ViGEmBus driver allows emulation of Xbox and PlayStation controllers. It is required for Aim Assist to work properly.

1. Visit the [ViGEmBus releases page](https://github.com/nefarius/ViGEmBus/releases).
2. Download the latest installer (e.g., `ViGEmBus_Setup_x.x.x.exe`).
3. Run the installer and follow the prompts to complete the installation.

*If you encounter any issues, please refer to the [ViGEmBus documentation](https://github.com/nefarius/ViGEmBus#installation).*

### 2. Clone this Repository

```sh
git clone https://github.com/pedrossntos/fps-aim-assist.git
cd aim-assist
```

### 3. Install Dependencies


```sh
pip install -r requirements.txt
```


## Usage

1. Ensure the ViGEmBus driver is installed and running.
2. Run the provided application
   
```sh
python main.py
```
3. Click in 'Start System' then 'Enable Mapping'.
