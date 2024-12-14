import psutil
import socket
import subprocess  
import time
from PIL import Image, ImageDraw, ImageFont
from papirus import Papirus
from pijuice import PiJuice  # Import the PiJuice library
import os

def is_papirus_connected():
    """
    Checks if the Papirus e-paper display is connected via I2C.
    """
    try:
        # Use i2cdetect to check for the Papirus I2C address (0x48)
        result = subprocess.check_output(["i2cdetect", "-y", "1"]).decode()
        return "48" in result  # 0x48 is the Papirus I2C address
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


# Initialize the PiJuice instance
pijuice = PiJuice(1, 0x14)  # I2C bus 1, address 0x14

def get_battery_status():
    """
    Fetches the battery percentage and charging status from PiJuice.
    """
    try:
        # Get battery charge level
        charge_level = pijuice.status.GetChargeLevel()['data']

        # Get charging status
        charging_status = pijuice.status.GetStatus()['data']['powerInput']

        # Interpret charging status
        if charging_status == "NOT_PRESENT":
            charging_status_str = "Discharging"
        elif charging_status == "PRESENT":
            charging_status_str = "Charging"
        else:
            charging_status_str = "Unknown"

        return charge_level, charging_status_str
    except Exception as e:
        # Handle any exceptions (e.g., PiJuice not detected)
        return "N/A", "Error"

def get_cpu_temperature():
    """
    Gets the CPU temperature from the Raspberry Pi's system files.
    """
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read().strip()) / 1000.0  # Convert from millidegrees to degrees
        return f"{temp:.1f}°C"
    except FileNotFoundError:
        return "N/A"

def get_ip_address():
    """
    Gets the IP address of the active network interface (not 127.0.0.1).
    """
    addrs = psutil.net_if_addrs()
    for interface_name, addr_list in addrs.items():
        for addr in addr_list:
            # Check for IPv4 address that's not 127.0.0.1
            if addr.family == socket.AF_INET and addr.address != "127.0.0.1":
                return addr.address
    return "N/A"

def get_network_activity():
    """
    Gets the network activity (bytes sent and received) from the primary network interface.
    """
    net_io = psutil.net_io_counters()
    sent = round(net_io.bytes_sent / (1024 * 1024), 2)  # Convert to MB
    recv = round(net_io.bytes_recv / (1024 * 1024), 2)  # Convert to MB
    return f"Sent: {sent} MB, Recv: {recv} MB"

def get_ssid():
    """
    Gets the current Wi-Fi SSID using the `iwgetid` command.
    """
    try:
        ssid = subprocess.check_output(["iwgetid", "-r"], stderr=subprocess.DEVNULL).decode().strip()
        return ssid if ssid else "N/A"
    except FileNotFoundError:
        return "N/A"
    except subprocess.CalledProcessError:
        return "N/A"

def is_tailscale_up():
    """
    Checks if the Tailscale interface `tailscale0` has an IP address.
    """
    addrs = psutil.net_if_addrs()
    if "tailscale0" in addrs:
        for addr in addrs["tailscale0"]:
            if addr.family == socket.AF_INET:  # Check for an IPv4 address
                return addr.address
    return "Down"

def get_system_status():
    """
    Fetches current system status including CPU load, memory usage, temperature,
    load average, IP address, network activity, SSID, Tailscale status, and battery info.
    """
    # CPU load
    cpu_load = psutil.cpu_percent(interval=1)

    # Battery status
    battery_percentage, charging_status = get_battery_status()

    # Memory usage
    memory = psutil.virtual_memory()
    mem_total = round(memory.total / (1024 * 1024), 1)  # Convert to MB
    mem_used = round(memory.used / (1024 * 1024), 1)    # Convert to MB

    # CPU temperature
    cpu_temp = get_cpu_temperature()

    # Load average (1, 5, 15 minutes)
    load_avg = psutil.getloadavg()
    load_avg_str = f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"

    # IP address
    ip_address = get_ip_address()

    # Network activity (split into two lines)
    net_io = psutil.net_io_counters()
    sent = round(net_io.bytes_sent / (1024 * 1024), 2)  # Convert to MB
    recv = round(net_io.bytes_recv / (1024 * 1024), 2)  # Convert to MB
    network_line_1 = f"Net: Sent: {sent} MB, Recv: {recv} MB"

    # SSID
    ssid = get_ssid()

    # Tailscale status
    tailscale_status = is_tailscale_up()

    # Combine CPU Load, Battery Percentage, and Charging Status
    cpu_battery_line = f"CPU: {cpu_load}%, Battery: {battery_percentage}%, {charging_status}"

    return [
        cpu_battery_line,
        f"Memory: {mem_used}/{mem_total} MB",
        f"CPU Temp: { cpu_temp}",
        f"Load Avg: {load_avg_str}",
        f"IP Addr: {ip_address}",
        network_line_1,
        f"Wi-Fi: {ssid}",
        f"Tailscale: {tailscale_status}",
    ]


def render_status_to_image(status, width, height, bold_font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 
                           regular_font_path="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size=10):
    """
    Renders system status as an image using Pillow with bold labels and regular data.
    """
    # Create a blank white image
    image = Image.new("1", (width, height), 255)
    draw = ImageDraw.Draw(image)

    # Load the fonts
    bold_font = ImageFont.truetype(bold_font_path, font_size)
    regular_font = ImageFont.truetype(regular_font_path, font_size)

    y = 0
    for line in status:
        if ":" in line:
            label, value = line.split(":", 1)
            # Ensure a space is preserved after the colon
            label_with_colon = f"{label}: "
            # Get the width of the bold label with the space
            label_width = bold_font.getbbox(label_with_colon)[2]
            draw.text((5, y), label_with_colon, font=bold_font, fill=0)
            draw.text((5 + label_width, y), value.strip(), font=regular_font, fill=0)
        else:
            draw.text((5, y), line, font=regular_font, fill=0)
        y += font_size + 2
    return image




def display_status(epaper, width, height):
    """
    Updates the e-paper display with system status rendered as an image.
    """
    status = get_system_status()
    image = render_status_to_image(status, width, height)
    epaper.display(image)
    epaper.update()

def main():
    if not is_papirus_connected():
        print("Papirus display not detected. Exiting.")
        return

    epaper = Papirus()
    width, height = epaper.width, epaper.height

    try:
        while True:
            display_status(epaper, width, height)
            time.sleep(10)
    except KeyboardInterrupt:
        print("Exiting...")


if __name__ == "__main__":
    main()

