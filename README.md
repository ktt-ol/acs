# Access Control System Scripts


# Install

**venv**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Debian**

```bash
apt-get install python3-sdnotify python3-dateutil python3-paho-mqtt 
```

# Run

Create the configuration and change it to your needs.
```bash
cp settings.conf.example settings.conf
vim settings.conf
```

Start:
```bash
source venv/bin/activate
./glass-door.py
```
