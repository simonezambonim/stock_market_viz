# Stock visualization

This script allows to visualize a specific asset and some indicators in different periods, the aim is to have a persolnalized view of the stocks of your choice.

## Getting Started

This app is still in development and many more functionalities can be added to it! 

### Prerequisites

The packages needed are in the requirements.txt file.


### Installing

Clone the repository and install all the packages necessary:

```
cd path
vintualenv venv
cd path\venv\Scripts\activate

pip install -r requirements.txt 
```

Use the following command to run the application:

```
streamlit run stock_viz.py
```

If you have problems installing TA-lib, check a full guide (here).[https://blog.quantinsti.com/install-ta-lib-python/]


## Built With

* [Streamlit](https://docs.streamlit.io/api.html) - The web framework 
* [Plotly](https://plotly.com/python/) - Interactive plots
* [TAlib](https://mrjbq7.github.io/ta-lib/)