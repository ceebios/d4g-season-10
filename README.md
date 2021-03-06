<p float="left">
<img src="https://dataforgood.fr/img/logo-dfg-new2.png" height="100" width="100" >
<img src="https://www.bing.com/th?id=AMMS_S_d6202e39-67f1-0881-9ed2-84dccd24401c&w=110&h=110&c=7&rs=1&qlt=95&pcl=f9f9f9&o=6&cdv=1&dpr=1.12&pid=16.1g" height="100" width="100" >
</p>

# Data4Good Season 10 + Ceebios: Biomimicry image search


## Tools
* [Github Kanban](https://github.com/ceebios/d4g-season-10/projects/1) - Project management (Kanban)
* [Drive](https://drive.google.com/drive/folders/1Cuofzm6OMu10irDNZYLIq_-9LQYiMp7p?usp=sharing) - 15Gb shared Google drive space
* [Miro](https://miro.com/app/board/uXjVOEkuccY=/?invite_link_id=929630349930) - brainstorming
* [Google Sheet](https://docs.google.com/spreadsheets/d/1qRU3aAArR5m_HRKkHwq1FvMkPpFYBqLx7n2IiI9EUc8/edit?usp=sharing) - Excel style collaboration

## Getting started
Clone this repo:
```
git clone https://github.com/ceebios/d4g-season-10.git
```

### Frontend
If you want to work on the front end (web design) and you are familiar (or want to learn)  React and Javascript this is the place for you.
* Install Node.js and NPM: [link](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm)
* Install the 'frontend' source dependencies:
```
cd frontend
npm install
```
* Check it runs ok
```
cd frontend
npm start
```

### Backend
If you want to work on the back end (Data science pack - Python, Pytorch, HuggingFace, FastAPI) this is the place for you.

* We'd recommend creating a new virtual environment and installing the dependencies there manually (see requirements.in). There is no proper 'requirements.txt' file as Pytorch installation in particular can vary depending on whether you have a GPU, you use Windows/Linux or Mac or use Conda instead of Pip for package dependencies.

* Please do not try to commit Jupyter Notebooks to Git - they can be very tricky to version control. Instead you can include links to Notebooks and share the notebooks natively through Colab for example. To keep track we can list all notebooks in the provided Google sheet.
    - Note: you can still put your notebooks in a /notebooks folder inside git, which has been added to the ignores in .gitignore

* If you work with scripts rather than notebooks - you can check those in the Scripts folder

You'll see that the back end is pre-populated with a few folders already which correspond to different streams of work:
* Parsing PDFs
* Parsing XMLs
* API design
* ML methods (Image, NLP, etc.)

### Data
All data is stored in the Google drive, until we run out of space. If and when that happens it will still be in Google drive probably but we'll pay for a subscription increasing capacity to 100Gb.
