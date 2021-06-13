## Automatic grain counting app

A Heroku web app that aims at helping in grain counting and thin section description.

### Demo

Short demo of how it works:

<img src="demo_gif.gif" width="800" height="400"/>

### Heroku deployed app

If you want to see an online version of the app please go to:

#### [https://petrography.herokuapp.com](https://petrography.herokuapp.com/)

### Local use

Using streamlit as frontend, clone the repo and run it with the following command:

Requirements are:

```bash
streamlit
opencv-python-headless==4.2.0.32
numpy
pillow
pandas
scikit-image
scipy
```

Alternatively run for installing the dependencies:

```bash
pip install -r requirements.txt
```

Clone the repo and run the following command:

```bash
streamlit run app.py
```

### To Do

- Add possibility to use hough transform to aid in line detection and inclusion counting (see https://github.com/ieferreira/DigitalPetrography)
- Solve issue with crashing HED algorithm on second run

## Author

Iván E. Ferreira - Unal Bogotá

## License

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
