# Papirus Status Service

This guide explains how to set up and configure the `papirus_status.py` script as a systemd service on a Raspberry Pi. The script displays system information on a Papirus e-paper display and ensures it runs continuously at startup, but only if the Papirus display is connected.

---

## Prerequisites

1. **Raspberry Pi with Papirus e-paper display** connected and I2C enabled.
2. **Python3** installed on your Raspberry Pi.
3. **Required Python libraries**:
   ```bash
   pip3 install pijuice pillow psutil
   ```

4. **Enable I2C**:
   Ensure I2C is enabled via `raspi-config`:
   ```bash
   sudo raspi-config
   ```
   - Navigate to **Interface Options** > **I2C** > **Enable**.

---

## Installation Steps

### 1. Copy the Script
1. Save the `papirus_status.py` script to `/usr/local/bin/`:
   ```bash
   sudo cp papirus_status.py /usr/local/bin/papirus_status.py
   ```

2. Make the script executable:
   ```bash
   sudo chmod +x /usr/local/bin/papirus_status.py
   ```

---

### 2. Create the Systemd Service File

1. Create the service file:
   ```bash
   sudo nano /etc/systemd/system/papirus_status.service
   ```

2. Add the following configuration to the file (change your user if needed):

   ```ini
   [Unit]
   Description=Papirus System Status Display
   After=network.target

   [Service]
   ExecStart=/usr/bin/python3 /usr/local/bin/papirus_status.py
   Restart=always
   User=pi
   Group=pi

   [Install]
   WantedBy=multi-user.target
   ```

3. Save and exit the file (`CTRL+O`, `CTRL+X`).

---

### 3. Enable and Start the Service

1. Reload the systemd daemon:
   ```bash
   sudo systemctl daemon-reload
   ```

2. Enable the service to start at boot:
   ```bash
   sudo systemctl enable papirus_status.service
   ```

3. Start the service immediately:
   ```bash
   sudo systemctl start papirus_status.service
   ```

4. Check the status of the service:
   ```bash
   sudo systemctl status papirus_status.service
   ```

---

## Testing the Service

1. **Verify the Service at Boot**:
   Reboot the Raspberry Pi:
   ```bash
   sudo reboot
   ```
   After the reboot, check the service status:
   ```bash
   sudo systemctl status papirus_status.service
   ```

2. **Logs**:
   If the service fails, view the logs for troubleshooting:
   ```bash
   sudo journalctl -u papirus_status.service
   ```

---

## Troubleshooting

1. **Papirus Not Detected**:
   Ensure the I2C interface is enabled via `raspi-config`.

2. **Service Fails to Start**:
   - Verify that the script is executable and located at `/usr/local/bin/papirus_status.py`.
   - Check the logs for detailed error messages.

3. **User Permissions**:
   If you want to run the service as the `pi` user instead of `root`, ensure `pi` is added to the `i2c` group:
   ```bash
   sudo adduser pi i2c
   ```

---

## Customization

- **Modify the Script**:
  Adjust the `papirus_status.py` script to include additional system information or customize its layout.

- **Update the Service File**:
  To run the script under a different user or customize restart policies, edit the service file:
  ```bash
  sudo nano /etc/systemd/system/papirus_status.service
  ```

---

## Uninstallation

To stop and remove the service:
1. Stop the service:
   ```bash
   sudo systemctl stop papirus_status.service
   ```

2. Disable the service:
   ```bash
   sudo systemctl disable papirus_status.service
   ```

3. Remove the service file:
   ```bash
   sudo rm /etc/systemd/system/papirus_status.service
   ```

4. Remove the script:
   ```bash
   sudo rm /usr/local/bin/papirus_status.py
   ```

---

## License

This project is licensed under the MIT License.

---

Let me know if you need any further changes!
