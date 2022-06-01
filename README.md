![Validate with hassfest](https://github.com/youdroid/home-assistant-sickchill/workflows/Validate%20with%20hassfest/badge.svg)
![Validate](https://github.com/youdroid/home-assistant-sickchill/workflows/Validate/badge.svg)
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/youdroid/home-assistant-sickchill)
![GitHub commit activity](https://img.shields.io/github/commit-activity/m/youdroid/home-assistant-sickchill)
![GitHub maintainer](https://img.shields.io/badge/maintainer-%40youdroid-blue)
# SickChill Wanted Tv Shows

Home Assistant component to feed Upcoming Media Card with SickChill's wanted media.

## Installation
1. Install this component by copying [these files](https://github.com/youdroid/home-assistant-sickchill/tree/master/custom_components/sickchill) to `custom_components/sickchill/`.
2. Install the card: [Upcoming Media Card](https://github.com/custom-cards/upcoming-media-card)
3. Add the code to your `configuration.yaml` using the config options below.
4. Add the card code to your `ui-lovelace.yaml`. 
5. **You will need to restart after installation for the component to start working.**

### Options

| Key | Default | Required | Description
| --- | --- | --- | ---
| token | | yes | Your SickChill token (Config > General > Interface > API Key > Generate)
| name | sickchill | no | Name of the sensor.
| host | localhost | no | The host which SickChill is running on.
| port | 8081 | no | The port which SickChill is running on.
| protocol | http | no | The HTTP protocol used by SickChill.
| sort | name | no | Parameter to sort TV Shows **[date, name]**
| webroot |  | no | WebRoot parameter if you change it in config.ini (Syntax : **/newWebRoot**)
| json | true | no | Return format of this integration (json or not)

#### :warning: Caution
By default this addon automatically downloads images (poster and fanart) from SickChill to your /www/custom-lovelace/sickchill/ directory. 
If you change the sensor's name, the directory will changes name too. (Example : /www/custom-lovelace/[SENSOR NAME]/)  
The directory is automatically created. When your show is over all posters and fanarts are removed automatically from the directory.  
I made this choice because if I pick up images directly from Sickchill which use http protocol and no https (my situation and may be many others), web browser redirect http flux to https and it can't works correctly. So I decided to dowload them.  
:pray: Currently I did'nt try on all operating systems and unfortunately, this function may not work on all systems.
***
## Exemples

### Example for minimal config needed in configuration.yaml:
```yaml
    sensor:
    - platform: sickchill
      token: YOUR_SICKCHILL_TOKEN
```
### Example for ui-lovelace.yaml:
```yaml
    - type: custom:upcoming-media-card
      entity: sensor.sickchill
      title: TV Shows Wanted
```
